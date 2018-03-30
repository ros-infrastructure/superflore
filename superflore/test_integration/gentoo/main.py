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
import os
import sys

from superflore.generators.ebuild.overlay_instance import RosOverlay
from superflore.TempfileManager import TempfileManager
from superflore.test_integration.gentoo.build_base import GentooBuilder
from superflore.utils import active_distros
from superflore.utils import url_to_repo_org
import yaml


def main():
    tester = GentooBuilder()
    parser = argparse.ArgumentParser(
        'Check if ROS packages are building for Gentoo Linux'
    )
    parser.add_argument(
        '--ros-distro',
        help='distro(s) to check',
        type=str,
        nargs="+",
        default=active_distros,
    )
    parser.add_argument(
        '--pkgs',
        help='packages to build',
        type=str,
        nargs='+',
    )
    parser.add_argument(
        '-f',
        help='build packages specified by the input file',
        type=str
    )
    parser.add_argument(
        '-v',
        '--verbose',
        help='show output from docker',
        action="store_true"
    )
    parser.add_argument(
        '--log-file',
        help='location to store the log file',
        type=str
    )
    parser.add_argument(
        '--set-upstream',
        help='URL for the overlay to test',
        type=str
    )
    parser.add_argument(
        '--branch',
        help='Branch to test',
        type=str
    )
    parser.add_argument(
        '--ci-mode',
        help='build packages from latest git commit',
        action="store_true"
    )
    args = parser.parse_args(sys.argv[1:])
    repo_org = 'ros'
    repo_name = 'ros-overlay'
    if args.f:
        # load the yaml file holding the test files
        with open(args.f, 'r') as test_file:
            test_dict = yaml.load(test_file)
            for distro, pkg_list in test_dict.items():
                for pkg in pkg_list:
                    tester.add_target(distro, pkg)
    elif args.pkgs:
        # use passed-in arguments to test
        for distro in args.ros_distro:
            for pkg in args.pkgs:
                tester.add_target(distro, pkg)
    elif not args.ci_mode:
        parser.error('Invalid args! You must supply a package list.')
        sys.exit(1)
    if args.set_upstream:
        tester.set_upstream(args.set_upstream, args.branch or 'master')
        repo_org, repo_name = url_to_repo_org(args.set_upstream)
    if args.ci_mode:
        # temporarily clone the repo and retrieve list
        build_list = list()
        with TempfileManager(None) as _repo:
            os.chmod(_repo, 17407)
            overlay = RosOverlay(_repo, True, org=repo_org, repo=repo_name)
            build_list = overlay.get_last_modified(args.branch or 'master')
        for p in build_list:
            tester.package_list[p] = 'unknown'
    results = tester.run(args.verbose, args.log_file)
    failures = 0
    for test_case in results.keys():
        if results[test_case] == 'failing':
            failures = failures + 1
    # set exit status to the number of failures
    sys.exit(failures)
