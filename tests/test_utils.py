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

from superflore.exceptions import UnknownLicense
from superflore.exceptions import UnknownPlatform
from superflore.TempfileManager import TempfileManager
from superflore.utils import clean_up
from superflore.utils import gen_delta_msg
from superflore.utils import get_license
from superflore.utils import gen_missing_deps_msg
from superflore.utils import get_pr_text
from superflore.utils import make_dir
from superflore.utils import rand_ascii_str
from superflore.utils import resolve_dep
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
        """Tests the make directory funciton"""
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
        self.assertEqual(ret, 'Apache-1.0')
        ret = get_license('BSD-3')
        self.assertEqual(ret, 'BSD')
        ret = get_license('Apache-2')
        self.assertEqual(ret, 'Apache-2.0')
        ret = get_license('CreativeCommons-Attribution-NonCommercial-NoDerivatives-4.0')
        self.assertEqual(ret, 'CC-BY-NC-ND-4.0')
        ret = get_license('CC BY-NC-SA 4.0')
        self.assertEqual(ret, 'CC-BY-NC-SA-4.0')
        ret = get_license('BoostSoftwareLicense Version1.0')
        self.assertEqual(ret, 'Boost-1.0')
        ret = get_license('GNU GPLv3')
        self.assertEqual(ret, 'GPL-3')
        ret = get_license('Public Domain')
        self.assertEqual(ret, 'public_domain')
        ret = get_license('GPL')
        self.assertEqual(ret, 'GPL-1')
        ret = get_license('GNU GENERAL PUBLIC LICENSE Version 3')
        self.assertEqual(ret, 'GPL-3')
        ret = get_license('GNU Lesser Public License 2.1')
        self.assertEqual(ret, 'LGPL-2.1')
        ret = get_license('Mozilla Public License Version 1.1')
        self.assertEqual(ret, 'MPL-1.1')
        ret = get_license('Mozilla Public License')
        self.assertEqual(ret, 'MPL-2.0')
        ret = get_license('BSD License 2.0')
        self.assertEqual(ret, 'BSD-2')
        ret = get_license('MIT')
        self.assertEqual(ret, 'MIT')
        ret = get_license('Creative Commons')
        self.assertEqual(ret, 'CC-BY-SA-3.0')
        with self.assertRaises(UnknownLicense):
            ret = get_license('TODO')

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
                 '---------------\n'\
                 '* baz\n\n'\
                 'Hydro Changes:\n'\
                 '---------------\n'\
                 '* bar\n'\
                 '* foo\n\n'
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
        expected = 'To reproduce this PR, run the following command.\n\n'\
                   '```\na b c d\n```\n'
        self.assertEqual(expected, get_pr_text())
        # test with an argument
        expected = 'sample\n'\
                   'To reproduce this PR, run the following command.\n\n'\
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
        """Test resolve dependency with Open Embedded"""
        # Note(allenh1): we're not going to test the hard-coded resolutions.
        self.assertEqual(resolve_dep('tinyxml2', 'oe'), 'libtinyxml2')
        self.assertEqual(resolve_dep('p2os_msgs', 'oe'), 'p2os-msgs')
