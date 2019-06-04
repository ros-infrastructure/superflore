# Copyright 2019 Open Source Robotics Foundation, Inc.
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

from superflore.generators.bitbake.oe_query import OpenEmbeddedLayersDB
import unittest


class TestOpenEmbeddedQuery(unittest.TestCase):
    def test_init(self):
        """Test OpenEmbedded Query __init__"""
        oe_query = OpenEmbeddedLayersDB()
        self.assertEqual(oe_query._oe_branch, 'thud')

    def test_sample_queries(self):
        """Test sample queries to OpenEmbedded layers database"""
        oe_query = OpenEmbeddedLayersDB()
        oe_query.query_recipe('')
        self.assertEqual(oe_query.exists(), False)
        self.assertIs('', str(oe_query))
        oe_query.query_recipe('clang')
        self.assertEqual(oe_query.exists(), True)
        self.assertIn('LLVM based C/C++ compiler', str(oe_query))
