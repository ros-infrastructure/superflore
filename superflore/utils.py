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
import random
import re
import string
import sys

from superflore.exceptions import UnknownLicense
from superflore.exceptions import UnknownPlatform
from superflore.rosdep_support import resolve_rosdep_key
from termcolor import colored


def warn(string):  # pragma: no cover
    print(colored('>>>> {0}'.format(string), 'yellow'))


def ok(string):  # pragma: no cover
    print(colored('>>>> {0}'.format(string), 'green'))


def err(string):  # pragma: no cover
    print(colored('!!!! {0}'.format(string), 'red'))


def info(string):  # pragma: no cover
    print(colored('>>>> {0}'.format(string), 'cyan'))


def file_pr(overlay, delta, missing_deps, comment):
    msg = ''
    if comment:
        msg += '%s\n' % comment
    msg += 'To reproduce this PR, run the following command.\n\n'
    args = sys.argv
    args[0] = args[0].split('/')[-1]
    msg += '```\n%s\n```' % ' '.join(args)
    try:
        overlay.pull_request('%s\n%s\n%s' % (msg, delta, missing_deps))
    except Exception as e:
        err(
            'Failed to file PR with the %s/%s repo!' % (
                overlay.repo.repo_owner,
                overlay.repo.repo_name
            )
        )
        err('Exception: {0}'.format(e))
        sys.exit(1)


def make_dir(dirname):
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(dirname):
            pass
        else:
            raise e


def get_pkg_version(distro, pkg_name):
    pkg = distro.release_packages[pkg_name]
    repo = distro.repositories[pkg.repository_name].release_repository
    maj_min_patch, deb_inc = repo.version.split('-')
    if deb_inc != '0':
        return '{0}-r{1}'.format(maj_min_patch, deb_inc)
    return maj_min_patch


def rand_ascii_str(length=10):
    """
    Generates a random string of ascii characters of length 'length'
    """
    return ''.join(random.choice(string.ascii_letters) for x in range(length))


def sanitize_string(string, illegal_chars):
    ret = str()
    for c in string:
        if c in illegal_chars:
            ret += '\\'
        ret += c
    return ret


def trim_string(string, length=80):
    if len(string) < length:
        return string
    end_string = '[...]'
    return string[:length - len(end_string)] + end_string


def get_license(l):
    bsd_re = '^(BSD)((.)*([124]))?'
    gpl_re = '(GPL)((.)*([123]))?'
    lgpl_re = '^(LGPL)((.)*([23]|2\\.1))?'
    apache_re = '^(Apache)((.)*(1\\.0|1\\.1|2\\.0|2))?'
    cc_re = '^(Creative(.)?Commons)((.)*)'
    cc_nc_nd_re = '^((Creative(.)?Commons)|CC)((.)*)' +\
                  '((Non(.)?Commercial)|NC)((.)*)((No(.)?Derivatives)|ND)'
    cc_by_nc_sa_re = '^(CC(.)?BY(.)?NC(.)?SA(.)?)'
    moz_re = '^(Mozilla)((.)*(1\\.1))?'
    boost_re = '^(Boost)((.)*([1]))?'
    pub_dom_re = '^(Public(.)?Domain)'
    mit_re = '^MIT'
    f = re.IGNORECASE

    if re.search(apache_re, l, f):
        version = re.search(apache_re, l, f).group(4)
        if version:
            return 'Apache-%.1f' % (float(version))
        return 'Apache-1.0'
    elif re.search(bsd_re, l, f):
        version = re.search(bsd_re, l, f).group(4)
        if version:
            return 'BSD-{0}'.format(version)
        return 'BSD'
    elif re.search(lgpl_re, l, f):
        version = re.search(lgpl_re, l, f).group(4)
        if version:
            return 'LGPL-{0}'.format(version)
        return 'LGPL-2'
    elif re.search(gpl_re, l, f):
        version = re.search(gpl_re, l, f).group(4)
        if version:
            return 'GPL-{0}'.format(version)
        return 'GPL-1'
    elif re.search(moz_re, l, f):
        version = re.search(moz_re, l, f).group(4)
        if version:
            return 'MPL-{0}'.format(version)
        return 'MPL-2.0'
    elif re.search(mit_re, l, f):
        return 'MIT'
    elif re.search(cc_nc_nd_re, l, f):
        return 'CC-BY-NC-ND-4.0'
    elif re.search(cc_by_nc_sa_re, l, f):
        return 'CC-BY-NC-SA-4.0'
    elif re.search(cc_re, l, f):
        return 'CC-BY-SA-3.0'
    elif re.search(boost_re, l, f):
        return 'Boost-1.0'
    elif re.search(pub_dom_re, l, f):
        return 'public_domain'
    else:
        err('Could not match license "{0}".'.format(l))
        raise UnknownLicense('bad license')


def resolve_dep(pkg, os):
    if os == 'oe':
        return _resolve_dep_open_embedded(pkg)
    elif os == 'gentoo':
        return resolve_rosdep_key(pkg, 'gentoo', '2.4.0')
    else:
        msg = "Unknown target platform '{0}'".format(os)
        raise UnknownPlatform(msg)


def _resolve_dep_open_embedded(pkg):
    """
    TODO(allenh1): integrate rosdep
    """
    if pkg == 'python-yaml':
        return 'python-pyyaml'
    elif pkg == 'tinyxml2':
        return 'libtinyxml2'
    elif pkg == 'tinyxml':
        return 'libtinyxml'
    elif pkg == 'pkg-config':
        return 'pkgconfig'
    elif pkg == 'libconsole-bridge':
        return 'console-bridge'
    elif pkg == 'libconsole-bridge-dev':
        return 'console-bridge'
    elif pkg == 'python-empy':
        return 'python-empy-native'
    elif pkg == 'catkin':
        return 'catkin-native catkin'
    elif pkg == 'python-catkin-pkg':
        return 'python-catkin-pkg-native'
    elif pkg == 'libpoco-dev':
        return 'poco'
    else:
        return pkg.replace('_', '-')
