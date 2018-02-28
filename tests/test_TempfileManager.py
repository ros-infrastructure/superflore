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

import os

from superflore.TempfileManager import TempfileManager
import unittest

class TestTempfileManager(unittest.TestCase):
    def test_create_specified(self):
        """Test making a directory in a legal location"""
        with TempfileManager('/tmp/test') as ret:
            self.assertEqual(ret, '/tmp/test')
        # clean up
        self.assertTrue(os.path.exists('/tmp/test'))
        os.rmdir('/tmp/test')
        
    def test_failed_to_create(self):
        """Test making a directory in a bad location"""
        with self.assertRaises(OSError):
            with TempfileManager('/root/bad_permissions') as tmp:
                # code should not enter here
                pass
