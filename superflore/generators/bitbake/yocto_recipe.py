# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 David Bensoussan, Synapticon GmbH
# Copyright (c) 2017 Open Source Robotics Foundation, Inc.
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal  in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import hashlib
import tarfile
import sys

from superflore.utils import resolve_dep
from superflore.exceptions import NoPkgXml


if sys.version_info[0] == 2:
    import requests
    import urllib

    def get_http(url):
        return requests.get(url).text
else:
    from urllib.request import urlopen
    import urllib

    def get_http(url):
        response = urlopen(url)
        return response.read()


class yoctoRecipe(object):
    def __init__(self):
        self.name = None
        self.version = None
        self.description = ''
        self.src_uri = None
        self.pkg_xml = None
        self.author = "OSRF"
        self.license = None
        self.depends = list()
        self.license_line = None
        self.license_md5 = None
        self.src_md5 = None
        self.src_sha256 = None

    def getSrcMD5(self):
        return hashlib.md5(
            open("./" + self.getArchiveName(), 'rb').read()).hexdigest()

    def getSrcSha256(self):
        return hashlib.sha256(
            open("./" + self.getArchiveName(), 'rb').read()).hexdigest()

    def getFolderName(self):
        return self.name.replace("-", "_") + "-" + str(self.version)

    def getArchiveName(self):
        return self.name.replace("-", "_") + \
               "-" + str(self.version) + \
               ".tar.gz"

    def get_license_line(self):
        self.license_line = ''
        self.license_md5 = ''
        i = 0
        if not self.pkg_xml:
            raise NoPkgXml('No package xml file!')
        for line in str(self.pkg_xml, 'utf-8').split('\n'):
            i += 1
            if 'license' in line:
                self.license_line = str(i)
                md5 = hashlib.md5()
                md5.update((line + '\n').encode())
                self.license_md5 = md5.hexdigest()
                break

    def downloadArchive(self):
        urllib.request.urlretrieve(self.src_uri, self.getArchiveName())

    def extractArchive(self):
        tar = tarfile.open(self.getArchiveName(), "r:gz")
        tar.extractall()
        tar.close()

    def add_depend(self, depend):
        if depend not in self.depends:
            self.depends.append(depend)

    def get_src_location(self):
        """
        Parse out the folder name.
        TODO(allenh1): add a case for non-GitHub packages,
        after they are supported.
        """
        github_start = 'https://github.com/'
        structure = self.src_uri.replace(github_start, '')
        dirs = structure.split('/')
        return '{0}-{1}-{2}-{3}-{4}'.format(dirs[1], dirs[3],
                                            dirs[4], dirs[5],
                                            dirs[6]).replace('.tar.gz', '')

    def get_recipe_text(self, distributor, license_text, die_msg=None):
        """
        Generate the Yocto Recipe, given the distributor line
        and the license text.
        """
        ret = '# Copyright 2017 ' + distributor + '\n'
        ret += '# Distributed under the terms of the ' + license_text
        ret += ' license\n\n'

        # description
        if self.description:
            self.description = self.description.replace('\n', ' ')
            ret += 'DESCRIPTION = "' + self.description + '"\n'
        else:
            ret += 'DESCRIPTION = "None"\n'
        # author
        ret += 'AUTHOR = "' + self.author + '"\n'
        # section
        ret += 'SECTION = "devel"\n'
        self.get_license_line()
        if isinstance(self.license, str):
            self.license = self.license.split(',')[0]
            self.license = self.license.replace(' ', '-')
            ret += 'LICENSE = "' + self.license + '"\n'
        elif isinstance(self.license, list):
            self.license = self.license[0].replace(' ', '-')
            ret += 'LICENSE = "' + self.license + '"\n'
            """
            TODO(allenh1): add this functionality
            first = True
            for lic in self.license:
                if not first:
                    ret += ' '
                    first = False
                ret += lic
            ret += '"\n'
            """
        ret += 'LIC_FILES_CHKSUM = "file://package.xml;beginline='
        ret += str(self.license_line)
        ret += ';endline='
        ret += str(self.license_line)
        ret += ';md5='
        ret += str(self.license_md5)
        ret += '"\n\n'

        # DEPEND
        first = True
        ret += 'DEPENDS = "'
        for dep in sorted(self.depends):
            if not first:
                ret += ' '
            ret += resolve_dep(dep, 'oe')
            first = False
        ret += '"\n'

        # SRC_URI
        ret += 'SRC_URI = "' + self.src_uri + ';'
        ret += 'downloadfilename=${ROS_SP}.tar.gz"\n\n'
        ret += 'SRC_URI[md5sum] = "' + self.getSrcMD5() + '"\n'
        ret += 'SRC_URI[sha256sum] = "' + self.getSrcSha256() + '"\n'
        ret += 'S = "${WORKDIR}/'
        ret += self.get_src_location() + '"\n\n'
        ret += 'inherit catkin\n'
        return ret
