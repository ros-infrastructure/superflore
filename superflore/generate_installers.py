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

import os

from rosinstall_generator.distro import get_distro
from rosinstall_generator.distro import get_package_names

from superflore.exceptions import UnresolvedDependency

from superflore.utils import err
from superflore.utils import get_pkg_version
from superflore.utils import ok
from superflore.utils import warn


def generate_installers(distro_name, overlay, gen_pkg, preserve_existing=True):
    distro = get_distro(distro_name)
    pkg_names = get_package_names(distro)
    total = float(len(pkg_names[0]))
    borkd_pkgs = dict()
    changes = []
    installers = []
    bad_installers = []
    succeeded = 0
    failed = 0

    for i, pkg in enumerate(sorted(pkg_names[0])):
        version = get_pkg_version(distro, pkg)
        ebuild_name =\
            '/ros-{0}/{1}/{1}-{2}.ebuild'.format(distro_name, pkg, version)
        ebuild_name = overlay.repo.repo_dir + ebuild_name
        ebuild_exists = os.path.exists(ebuild_name)
        patch_path = '/ros-{}/{}/files'.format(distro_name, pkg)
        patch_path = overlay.repo.repo_dir + patch_path
        percent = '%.1f' % (100 * (float(i) / total))

        if preserve_existing and ebuild_exists:
            skip_msg = 'Ebuild for package '
            skip_msg += '{0} up to date, skipping...'.format(pkg)
            status = '{0}%: {1}'.format(percent, skip_msg)
            ok(status)
            succeeded = succeeded + 1
            continue
        try:
            current = gen_pkg(overlay=overlay, pkg=pkg, distro=distro)
            success_msg = 'Successfully generated installer for package'
            ok('{0}%: {1} \'{2}\'.'.format(percent, success_msg, pkg))
            succeeded = succeeded + 1
            changes.append('*{0} --> {1}*'.format(pkg, version))
            installers.append(current)
        except (KeyError, UnresolvedDependency):
            failed_msg = 'Failed to generate installer'
            err("{0}%: {1} for package {2}!".format(percent, failed_msg, pkg))
            bad_installers.append(pkg)
            failed = failed + 1
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
