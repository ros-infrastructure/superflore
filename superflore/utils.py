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
import time

from superflore.exceptions import UnknownLicense
from superflore.exceptions import UnknownPlatform
from superflore.rosdep_support import resolve_rosdep_key
from termcolor import colored

# Modify if a new distro is added
active_distros = ['indigo', 'kinetic', 'lunar', 'melodic']
ros2_distros = ['ardent', 'bouncy']


def warn(string):  # pragma: no cover
    print(colored('>>>> {0}'.format(string), 'yellow'))


def ok(string):  # pragma: no cover
    print(colored('>>>> {0}'.format(string), 'green'))


def err(string):  # pragma: no cover
    print(colored('!!!! {0}'.format(string), 'red'))


def info(string):  # pragma: no cover
    print(colored('>>>> {0}'.format(string), 'cyan'))


def get_pr_text(comment=None):
    msg = ''
    if comment:
        msg += '%s\n' % comment
    msg += 'To reproduce this PR, run the following command.\n\n'
    args = sys.argv
    args[0] = args[0].split('/')[-1]
    msg += '```\n%s\n```' % ' '.join(args) + '\n'
    return msg


def save_pr(overlay, delta, missing_deps, comment):
    with open('.pr-title.tmp', 'w') as title_file:
        title_file.write('rosdistro sync, {0}\n'.format(time.ctime()))
    with open('.pr-message.tmp', 'w') as pr_msg_file:
        pr_msg_file.write('%s\n' % get_pr_text(comment))


def load_pr():
    try:
        with open('.pr-message.tmp', 'r') as msg_file:
            msg = msg_file.read().rstrip('\n')
        with open('.pr-title.tmp', 'r') as title_file:
            title = title_file.read().rstrip('\n')
    except OSError:
        err('Failed to open PR title/message file!')
        err(
            'Please supply the %s and %s files' % (
                '.pr_message.tmp',
                '.pr_title.tmp'
            )
        )
        raise
    return msg, title
    clean_up()


def file_pr(overlay, delta, missing_deps, comment, distro=None):
    try:
        msg = get_pr_text(comment)
        overlay.pull_request('%s\n%s\n%s' % (msg, delta, missing_deps), distro)
    except Exception as e:
        err(
            'Failed to file PR with the %s/%s repo!' % (
                overlay.repo.repo_owner,
                overlay.repo.repo_name
            )
        )
        err('Exception: {0}'.format(e))
        sys.exit(1)


def clean_up():
    if os.path.exists('.pr-message.tmp'):
        os.remove('.pr-message.tmp')
    if os.path.exists('.pr-title.tmp'):
        os.remove('.pr-title.tmp')


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
    gpl_re = '((([^L])*(GPL)([^0-9]*))|'\
        '(GNU(.)*GENERAL(.)*PUBLIC(.)*LICENSE([^0-9])*))([0-9])?'
    lgpl_re = '(((LGPL)([^0-9]*))|'\
        '(GNU(.)*Lesser(.)*Public(.)*License([^0-9])*))([0-9]?\\.[0-9])?'
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
        version = re.search(lgpl_re, l, f)
        grp = len(version.groups())
        version = version.group(grp)
        if version:
            return 'LGPL-{0}'.format(version)
        return 'LGPL-2'
    elif re.search(gpl_re, l, f):
        version = re.search(gpl_re, l, f)
        grp = len(version.groups())
        version = version.group(grp)
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


def gen_delta_msg(total_changes):
    """Return string of changes for the PR message."""
    delta = "Changes:\n"
    delta += "========\n"
    for distro in sorted(total_changes):
        if not total_changes[distro]:
            continue
        delta += "%s Changes:\n" % distro.title()
        delta += "---------------\n"
        for d in sorted(total_changes[distro]):
            delta += '* {0}\n'.format(d)
        delta += "\n"
    return delta


def gen_missing_deps_msg(missing_list):
    """Return string of missing deps for the PR message."""
    missing_deps = None
    if len(missing_list) > 0:
        missing_deps = "Missing Dependencies:\n"
        missing_deps += "=====================\n"
        for pkg in sorted(missing_list):
            missing_deps += " * [ ] {0}\n".format(pkg)
    return missing_deps or 'No missing dependencies.\n'


def url_to_repo_org(url):
    """Extract owner and repository from GitHub url."""
    # check that the upstream_repo is a github repo
    if 'github.com' not in url:
        raise RuntimeError(
            'Extraction of repository and owner info from non-GitHub'
            'repositories is not yet supported!'
        )
    url = url.replace('https://github.com/', '').split('/')
    return url[0], url[1]
