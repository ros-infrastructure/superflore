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

import unittest

from superflore.generators.nix.nix_expression import NixLicense


class TestNixLicense(unittest.TestCase):

    def test_known_license(self):
        l = NixLicense('GPL 3')
        self.assertEqual(l.nix_code, 'gpl3')

    def test_unknown_license(self):
        l = NixLicense("some license")
        self.assertEqual(l.nix_code, '"some-license"')

    def test_public_domain(self):
        l = NixLicense("Public Domain")
        self.assertEqual(l.nix_code, 'publicDomain')
