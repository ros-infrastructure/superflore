import hashlib
import itertools
import os
import re
import tarfile
from typing import Dict, Iterable, Set

from rosdistro import DistributionFile
from rosdistro.dependency_walker import DependencyWalker
from rosdistro.rosdistro import RosPackage
from rosinstall_generator.distro import _generate_rosinstall

from superflore.exceptions import UnresolvedDependency
from superflore.generators.nix.nix_derivation import NixDerivation, NixLicense
from superflore.PackageMetadata import PackageMetadata
from superflore.utils import (download_file, get_distro_condition_context,
                              get_distros, get_pkg_version, info, resolve_dep,
                              retry_on_exception, warn)


class NixPackage:
    """
    Retrieves the required metadata to define a Nix package derivation.
    """

    def __init__(self, name: str, distro: DistributionFile, tar_dir: str,
                 sha256_cache: Dict[str, str], all_pkgs: Set[str]) -> None:
        self.distro = distro
        self._all_pkgs = all_pkgs

        pkg = distro.release_packages[name]
        repo = distro.repositories[pkg.repository_name].release_repository
        ros_pkg = RosPackage(name, repo)

        rosinstall = _generate_rosinstall(name, repo.url,
                                          repo.get_release_tag(name), True)

        normalized_name = NixPackage.normalize_name(name)
        version = get_pkg_version(distro, name)
        src_uri = rosinstall[0]['tar']['uri']

        archive_path = os.path.join(tar_dir, '{}-{}-{}.tar.gz'
                                    .format(self.normalize_name(name),
                                            version, distro.name))

        downloaded_archive = False
        if os.path.exists(archive_path):
            info("using cached archive for package '{}'...".format(name))
        else:
            info("downloading archive version for package '{}'..."
                 .format(name))
            retry_on_exception(download_file, src_uri, archive_path,
                               retry_msg="network error downloading '{}'".format(src_uri),
                               error_msg="failed to download archive for '{}'".format(name))
            downloaded_archive = True

        if downloaded_archive or archive_path not in sha256_cache:
            sha256_cache[archive_path] = hashlib.sha256(
                open(archive_path, 'rb').read()).hexdigest()
        src_sha256 = sha256_cache[archive_path]

        # We already have the archive, so try to extract package.xml from it.
        # This is much faster than downloading it from GitHub.
        package_xml_regex = re.compile(r'^[^/]+/package\.xml$')
        package_xml = None
        archive = tarfile.open(archive_path, 'r|*')
        for file in archive:
            if package_xml_regex.match(file.name):
                package_xml = archive.extractfile(file).read()
                break
        # Fallback to the standard method of fetching package.xml
        if package_xml is None:
            warn("failed to extract package.xml from archive")
            package_xml = retry_on_exception(ros_pkg.get_package_xml,
                                             distro.name)

        metadata = PackageMetadata(
            package_xml, NixPackage._get_condition_context(distro.name))

        dep_walker = DependencyWalker(distro,
                                      get_distro_condition_context(
                                          distro.name))

        buildtool_deps = dep_walker.get_depends(pkg.name, "buildtool")
        buildtool_export_deps = dep_walker.get_depends(pkg.name, "buildtool_export")
        build_deps = dep_walker.get_depends(pkg.name, "build")
        build_export_deps = dep_walker.get_depends(pkg.name, "build_export")
        exec_deps = dep_walker.get_depends(pkg.name, "exec")
        test_deps = dep_walker.get_depends(pkg.name, "test")

        self.unresolved_dependencies = set()

        # buildtool_depends are added to buildInputs and nativeBuildInputs. Some
        # (such as CMake) have binaries that need to run at build time (and
        # therefore need to be in nativeBuildInputs. Others (such as
        # ament_cmake_*) need to be added to CMAKE_PREFIX_PATH and therefore
        # need to be in buildInputs. There is no easy way to distinguish these
        # two cases, so they are added to both, which generally works fine.
        build_inputs = set(self._resolve_dependencies(build_deps | buildtool_deps))
        propagated_build_inputs = self._resolve_dependencies(exec_deps | build_export_deps | buildtool_export_deps)
        build_inputs -= propagated_build_inputs

        check_inputs = self._resolve_dependencies(test_deps)
        check_inputs -= build_inputs

        native_build_inputs = self._resolve_dependencies(buildtool_deps | buildtool_export_deps)

        self._derivation = NixDerivation(
            name=normalized_name,
            version=version,
            src_url=src_uri,
            src_sha256=src_sha256,
            description=metadata.description,
            licenses=map(NixLicense, metadata.upstream_license),
            distro_name=distro.name,
            build_type=metadata.build_type,
            build_inputs=build_inputs,
            propagated_build_inputs=propagated_build_inputs,
            check_inputs=check_inputs,
            native_build_inputs=native_build_inputs)

    def _resolve_dependencies(self, deps: Iterable[str]) -> Set[str]:
        return set(itertools.chain.from_iterable(
            map(self._resolve_dependency, deps)))

    def _resolve_dependency(self, d: str) -> Iterable[str]:
        try:
            return (self.normalize_name(d),) \
                if d in self._all_pkgs \
                else resolve_dep(d, 'nix')[0]
        except UnresolvedDependency:
            self.unresolved_dependencies.add(d)
            return tuple()

    @staticmethod
    def _get_ros_version(distro):
        distros = get_distros()
        return 2 if distro not in distros \
            else int(distros[distro]['distribution_type'][len('ros'):])

    @staticmethod
    def _get_ros_python_version(distro):
        return 2 if distro in ['melodic'] else 3

    @staticmethod
    def _get_condition_context(distro):
        context = dict()
        context["ROS_OS_OVERRIDE"] = "nixos"
        context["ROS_DISTRO"] = distro
        context["ROS_VERSION"] = str(NixPackage._get_ros_version(distro))
        context["ROS_PYTHON_VERSION"] = str(
            NixPackage._get_ros_python_version(distro))
        return context

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Convert underscores to dashes to match normal Nix package naming
        conventions.

        :param name: original package name
        :return: normalized package name
        """
        return name.replace('_', '-')

    @property
    def derivation(self):
        if self.unresolved_dependencies:
            raise UnresolvedDependency("failed to resolve dependencies!")

        return self._derivation
