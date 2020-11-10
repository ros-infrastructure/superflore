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

import os
import string
import sys
import time

from pkg_resources import parse_version
from superflore import __version__
from superflore.exceptions import UnknownPlatform
from superflore.exceptions import UnresolvedDependency
from superflore.TempfileManager import TempfileManager
from superflore.utils import clean_up
from superflore.utils import gen_delta_msg
from superflore.utils import get_license
from superflore.utils import gen_missing_deps_msg
from superflore.utils import get_pr_text
from superflore.utils import get_superflore_version
from superflore.utils import make_dir
from superflore.utils import rand_ascii_str
from superflore.utils import resolve_dep
from superflore.utils import retry_on_exception
from superflore.utils import sanitize_string
from superflore.utils import trim_string
from superflore.utils import url_to_repo_org

import unittest


class TestUtils(unittest.TestCase):
    def set_lang_env(self):
        os.environ['LANG'] = 'en_US.UTF-8'
        os.environ['LC_ALL'] = 'en_US.UTF-8'

    def test_sanitize(self):
        """Test sanitize string function"""
        # test with an empty string
        ret = sanitize_string('', 'aeiouy')
        self.assertEqual(ret, '')
        # test empty second argument
        ret = sanitize_string('first', '')
        self.assertEqual(ret, 'first')
        # test escaping every character
        ret = sanitize_string('aaaaeeeeoooo', 'aeo')
        self.assertEqual(ret, '\\a\\a\\a\\a\\e\\e\\e\\e\\o\\o\\o\\o')

    def test_trim_string(self):
        """Test trim string function"""
        # test overflow
        ret = trim_string('abcde', length=5)
        self.assertEqual(ret, '[...]')
        # test usual case
        ret = trim_string('abcde')
        self.assertEqual(ret, 'abcde')
        # test mixed case
        ret = trim_string('abcdef', length=6)
        self.assertEqual(ret, 'a[...]')

    def test_mkdir(self):
        """Tests the make directory function"""
        with TempfileManager(None) as temp_dir:
            created = '%s/test' % temp_dir
            make_dir(created)
            self.assertTrue(os.path.isdir(created))
            # try and create the directory again, should pass
            make_dir(created)
            self.assertTrue(os.path.isdir(created))

    def test_rand_ascii_str(self):
        """Test the random ascii generation function"""
        rand = rand_ascii_str(100)
        self.assertEqual(len(rand), 100)
        self.assertTrue(all(c in string.ascii_letters for c in rand))

    def test_get_license(self):
        """Test license recognition function"""
        ret = get_license('Apache License 2.0')
        self.assertEqual(ret, 'Apache-2.0')
        ret = get_license('Apache 2.0')
        self.assertEqual(ret, 'Apache-2.0')
        ret = get_license('Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)')
        self.assertEqual(ret, 'Apache-2.0')
        ret = get_license('Apache')
        self.assertEqual(ret, 'Apache')
        ret = get_license('BSD-3')
        self.assertEqual(ret, 'BSD-3-Clause')
        ret = get_license('Apache2')
        self.assertEqual(ret, 'Apache-2.0')
        ret = get_license('CreativeCommons-Attribution-NonCommercial-NoDerivatives-4.0')
        self.assertEqual(ret, 'CC-BY-NC-ND-4.0')
        ret = get_license('CC BY-NC-SA 4.0')
        self.assertEqual(ret, 'CC-BY-NC-SA-4.0')
        ret = get_license('Boost Software License, Version 1.0')
        self.assertEqual(ret, 'BSL-1.0')
        ret = get_license('GNU GPL v3.0')
        self.assertEqual(ret, 'GPL-3.0-only')
        ret = get_license('Public Domain')
        self.assertEqual(ret, 'PD')
        ret = get_license('GPL')
        self.assertEqual(ret, 'GPL')
        ret = get_license('GNU General Public License v2.0')
        self.assertEqual(ret, 'GPL-2.0-only')
        ret = get_license('GNU Lesser Public License 2.1')
        self.assertEqual(ret, 'LGPL-2.1-only')
        ret = get_license('Mozilla Public License Version 1.1')
        self.assertEqual(ret, 'MPL-1.1')
        ret = get_license('Mozilla Public License')
        self.assertEqual(ret, 'Mozilla-Public-License')
        ret = get_license('BSD License 2.0')
        self.assertEqual(ret, 'BSD-License-2.0')
        ret = get_license('MIT')
        self.assertEqual(ret, 'MIT')
        ret = get_license('Creative Commons')
        self.assertEqual(ret, 'Creative-Commons')
        ret = get_license('United States Government Purpose')
        self.assertEqual(ret, 'United-States-Government-Purpose')

    def test_delta_msg(self):
        """Test the delta message generated for the PR"""
        self.set_lang_env()
        total_changes = dict()
        total_changes['hydro'] = ['foo', 'bar']
        total_changes['boxturtle'] = ['baz']
        total_changes['C'] = []
        expect = 'Changes:\n'\
                 '========\n'\
                 'Boxturtle Changes:\n'\
                 '------------------\n'\
                 '* *baz*\n\n'\
                 'Hydro Changes:\n'\
                 '--------------\n'\
                 '* *bar*\n'\
                 '* *foo*\n\n'
        got = gen_delta_msg(total_changes)
        self.assertEqual(expect, got)

    def test_missing_deps_msg(self):
        """Test the missing dependencies list"""
        self.set_lang_env()
        self.assertEqual(
            gen_missing_deps_msg([]), 'No missing dependencies.\n'
        )
        ret = gen_missing_deps_msg(['python3', 'cmake'])
        expect = 'Missing Dependencies:\n'\
                 '=====================\n'\
                 ' * [ ] cmake\n'\
                 ' * [ ] python3\n'
        self.assertEqual(ret, expect)

    def test_url_to_repo_org(self):
        """Test the owner/repo extraction from a GitHub url"""
        with self.assertRaises(RuntimeError):
            owner, repo = url_to_repo_org('https://gitlab.com/allenh1/p2os')
        owner, repo = url_to_repo_org('https://github.com/allenh1/p2os')
        self.assertEqual(owner, 'allenh1')
        self.assertEqual(repo, 'p2os')

    def test_unknown_platform(self):
        """Test resolve_dep with bad OS"""
        with self.assertRaises(UnknownPlatform):
            ret = resolve_dep('cmake', 'Windoughs8')

    def test_get_pr_text(self):
        """Test get PR text"""
        tmp = sys.argv
        sys.argv = ['a', 'b', 'c', 'd']
        expected = 'This pull request was generated by running the following command:\n\n'\
                   '```\na b c d\n```\n'
        self.assertEqual(expected, get_pr_text())
        # test with an argument
        expected = 'sample\n'\
                   'This pull request was generated by running the following command:\n\n'\
                   '```\na b c d\n```\n'
        self.assertEqual(expected, get_pr_text('sample'))

    def test_cleanup(self):
        """Test PR dry run cleanup"""
        # should pass
        clean_up()
        # should remove files
        with TempfileManager(None) as tempdir:
            with open('%s/.pr-message.tmp' % tempdir, 'w') as msg_file:
                msg_file.write("message")
            with open('%s/.pr-title.tmp' % tempdir, 'w') as title_file:
                title_file.write("title")
            os.chdir(tempdir)
            clean_up()
            self.assertFalse(os.path.exists('%s/.pr-message.tmp' % tempdir))
            self.assertFalse(os.path.exists('%s/.pr-title.tmp' % tempdir))

    def test_resolve_dep_oe(self):
        """Test resolve dependency with OpenEmbedded"""
        self.assertEqual(resolve_dep('tinyxml2', 'openembedded')[0],
            ['libtinyxml2@meta-oe'])
        # Note: since p2os_msgs is a ROS package, rosdep resolve will fail
        with self.assertRaises(UnresolvedDependency):
            resolved_deps = resolve_dep('p2os_msgs', 'openembedded')

    def test_retry_on_exception(self):
        """Test retry on exception"""
        def callback_basic(must_be_one):
            if must_be_one == 1:
                return 'Success'
            raise Exception('Failure')

        def callback_params(must_be_three, must_be_four):
            if must_be_three == 3 and must_be_four == 4:
                return 'Success'
            return None

        def callback_retries(expected_num_retries):
            if callback_retries.limit >= expected_num_retries:
                return callback_retries.limit
            callback_retries.limit += 1
            raise Exception('Failure')
        # Checks success case
        self.assertEqual(retry_on_exception(callback_basic, 1), 'Success')
        # Checks failure case
        with self.assertRaises(Exception):
            retry_on_exception(callback_basic, 2)
        # Checks callback can receive multiple params
        self.assertEqual(retry_on_exception(callback_params, 3, 4), 'Success')
        # Checks it doesn't retry when max_retries is zero; runs just once
        callback_retries.limit = -1
        with self.assertRaises(Exception):
            retry_on_exception(callback_retries, 0, max_retries=0)
        self.assertEqual(callback_retries.limit, 0)
        # Checks it doesn't retry when max_retries is negative; runs just once
        callback_retries.limit = -1
        with self.assertRaises(Exception):
            retry_on_exception(callback_retries, 0, max_retries=-1)
        self.assertEqual(callback_retries.limit, 0)
        # Checks it gets retried 2 times before succeeding at the 3rd
        callback_retries.limit = 0
        self.assertEqual(retry_on_exception(
            callback_retries, 3, max_retries=3), 3)
        # Checks it gets retried 3 times before giving up fully
        callback_retries.limit = -1
        with self.assertRaises(Exception):
            retry_on_exception(callback_retries, 4, max_retries=3)
        self.assertEqual(callback_retries.limit, 3)
        # Check that when retrying 9 times it'll sleep at least 16 seconds
        # 0 + 0.125 + 0.25 + 0.5 + 1 + 2 + 4 + 8 + 0.125 = 16 seconds
        time_before = time.time()
        with self.assertRaises(Exception):
            retry_on_exception(callback_basic, 2, max_retries=9)
        elapsed_time = time.time()-time_before
        self.assertAlmostEqual(elapsed_time, 16, places=0)

    def test_get_superflore_version(self):
        """Test get SuperFlore version"""
        if __version__ != 'unset':
            self.assertGreaterEqual(parse_version(get_superflore_version()),
                                    parse_version('0.2.1'))
