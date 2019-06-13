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


class metadata_xml(object):
    def __init__(self):
        self.email = "hunterlallen@protonmail.com"
        self.name = "Hunter L. Allen"
        self.upstream_name = None
        self.upstream_email = None
        self.upstream_bug_url = None
        self.maintainer_type = "person"
        self.longdescription = None

    def get_metadata_text(self):
        ret = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        ret += "<!DOCTYPE pkgmetadata SYSTEM "
        ret += "\"http://www.gentoo.org/dtd/metadata.dtd\">\n"
        ret += "<pkgmetadata>\n"
        if self.longdescription and isinstance(self.longdescription, str):
            ret += "  <longdescription>\n"
            ret += "    " + self.longdescription + "\n"
            ret += "  </longdescription>\n"
        ret += "  <maintainer type=\"" + self.maintainer_type + "\">\n"
        ret += "    <email>" + self.email + "</email>\n"
        ret += "    <name>" + self.name + "</name>\n"
        ret += "  </maintainer>\n"
        if self.upstream_email and self.upstream_name:
            ret += "  <upstream>\n"
            ret += "    <maintainer status=\"active\">\n"
            ret += "      <email>" + self.upstream_email + "</email>\n"
            ret += "      <name>" + self.upstream_name + "</name>\n"
            ret += "    </maintainer>\n"
            if self.upstream_bug_url:
                ret += "    <bugs-to>" + self.upstream_bug_url + "</bugs-to>\n"
            ret += "  </upstream>\n"
        ret += "</pkgmetadata>\n"
        return ret
