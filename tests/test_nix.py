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
        license = NixLicense('GPL 3')
        self.assertEqual(license.nix_code, 'gpl3')

    def test_unknown_license(self):
        license = NixLicense('some license')
        self.assertEqual(license.nix_code, '"some-license"')

    def test_public_domain(self):
        license = NixLicense('Public Domain')
        self.assertEqual(license.nix_code, 'publicDomain')

    def test_escape_quote_backslash(self):
        license = NixLicense(r'license with "quotes" and \backslash" ')
        self.assertEqual(
            license.nix_code,
            r'"license-with-\"quotes\"-and-\\backslash\"-"',
        )

    def test_escape_quote_dollar_brace(self):
        license = NixLicense('some license with the "${" sequence')
        self.assertEqual(
            license.nix_code,
            r'"some-license-with-the-\"\${\"-sequence"',
        )
