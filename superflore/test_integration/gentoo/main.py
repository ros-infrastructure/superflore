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
import sys

from superflore.test_integration.gentoo.build_base import GentooBuilder
from superflore.utils import get_distros_by_status
import yaml


def main():
    tester = GentooBuilder()
    parser = argparse.ArgumentParser(
        description='Check if ROS packages are building for Gentoo Linux'
    )
    parser.add_argument(
        '--ros-distro',
        help='distro(s) to check',
        type=str,
        nargs="+",
        default=get_distros_by_status('active'),
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
    args = parser.parse_args(sys.argv[1:])

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
    else:
        parser.error('Invalid args! You must supply a package list.')
        sys.exit(1)
    results = tester.run(args.verbose, args.log_file)
    failures = 0
    for test_case in results.keys():
        if results[test_case] == 'failing':
            failures = failures + 1
    # set exit status to the number of failures
    sys.exit(failures)
