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


class UnresolvedDependency(Exception):
    def __init__(self, message):
        self.message = message


class UnknownPlatform(Exception):
    def __init__(self, message):
        self.message = message


class NoPkgXml(Exception):
    def __init__(self, message):
        self.message = message


class NoGitHubAuthToken(Exception):
    def __init__(self):
        self.message = 'Please create an OAuth token for Superflore, ' \
            'and place the string in the environment variable ' \
            'SUPERFLORE_GITHUB_TOKEN'


class UnknownBuildType(Exception):
    """Raised when we don't know what to inherit to build the package"""
    def __init__(self, msg):
        self.message = msg
