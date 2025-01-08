# Copyright 2017 Open Source Robotics Foundation, Inc.
# Copyright 2024 Codethink
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

from rosdistro.dependency_walker import DependencyWalker
from rosinstall_generator.distro import get_distro
from rosinstall_generator.distro import get_package_names
from superflore.CacheManager import CacheManager
from superflore.generate_installers import generate_installers
from superflore.generators.buildstream.gen_packages import regenerate_pkg
from superflore.generators.buildstream.ros_bst_repo import RosBstRepo
from superflore.generators.buildstream.bst_element import BstElement
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


def get_recursive_dependencies(distro, package_names, excludes=None, limit_depth=None):
    excludes = set(excludes or [])
    dependencies = set([])
    walker = DependencyWalker(distro)
    for pkg_name in package_names:
        try:
            dependencies |= walker.get_recursive_depends(
                pkg_name,
                ['buildtool', 'buildtool_export', 'build', 'build_export', 'run'],
                ros_packages_only=True,
                ignore_pkgs=dependencies | excludes, limit_depth=limit_depth)
        except AssertionError as e:
            raise RuntimeError("Failed to fetch recursive dependencies of package '%s': %s" % (pkg_name, e))
    dependencies -= set(package_names)
    return dependencies


def main():
    overlay = None
    parser = get_parser(
        'Generate BuildStream elements for ROS packages',
        exclude_all=True,
        require_rosdistro=True,
        require_dryrun=True)
    parser.add_argument(
        '--tar-archive-dir',
        help='location to store archived packages',
        type=str
    )
    parser.add_argument(
            '--generated-element-dir',
            default="elements/generated",
            help='directory for generated bst elements',
            type=str)
    parser.add_argument(
            '--exclude-sources-for',
            default=[],
            nargs='+',
            help='do not generate sources for the specified packages',
            type=str)
    args = parser.parse_args(sys.argv[1:])
    pr_comment = args.pr_comment
    skip_keys = set(args.skip_keys) if args.skip_keys else set()
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
    selected_targets = [args.ros_distro]
    preserve_existing = False
    now = os.getenv(
        'SUPERFLORE_GENERATION_DATETIME',
        get_utcnow_timestamp_str())
    # No default upstream repo yet
    repo_org = None
    repo_name = None
    if args.upstream_repo:
        repo_org, repo_name = url_to_repo_org(args.upstream_repo)
    # open cached tar file if it exists
    with TempfileManager(args.output_repository_path) as _repo:
        if not args.output_repository_path:
            # give our group write permissions to the temp dir
            os.chmod(_repo, 17407)
        # clone if args.output_repository_path is None
        overlay = RosBstRepo(
            _repo,
            not args.output_repository_path,
            branch=(('superflore/{}'.format(now)) if not args.no_branch
                    else None),
            org=repo_org,
            repo=repo_name,
            from_branch=args.upstream_branch,
            generated_elements_dir=args.generated_element_dir
        )
        if not args.only:
            pr_comment = pr_comment or (
                'Elements generated by **superflore** for all packages in ROS '
                'distribution {}.\n'.format(selected_targets[0])
            )
        else:
            pr_comment = pr_comment or (
                'Elements generated by **superflore** for package(s) {} in ROS '
                'distribution {}.\n'.format(args.only, args.ros_distro)
            )

        external_repos = {}
        external_repos["freedesktop-sdk.bst:components/"] = args.output_repository_path + "/../freedesktop-sdk/elements/components"
        external_repos["external-deps/"] = args.output_repository_path + "/elements/external-deps"

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
                packages = args.only
                exclude_sources_for = args.exclude_sources_for
                include_dependencies = True
                if include_dependencies:
                    packages = set(packages) | \
                        get_recursive_dependencies(distro, packages, excludes=skip_keys)
                for pkg in packages:
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
                            preserve_existing,
                            srcrev_cache,
                            skip_keys=skip_keys,
                            external_repos=external_repos,
                            exclude_source=pkg in exclude_sources_for
                        )
                    except KeyError:
                        err("No package to satisfy key '%s' available "
                            "packages in selected distro: %s" %
                            (pkg, get_package_names(distro)))
                        sys.exit(1)
                # Commit changes and file pull request
                title =\
                    '{{{0}}} Selected elements generated from '\
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

            overlay.clean_ros_element_dirs(args.ros_distro)
            for adistro in selected_targets:
                distro = get_distro(adistro)

                distro_installers, _, distro_changes =\
                    generate_installers(
                        distro,
                        overlay,
                        regenerate_pkg,
                        preserve_existing,
                        srcrev_cache,
                        skip_keys,
                        external_repos,
                        skip_keys=skip_keys,
                        is_oe=True,
                    )
                total_changes[adistro] = distro_changes
                total_installers[adistro] = distro_installers
                BstElement.generate_newer_platform_components(
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
                info('But there are some changes in other regenerated files: '
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
