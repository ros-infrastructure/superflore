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

import argparse
import os
import sys

from superflore.generate_installers import generate_installers
from superflore.generators.bitbake.gen_packages import regenerate_installer
from superflore.generators.bitbake.ros_meta import RosMeta
from superflore.TempfileManager import TempfileManager
from superflore.utils import err
from superflore.utils import info
from superflore.utils import ok
from superflore.utils import warn

# Modify if a new distro is added
active_distros = ['indigo', 'kinetic', 'lunar']
# just update packages, by default.
mode = 'update'
preserve_existing = True
overlay = None


def file_pr(overlay, delta, missing_deps):
    try:
        overlay.pull_request('{0}\n{1}'.format(delta, missing_deps))
    except Exception as e:
        err('Failed to file PR with allenh1/meta-ros repo!')
        err('  Exception: {0}'.format(e))
        sys.exit(1)


def main():
    global overlay
    global preserve_existing

    parser = argparse.ArgumentParser('Deploy ROS packages into Yocto Linux')
    parser.add_argument(
        '--ros-distro',
        help='regenerate packages for the specified distro',
        type=str
    )
    parser.add_argument(
        '--all',
        help='regenerate all packages in all distros',
        action="store_true"
    )
    parser.add_argument(
        '--output-repository-path',
        help='location of the Git repo',
        type=str
    )
    parser.add_argument(
        '--tar-archive-dir',
        help='location to store archived packages',
        type=str
    )

    args = parser.parse_args(sys.argv[1:])
    with TempfileManager(args.output_repository_path) as _repo:
        if not args.output_repository_path:
            # give our group write permissions to the temp dir
            os.chmod(_repo, 17407)
        overlay = RosMeta(_repo, not args.output_repository_path)
        selected_targets = active_distros
        if args.all:
            warn('"All" mode detected... this may take a while!')
            preserve_existing = False
        elif args.ros_distro:
            selected_targets = [args.ros_distro]
            preserve_existing = False
        # clone current repo
        selected_targets = active_distros
        # generate installers
        total_installers = dict()
        total_broken = set()
        total_changes = dict()

        with TempfileManager(args.tar_archive_dir) as tar_dir:
            for distro in selected_targets:
                distro_installers, distro_broken, distro_changes =\
                    generate_installers(
                        distro,
                        overlay,
                        regenerate_installer,
                        preserve_existing,
                        tar_dir
                    )
                for key in distro_broken.keys():
                    for pkg in distro_broken[key]:
                        total_broken.add(pkg)

                total_changes[distro] = distro_changes
                total_installers[distro] = distro_installers

        num_changes = 0
        for distro_name in total_changes:
            num_changes += len(total_changes[distro_name])

        if num_changes == 0:
            info('ROS distro is up to date.')
            info('Exiting...')
            sys.exit(0)

        # remove duplicates
        inst_list = total_broken

        delta = "Changes:\n"
        delta += "========\n"

        if 'indigo' in total_changes and len(total_changes['indigo']) > 0:
            delta += "Indigo Changes:\n"
            delta += "---------------\n"

            for d in sorted(total_changes['indigo']):
                delta += '* {0}\n'.format(d)
            delta += "\n"

        if 'kinetic' in total_changes and len(total_changes['kinetic']) > 0:
            delta += "Kinetic Changes:\n"
            delta += "----------------\n"

            for d in sorted(total_changes['kinetic']):
                delta += '* {0}\n'.format(d)
            delta += "\n"

        if 'lunar' in total_changes and len(total_changes['lunar']) > 0:
            delta += "Lunar Changes:\n"
            delta += "--------------\n"

            for d in sorted(total_changes['lunar']):
                delta += '* {0}\n'.format(d)
            delta += "\n"

        missing_deps = ''

        if len(inst_list) > 0:
            missing_deps = "Missing Dependencies:\n"
            missing_deps += "=====================\n"
            for pkg in sorted(inst_list):
                missing_deps += " * [ ] {0}\n".format(pkg)

        # Commit changes and file pull request
        overlay.commit_changes(args.ros_distro)
        file_pr(overlay, delta, missing_deps)
        ok('Successfully synchronized repositories!')
