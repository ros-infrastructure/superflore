#!/usr/bin/python
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


from superflore.generators.ebuild.gen_packages import generate_installers
from superflore.generators.ebuild.overlay_instance import ros_overlay
from superflore.utils import download_yamls
from superflore.repo_instance import repo_instance
import argparse
import shutil
import sys
import os

# Modify if a new distro is added
active_distros = ['indigo', 'kinetic', 'lunar']
# just update packages, by default.
preserve_existing = True
overlay = None


def link_existing_files(mode):
    global overlay
    sym_link_msg = 'Symbolicly linking files from {0}/ros-{1}...'
    dir_fmt = '{0}/ros-{1}'
    if not mode:
        for x in active_distros:
            ros_overlay.info(sym_link_msg.format(overlay.repo_dir, x))
            os.symlink(dir_fmt.format(overlay.repo_dir, x), './ros-' + x)
    else:
        # only link the relevant directory.
        ros_overlay.info(sym_link_msg.format(overlay.repo_dir, mode))
        os.symlink(dir_fmt.format(overlay.repo_dir, mode), './ros-' + mode)


def get_existing_repo():
    existing_path = None
    for x in active_distros:
        curr = './ros-{0}'.format(x)
        if os.path.exists(curr):
            existing_path = curr
            break
    if not existing_path:
        raise RuntimeException('No existing repo found')
    # get the actual location of the repo
    repo_dir = os.path.realpath('{0}/../'.format(existing_path))
    # TODO(allenh1): make this configurable
    git_repo = repo_instance('ros', 'ros-overlay', repo_dir, do_clone=False)
    return git_repo


def clean_up(distro):
    global overlay
    clean_msg = 'Cleaning up tmp directory {0}...'.format(overlay.repo_dir)
    ros_overlay.info(clean_msg)
    shutil.rmtree(overlay.repo_dir)
    ros_overlay.info('Cleaning up symbolic links...')
    if distro in active_distros:
        os.remove('ros-{0}'.format(distro))
    else:
        for x in active_distros:
            os.remove('ros-{0}'.format(x))


def file_pr(overlay, delta, missing_deps):
    try:
        overlay.pull_request('{0}\n{1}'.format(delta, missing_deps))
    except Exception as e:
        overlay.error('Failed to file PR with ros/ros-overlay repo!')
        overlay.error('Exception: {0}'.format(e))
        sys.exit(1)


def main():
    global overlay
    global preserve_existing

    parser = argparse.ArgumentParser('Deploy ROS packages into Gentoo Linux')
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
        '--dry-run',
        help='run without filing a PR to remote',
        action="store_true"
    )
    parser.add_argument(
        '--pr-only',
        help='ONLY file a PR to remote',
        action='store_true'
    )

    args = parser.parse_args(sys.argv[1:])

    if args.all:
        ros_overlay.warn('"All" mode detected... This may take a while!')
        preserve_existing = False
    elif args.ros_distro:
        selected_targets = [args.ros_distro]
        preserve_existing = False
    elif args.dry_run and args.pr_only:
        ros_overlay.err('Invalid args! cannot dry-run and file PR')
        sys.exit(1)
    elif args.pr_only:
        try:
            with open('.pr_message.tmp', 'r') as msg_file:
                msg = msg_file.read()
            with open('.pr_title.tmp', 'r') as title_file:
                title = title_file.read()
        except:
            ros_overlay.err('Failed to open PR title/message file!')
            ros_overlay.err(
                'Please supply the %s and %s files' % (
                    '.pr_message.tmp',
                    '.pr_title.tmp'
                )
            )
            sys.exit(1)
        try:
            prev_overlay = get_existing_repo()
            prev_overlay.repo.git.pull_request(
                m=('%s' % msg), title=('%s' % title)
            )
            ros_overlay.happy('Successfully filed PR.')
            clean_up()
            sys.exit(0)
        except:
            ros_overlay.err('Failed to file PR!')
            sys.exit(1)
    # clone current repo
    overlay = ros_overlay()
    selected_targets = active_distros

    try:
        link_existing_files(args.ros_distro)
    except os.FileExistsError:
        warn_msg = 'Detected existing rosdistro ebuild structure... '
        warn_msg += 'Removing and overwriting.'
        ros_overlay.warn(warn_msg)
        for x in active_distros:
            try:
                os.remove('ros-{0}'.format(x))
            except:
                pass

        link_existing_files(args.ros_distro)
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
        ros_overlay.info('ROS distro is up to date.')
        ros_overlay.info('Exiting...')
        clean_up(args.ros_distro)
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
    overlay.regenerate_manifests(args.ros_distro)
    overlay.commit_changes(args.ros_distro)

    if args.dry_run:
        ros_overlay.info('Running in dry mode, not filing PR')
        title_file = open('.pr-title.tmp', 'w')
        title_file.write('rosdistro sync, {0}'.format(time.ctime()))
        pr_message_file = open('.pr-message.tmp', 'w')
        pr_missage_file.write('%s\n%s' % (delta, missing_deps))
        sys.exit(0)
    file_pr(overlay, delta, missing_deps)

    clean_up(args.ros_distro)
    ros_overlay.happy('Successfully synchronized repositories!')
