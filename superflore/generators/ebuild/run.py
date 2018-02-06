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

import argparse
import os
import sys

from rosinstall_generator.distro import get_distro
from superflore.generate_installers import generate_installers
from superflore.generators.ebuild.gen_packages import regenerate_pkg
from superflore.generators.ebuild.overlay_instance import RosOverlay
from superflore.parser import get_parser
from superflore.repo_instance import RepoInstance
from superflore.TempfileManager import TempfileManager
from superflore.utils import clean_up
from superflore.utils import err
from superflore.utils import file_pr
from superflore.utils import info
from superflore.utils import load_pr
from superflore.utils import ok
from superflore.utils import save_pr
from superflore.utils import warn

# Modify if a new distro is added
active_distros = ['indigo', 'kinetic', 'lunar']


def main():
    overlay = None
    preserve_existing = True
    parser = get_parser('Deploy ROS packages into Gentoo Linux')
    args = parser.parse_args(sys.argv[1:])
    pr_comment = args.pr_comment
    selected_targets = None
    if args.all:
        warn('"All" mode detected... This may take a while!')
        preserve_existing = False
    elif args.ros_distro:
        selected_targets = [args.ros_distro]
        preserve_existing = False
    elif args.dry_run and args.pr_only:
        parser.error('Invalid args! cannot dry-run and file PR')
    elif args.pr_only and not args.output_repository_path:
        parser.error('Invalid args! no repository specified')
    elif args.pr_only:
        try:
            prev_overlay = RepoInstance(args.output_repository_path, False)
            msg, title = load_pr()
            prev_overlay.pull_request(msg, title)
            clean_up()
            sys.exit(0)
        except Exception as e:
            err('Failed to file PR!')
            err('reason: {0}'.format(e))
            sys.exit(1)
    if not selected_targets:
        selected_targets = active_distros
    repo_org = 'ros'
    repo_name = 'ros-overlay'
    if args.upstream_repo:
        # check that the upstream_repo is a github repo
        if 'github.com' not in args.upstream_repo:
            raise RuntimeError('Non-GitHub repos are not supported!')
        upstream = args.upstream_repo
        upstream = upstream.replace('https://github.com/', '').split('/')
        repo_org = upstream[0]
        repo_name = upstream[1]
    with TempfileManager(args.output_repository_path) as _repo:
        if not args.output_repository_path:
            # give our group write permissions to the temp dir
            os.chmod(_repo, 17407)
        # clone if args.output_repository_path is None
        overlay = RosOverlay(
            _repo,
            not args.output_repository_path,
            org=repo_org,
            repo=repo_name
        )
        if not preserve_existing and not args.only:
            pr_comment = pr_comment or (
                'Superflore ebuild generator began regeneration of all'
                ' packages from ROS distro %s from ROS-Overlay commit %s.' % (
                    selected_targets,
                    overlay.repo.get_last_hash()
                )
            )
        elif not args.only:
            pr_comment = pr_comment or (
                'Superflore ebuild generator ran update from ROS-Overlay ' +
                'commit %s.' % (overlay.repo.get_last_hash())
            )
        # generate installers
        total_installers = dict()
        total_broken = set()
        total_changes = dict()
        if args.only:
            pr_comment = pr_comment or (
                'Superflore ebuild generator began regeneration of ' +
                'package(s) %s from commit %s.' % (
                    args.only,
                    overlay.repo.get_last_hash()
                )
            )
            for pkg in args.only:
                info("Regenerating package '%s'..." % pkg)
                try:
                    regenerate_pkg(
                        overlay,
                        pkg,
                        get_distro(args.ros_distro),
                        preserve_existing
                    )
                except KeyError:
                    err("No package to satisfy key '%s'" % pkg)
                    sys.exit(1)
            # Commit changes and file pull request
            regen_dict = dict()
            regen_dict[args.ros_distro] = args.only
            overlay.regenerate_manifests(regen_dict)
            overlay.commit_changes(args.ros_distro)
            if args.dry_run:
                save_pr(overlay, args.only, pr_comment)
                sys.exit(0)
            file_pr(overlay, '', '', pr_comment)
            clean_up()
            ok('Successfully synchronized repositories!')
            sys.exit(0)

        for distro in selected_targets:
            distro_installers, distro_broken, distro_changes =\
                generate_installers(
                    distro_name=distro,
                    overlay=overlay,
                    gen_pkg_func=regenerate_pkg,
                    preserve_existing=preserve_existing
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
        overlay.regenerate_manifests(total_installers)
        overlay.commit_changes(args.ros_distro)

        if args.dry_run:
            info('Running in dry mode, not filing PR')
            save_pr(overlay, delta, missing_deps, pr_comment)
            sys.exit(0)
        file_pr(overlay, delta, missing_deps, pr_comment)

        clean_up()
        ok('Successfully synchronized repositories!')
