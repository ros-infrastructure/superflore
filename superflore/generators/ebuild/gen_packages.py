# Copyright 2017 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import os

from rosdistro.dependency_walker import DependencyWalker
from rosdistro.manifest_provider import get_release_tag
from rosdistro.rosdistro import RosPackage
from rosinstall_generator.distro import _generate_rosinstall
from rosinstall_generator.distro import get_package_names
from superflore.exceptions import UnresolvedDependency
from superflore.generators.ebuild.ebuild import Ebuild
from superflore.generators.ebuild.metadata_xml import metadata_xml
from superflore.PackageMetadata import PackageMetadata
from superflore.utils import err
from superflore.utils import get_distros
from superflore.utils import get_pkg_version
from superflore.utils import make_dir
from superflore.utils import ok
from superflore.utils import retry_on_exception
from superflore.utils import warn

# TODO(allenh1): This is a blacklist of things that
# do not yet support Python 3. This will be updated
# on an as-needed basis until a better solution is
# found (CI?).

no_python3 = ['tf']

org = "Open Source Robotics Foundation"
org_license = "BSD"


def regenerate_pkg(overlay, pkg, distro, preserve_existing=False):
    version = get_pkg_version(distro, pkg)
    ebuild_name =\
        '/ros-{0}/{1}/{1}-{2}.ebuild'.format(distro.name, pkg, version)
    ebuild_name = overlay.repo.repo_dir + ebuild_name
    patch_path = '/ros-{}/{}/files'.format(distro.name, pkg)
    patch_path = overlay.repo.repo_dir + patch_path
    is_ros2 = get_distros()[distro.name]['distribution_type'] == 'ros2'
    has_patches = os.path.exists(patch_path)
    pkg_names = get_package_names(distro)[0]
    patches = None
    if os.path.exists(patch_path):
        patches = [
            f for f in glob.glob('%s/*.patch' % patch_path)
        ]
    if pkg not in pkg_names:
        raise RuntimeError("Unknown package '%s'" % (pkg))
    # otherwise, remove a (potentially) existing ebuild.
    prefix = '{0}/ros-{1}/{2}/'.format(overlay.repo.repo_dir, distro.name, pkg)
    existing = glob.glob('%s*.ebuild' % prefix)
    previous_version = None
    if preserve_existing and os.path.isfile(ebuild_name):
        ok("ebuild for package '%s' up to date, skipping..." % pkg)
        return None, [], None
    elif existing:
        overlay.repo.remove_file(existing[0])
        previous_version = existing[0].lstrip(prefix).rstrip('.ebuild')
        manifest_file = '{0}/ros-{1}/{2}/Manifest'.format(
            overlay.repo.repo_dir, distro.name, pkg
        )
        overlay.repo.remove_file(manifest_file)
    try:
        current = gentoo_ebuild(distro, pkg, has_patches)
        current.ebuild.name = pkg
        current.ebuild.patches = patches
        current.ebuild.is_ros2 = is_ros2
    except Exception as e:
        err('Failed to generate ebuild for package {}!'.format(pkg))
        raise e
    try:
        ebuild_text = current.ebuild_text()
        metadata_text = current.metadata_text()
    except UnresolvedDependency:
        dep_err = 'Failed to resolve required dependencies for'
        err("{0} package {1}!".format(dep_err, pkg))
        unresolved = current.ebuild.get_unresolved()
        for dep in unresolved:
            err(" unresolved: \"{}\"".format(dep))
        return None, current.ebuild.get_unresolved(), None
    except KeyError as ke:
        err("Failed to parse data for package {}!".format(pkg))
        raise ke
    make_dir(
        "{}/ros-{}/{}".format(overlay.repo.repo_dir, distro.name, pkg)
    )
    success_msg = 'Successfully generated ebuild for package'
    ok('{0} \'{1}\'.'.format(success_msg, pkg))

    try:
        ebuild_file = '{0}/ros-{1}/{2}/{2}-{3}.ebuild'.format(
            overlay.repo.repo_dir,
            distro.name, pkg, version
        )
        ebuild_file = open(ebuild_file, "w")
        metadata_file = '{0}/ros-{1}/{2}/metadata.xml'.format(
            overlay.repo.repo_dir,
            distro.name, pkg
        )
        metadata_file = open(metadata_file, "w")
        ebuild_file.write(ebuild_text)
        metadata_file.write(metadata_text)
    except Exception as e:
        err("Failed to write ebuild/metadata to disk!")
        raise e
    return current, previous_version, pkg


