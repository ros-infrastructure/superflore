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
import sys

from rosinstall_generator.distro import get_distro
from rosinstall_generator.distro import get_package_names
from superflore.CacheManager import CacheManager
from superflore.generate_installers import generate_installers
from superflore.generators.bitbake.gen_packages import regenerate_pkg
from superflore.generators.bitbake.ros_meta import RosMeta
from superflore.generators.bitbake.yocto_recipe import yoctoRecipe
from superflore.parser import get_parser
from superflore.repo_instance import RepoInstance
from superflore.TempfileManager import TempfileManager
from superflore.utils import clean_up
from superflore.utils import err
from superflore.utils import file_pr
from superflore.utils import gen_delta_msg
from superflore.utils import get_pr_text
from superflore.utils import get_utcnow_timestamp_str
from superflore.utils import info
from superflore.utils import load_pr
from superflore.utils import ok
from superflore.utils import save_pr
from superflore.utils import url_to_repo_org
from superflore.utils import warn


def main():
    overlay = None
    parser = get_parser(
        'Generate OpenEmbedded recipes for ROS packages',
        exclude_all=True,
        require_rosdistro=True,
        require_dryrun=True)
    parser.add_argument(
        '--tar-archive-dir',
        help='location to store archived packages',
        type=str
    )
    args = parser.parse_args(sys.argv[1:])
    pr_comment = args.pr_comment
    skip_keys = set(args.skip_keys) if args.skip_keys else set()

    if args.license_org:
        yoctoRecipe.org = args.license_org
    if args.license_text:
        yoctoRecipe.org_license = args.license_text
    if args.pr_only:
        if args.dry_run:
            parser.error('Invalid args! cannot dry-run and file PR')
        if not args.output_repository_path:
            parser.error('Invalid args! no repository specified')
        try:
            prev_overlay = RepoInstance(args.output_repository_path, False)
            msg, title = load_pr()
            prev_overlay.pull_request(msg, title=title)
            clean_up()
            sys.exit(0)
        except Exception as e:
            err('Failed to file PR!')
            err('reason: {0}'.format(e))
            sys.exit(1)
    warn('"{0}" distro detected...'.format(args.ros_distro))
    """
    No longer supporting generation for multiple targets, but left the code in
    place to handle them in case it might be needed again in the future.
    """
    selected_targets = [args.ros_distro]
    preserve_existing = args.only
    now = os.getenv(
        'SUPERFLORE_GENERATION_DATETIME',
        get_utcnow_timestamp_str())
    repo_org = 'ros'
    repo_name = 'meta-ros'
    if args.upstream_repo:
        repo_org, repo_name = url_to_repo_org(args.upstream_repo)
    # open cached tar file if it exists
    with TempfileManager(args.output_repository_path) as _repo:
        if not args.output_repository_path:
            # give our group write permissions to the temp dir
            os.chmod(_repo, 17407)
        # clone if args.output_repository_path is None
        overlay = RosMeta(
            _repo,
            not args.output_repository_path,
            branch=(('superflore/{}'.format(now)) if not args.no_branch
                    else None),
            org=repo_org,
            repo=repo_name,
            from_branch=args.upstream_branch,
        )
        if not args.only:
            pr_comment = pr_comment or (
                'Recipes generated by **superflore** for all packages in ROS '
                'distribution {}.\n'.format(selected_targets[0])
            )
        else:
            pr_comment = pr_comment or (
                'Recipes generated by **superflore** for package(s) {} in ROS '
                'distribution {}.\n'.format(args.only, args.ros_distro)
            )
        # generate installers
        total_installers = dict()
        total_changes = dict()
        if args.tar_archive_dir:
            srcrev_filename = '%s/srcrev_cache.pickle' % args.tar_archive_dir
        else:
            srcrev_filename = None
        with CacheManager(srcrev_filename) as srcrev_cache:
            if args.only:
                distro = get_distro(args.ros_distro)
                for pkg in args.only:
                    if pkg in skip_keys:
                        warn("Package '%s' is in skip-keys list, skipping..."
                             % pkg)
                        continue
                    info("Regenerating package '%s'..." % pkg)
                    try:
                        regenerate_pkg(
                            overlay,
                            pkg,
                            distro,
                            False,  # preserve_existing
                            srcrev_cache,
                            skip_keys=skip_keys,
                        )
                    except KeyError:
                        err("No package to satisfy key '%s' available "
                            "packages in selected distro: %s" %
                            (pkg, get_package_names(distro)))
                        sys.exit(1)
                # Commit changes and file pull request
                title =\
                    '{{{0}}} Selected recipes generated from '\
                    'files/{0}/generated/cache.yaml '\
                    'as of {1}\n'.format(
                            args.ros_distro,
                            now)
                regen_dict = dict()
                regen_dict[args.ros_distro] = args.only
                delta = "Regenerated: '%s'\n" % args.only
                overlay.add_generated_files(args.ros_distro)
                commit_msg = '\n'.join([get_pr_text(
                    title + '\n' + pr_comment.replace(
                        '**superflore**', 'superflore'), markup=''), delta])
                overlay.commit_changes(args.ros_distro, commit_msg)
                if args.dry_run:
                    save_pr(overlay, args.only, '', pr_comment, title=title)
                    sys.exit(0)
                file_pr(overlay, delta, '', pr_comment, distro=args.ros_distro,
                        title=title)
                ok('Successfully synchronized repositories!')
                sys.exit(0)

            overlay.clean_ros_recipe_dirs(args.ros_distro)
            for adistro in selected_targets:
                yoctoRecipe.reset()
                distro = get_distro(adistro)

                distro_installers, _, distro_changes =\
                    generate_installers(
                        distro,
                        overlay,
                        regenerate_pkg,
                        preserve_existing,
                        srcrev_cache,
                        skip_keys,
                        skip_keys=skip_keys,
                        is_oe=True,
                    )
                total_changes[adistro] = distro_changes
                total_installers[adistro] = distro_installers
                yoctoRecipe.generate_ros_distro_inc(
                    _repo, args.ros_distro, overlay.get_file_revision_logs(
                        'meta-ros{0}-{1}/files/{1}/generated/cache.yaml'
                        .format(
                            yoctoRecipe._get_ros_version(args.ros_distro),
                            args.ros_distro)),
                    distro.release_platforms, skip_keys)
                yoctoRecipe.generate_superflore_datetime_inc(
                    _repo, args.ros_distro, now)
                yoctoRecipe.generate_rosdep_resolve(_repo, args.ros_distro)
                yoctoRecipe.generate_newer_platform_components(
                    _repo, args.ros_distro)
                overlay.add_generated_files(args.ros_distro)

        num_changes = 0
        for distro_name in total_changes:
            num_changes += len(total_changes[distro_name])

        if num_changes == 0:
            info('ROS distro is up to date.')
            summary = overlay.get_change_summary(args.ros_distro)
            if len(summary) == 0:
                info('Exiting...')
                clean_up()
                sys.exit(0)
            else:
                info('But there are some changes in other regenerated files:'
                     '%s' % summary)

        # remove duplicates
        delta = gen_delta_msg(total_changes, markup='')
        # Commit changes and file pull request
        title = '{{{0}}} Sync to files/{0}/generated/'\
            'cache.yaml as of {1}\n'.format(
                args.ros_distro,
                now)
        commit_msg = '\n'.join([get_pr_text(
            title + '\n' + pr_comment.replace('**superflore**', 'superflore'),
            markup=''), delta])
        overlay.commit_changes(args.ros_distro, commit_msg)
        delta = gen_delta_msg(total_changes)
        if args.dry_run:
            info('Running in dry mode, not filing PR')
            save_pr(
                overlay, delta, '', pr_comment, title=title,
            )
            sys.exit(0)
        file_pr(overlay, delta, '', comment=pr_comment, title=title)
        clean_up()
        ok('Successfully synchronized repositories!')
