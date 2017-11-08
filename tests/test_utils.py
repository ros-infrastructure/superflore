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

from superflore.utils import sanitize_string
from superflore.utils import trim_string
from superflore.utils import get_license

import unittest


class TestUtils(unittest.TestCase):
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

    def test_get_license(self):
        """Test license recognition function"""
        ret = get_license('Apache License 2.0')
        self.assertEqual(ret, 'Apache-2.0')
        ret = get_license('Apache 2.0')
        self.assertEqual(ret, 'Apache-2.0')
        ret = get_license('Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)')
        self.assertEqual(ret, 'Apache-2.0')
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

if __name__ == '__main__':
    unittest.main()
