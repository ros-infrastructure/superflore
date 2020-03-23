# Copyright 2018 Open Source Robotics Foundation, Inc.
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


# set up a parser and return it
def get_parser(
    tool_tip, is_generator=True, exclude_all=False,
    require_dryrun=False,
    require_rosdistro=False
):
    parser = argparse.ArgumentParser(description=tool_tip)
    if is_generator:
        parser.add_argument(
            '--ros-distro',
            help='regenerate packages for the specified distro',
            required=require_rosdistro,
            type=str
        )
        if not exclude_all:
            parser.add_argument(
                '--all',
                help='regenerate all packages in all distros',
                action="store_true"
            )
        parser.add_argument(
            '--dry-run',
            help='run without filing a PR to remote',
            required=require_dryrun,
            action="store_true"
        )
        parser.add_argument(
            '--pr-only',
            help='ONLY file a PR to remote',
            action='store_true'
        )
        parser.add_argument(
            '--no-branch',
            help='Do not create a new branch automatically',
            action='store_true'
        )
        parser.add_argument(
            '--output-repository-path',
            help='location of the Git repo',
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
        parser.add_argument(
            '--upstream-repo',
            help='location of the upstream repository as in '
                 + 'https://github.com/<owner>/<repository>',
            type=str
        )
        parser.add_argument(
            '--upstream-branch',
            help='branch of the upstream repository',
            type=str
        )
        parser.add_argument(
            '--skip-keys',
            nargs='+',
            help='packages to skip during regeneration'
        )
    return parser
