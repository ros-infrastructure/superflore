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

import sys
import os
import xmltodict
import glob
from termcolor import colored

from rosinstall_generator.distro import get_distro, get_package_names
from rosinstall_generator.distro import _generate_rosinstall
from rosdistro.dependency_walker import DependencyWalker
from rosdistro.manifest_provider import get_release_tag
from rosdistro.rosdistro import RosPackage

from .yocto_recipe import yoctoRecipe
from superflore.exceptions import UnresolvedDependency, NoPkgXml

org = "Open Source Robotics Foundation"
org_license = "BSD"


def warn(string):
    print(colored('>>>> {0}'.format(string), 'yellow'))


def ok(string):
    print(colored('>>>> {0}'.format(string), 'green'))


def err(string):
    print(colored('!!!! {0}'.format(string), 'red'))


def info(string):
    print(colored('>>>> {0}'.format(string), 'cyan'))


def make_dir(dirname):
    try:
        os.makedirs(dirname)
    except:
        pass


def get_pkg_version(distro, pkg_name):
    pkg = distro.release_packages[pkg_name]
    repo = distro.repositories[pkg.repository_name].release_repository
    maj_min_patch, deb_inc = repo.version.split('-')
    if deb_inc != '0':
        return '{0}-r{1}'.format(maj_min_patch, deb_inc)
    return maj_min_patch


def generate_installers(distro_name, overlay, preserve_existing=True):
    make_dir("recipes-ros-{}".format(distro_name))
    distro = get_distro(distro_name)
    pkg_names = get_package_names(distro)
    total = float(len(pkg_names[0]))
    borkd_pkgs = dict()
    changes = []
    installers = []
    succeeded = 0
    failed = 0

    for i, pkg in enumerate(sorted(pkg_names[0])):
        version = get_pkg_version(distro, pkg)
        """
        recipe_exists = os.path.exists(
            'ros-{}/{}/{}-{}.ebuild'.format(distro_name, pkg, pkg, version))
        patch_path = 'ros-{}/{}/files'.format(distro_name, pkg)
        has_patches = os.path.exists(patch_path)
        """
        percent = '%.1f' % (100 * (float(i) / total))

        """
        if preserve_existing and ebuild_exists:
            skip_msg = 'Ebuild for package '
            skip_msg += '{0} up to date, skipping...'.format(pkg)
            status = '{0}%: {1}'.format(percent, skip_msg)
            ok(status)
            succeeded = succeeded + 1
            continue
        """
        # otherwise, remove a (potentially) existing recipe.
        existing = glob.glob(
            'recipes-ros-{0}/{1}/*.bb'.format(distro_name, pkg)
        )
        if len(existing) > 0:
            overlay.remove_file(existing[0])
        try:
            current = oe_installer(distro, pkg)
            current.recipe.name = pkg.replace('_', '-')
        except Exception as e:
            err('Failed to generate installer for package {}!'.format(pkg))
            err('  exception: {0}'.format(e))
            failed = failed + 1
            continue
        try:
            info(' downloading archive version for package \'%s\'' % pkg)
            current.recipe.downloadArchive()
            recipe_text = current.recipe_text()
        except NoPkgXml:
            err('  No package.xml file for pkg \'{0}\'!'.format(pkg))
            err("Failed to generate installer for package {}!".format(pkg))
            failed = failed + 1
            continue  # cannot generate package
        except UnresolvedDependency:
            dep_err = 'Failed to resolve required dependencies for'
            err("{0} package {1}!".format(dep_err, pkg))
            unresolved = current.recipe.get_unresolved()
            borkd_pkgs[pkg] = list()
            for dep in unresolved:
                err(" unresolved: \"{}\"".format(dep))
                borkd_pkgs[pkg].append(dep)
            err("Failed to generate installer for package {}!".format(pkg))
            failed = failed + 1
            continue  # do not generate an incomplete ebuild
        """
        except KeyError:
            err("Failed to parse data for package {}!".format(pkg))
            unresolved = current.recipe.get_unresolved()
            err("Failed to generate installer for package {}!".format(pkg))
            failed = failed + 1
            continue  # do not generate an incomplete ebuild
        """
        make_dir(
            "recipes-ros-{}/{}".format(distro_name, pkg.replace('_', '-'))
        )
        success_msg = 'Successfully generated installer for package'
        ok('{0}%: {1} \'{2}\'.'.format(percent, success_msg, pkg))
        succeeded = succeeded + 1

        # try:
        recipe_name = '{0}/{1}/{1}_{2}'.format(
            distro_name,
            pkg.replace('_', '-'),
            version
        )
        recipe_file = open('recipes-ros-{0}.bb'.format(recipe_name), "w")

        recipe_file.write(recipe_text)
        changes.append('*{0} --> {1}*'.format(pkg, version))
        """
        except Exception as e:
            err("Failed to write recipe to disk!")
            err(" exception: %s" % (e))
            installers.append(current)
            failed_msg = 'Failed to generate installer'
            err("{0}%: {1} for package {2}!".format(percent, failed_msg, pkg))
            bad_installers.append(current)
            failed = failed + 1
        """
        results = 'Generated {0} / {1}'.format(succeeded, failed + succeeded)
        results += ' for distro {0}'.format(distro_name)
    print("------ {0} ------".format(results))
    print()

    if len(borkd_pkgs) > 0:
        warn("Unresolved:")
        for broken in borkd_pkgs.keys():
            warn("{}:".format(broken))
            warn("  {}".format(borkd_pkgs[broken]))

    return installers, borkd_pkgs, changes


