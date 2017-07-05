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

from superflore.generators.bitbake.gen_packages import generate_installers
from superflore.generators.bitbake.ros_meta import ros_meta
import shutil
import sys
import os

# Modify if a new distro is added
active_distros = ['indigo', 'kinetic', 'lunar']
# just update packages, by default.
mode = 'update'
preserve_existing = True
overlay = ros_meta()


def link_existing_files():
    global overlay
    global mode
    sym_link_msg = 'Symbolicly linking files from {0}/recipes-ros-{1}...'
    dir_fmt = '{0}/recipes-ros-{1}'
    if mode == 'all' or mode == 'update':
        for x in active_distros:
            ros_meta.info(sym_link_msg.format(overlay.repo_dir, x))
            os.symlink(dir_fmt.format(overlay.repo_dir, x), './recipes-ros-' + x)
    else:
        # only link the relevant directory.
        ros_meta.info(sym_link_msg.format(overlay.repo_dir, mode))
        os.symlink(dir_fmt.format(overlay.repo_dir, mode), './recipes-ros-' + mode)


def clean_up():
    global overlay
    global mode
    clean_msg = 'Cleaning up tmp directory {0}...'.format(overlay.repo_dir)
    ros_meta.info(clean_msg)
    shutil.rmtree(overlay.repo_dir)
    ros_meta.info('Cleaning up symbolic links...')
    if mode != 'all' and mode != 'update':
        os.remove('recipes-ros-{0}'.format(mode))
    else:
        for x in active_distros:
            os.remove('recipes-ros-{0}'.format(x))


def print_usage():
    usage = 'Usage: {0} [ --all'.format(sys.argv[0])
    for distro in active_distros:
        usage += '| --{0}'.format(distro)
    usage += ' ]'
    ros_meta.info(usage)


def main():
    global overlay
    global mode
    if len(sys.argv) == 2:
        arg1 = sys.argv[1].replace('--', '')

        if arg1 == 'all' or arg1 == 'update':
            mode = arg1
            preserve_existing = arg1 == 'all'
        else:
            preserve_existing = False
            if arg1 not in active_distros:
                ros_meta.error('Unknown ros distro "{0}"'.format(arg1))
                ros_meta.error('Exiting...')
                sys.exit(1)
            else:
                msg = 'Regenerating all packages for distro "{0}"'.format(arg1)
                ros_meta.info(msg)
                mode = arg1
    elif len(sys.argv) >= 2:
        ros_meta.error('Invalid arguments!')
        print_usage()

    # clone current repo
    selected_targets = active_distros

    if mode == 'all':
        ros_meta.warn('"All" mode detected... This may take a while!')
    elif mode != 'update':
        selected_targets = [mode]
    # try:
    link_existing_files()
    """
    except FileExistsError:
        warn_msg = 'Detected existing rosdistro ebuild structure... '
        warn_msg += 'Removing and overwriting.'
        ros_meta.warn(warn_msg)
        for x in active_distros:
            try:
                os.remove('recipes-ros-{0}'.format(x))
            except:
                pass
        link_existing_files()
    """
    # generate installers
    total_installers = dict()
    total_broken = set()
    total_changes = dict()

    for distro in selected_targets:
        distro_installers, distro_broken, distro_changes =\
            generate_installers(distro, overlay, preserve_existing)
        for key in distro_broken.keys():
            for pkg in distro_broken[key]:
                total_broken.add(pkg)

        total_changes[distro] = distro_changes
        total_installers[distro] = distro_installers

    num_changes = 0
    for distro_name in total_changes:
        num_changes += len(total_changes[distro_name])

    if num_changes == 0:
        ros_meta.info('ROS distro is up to date.')
        ros_meta.info('Exiting...')
        clean_up()
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
    # overlay.regenerate_manifests(mode)
    overlay.commit_changes(mode)
    try:
        overlay.pull_request('{0}\n{1}'.format(delta, missing_deps))
    except Exception as e:
        overlay.error('Failed to file PR with allenh1/meta-ros repo!')
        overlay.error('Exception: {0}'.format(e))
        sys.exit(1)

    clean_up()
    ros_meta.happy('Successfully synchronized repositories!')
