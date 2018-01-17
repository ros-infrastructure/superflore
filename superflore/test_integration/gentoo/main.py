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
import time

from superflore.test_integration.gentoo.build_base import GentooBuilder


active_distros = ['indigo', 'kinetic', 'lunar']

def main():
    # TODO(allenh1): parse for '-f [filename]'
    distros = active_distros
    tester = GentooBuilder()
    parser = argparse.ArgumentParser('Check if ROS packages are building for Gentoo Linux')
    parser.add_argument(
        '--ros-distro',
        help='distro(s) to check',
        type=str,
        nargs="+",
        default=active_distros
    )
    parser.add_argument(
        'pkgs',
        metavar='package',
        help='packages to build',
        type=str,
        nargs='+'
    )
    args = parser.parse_args(sys.argv[1:])

    for distro in args.ros_distro:
        for pkg in args.pkgs:
            tester.add_target(distro, pkg)
    results = tester.run()
    failures = 0
    for test_case in results.keys():
        if results[test_case] == 'failing':
            failures = failures + 1
    # set exit status to the number of failures
    sys.exit(failures)
