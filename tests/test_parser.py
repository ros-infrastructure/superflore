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

import sys

from superflore.parser import get_parser
import unittest


class TestParserSetup(unittest.TestCase):
    def test_get_parser(self):
        """Tests the get_parser function"""
        p = get_parser('test parser')
        self.assertEqual(p.description, 'test parser')
        sys.argv = []
        ret = p.parse_args()
        self.assertIn('all', ret)
        self.assertIn('dry_run', ret)
        self.assertIn('only', ret)
        self.assertIn('output_repository_path', ret)
        self.assertIn('pr_comment', ret)
        self.assertIn('pr_only', ret)
        self.assertIn('ros_distro', ret)
        self.assertIn('upstream_repo', ret)
        self.assertIn('upstream_branch', ret)
        self.assertIn('skip_keys', ret)
