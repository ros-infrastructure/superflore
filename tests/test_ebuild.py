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

from superflore.generators.ebuild.ebuild import Ebuild
from superflore.exceptions import UnresolvedDependency
import unittest


class TestEbuildOutput(unittest.TestCase):
    def test_simple(self):
        """Test Ebuild Format"""
        ebuild = Ebuild()
        ebuild.homepage = 'https://www.website.com'
        ebuild.description = 'an ebuild'
        ebuild.add_run_depend('p2os_driver')
        ebuild.src_uri = 'https://www.website.com/download/stuff.tar.gz'
        ebuild.distro = 'lunar'
        got_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        with open('tests/ebuild/simple_expected.ebuild', 'r') as expect_file:
            correct_text = expect_file.read()
        self.assertEqual(got_text, correct_text)

    def test_bad_build_depend(self):
        """Test Bad Build Dependency"""
        ebuild = Ebuild()
        ebuild.homepage = 'https://www.website.com'
        ebuild.description = 'an ebuild'
        ebuild.src_uri = 'https://www.website.com/download/stuff.tar.gz'
        ebuild.distro = 'lunar'
        ebuild.add_run_depend('p2os_driver')
        ebuild.add_build_depend('fake_package', False)
        with self.assertRaises(UnresolvedDependency):
            ebuild_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')

    def test_bad_run_depend(self):
        """Test Bad Build Dependency"""
        ebuild = Ebuild()
        ebuild.homepage = 'https://www.website.com'
        ebuild.description = 'an ebuild'
        ebuild.src_uri = 'https://www.website.com/download/stuff.tar.gz'
        ebuild.distro = 'lunar'
        ebuild.add_run_depend('p2os_driver')
        ebuild.add_run_depend('fake_package', False)
        with self.assertRaises(UnresolvedDependency):
            ebuild_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
