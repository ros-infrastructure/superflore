# Copyright 2017 Open Source Robotics Foundation, Inc.
# Copyright 2024 Codethink
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

from catkin_pkg.package import InvalidPackage
from rosdistro.dependency_walker import DependencyWalker
from rosdistro.manifest_provider import get_release_tag
from rosdistro.rosdistro import RosPackage
from rosinstall_generator.distro import _generate_rosinstall
from rosinstall_generator.distro import get_package_names
from superflore.exceptions import NoPkgXml
from superflore.generators.buildstream.bst_element import BstElement
from superflore.utils import err
from superflore.utils import get_pkg_version
from superflore.utils import make_dir
from superflore.utils import ok
from superflore.utils import retry_on_exception
from superflore.utils import warn

org = "Open Source Robotics Foundation"


def regenerate_pkg(
    overlay, pkg, rosdistro, preserve_existing, srcrev_cache,
    skip_keys, external_repos, generated_elements_dir = "elements/generated"
):
    pkg_names = get_package_names(rosdistro)[0]
    if pkg not in pkg_names:
        raise RuntimeError("Unknown package '%s' available packages"
                           " in selected distro: %s" %
                           (pkg, get_package_names(rosdistro)))
    try:
        version = get_pkg_version(rosdistro, pkg, is_oe=True)
    except KeyError as ke:
        raise ke
    repo_dir = overlay.repo.repo_dir
    component_name = BstElement.convert_dep_name(rosdistro.release_packages[pkg].repository_name)
    element = BstElement.convert_to_bst_name(pkg)
    # check for an existing element which was removed by clean_ros_element_dirs
    prefix = '{0}/*/{1}'.format(
        generated_elements_dir, element
    )
    existing = overlay.repo.git.status('--porcelain', '--', prefix)
    if existing:
        # The git status --porcelain output will look like this:
        # D  elements/generated/variants/ros-base.bst
        # we want just the path with filename
        if len(existing.split('\n')) > 1:
            warn('More than 1 element was output by "git status --porcelain '
                 '{0}/*/{1}": "{2}"'
                 .format(
                     generated_elements_dir,
                     element,
                     existing))
        if existing.split()[0] != 'D':
            err('Unexpected output from "git status --porcelain '
                 '{0}/*/{1}": "{2}"'
                 .format(
                     generated_elements_dir,
                     element,
                     existing))

        existing = existing.split()[1]
    else:
        # If it isn't shown in git status, it could still exist as normal
        # unchanged file when --only option is being used
        import glob
        existing = glob.glob('{0}/{1}'.format(repo_dir, prefix))
        if existing:
            if len(existing) > 1:
                err('More than 1 element was output by "git status '
                    '--porcelain '
                     '{0}/*/{1}": "{2}"'
                     .format(
                         generated_elements_dir,
                         element,
                         existing))
            existing = existing[0]

    previous_version = None
    if preserve_existing and existing:
        ok("element for package '%s' up to date, skipping..." % pkg)
        return None, [], None
    elif existing:
        overlay.repo.remove_file(existing, True)
    try:
        current = bst_element(
            rosdistro, pkg, srcrev_cache, skip_keys, repo_dir, external_repos
        )
    except InvalidPackage as e:
        err('Invalid package: ' + str(e))
        return None, [], None
    except Exception as e:
        err('Failed generating element for {}! {}'.format(pkg, str(e)))
        raise e ### debug
        return None, [], None
    try:
        element_text = current.element_text()
    except NoPkgXml as nopkg:
        err("Could not fetch pkg! {}".format(str(nopkg)))
        return None, [], None
    except KeyError as ke:
        err("Failed to parse data for package {}! {}".format(pkg, str(ke)))
        return None, [], None
    make_dir(
        "{0}/{1}/{2}".format(
            repo_dir,
            generated_elements_dir,
            component_name
        )
    )
    success_msg = 'Successfully generated element for package'
    ok('{0} \'{1}\'.'.format(success_msg, pkg))
    element_file_name = '{0}/{1}/{2}/' \
        '{3}'.format(
            repo_dir,
            generated_elements_dir,
            component_name,
            element
        )
    try:
        with open('{0}'.format(element_file_name), "w") as element_file:
            ok('Writing element {0}'.format(element_file_name))
            element_file.write(element_text)
    except Exception:
        err("Failed to write element to disk!")
        return None, [], None
    return current, previous_version, element


def _gen_element_for_package(
    rosdistro, pkg_name, pkg, repo, ros_pkg,
    pkg_rosinstall, srcrev_cache, skip_keys, repo_dir, external_repos
):
    pkg_names = get_package_names(rosdistro)
    pkg_dep_walker = DependencyWalker(rosdistro)
    pkg_buildtool_deps = pkg_dep_walker.get_depends(pkg_name, "buildtool")
    pkg_build_deps = pkg_dep_walker.get_depends(pkg_name, "build")
    pkg_build_export_deps = pkg_dep_walker.get_depends(
        pkg_name, "build_export")
    pkg_buildtool_export_deps = pkg_dep_walker.get_depends(
        pkg_name, "buildtool_export")
    pkg_exec_deps = pkg_dep_walker.get_depends(pkg_name, "exec")
    src_uri = pkg_rosinstall[0]['tar']['uri']

    # parse through package xml
    err_msg = 'Failed to fetch metadata for package {}'.format(pkg_name)
    pkg_xml = retry_on_exception(ros_pkg.get_package_xml, rosdistro.name,
                                 retry_msg='Could not get package xml!',
                                 error_msg=err_msg)

    pkg_element = BstElement(
        pkg.repository_name,
        pkg_name,
        pkg_xml,
        rosdistro,
        src_uri,
        srcrev_cache,
        skip_keys,
        repo_dir,
        external_repos,
    )
    # add build dependencies
    for bdep in pkg_build_deps:
        pkg_element.add_build_depend(bdep, rosdistro.release_packages.get(bdep))

    # add build tool dependencies
    for btdep in pkg_buildtool_deps:
        pkg_element.add_buildtool_depend(btdep, rosdistro.release_packages.get(btdep))

    # add export dependencies
    for edep in pkg_build_export_deps:
        pkg_element.add_export_depend(edep, rosdistro.release_packages.get(edep))

    # add buildtool export dependencies
    for btedep in pkg_buildtool_export_deps:
        pkg_element.add_buildtool_export_depend(btedep, rosdistro.release_packages.get(btedep))

    # add exec dependencies
    for xdep in pkg_exec_deps:
        pkg_element.add_run_depend(xdep, rosdistro.release_packages.get(xdep))

    return pkg_element


class bst_element(object):
    def __init__(
        self, rosdistro, pkg_name, srcrev_cache, skip_keys, repo_dir, external_repos
    ):
        pkg = rosdistro.release_packages[pkg_name]
        repo = rosdistro.repositories[pkg.repository_name].release_repository
        ros_pkg = RosPackage(pkg_name, repo)

        pkg_rosinstall = _generate_rosinstall(
            pkg_name, repo.url, get_release_tag(repo, pkg_name), True
        )

        self.element = _gen_element_for_package(
            rosdistro, pkg_name, pkg, repo, ros_pkg, pkg_rosinstall,
            srcrev_cache, skip_keys, repo_dir, external_repos
        )

    def element_text(self):
        return self.element.get_element_text(org)