def _gen_metadata_for_package(
    distro, pkg_name, pkg, repo, ros_pkg, pkg_rosinstall
):
    pkg_metadata_xml = metadata_xml()
    try:
        pkg_xml = retry_on_exception(ros_pkg.get_package_xml, distro.name)
    except Exception:
        warn("fetch metadata for package {}".format(pkg_name))
        return pkg_metadata_xml
    pkg = PackageMetadata(pkg_xml)
    pkg_metadata_xml.upstream_email = pkg.upstream_email
    pkg_metadata_xml.upstream_name = pkg.upstream_name
    pkg_metadata_xml.longdescription = pkg.longdescription
    pkg_metadata_xml.upstream_bug_url =\
        repo.url.replace("-release", "").replace(".git", "/issues")
    return pkg_metadata_xml


def _gen_ebuild_for_package(
    distro, pkg_name, pkg, repo, ros_pkg, pkg_rosinstall
):
    pkg_ebuild = Ebuild()

    pkg_ebuild.distro = distro.name
    pkg_ebuild.src_uri = pkg_rosinstall[0]['tar']['uri']
    pkg_names = get_package_names(distro)
    pkg_dep_walker = DependencyWalker(distro)

    pkg_buildtool_deps = pkg_dep_walker.get_depends(pkg_name, "buildtool")
    pkg_build_deps = pkg_dep_walker.get_depends(pkg_name, "build")
    pkg_run_deps = pkg_dep_walker.get_depends(pkg_name, "run")
    pkg_test_deps = pkg_dep_walker.get_depends(pkg_name, "test")

    pkg_keywords = ['x86', 'amd64', 'arm', 'arm64']

    # add run dependencies
    for rdep in pkg_run_deps:
        pkg_ebuild.add_run_depend(rdep, rdep in pkg_names[0])

    # add build dependencies
    for bdep in pkg_build_deps:
        pkg_ebuild.add_build_depend(bdep, bdep in pkg_names[0])

    # add build tool dependencies
    for tdep in pkg_buildtool_deps:
        pkg_ebuild.add_build_depend(tdep, tdep in pkg_names[0])

    # add test dependencies
    for test_dep in pkg_test_deps:
        pkg_ebuild.add_test_depend(test_dep, test_dep in pkg_names[0])

    # add keywords
    for key in pkg_keywords:
        pkg_ebuild.add_keyword(key)

    # parse through package xml
    try:
        pkg_xml = retry_on_exception(ros_pkg.get_package_xml, distro.name)
    except Exception:
        warn("fetch metadata for package {}".format(pkg_name))
        return pkg_ebuild
    pkg = PackageMetadata(pkg_xml)
    pkg_ebuild.upstream_license = pkg.upstream_license
    pkg_ebuild.description = pkg.description
    pkg_ebuild.homepage = pkg.homepage
    pkg_ebuild.build_type = pkg.build_type
    return pkg_ebuild


class gentoo_ebuild(object):
    def __init__(self, distro, pkg_name, has_patches=False):
        pkg = distro.release_packages[pkg_name]
        repo = distro.repositories[pkg.repository_name].release_repository
        ros_pkg = RosPackage(pkg_name, repo)

        pkg_rosinstall =\
            _generate_rosinstall(pkg_name, repo.url,
                                 get_release_tag(repo, pkg_name), True)

        self.metadata_xml =\
            _gen_metadata_for_package(distro, pkg_name,
                                      pkg, repo, ros_pkg, pkg_rosinstall)
        self.ebuild =\
            _gen_ebuild_for_package(distro, pkg_name,
                                    pkg, repo, ros_pkg, pkg_rosinstall)
        self.ebuild.has_patches = has_patches

        if pkg_name in no_python3:
            self.ebuild.python_3 = False

    def metadata_text(self):
        return self.metadata_xml.get_metadata_text()

    def ebuild_text(self):
        return self.ebuild.get_ebuild_text(org, org_license)
