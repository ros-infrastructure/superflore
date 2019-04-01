# Copyright 2019 Open Source Robotics Foundation, Inc.
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
import os
from typing import Iterable

from rosdistro import DistributionFile
from rosinstall_generator.distro import get_package_names

from superflore.exceptions import NoPkgXml
from superflore.exceptions import UnresolvedDependency
from superflore.generators.nix.nix_package import NixPackage
from superflore.generators.nix.nix_package_set import NixPackageSet
from superflore.utils import err
from superflore.utils import make_dir
from superflore.utils import ok

org = "Open Source Robotics Foundation"
org_license = "BSD"


def regenerate_pkg(overlay, pkg: str, distro: DistributionFile,
                   preserve_existing: bool, tar_dir: str, sha256_cache):
    pkg_names = get_package_names(distro)[0]

    if pkg not in pkg_names:
        raise RuntimeError("Unknown package '{}'".format(pkg))

    normalized_pkg = NixPackage.normalize_name(pkg)

    package_dir = os.path.join(overlay.repo.repo_dir, distro.name,
                               normalized_pkg)
    package_file = os.path.join(package_dir, 'default.nix')
    make_dir(package_dir)

    # check for an existing package
    existing = os.path.exists(package_file)

    if preserve_existing and existing:
        ok("derivation for package '{}' up to date, skipping...".format(pkg))
        return None, []

    try:
        current = NixPackage(pkg, distro, tar_dir, sha256_cache)
    except Exception as e:
        err('Failed to generate derivation for package {}!'.format(pkg))
        raise e

    try:
        derivation_text = current.derivation.get_text(org, org_license)
    except UnresolvedDependency:
        err("'Failed to resolve required dependencies for package {}!"
            .format(pkg))
        unresolved = current.unresolved_dependencies
        for dep in unresolved:
            err(" unresolved: \"{}\"".format(dep))
        return None, unresolved
    except NoPkgXml:
        err("Could not fetch pkg!")
        return None, []
    except Exception as e:
        err('Failed to generate derivation for package {}!'.format(pkg))
        raise e

    ok("Successfully generated derivation for package '{}'.".format(pkg))
    try:
        with open('{0}'.format(package_file), "w") as recipe_file:
            recipe_file.write(derivation_text)
    except Exception as e:
        err("Failed to write derivation to disk!")
        raise e
    return current, []


def regenerate_pkg_set(overlay, distro_name: str, pkg_names: Iterable[str]):
    distro_dir = os.path.join(overlay.repo.repo_dir, distro_name)
    overlay_file = os.path.join(distro_dir, 'generated.nix')
    make_dir(distro_dir)

    package_set = NixPackageSet(pkg_names)

    try:
        with open(overlay_file, "w") as recipe_file:
            recipe_file.write(package_set.get_text(org, org_license))
    except Exception as e:
        err("Failed to write derivation to disk!")
        raise e
