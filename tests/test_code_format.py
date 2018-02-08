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
import subprocess
import sys


def test_flake8():
    """Test source code for pyFlakes conformance"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(this_dir, '..', 'superflore')
    cmd = [sys.executable, '-m', 'flake8', source_dir, '--count']
    # if flake8_import_order is installed, set the style to google
    try:
        import flake8_import_order  # noqa
        cmd.extend(['--import-order-style=google'])
    except ImportError:
        pass
    # work around for https://gitlab.com/pycqa/flake8/issues/179
    cmd.extend(['--jobs', '1'])
    if sys.version_info < (3, 4):
        # Unless Python3, skip files with new syntax, like `yield from`
        cmd.append('--exclude={0}/*async_execute_process_asyncio/impl.py'.format(source_dir))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    print(stdout)
    assert p.returncode == 0, \
        "Command '{0}' returned non-zero exit code '{1}'".format(' '.join(cmd), p.returncode)


def test_pep8():
    """Test source code for PEP8 conformance"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(this_dir, '..', 'superflore')
    cmd = [sys.executable, '-m', 'pycodestyle', source_dir, '--count']
    if sys.version_info < (3, 4):
        # Unless Python3, skip files with new syntax, like `yield from`
        cmd.append('--exclude={0}/*async_execute_process_asyncio/impl.py'.format(source_dir))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    print(stdout)
    assert p.returncode == 0, \
        "Command '{0}' returned non-zero exit code '{1}'".format(' '.join(cmd), p.returncode)
