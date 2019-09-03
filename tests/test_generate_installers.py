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

import re

from rosinstall_generator.distro import get_distro
from superflore.exceptions import UnknownBuildType
from superflore.generate_installers import generate_installers
import unittest


def _gen_package(overlay, pkg, distro, preserve_existing, collector):
    """This is just a stub. We just add to the collector"""
    collector.append(pkg)
    # return new installer, name it.
    return True, pkg, pkg


def _fail_if_p2os(overlay, pkg, distro, preserve_existing, collector):
    """Fail if it's a p2os package"""
    collector.append(pkg)
    if 'p2os' in pkg:
        return False, True, pkg
    return True, True, pkg


def _skip_if_p2os(overlay, pkg, distro, preserve_existing, collector):
    """Skip if it's a p2os package"""
    collector.append(pkg)
    if 'p2os' in pkg:
        return False, False, pkg
    return True, pkg, pkg


def _create_if_p2os(overlay, pkg, distro, preserve_existing, collector):
    """Don't if the package is p2os"""
    collector.append(pkg)
    if 'p2os' in pkg:
        return True, False, pkg
    return True, True, pkg


def _raise_exceptions(overlay, pkg, distro, preserve_existing, collector):
    """Raise exceptions"""
    collector.append(pkg)
    if 'b' in pkg:
        raise UnknownBuildType('b')
    elif 'k' in pkg:
        raise KeyError('k')
    return True, pkg, pkg


class TestGenerateInstallers(unittest.TestCase):
    def test_generation(self):
        """Test Generate Installers"""
        acc = list()
        # attempt to generate the installers
        inst, broken, changes = generate_installers(
            get_distro('lunar'), None, _gen_package, False, acc
        )
        # since we don't do anything, there should be no failures.
        self.assertEqual(broken,{})
        # make sure all packages got indexed
        self.assertEqual(sorted(acc), sorted(inst))

    def test_unresolved(self):
        """Test for an unresolved dependency"""
        acc = list()
        inst, broken, changes = generate_installers(
            get_distro('lunar'), None, _fail_if_p2os, False, acc
        )
        broken = [b for b in broken]
        total_list = inst + broken
        # total list should have all packages in acc
        self.assertEqual(sorted(total_list), sorted(acc))
        # find missing packages, generate the change
        missing = [p for p in acc if not p in inst]
        # compare the contents
        self.assertEqual(sorted(broken), sorted(missing))

    def test_skipped(self):
        """Test how skipped packages are handled"""
        acc = list()
        inst, broken, changes = generate_installers(
            get_distro('lunar'), None, _skip_if_p2os, True, acc
        )
        broken = [b for b in broken]
        total_list = inst + broken
        # total list should have less than acc
        self.assertNotEqual(sorted(total_list), sorted(broken))
        missing = [p for p in acc if not p in total_list]
        # should only have 'p2os' packages
        non_p2os = [p for p in missing if 'p2os' not in p]
        self.assertEqual(non_p2os, [])

    def test_exceptions(self):
        """Test exceptions"""
        acc = list()
        inst, broken, changes = generate_installers(
            get_distro('lunar'), None, _raise_exceptions, True, acc
        )
        # anything with a 'k', 'l', or a 'b' has been skipped
        for p in inst:
            self.assertNotIn('k', p)
            self.assertNotIn('b', p)

    def test_changes(self):
        """Tests changes represented by generate installers"""
        changes_re = '(([a-zA-Z]|\_|[0-9])+)\ [0-9]\.[0-9]\.[0-9]("-r"[0-9])?'
        acc = list()
        inst, broken, changes = generate_installers(
            get_distro('lunar'), None, _create_if_p2os, True, acc
        )
        found = False
        for c in changes:
            ret = re.search(changes_re, c)
            if ret:
                found = True
                print(ret.groups())
                self.assertIn('p2os', ret.group(0))
        self.assertTrue(found)
