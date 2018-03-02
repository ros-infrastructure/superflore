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

from superflore.CacheManager import CacheManager
from superflore.TempfileManager import TempfileManager
import unittest


class TestCacheManager(unittest.TestCase):
    def test_CacheFile(self):
        """Test the CacheManager"""
        with TempfileManager(None) as tmp:
            os.chmod(tmp, 17407)
            cache_file = '%s/my_cache.pickle' % tmp
            with CacheManager(cache_file) as cache:
                cache['a'] = 'A'
                cache['b'] = 'B'
                cache['c'] = 'C'
            with CacheManager(cache_file) as cache:
                self.assertEqual(cache['a'], 'A')
                self.assertEqual(cache['b'], 'B')
                self.assertEqual(cache['c'], 'C')
            self.assertTrue(os.path.exists(cache_file))
