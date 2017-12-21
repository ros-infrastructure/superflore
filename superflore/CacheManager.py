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
import pickle

from superflore.utils import info


class CacheManager:
    def __init__(self, filename):
        self.filename = filename
        self.cache = dict()

    def __enter__(self):
        # load the initial cache, if it exists
        if self.filename and os.path.isfile(self.filename):
            info("Loading cached file '%s'" % self.filename)
            self.cache_file = open(self.filename, 'rb')
            self.cache = pickle.load(self.cache_file)
            self.cache_file.close()
        return self.cache

    def __exit__(self, *args):
        # save the cache, if it exists
        if self.filename:
            info("Saving cached file '%s'" % self.filename)
            self.cache_file = open(self.filename, 'wb')
            pickle.dump(self.cache, self.cache_file)
            self.cache_file.close()
