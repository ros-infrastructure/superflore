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

from rosinstall_generator.distro import get_package_names
from superflore.exceptions import UnknownBuildType
from superflore.utils import err
from superflore.utils import get_pkg_version
from superflore.utils import info
from superflore.utils import ok
from superflore.utils import warn


def generate_installers(
    distro,                  # ros distro
    overlay,                 # repo instance
    gen_pkg_func,            # function to call for generating
    preserve_existing=True,  # don't regenerate if installer exists
    *args,                   # any additional args for gen_pkg_func
    **kwargs                 # any additional keyword arguments
):
    distro_name = distro.name
    pkg_names = get_package_names(distro)
    total = float(len(pkg_names[0]))
    borkd_pkgs = dict()
    changes = []
    installers = []
    bad_installers = []
    succeeded = 0
    failed = 0
    what_generating = 'recipe' if kwargs.get('is_oe', False) else 'ebuild'

    info("Generating %ss for distro '%s'" % (what_generating, distro_name))
    for i, pkg in enumerate(sorted(pkg_names[0])):
        if 'skip_keys' in kwargs and pkg in kwargs['skip_keys']:
            warn("Package '%s' is in skip-keys list, skipping..." % pkg)
            continue
        version = get_pkg_version(distro, pkg, **kwargs)
        percent = '%.1f' % (100 * (float(i) / total))
        try:
            current, current_info, installer_name = gen_pkg_func(
                overlay, pkg, distro, preserve_existing, *args
            )
            if not current:
                if current_info:
                    # we are missing dependencies
                    borkd_pkgs[pkg] = current_info
                elif preserve_existing:
                    # don't replace the installer
                    succeeded += 1
                    continue
                failed_msg = "{0}%: Failed to generate".format(percent)
                failed_msg += " %s for package '%s'!" % (what_generating, pkg)
                err(failed_msg)
                failed = failed + 1
                continue
            success_msg = 'Successfully generated %s for package' % \
                what_generating
            ok('{0}%: {1} \'{2}\'.'.format(percent, success_msg, pkg))
            succeeded += 1
            if not current_info:
                changes.append('{0} {1}'.format(installer_name, version))
            elif current_info != version:
                changes.append(
                    '{0} {1} --> {2}'.format(
                        installer_name, current_info, version
                    )
                )
            installers.append(pkg)
        except UnknownBuildType as ub:
            err(
                "{0}%: Unknown Build type '{1}' for package '{2}'".format(
                    percent, str(ub), pkg
                )
            )
            failed = failed + 1
        except KeyError:
            failed_msg = 'Failed to generate %s' % what_generating
            err("{0}%: {1} for package {2}!".format(percent, failed_msg, pkg))
            bad_installers.append(pkg)
            failed = failed + 1
    results = 'Generated {0} / {1}'.format(succeeded, failed + succeeded)
    results += ' for distro {0}'.format(distro_name)
    info("------ {0} ------\n".format(results))

    if len(borkd_pkgs) > 0:
        warn("Unresolved:")
        for broken in borkd_pkgs.keys():
            warn("{}:".format(broken))
            warn("  {}".format(borkd_pkgs[broken]))

    return installers, borkd_pkgs, changes
