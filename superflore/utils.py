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

from datetime import datetime
import errno
import os
import random
import re
import string
import sys
import time

from pkg_resources import DistributionNotFound, get_distribution
from superflore.exceptions import UnknownPlatform
from superflore.rosdep_support import get_cached_index, resolve_rosdep_key
from termcolor import colored


def warn(string):  # pragma: no cover
    print(colored('>>>> {0}'.format(string), 'yellow'))


def ok(string):  # pragma: no cover
    print(colored('>>>> {0}'.format(string), 'green'))


def err(string):  # pragma: no cover
    print(colored('!!!! {0}'.format(string), 'red'))


def info(string):  # pragma: no cover
    print(colored('>>>> {0}'.format(string), 'cyan'))


def get_pr_text(comment=None, markup='```'):
    msg = ''
    if comment:
        msg += '%s\n' % comment
    msg += 'This pull request was generated by running the following command:'
    msg += '\n\n'
    args = sys.argv
    args[0] = args[0].split('/')[-1]
    msg += '{1}\n{0}\n{1}\n'.format(' '.join(args), markup)
    return msg


def save_pr(overlay, delta, missing_deps, comment,
            title='rosdistro sync, {0}\n'.format(time.ctime())):
    with open('.pr-title.tmp', 'w') as title_file:
        title_file.write(title)
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
                '.pr-message.tmp',
                '.pr-title.tmp'
            )
        )
        raise
    return msg, title


def file_pr(overlay, delta, missing_deps, comment, distro=None, title=''):
    try:
        msg = get_pr_text(comment)
        overlay.pull_request('{}\n{}\n{}'.format(msg, delta, missing_deps),
                             distro, title=title)
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
        if e.errno != errno.EEXIST or not os.path.isdir(dirname):
            raise e


def get_pkg_version(distro, pkg_name, **kwargs):
    pkg = distro.release_packages[pkg_name]
    repo = distro.repositories[pkg.repository_name].release_repository
    maj_min_patch, deb_inc = repo.version.split('-')
    if deb_inc == '0':
        return maj_min_patch
    is_oe = kwargs.get('is_oe', False)
    return '{0}-{1}{2}'.format(maj_min_patch, '' if is_oe else 'r', deb_inc)


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