def _gen_recipe_for_package(distro, pkg_name, pkg,
                            repo, ros_pkg, pkg_rosinstall):
    pkg_recipe = yoctoRecipe()
    pkg_recipe.name = pkg_name
    pkg_recipe.distro = distro.name
    pkg_recipe.src_uri = pkg_rosinstall[0]['tar']['uri']
    pkg_dep_walker = DependencyWalker(distro)

    pkg_buildtool_deps = pkg_dep_walker.get_depends(pkg_name, "buildtool")
    pkg_build_deps = pkg_dep_walker.get_depends(pkg_name, "build")
    pkg_run_deps = pkg_dep_walker.get_depends(pkg_name, "run")

    # add run dependencies
    for rdep in pkg_run_deps:
        pkg_recipe.add_depend(rdep)

    # add build dependencies
    for bdep in pkg_build_deps:
        pkg_recipe.add_depend(bdep)

    # add build tool dependencies
    for tdep in pkg_buildtool_deps:
        pkg_recipe.add_depend(tdep)

    # parse throught package xml
    try:
        pkg_xml = ros_pkg.get_package_xml(distro.name)
    except Exception as e:
        warn("fetch metadata for package {}".format(pkg_name))
        return pkg_recipe
    pkg_fields = xmltodict.parse(pkg_xml)

    pkg_recipe.pkg_xml = pkg_xml
    pkg_recipe.license = pkg_fields['package']['license']
    pkg_recipe.description = pkg_fields['package']['description']
    if not isinstance(pkg_recipe.description, str):
        if '#text' in pkg_recipe.description:
            pkg_recipe.description = pkg_recipe.description['#text']
        else:
            pkg_recipe.description = "None"
    pkg_recipe.description = pkg_recipe.description.replace('`', "")
    if len(pkg_recipe.description) > 80:
        pkg_recipe.description = pkg_recipe.description[:80]
    try:
        if 'url' not in pkg_fields['package']:
            warn("no website field for package {}".format(pkg_name))
        elif sys.version_info <= (3, 0):
                pkg_recipe.recipe = pkg_fields['package']['url'].decode()
        elif isinstance(pkg_fields['package']['url'], str):
            pkg_recipe.homepage = pkg_fields['package']['url']
        elif '@type' in pkg_fields['package']['url']:
            if pkg_fields['package']['url']['@type'] == 'website':
                if '#text' in pkg_fields['package']['url']:
                    pkg_recipe.homepage = pkg_fields['package']['url']['#text']
        else:
            warn("failed to parse website for package {}".format(pkg_name))
    except TypeError as e:
        warn("failed to parse website package {}: {}".format(pkg_name, e))
    return pkg_recipe


class oe_installer(object):
    def __init__(self, distro, pkg_name, has_patches=False):
        pkg = distro.release_packages[pkg_name]
        repo = distro.repositories[pkg.repository_name].release_repository
        ros_pkg = RosPackage(pkg_name, repo)

        pkg_rosinstall =\
            _generate_rosinstall(pkg_name, repo.url,
                                 get_release_tag(repo, pkg_name), True)

        self.recipe =\
            _gen_recipe_for_package(distro, pkg_name,
                                    pkg, repo, ros_pkg, pkg_rosinstall)

    def recipe_text(self):
        return self.recipe.get_recipe_text(org, org_license)
