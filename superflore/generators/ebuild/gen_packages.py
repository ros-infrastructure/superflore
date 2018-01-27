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
from superflore.utils import err
from superflore.utils import get_pkg_version
from superflore.utils import make_dir
from superflore.utils import ok
from superflore.utils import warn
import xmltodict

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
    has_patches = os.path.exists(patch_path)
    pkg_names = get_package_names(distro)[0]

    if pkg not in pkg_names:
        raise RuntimeError("Unknown package '%s'" % (pkg))
    # otherwise, remove a (potentially) existing ebuild.
    prefix = '{0}/ros-{1}/{2}/'.format(overlay.repo.repo_dir, distro.name, pkg)
    existing = glob.glob('%s*.ebuild' % prefix)
    previous_version = None
    if preserve_existing and os.path.isfile(ebuild_name):
        ok("ebuild for package '%s' up to date, skipping..." % pkg)
        return None, []
    elif existing:
        overlay.repo.remove_file(existing[0])
        previous_version = existing[0].lstrip(prefix).rstrip('.ebuild')
        manifest_file = '{0}/ros-{1}/{2}/Manifest'.format(
            overlay.repo.repo_dir, distro.name, pkg
        )
        overlay.repo.remove_file(manifest_file)
    try:
        current = gentoo_installer(distro, pkg, has_patches)
        current.ebuild.name = pkg
    except Exception as e:
        err('Failed to generate installer for package {}!'.format(pkg))
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
        return None, current.ebuild.get_unresolved()
    except KeyError as ke:
        err("Failed to parse data for package {}!".format(pkg))
        raise ke
    make_dir(
        "{}/ros-{}/{}".format(overlay.repo.repo_dir, distro.name, pkg)
    )
    success_msg = 'Successfully generated installer for package'
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
    return current, previous_version


def _gen_metadata_for_package(distro, pkg_name, pkg,
                              repo, ros_pkg, pkg_rosinstall):
    pkg_metadata_xml = metadata_xml()
    try:
        pkg_xml = ros_pkg.get_package_xml(distro.name)
    except Exception:
        warn("fetch metadata for package {}".format(pkg_name))
        return pkg_metadata_xml
    pkg_fields = xmltodict.parse(pkg_xml)
    if 'description' in pkg_fields['package']:
        # fill longdescription, if available (defaults to "NONE").
        pkg_metadata_xml.longdescription = pkg_fields['package']['description']
    if 'maintainer' in pkg_fields['package']:
        if isinstance(pkg_fields['package']['maintainer'], list):
            pkg_metadata_xml.upstream_email =\
                pkg_fields['package']['maintainer'][0]['@email']
            pkg_metadata_xml.upstream_name =\
                pkg_fields['package']['maintainer'][0]['#text']
        elif isinstance(pkg_fields['package']['maintainer']['@email'], list):
            pkg_metadata_xml.upstream_email =\
                pkg_fields['package']['maintainer'][0]['@email']
            pkg_metadata_xml.upstream_name =\
                pkg_fields['package']['maintainer'][0]['#text']
        else:
            pkg_metadata_xml.upstream_email =\
                pkg_fields['package']['maintainer']['@email']
            if '#text' in pkg_fields['package']['maintainer']:
                pkg_metadata_xml.upstream_name =\
                    pkg_fields['package']['maintainer']['#text']
            else:
                pkg_metadata_xml.upstream_name = "UNKNOWN"

        pkg_metadata_xml.upstream_bug_url =\
            repo.url.replace("-release", "").replace(".git", "/issues")
    return pkg_metadata_xml


def _gen_ebuild_for_package(distro, pkg_name, pkg,
                            repo, ros_pkg, pkg_rosinstall):
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

    # parse throught package xml
    try:
        pkg_xml = ros_pkg.get_package_xml(distro.name)
    except Exception as e:
        warn("fetch metadata for package {}".format(pkg_name))
        return pkg_ebuild
    pkg_fields = xmltodict.parse(pkg_xml)

    pkg_ebuild.upstream_license = pkg_fields['package']['license']
    pkg_ebuild.description = pkg_fields['package']['description']
    if isinstance(pkg_ebuild.description, str):
        pkg_ebuild.description = pkg_ebuild.description.replace('`', "")
    if len(pkg_ebuild.description) > 80:
        pkg_ebuild.description = pkg_ebuild.description[:80]
    try:
        if 'url' not in pkg_fields['package']:
            warn("no website field for package {}".format(pkg_name))
        elif isinstance(pkg_fields['package']['url'], str):
            pkg_ebuild.homepage = pkg_fields['package']['url']
        elif '@type' in pkg_fields['package']['url']:
            if pkg_fields['package']['url']['@type'] == 'website':
                if '#text' in pkg_fields['package']['url']:
                    pkg_ebuild.homepage = pkg_fields['package']['url']['#text']
        else:
            warn("failed to parse website for package {}".format(pkg_name))
    except TypeError as e:
        warn("failed to parse website package {}: {}".format(pkg_name, e))
    return pkg_ebuild


class gentoo_installer(object):
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
