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

from catkin_pkg.package import InvalidPackage
from rosdistro.dependency_walker import DependencyWalker
from rosdistro.manifest_provider import get_release_tag
from rosdistro.rosdistro import RosPackage
from rosinstall_generator.distro import _generate_rosinstall
from rosinstall_generator.distro import get_package_names
from superflore.exceptions import NoPkgXml
from superflore.generators.bitbake.yocto_recipe import yoctoRecipe
from superflore.utils import err
from superflore.utils import get_pkg_version
from superflore.utils import make_dir
from superflore.utils import ok
from superflore.utils import retry_on_exception

org = "Open Source Robotics Foundation"


def regenerate_pkg(
    overlay, pkg, distro, preserve_existing, tar_dir, md5_cache, sha256_cache,
    skip_keys
):
    pkg_names = get_package_names(distro)[0]
    if pkg not in pkg_names:
        yoctoRecipe.not_generated_recipes.add(pkg)
        raise RuntimeError("Unknown package '%s'" % pkg)
    try:
        version = get_pkg_version(distro, pkg, is_oe=True)
    except KeyError as ke:
        yoctoRecipe.not_generated_recipes.add(pkg)
        raise ke
    repo_dir = overlay.repo.repo_dir
    component_name = yoctoRecipe.convert_to_oe_name(
        distro.release_packages[pkg].repository_name)
    recipe = yoctoRecipe.convert_to_oe_name(pkg)
    # check for an existing recipe
    glob_pattern = '{0}/generated-recipes-{1}/{2}/{3}*.bb'.format(
        repo_dir,
        distro.name,
        component_name,
        recipe
    )
    existing = glob.glob(glob_pattern)
    if preserve_existing and existing:
        ok("recipe for package '%s' up to date, skipping..." % pkg)
        yoctoRecipe.not_generated_recipes.add(pkg)
        return None, []
    elif existing:
        overlay.repo.remove_file(existing[0], True)
    try:
        current = oe_installer(
            distro, pkg, tar_dir, md5_cache, sha256_cache, skip_keys
        )
    except InvalidPackage as e:
        err('Invalid package: ' + str(e))
        yoctoRecipe.not_generated_recipes.add(pkg)
        return None, []
    except Exception as e:
        err('Failed generating installer for {}! {}'.format(pkg, str(e)))
        yoctoRecipe.not_generated_recipes.add(pkg)
        return None, []
    try:
        recipe_text = current.recipe_text()
    except NoPkgXml as nopkg:
        err("Could not fetch pkg! {}".format(str(nopkg)))
        yoctoRecipe.not_generated_recipes.add(pkg)
        return None, []
    except KeyError as ke:
        err("Failed to parse data for package {}! {}".format(pkg, str(ke)))
        yoctoRecipe.not_generated_recipes.add(pkg)
        return None, []
    make_dir(
        "{0}/generated-recipes-{1}/{2}".format(
            repo_dir,
            distro.name,
            component_name
        )
    )
    success_msg = 'Successfully generated installer for package'
    ok('{0} \'{1}\'.'.format(success_msg, pkg))
    recipe_file_name = '{0}/generated-recipes-{1}/{2}/{3}_{4}.bb'.format(
        repo_dir,
        distro.name,
        component_name,
        recipe,
        version
    )
    try:
        with open('{0}'.format(recipe_file_name), "w") as recipe_file:
            ok('Writing recipe {0}'.format(recipe_file_name))
            recipe_file.write(recipe_text)
            yoctoRecipe.generated_components.add(component_name)
            yoctoRecipe.generated_recipes[recipe] = (version, component_name)
    except Exception:
        err("Failed to write recipe to disk!")
        yoctoRecipe.not_generated_recipes.add(pkg)
        return None, []
    return current, []


def _gen_recipe_for_package(
    distro, pkg_name, pkg, repo, ros_pkg,
    pkg_rosinstall, tar_dir, md5_cache, sha256_cache, skip_keys
):
    pkg_names = get_package_names(distro)
    pkg_dep_walker = DependencyWalker(distro,
                                      evaluate_condition_context=os.environ)
    pkg_buildtool_deps = pkg_dep_walker.get_depends(pkg_name, "buildtool")
    pkg_build_deps = pkg_dep_walker.get_depends(pkg_name, "build")
    pkg_build_export_deps = pkg_dep_walker.get_depends(
        pkg_name, "build_export")
    pkg_buildtool_export_deps = pkg_dep_walker.get_depends(
        pkg_name, "buildtool_export")
    pkg_exec_deps = pkg_dep_walker.get_depends(pkg_name, "exec")
    pkg_test_deps = pkg_dep_walker.get_depends(pkg_name, "test")
    src_uri = pkg_rosinstall[0]['tar']['uri']

    # parse through package xml
    err_msg = 'Failed to fetch metadata for package {}'.format(pkg_name)
    pkg_xml = retry_on_exception(ros_pkg.get_package_xml, distro.name,
                                 retry_msg='Could not get package xml!',
                                 error_msg=err_msg)

    pkg_recipe = yoctoRecipe(
        pkg.repository_name,
        len(ros_pkg.repository.package_names),
        pkg_name,
        pkg_xml,
        distro,
        src_uri,
        tar_dir,
        md5_cache,
        sha256_cache,
        skip_keys,
    )
    # add build dependencies
    for bdep in pkg_build_deps:
        pkg_recipe.add_build_depend(bdep, bdep in pkg_names[0])

    # add build tool dependencies
    for btdep in pkg_buildtool_deps:
        pkg_recipe.add_buildtool_depend(btdep, btdep in pkg_names[0])

    # add export dependencies
    for edep in pkg_build_export_deps:
        pkg_recipe.add_export_depend(edep, edep in pkg_names[0])

    # add buildtool export dependencies
    for btedep in pkg_buildtool_export_deps:
        pkg_recipe.add_buildtool_export_depend(btedep, btedep in pkg_names[0])

    # add exec dependencies
    for xdep in pkg_exec_deps:
        pkg_recipe.add_run_depend(xdep, xdep in pkg_names[0])

    # add test dependencies
    for tdep in pkg_test_deps:
        pkg_recipe.add_test_depend(tdep, tdep in pkg_names[0])

    return pkg_recipe


class oe_installer(object):
    def __init__(
        self, distro, pkg_name, tar_dir, md5_cache, sha256_cache, skip_keys
    ):
        pkg = distro.release_packages[pkg_name]
        repo = distro.repositories[pkg.repository_name].release_repository
        ros_pkg = RosPackage(pkg_name, repo)

        pkg_rosinstall = _generate_rosinstall(
            pkg_name, repo.url, get_release_tag(repo, pkg_name), True
        )

        self.recipe = _gen_recipe_for_package(
            distro, pkg_name, pkg, repo, ros_pkg, pkg_rosinstall,
            tar_dir, md5_cache, sha256_cache, skip_keys
        )

    def recipe_text(self):
        return self.recipe.get_recipe_text(org)