def get_license(lic):
    """
    Temporary import the license modification from catkin_pkg validation.

    Once all active ROS packages are updated to have more reasonble license
    values, this whole function can be dropped and the value should be the
    same as what package.xml says.
    """
    def is_valid_spdx_identifier(lic):
        """
        Checks if the license is already one of valid SPDX Identifiers from
        https://spdx.org/licenses/

        The list was created with:
        cat doc/spdx-3.10-2020-08-03.csv | cut -f 2 | grep -v ^Identifier$ \
            | sed 's/^/"/g; s/$/",/g' | xargs --delimiter='\n'
        """

        return lic in ["0BSD",
                       "AAL",
                       "Abstyles",
                       "Adobe-2006",
                       "Adobe-Glyph",
                       "ADSL",
                       "AFL-1.1",
                       "AFL-1.2",
                       "AFL-2.0",
                       "AFL-2.1",
                       "AFL-3.0",
                       "Afmparse",
                       "AGPL-1.0-only",
                       "AGPL-1.0-or-later",
                       "AGPL-3.0-only",
                       "AGPL-3.0-or-later",
                       "Aladdin",
                       "AMDPLPA",
                       "AML",
                       "AMPAS",
                       "ANTLR-PD",
                       "Apache-1.0",
                       "Apache-1.1",
                       "Apache-2.0",
                       "APAFML",
                       "APL-1.0",
                       "APSL-1.0",
                       "APSL-1.1",
                       "APSL-1.2",
                       "APSL-2.0",
                       "Artistic-1.0",
                       "Artistic-1.0-cl8",
                       "Artistic-1.0-Perl",
                       "Artistic-2.0",
                       "Bahyph",
                       "Barr",
                       "Beerware",
                       "BitTorrent-1.0",
                       "BitTorrent-1.1",
                       "blessing",
                       "BlueOak-1.0.0",
                       "Borceux",
                       "BSD-1-Clause",
                       "BSD-2-Clause",
                       "BSD-2-Clause-Patent",
                       "BSD-2-Clause-Views",
                       "BSD-3-Clause",
                       "BSD-3-Clause-Attribution",
                       "BSD-3-Clause-Clear",
                       "BSD-3-Clause-LBNL",
                       "BSD-3-Clause-No-Nuclear-License",
                       "BSD-3-Clause-No-Nuclear-License-2014",
                       "BSD-3-Clause-No-Nuclear-Warranty",
                       "BSD-3-Clause-Open-MPI",
                       "BSD-4-Clause",
                       "BSD-4-Clause-UC",
                       "BSD-Protection",
                       "BSD-Source-Code",
                       "BSL-1.0",
                       "bzip2-1.0.5",
                       "bzip2-1.0.6",
                       "CAL-1.0",
                       "CAL-1.0-Combined-Work-Exception",
                       "Caldera",
                       "CATOSL-1.1",
                       "CC-BY-1.0",
                       "CC-BY-2.0",
                       "CC-BY-2.5",
                       "CC-BY-3.0",
                       "CC-BY-3.0-AT",
                       "CC-BY-4.0",
                       "CC-BY-NC-1.0",
                       "CC-BY-NC-2.0",
                       "CC-BY-NC-2.5",
                       "CC-BY-NC-3.0",
                       "CC-BY-NC-4.0",
                       "CC-BY-NC-ND-1.0",
                       "CC-BY-NC-ND-2.0",
                       "CC-BY-NC-ND-2.5",
                       "CC-BY-NC-ND-3.0",
                       "CC-BY-NC-ND-3.0-IGO",
                       "CC-BY-NC-ND-4.0",
                       "CC-BY-NC-SA-1.0",
                       "CC-BY-NC-SA-2.0",
                       "CC-BY-NC-SA-2.5",
                       "CC-BY-NC-SA-3.0",
                       "CC-BY-NC-SA-4.0",
                       "CC-BY-ND-1.0",
                       "CC-BY-ND-2.0",
                       "CC-BY-ND-2.5",
                       "CC-BY-ND-3.0",
                       "CC-BY-ND-4.0",
                       "CC-BY-SA-1.0",
                       "CC-BY-SA-2.0",
                       "CC-BY-SA-2.5",
                       "CC-BY-SA-3.0",
                       "CC-BY-SA-3.0-AT",
                       "CC-BY-SA-4.0",
                       "CC-PDDC",
                       "CC0-1.0",
                       "CDDL-1.0",
                       "CDDL-1.1",
                       "CDLA-Permissive-1.0",
                       "CDLA-Sharing-1.0",
                       "CECILL-1.0",
                       "CECILL-1.1",
                       "CECILL-2.0",
                       "CECILL-2.1",
                       "CECILL-B",
                       "CECILL-C",
                       "CERN-OHL-1.1",
                       "CERN-OHL-1.2",
                       "CERN-OHL-P-2.0",
                       "CERN-OHL-S-2.0",
                       "CERN-OHL-W-2.0",
                       "ClArtistic",
                       "CNRI-Jython",
                       "CNRI-Python",
                       "CNRI-Python-GPL-Compatible",
                       "Condor-1.1",
                       "copyleft-next-0.3.0",
                       "copyleft-next-0.3.1",
                       "CPAL-1.0",
                       "CPL-1.0",
                       "CPOL-1.02",
                       "Crossword",
                       "CrystalStacker",
                       "CUA-OPL-1.0",
                       "Cube",
                       "curl",
                       "D-FSL-1.0",
                       "diffmark",
                       "DOC",
                       "Dotseqn",
                       "DSDP",
                       "dvipdfm",
                       "ECL-1.0",
                       "ECL-2.0",
                       "EFL-1.0",
                       "EFL-2.0",
                       "eGenix",
                       "Entessa",
                       "EPICS",
                       "EPL-1.0",
                       "EPL-2.0",
                       "ErlPL-1.1",
                       "etalab-2.0",
                       "EUDatagrid",
                       "EUPL-1.0",
                       "EUPL-1.1",
                       "EUPL-1.2",
                       "Eurosym",
                       "Fair",
                       "Frameworx-1.0",
                       "FreeImage",
                       "FSFAP",
                       "FSFUL",
                       "FSFULLR",
                       "FTL",
                       "GFDL-1.1-invariants-only",
                       "GFDL-1.1-invariants-or-later",
                       "GFDL-1.1-no-invariants-only",
                       "GFDL-1.1-no-invariants-or-later",
                       "GFDL-1.1-only",
                       "GFDL-1.1-or-later",
                       "GFDL-1.2-invariants-only",
                       "GFDL-1.2-invariants-or-later",
                       "GFDL-1.2-no-invariants-only",
                       "GFDL-1.2-no-invariants-or-later",
                       "GFDL-1.2-only",
                       "GFDL-1.2-or-later",
                       "GFDL-1.3-invariants-only",
                       "GFDL-1.3-invariants-or-later",
                       "GFDL-1.3-no-invariants-only",
                       "GFDL-1.3-no-invariants-or-later",
                       "GFDL-1.3-only",
                       "GFDL-1.3-or-later",
                       "Giftware",
                       "GL2PS",
                       "Glide",
                       "Glulxe",
                       "GLWTPL",
                       "gnuplot",
                       "GPL-1.0-only",
                       "GPL-1.0-or-later",
                       "GPL-2.0-only",
                       "GPL-2.0-or-later",
                       "GPL-3.0-only",
                       "GPL-3.0-or-later",
                       "gSOAP-1.3b",
                       "HaskellReport",
                       "Hippocratic-2.1",
                       "HPND",
                       "HPND-sell-variant",
                       "IBM-pibs",
                       "ICU",
                       "IJG",
                       "ImageMagick",
                       "iMatix",
                       "Imlib2",
                       "Info-ZIP",
                       "Intel",
                       "Intel-ACPI",
                       "Interbase-1.0",
                       "IPA",
                       "IPL-1.0",
                       "ISC",
                       "JasPer-2.0",
                       "JPNIC",
                       "JSON",
                       "LAL-1.2",
                       "LAL-1.3",
                       "Latex2e",
                       "Leptonica",
                       "LGPL-2.0-only",
                       "LGPL-2.0-or-later",
                       "LGPL-2.1-only",
                       "LGPL-2.1-or-later",
                       "LGPL-3.0-only",
                       "LGPL-3.0-or-later",
                       "LGPLLR",
                       "Libpng",
                       "libpng-2.0",
                       "libselinux-1.0",
                       "libtiff",
                       "LiLiQ-P-1.1",
                       "LiLiQ-R-1.1",
                       "LiLiQ-Rplus-1.1",
                       "Linux-OpenIB",
                       "LPL-1.0",
                       "LPL-1.02",
                       "LPPL-1.0",
                       "LPPL-1.1",
                       "LPPL-1.2",
                       "LPPL-1.3a",
                       "LPPL-1.3c",
                       "MakeIndex",
                       "MirOS",
                       "MIT",
                       "MIT-0",
                       "MIT-advertising",
                       "MIT-CMU",
                       "MIT-enna",
                       "MIT-feh",
                       "MITNFA",
                       "Motosoto",
                       "mpich2",
                       "MPL-1.0",
                       "MPL-1.1",
                       "MPL-2.0",
                       "MPL-2.0-no-copyleft-exception",
                       "MS-PL",
                       "MS-RL",
                       "MTLL",
                       "MulanPSL-1.0",
                       "MulanPSL-2.0",
                       "Multics",
                       "Mup",
                       "NASA-1.3",
                       "Naumen",
                       "NBPL-1.0",
                       "NCGL-UK-2.0",
                       "NCSA",
                       "Net-SNMP",
                       "NetCDF",
                       "Newsletr",
                       "NGPL",
                       "NIST-PD",
                       "NIST-PD-fallback",
                       "NLOD-1.0",
                       "NLPL",
                       "Nokia",
                       "NOSL",
                       "Noweb",
                       "NPL-1.0",
                       "NPL-1.1",
                       "NPOSL-3.0",
                       "NRL",
                       "NTP",
                       "NTP-0",
                       "O-UDA-1.0",
                       "OCCT-PL",
                       "OCLC-2.0",
                       "ODbL-1.0",
                       "ODC-By-1.0",
                       "OFL-1.0",
                       "OFL-1.0-no-RFN",
                       "OFL-1.0-RFN",
                       "OFL-1.1",
                       "OFL-1.1-no-RFN",
                       "OFL-1.1-RFN",
                       "OGC-1.0",
                       "OGL-Canada-2.0",
                       "OGL-UK-1.0",
                       "OGL-UK-2.0",
                       "OGL-UK-3.0",
                       "OGTSL",
                       "OLDAP-1.1",
                       "OLDAP-1.2",
                       "OLDAP-1.3",
                       "OLDAP-1.4",
                       "OLDAP-2.0",
                       "OLDAP-2.0.1",
                       "OLDAP-2.1",
                       "OLDAP-2.2",
                       "OLDAP-2.2.1",
                       "OLDAP-2.2.2",
                       "OLDAP-2.3",
                       "OLDAP-2.4",
                       "OLDAP-2.5",
                       "OLDAP-2.6",
                       "OLDAP-2.7",
                       "OLDAP-2.8",
                       "OML",
                       "OpenSSL",
                       "OPL-1.0",
                       "OSET-PL-2.1",
                       "OSL-1.0",
                       "OSL-1.1",
                       "OSL-2.0",
                       "OSL-2.1",
                       "OSL-3.0",
                       "Parity-6.0.0",
                       "Parity-7.0.0",
                       "PDDL-1.0",
                       "PHP-3.0",
                       "PHP-3.01",
                       "Plexus",
                       "PolyForm-Noncommercial-1.0.0",
                       "PolyForm-Small-Business-1.0.0",
                       "PostgreSQL",
                       "PSF-2.0",
                       "psfrag",
                       "psutils",
                       "Python-2.0",
                       "Qhull",
                       "QPL-1.0",
                       "Rdisc",
                       "RHeCos-1.1",
                       "RPL-1.1",
                       "RPL-1.5",
                       "RPSL-1.0",
                       "RSA-MD",
                       "RSCPL",
                       "Ruby",
                       "SAX-PD",
                       "Saxpath",
                       "SCEA",
                       "Sendmail",
                       "Sendmail-8.23",
                       "SGI-B-1.0",
                       "SGI-B-1.1",
                       "SGI-B-2.0",
                       "SHL-0.5",
                       "SHL-0.51",
                       "SimPL-2.0",
                       "SISSL",
                       "SISSL-1.2",
                       "Sleepycat",
                       "SMLNJ",
                       "SMPPL",
                       "SNIA",
                       "Spencer-86",
                       "Spencer-94",
                       "Spencer-99",
                       "SPL-1.0",
                       "SSH-OpenSSH",
                       "SSH-short",
                       "SSPL-1.0",
                       "SugarCRM-1.1.3",
                       "SWL",
                       "TAPR-OHL-1.0",
                       "TCL",
                       "TCP-wrappers",
                       "TMate",
                       "TORQUE-1.1",
                       "TOSL",
                       "TU-Berlin-1.0",
                       "TU-Berlin-2.0",
                       "UCL-1.0",
                       "Unicode-DFS-2015",
                       "Unicode-DFS-2016",
                       "Unicode-TOU",
                       "Unlicense",
                       "UPL-1.0",
                       "Vim",
                       "VOSTROM",
                       "VSL-1.0",
                       "W3C",
                       "W3C-19980720",
                       "W3C-20150513",
                       "Watcom-1.0",
                       "Wsuipa",
                       "WTFPL",
                       "X11",
                       "Xerox",
                       "XFree86-1.1",
                       "xinetd",
                       "Xnet",
                       "xpp",
                       "XSkat",
                       "YPL-1.0",
                       "YPL-1.1",
                       "Zed",
                       "Zend-2.0",
                       "Zimbra-1.3",
                       "Zimbra-1.4",
                       "Zlib",
                       "zlib-acknowledgement",
                       "ZPL-1.1",
                       "ZPL-2.0",
                       "ZPL-2.1"]

    def map_license_to_spdx(lic):
        """
        Map some commonly used license values to one of valid SPDX Identifiers
        from https://spdx.org/licenses/

        This is mapping only whatever value is listed in package.xml without
        any knowledge about the actual license used in the source files - it
        can map only the clear unambiguous cases (while triggering an warning)
        The rest needs to be fixed in package.xml, so it will trigger an error

        This is similar to what e.g. Openembedded is doing in:
        http://git.openembedded.org/openembedded-core/tree/meta/conf/licenses.conf
        """
        return {
            'Apache License Version 2.0': 'Apache-2.0',
            'Apachi 2': 'Apache-2.0',
            'Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)': 'Apache-2.0',  # noqa: E501
            'Apache v2': 'Apache-2.0',
            'Apache v2.0': 'Apache-2.0',
            'Apache2.0': 'Apache-2.0',
            'APACHE2.0': 'Apache-2.0',
            'Apache2': 'Apache-2.0',
            'Apache License, Version 2.0': 'Apache-2.0',
            'Apache 2': 'Apache-2.0',
            'Apache 2.0': 'Apache-2.0',
            'Apache License 2.0': 'Apache-2.0',
            'LGPL v2': 'LGPL-2.0-only',
            'LGPL v2.1 or later': 'LGPL-2.1-or-later',
            'LGPL v2.1': 'LGPL-2.1-only',
            'LGPL-2.1': 'LGPL-2.1-only',
            'LGPLv2.1': 'LGPL-2.1-only',
            'GNU Lesser Public License 2.1': 'LGPL-2.1-only',
            'LGPL3': 'LGPL-3.0-only',
            'LGPLv3': 'LGPL-3.0-only',
            'GPL-2.0': 'GPL-2.0-only',
            'GPLv2': 'GPL-2.0-only',
            'GNU General Public License v2.0': 'GPL-2.0-only',
            'GNU GPL v3.0': 'GPL-3.0-only',
            'GPL v3': 'GPL-3.0-only',
            'GPLv3': 'GPL-3.0-only',
            'ECL2.0': 'EPL-2.0',
            'Eclipse Public License 2.0': 'EPL-2.0',
            'Mozilla Public License Version 1.1': 'MPL-1.1',
            'Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International Public License': 'CC-BY-NC-ND-4.0',  # noqa: E501
            'CreativeCommons-Attribution-NonCommercial-NoDerivatives-4.0': 'CC-BY-NC-ND-4.0',  # noqa: E501
            'CreativeCommons-Attribution-NonCommercial-ShareAlike-4.0-International': 'CC-BY-NC-SA-4.0',  # noqa: E501
            'CC BY-NC-SA 4.0': 'CC-BY-NC-SA-4.0',
            'CreativeCommons-by-nc-4.0': 'CC-BY-NC-4.0',
            'CreativeCommons-by-nc-sa-2.0': 'CC-BY-NC-SA-2.0',
            'Creative Commons BY-NC-ND 3.0': 'CC-BY-NC-ND-3.0',
            'BSD 3-clause Clear License': 'BSD-2-Clause',
            'BSD 3-clause. See license attached': 'BSD-2-Clause',
            'BSD 2-Clause License': 'BSD-2-Clause',
            'BSD2': 'BSD-2-Clause',
            'BSD-3': 'BSD-3-Clause',
            'BSD 3-Clause': 'BSD-3-Clause',
            'Boost Software License 1.0': 'BSL-1.0',
            'Boost': 'BSL-1.0',
            'Boost Software License, Version 1.0': 'BSL-1.0',
            'Boost Software License': 'BSL-1.0',
            'BSL1.0': 'BSL-1.0',
            'MIT License': 'MIT',
            'zlib License': 'Zlib',
            'zlib': 'Zlib'
        }.get(lic, None)

    def map_license_to_more_common_format(lic):
        """
        These aren't SPDX Identifiers, but lets unify them to use at least
        similar format.
        """
        return {
            "Check author's website": 'Check-authors-website',
            'proprietary': 'Proprietary',
            'Public Domain': 'PD',
            'Public domain': 'PD',
            'TODO': 'TODO-CATKIN-PACKAGE-LICENSE'
        }.get(lic, None)

    def map_license_to_ampersand_separated_list(lic):
        """
        Check if the license tag contains multiple license values.

        Show warning about using multiple license tags when the
        value is one of the listed.
        """
        return {
            'LGPLv2.1, modified BSD': 'LGPL-2.1-only & modified BSD',
            'Lesser GPL and Apache License': 'Lesser GPL & Apache License',
            'BSD,GPL because of list.h; other files released under BSD,GPL': 'BSD & GPL because of list.h & other files released under BSD & GPL',  # noqa: E501
            'GPL because of list.h; other files released under BSD': 'GPL because of list.h & other files released under BSD',  # noqa: E501
            'BSD, some icons are licensed under the GNU Lesser General Public License (LGPL) or Creative Commons Attribution-Noncommercial 3.0 License': 'BSD & some icons are licensed under LGPL or CC-BY-NC-3.0',  # noqa: E501
            'BSD,LGPL,LGPL (amcl)': 'BSD & LGPL & LGPL (amcl)',
            'BSD, GPL': 'BSD & GPL',
            'BSD, Apache 2.0': 'BSD & Apache-2.0',
            'BSD, LGPL': 'BSD & LGPL',
            'BSD,LGPL,Apache 2.0': 'BSD & LGPL & Apache-2.0'
         }.get(lic, None)

    def translate_license(lic):
        conversion_table = {ord(' '): '-', ord('/'): '-', ord(':'): '-',
                            ord('+'): '-', ord('('): '-', ord(')'): '-'}
        multi_hyphen_re = re.compile('-{2,}')
        return multi_hyphen_re.sub('-', lic.translate(conversion_table))

    if is_valid_spdx_identifier(lic):
        return lic
    common = map_license_to_more_common_format(lic)
    if common:
        lic = common
    multiple = map_license_to_ampersand_separated_list(lic)
    if multiple:
        lic = multiple
    spdx = map_license_to_spdx(lic)
    if spdx:
        lic = spdx
    return translate_license(lic)


