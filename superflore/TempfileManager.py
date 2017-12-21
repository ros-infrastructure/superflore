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

import errno
import os
import shutil
import subprocess
import tempfile

from superflore.utils import err
from superflore.utils import info


class TempfileManager:
    def __init__(self, path):
        self.arg_path = path
        self.temp_path = None

    def __enter__(self):
        if self.arg_path:
            try:
                os.mkdir(self.arg_path)
            except OSError as ex:
                if ex.errno != errno.EEXIST:
                    raise
            return self.arg_path
        else:
            self.temp_path = tempfile.mkdtemp()
            info("Working in temporary directory %s" % self.temp_path)
        return self.temp_path

    def __exit__(self, *args):
        if self.temp_path:
            info("Cleaning up temporary directory %s" % self.temp_path)
            try:
                shutil.rmtree(self.temp_path)
            except OSError as ex:
                if ex.errno == errno.EPERM:
                    err("Failed to rmtree %s" % self.temp_path)
                    err("Escalating to sudo rm -rf %s" % self.temp_path)
                    subprocess.check_call(
                        ('sudo rm -rf %s' % self.temp_path).split()
                    )
                else:
                    raise
            self.temp_path = None
