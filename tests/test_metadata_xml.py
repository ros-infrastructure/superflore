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

from superflore.generators.ebuild.metadata_xml import metadata_xml
import xmltodict
import unittest


class TestMetadataXml(unittest.TestCase):
    def get_metadata_xml(self):
        xml = metadata_xml()
        xml.upstream_name = "Someone Important"
        xml.upstream_email = "someone@example.com"
        xml.upstream_bug_url = "https://bugzilla.someone.com"
        xml.maintainer_type = "person"
        xml.longdescription = "A ROS node that does cool stuff"
        return xml.get_metadata_text()

    def test_metadata_format(self):
        """Test for parsing"""
        doc = xmltodict.parse(self.get_metadata_xml())
        metadata = doc['pkgmetadata']
        self.assertEqual(metadata['longdescription'], 'A ROS node that does cool stuff')
        who = metadata['upstream']['maintainer']
        self.assertEqual(who['email'], 'someone@example.com')
        self.assertEqual(who['name'], 'Someone Important')
        self.assertEqual(metadata['upstream']['bugs-to'], 'https://bugzilla.someone.com')