def resolve_dep(pkg, os, distro=None):
    if os == 'openembedded':
        return resolve_rosdep_key(pkg, 'openembedded', '', distro)
    elif os == 'gentoo':
        return resolve_rosdep_key(pkg, 'gentoo', '2.4.0')
    else:
        msg = "Unknown target platform '{0}'".format(os)
        raise UnknownPlatform(msg)


def get_distros():
    index = get_cached_index()
    return index.distributions


def get_distros_by_status(status='active'):
    return [t[0] for t in get_distros().items()
            if t[1].get('distribution_status') == status]


def get_ros_version(distro_name):
    distros = get_distros()
    return 2 if distro_name not in distros \
        else int(distros[distro_name]['distribution_type'][len('ros'):])


def get_ros_python_version(distro_name):
    return 2 if distro_name in ['melodic'] else 3


def gen_delta_msg(total_changes, markup='*'):
    """Return string of changes for the PR message."""
    delta = ''
    is_single_distro = len(total_changes) == 1
    distro_header = '='
    if not is_single_distro:
        delta += "Changes:\n"
        delta += "========\n"
        distro_header = '-'
    for distro in sorted(total_changes):
        if not total_changes[distro]:
            continue
        heading = "{} Changes:\n".format(distro.title())
        delta += heading
        delta += distro_header * (len(heading) - 1)
        delta += "\n"
        for d in sorted(total_changes[distro]):
            delta += '* {1}{0}{1}\n'.format(d, markup)
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


def retry_on_exception(callback, *args, max_retries=5, num_retry=0,
                       retry_msg='', error_msg='', sleep_secs=0.125):
    try:
        return callback(*args)
    except Exception as e:
        if num_retry >= max_retries or max_retries < 0 or num_retry < 0:
            if error_msg:
                err('{0} {1} {2}/{3}'.format(str(e), error_msg,
                    num_retry, max_retries))
            raise e from None
        if num_retry > 0:
            if retry_msg:
                warn('{0} {1} {2}/{3}...'.format(str(e), retry_msg,
                     num_retry, max_retries))
            time.sleep(sleep_secs)
            if num_retry <= 6:
                sleep_secs *= 2
            else:
                sleep_secs = 0.125
        elif num_retry == 0:
            warn('{0}'.format(str(e)))
        return retry_on_exception(callback, *args, max_retries=max_retries,
                                  num_retry=num_retry+1, retry_msg=retry_msg,
                                  error_msg=error_msg, sleep_secs=sleep_secs)


def get_superflore_version():
    try:
        version = get_distribution("superflore").version
    except DistributionNotFound:
        version = 'Unknown'
    return version


def get_utcnow_timestamp_str():
    return datetime.utcnow().strftime('%Y%m%d%H%M%S')
