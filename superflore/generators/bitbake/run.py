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
from superflore.CacheManager import CacheManager
from superflore.generate_installers import generate_installers
from superflore.generators.bitbake.gen_packages import regenerate_installer
from superflore.generators.bitbake.ros_meta import RosMeta
from superflore.TempfileManager import TempfileManager
from superflore.utils import err
from superflore.utils import file_pr
from superflore.utils import info
from superflore.utils import ok
from superflore.utils import warn

# Modify if a new distro is added
active_distros = ['indigo', 'kinetic', 'lunar']
# just update packages, by default.
mode = 'update'
preserve_existing = True
overlay = None


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
    parser.add_argument(
        '--only',
        nargs='+',
        help='generate only the specified packages'
    )
    parser.add_argument(
        '--pr-comment',
        help='comment to add to the PR',
        type=str
    )
    selected_targets = active_distros
    args = parser.parse_args(sys.argv[1:])
    pr_comment = args.pr_comment
    if args.all:
        warn('"All" mode detected... this may take a while!')
        preserve_existing = False
    elif args.ros_distro:
        warn('"{0}" distro detected...'.format(args.ros_distro))
        selected_targets = [args.ros_distro]
        preserve_existing = False
    # open cached tar file if it exists
    with TempfileManager(args.output_repository_path) as _repo:
        if not args.output_repository_path:
            # give our group write permissions to the temp dir
            os.chmod(_repo, 17407)
        # clone if args.output-repository_path is None
        overlay = RosMeta(_repo, not args.output_repository_path)
        if not args.only:
            pr_comment = pr_comment or (
                'Superflore yocto generator began regeneration of all ' +
                'packages form ROS distribution(s) %s from allenh1\'s ' +
                'fork of Meta-ROS from commit %s.' % (
                    selected_targets,
                    overlay.repo.get_last_hash()
                )
            )
        else:
            pr_comment = pr_comment or (
                'Superflore yocto generator began regeneration of package(s)' +
                ' %s from ROS distro %s from allenh1\'s fork of Meta-ROS ' +
                'from commit %s.' % (
                    args.only,
                    overlay.repo.get_last_hash()
                )
            )
        # generate installers
        total_installers = dict()
        total_broken = set()
        total_changes = dict()
        if args.tar_archive_dir:
            sha256_filename = '%s/sha256_cache.pickle' % args.tar_archive_dir
            md5_filename = '%s/md5_cache.pickle' % args.tar_archive_dir
        else:
            sha256_filename = None
            md5_filename = None
        with TempfileManager(args.tar_archive_dir) as tar_dir,\
            CacheManager(sha256_filename) as sha256_cache,\
            CacheManager(md5_filename) as md5_cache:  # noqa
            if args.only:
                for pkg in args.only:
                    info("Regenerating package '%s'..." % pkg)
                    try:
                        regenerate_installer(
                            overlay,
                            pkg,
                            get_distro(args.ros_distro),
                            preserve_existing,
                            tar_dir,
                            md5_cache,
                            sha256_cache
                        )
                    except KeyError:
                        err("No package to satisfy key '%s'" % pkg)
                        sys.exit(1)
                # Commit changes and file pull request
                regen_dict = dict()
                regen_dict[args.ros_distro] = args.only
                overlay.regenerate_manifests(regen_dict)
                overlay.commit_changes(args.ros_distro)
                delta = "Regenerated: '%s'\n" % args.only
                file_pr(overlay, delta, '', pr_comment)
                ok('Successfully synchronized repositories!')
                sys.exit(0)

            for distro in selected_targets:
                distro_installers, distro_broken, distro_changes =\
                    generate_installers(
                        distro,
                        overlay,
                        regenerate_installer,
                        preserve_existing,
                        tar_dir,
                        md5_cache,
                        sha256_cache
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
        file_pr(overlay, delta, missing_deps, pr_comment)
        ok('Successfully synchronized repositories!')
