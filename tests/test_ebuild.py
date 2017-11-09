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
from superflore.generators.ebuild.ebuild import ebuild_keyword
from superflore.exceptions import UnresolvedDependency
import unittest


class TestEbuildOutput(unittest.TestCase):
    def get_ebuild(self):
        ebuild = Ebuild()
        ebuild.homepage = 'https://www.website.com'
        ebuild.description = 'an ebuild'
        ebuild.src_uri = 'https://www.website.com/download/stuff.tar.gz'
        ebuild.distro = 'lunar'
        return ebuild

    def test_simple(self):
        """Test Ebuild Format"""
        ebuild = self.get_ebuild()
        ebuild.add_run_depend('p2os_driver')
        got_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        with open('tests/ebuild/simple_expected.ebuild', 'r') as expect_file:
            correct_text = expect_file.read()
        self.assertEqual(got_text, correct_text)

    def test_bad_external_build_depend(self):
        """Test Bad External Build Dependency"""
        ebuild = self.get_ebuild()
        ebuild.add_run_depend('p2os_driver')
        ebuild.add_build_depend('fake_package', False)
        with self.assertRaises(UnresolvedDependency):
            ebuild_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')

    def test_bad_external_run_depend(self):
        """Test Bad External Run Dependency"""
        ebuild = self.get_ebuild()
        ebuild.add_run_depend('p2os_driver')
        ebuild.add_run_depend('fake_package', False)
        with self.assertRaises(UnresolvedDependency):
            ebuild_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')

    def test_external_build_depend(self):
        """Test External Build Dependency"""
        ebuild = self.get_ebuild()
        ebuild.add_run_depend('p2os_driver')
        ebuild.add_build_depend('cmake', False)
        ebuild_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        self.assertTrue('dev-util/cmake' in ebuild_text)

    def test_external_run_depend(self):
        """Test External Run Dependency"""
        ebuild = self.get_ebuild()
        ebuild.add_run_depend('p2os_driver')
        ebuild.add_run_depend('cmake', False)
        ebuild_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        self.assertTrue('dev-util/cmake' in ebuild_text)

    def test_rdepend_depend(self):
        """Test Disjoint RDEPEND/DEPEND"""
        ebuild = self.get_ebuild()
        ebuild.add_run_depend('p2os_driver')
        self.assertTrue('p2os_driver' in ebuild.rdepends)
        ebuild.add_build_depend('p2os_driver')
        self.assertTrue('p2os_driver' in ebuild.rdepends)
        self.assertFalse('p2os_driver' in ebuild.depends)
        ebuild.add_run_depend('cmake', False)
        self.assertTrue('cmake' in ebuild.rdepends_external)
        self.assertFalse('cmake' in ebuild.rdepends)
        ebuild.add_build_depend('cmake', False)
        self.assertTrue('cmake' in ebuild.rdepends_external)
        self.assertFalse('cmake' in ebuild.depends_external)
        self.assertFalse('cmake' in ebuild.rdepends)
        self.assertFalse('cmake' in ebuild.depends)

    def test_build_depend_internal(self):
        """Test build depends when internal/external"""
        ebuild = self.get_ebuild()
        ebuild.add_build_depend('p2os_driver', True)
        self.assertTrue('p2os_driver' in ebuild.depends)
        self.assertFalse('p2os_driver' in ebuild.depends_external)

    def test_run_depend_internal(self):
        """Test build depends when internal/external"""
        ebuild = self.get_ebuild()
        ebuild.add_run_depend('p2os_driver', True)
        self.assertTrue('p2os_driver' in ebuild.rdepends)
        self.assertFalse('p2os_driver' in ebuild.rdepends_external)

    def test_depend_only_pkgs(self):
        """Test DEPEND only packages"""
        ebuild = self.get_ebuild()
        ebuild.add_run_depend('virtual/pkgconfig', False)
        self.assertTrue('virtual/pkgconfig' in ebuild.depends_external)
        self.assertFalse('virtual/pkgconfig' in ebuild.rdepends_external)

    def test_ebuild_keyword_unstable(self):
        """Test Unstable Keyword"""
        keyword = ebuild_keyword('amd64', False)
        self.assertEqual(keyword.to_string(), '~amd64')

    def test_ebuild_keyword_stable(self):
        """Test Stable Keyword"""
        keyword = ebuild_keyword('amd64', True)
        self.assertEqual(keyword.to_string(), 'amd64')

    def test_add_keyword(self):
        """Test Add Keyword"""
        ebuild = self.get_ebuild()
        ebuild.add_keyword('amd64', True)
        ebuild.add_keyword('arm64', False)
        amd64_stable = ebuild_keyword('amd64', True)
        arm64_unstable = ebuild_keyword('arm64', False)
        self.assertTrue(amd64_stable in ebuild.keys)
        self.assertTrue(arm64_unstable in ebuild.keys)

    def test_remove_python3(self):
        """Test The python_3 Boolean"""
        ebuild = self.get_ebuild()
        ebuild.python_3 = False
        got_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        self.assertTrue('PYTHON_COMPAT=( python2_7 )' in got_text)

    def test_default_python2_python3(self):
        """Test That Python2/3 Is the Default"""
        ebuild = self.get_ebuild()
        got_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        self.assertTrue('PYTHON_COMPAT=( python{2_7,3_5} )' in got_text)

    def test_has_patches(self):
        """Test Patch Code Generation"""
        ebuild = self.get_ebuild()
        ebuild.has_patches = True;
        got_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        self.assertTrue('EPATCH_SOURCE="${FILESDIR}"' in got_text)
        self.assertTrue('EPATCH_SUFFIX="patch"' in got_text)
        self.assertTrue('EPATCH_FORCE="yes"' in got_text)
        self.assertTrue('epatch' in got_text)

    def test_lacks_patches(self):
        """Test Non-Patched Code Generation"""
        ebuild = self.get_ebuild()
        got_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        self.assertFalse('EPATCH_SOURCE="${FILESDIR}"' in got_text)
        self.assertFalse('EPATCH_SUFFIX="patch"' in got_text)
        self.assertFalse('EPATCH_FORCE="yes"' in got_text)
        self.assertFalse('epatch' in got_text)

    def test_opencv3_filter_flags(self):
        """Test Filter Flags for OpenCV3"""
        ebuild = self.get_ebuild()
        ebuild.name = 'opencv3'
        got_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        self.assertTrue("filter-flags '-march=*' '-mcpu=*' '-mtune=*'" in got_text)

    def test_stage_filter_flags(self):
        """Test Filter Flags for Stage"""
        ebuild = self.get_ebuild()
        ebuild.name = 'stage'
        got_text = ebuild.get_ebuild_text('Open Source Robotics Foundation', 'BSD')
        self.assertTrue("filter-flags '-std=*'" in got_text)