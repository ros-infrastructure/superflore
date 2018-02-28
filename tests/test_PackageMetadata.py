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

from superflore.PackageMetadata import PackageMetadata
import unittest


class TestPackageMetadata(unittest.TestCase):
    def test_metadata(self):
        """Test the Package Metadata parsing"""
        with open('tests/PackageXml/test.xml', 'r') as test_file:
            test_xml = test_file.read()
        ret = PackageMetadata(test_xml)
        self.assertEqual(ret.upstream_email, 'someone@example.com')
        self.assertEqual(ret.upstream_name, 'Someone')
        self.assertEqual(ret.description, 'This is my package\'s description.')
        self.assertEqual(ret.longdescription, 'This is my package\'s description.')
        self.assertEqual(ret.homepage, 'http://wiki.ros.org/my_package')
        self.assertEqual(ret.build_type, 'my_builder')

    def test_no_homepage(self):
        """Test Package Metadata parsing without a homepage field"""
        with open('tests/PackageXml/test2.xml', 'r') as test_file:
            test_xml = test_file.read()
        ret = PackageMetadata(test_xml)
        self.assertEqual(ret.homepage, 'http://www.github.com/my_org/my_package')
