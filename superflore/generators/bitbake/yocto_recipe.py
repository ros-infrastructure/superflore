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
import os.path
import tarfile
from time import gmtime, strftime
from urllib.request import urlretrieve

from superflore.exceptions import NoPkgXml
from superflore.utils import get_license
from superflore.utils import get_pkg_version
from superflore.utils import info
from superflore.utils import resolve_dep


class yoctoRecipe(object):
    def __init__(
        self, name, distro, src_uri, tar_dir, md5_cache, sha256_cache
    ):
        self.name = name
        self.distro = distro.name
        self.version = get_pkg_version(distro, name)
        self.description = ''
        self.src_uri = src_uri
        self.pkg_xml = None
        self.author = "OSRF"
        self.license = None
        self.depends = list()
        self.license_line = None
        self.archive_name = None
        self.license_md5 = None
        self.tar_dir = tar_dir
        if self.getArchiveName() not in md5_cache or \
           self.getArchiveName() not in sha256_cache:
                self.downloadArchive()
                md5_cache[self.getArchiveName()] = hashlib.md5(
                    open(self.getArchiveName(), 'rb').read()).hexdigest()
                sha256_cache[self.getArchiveName()] = hashlib.sha256(
                    open(self.getArchiveName(), 'rb').read()).hexdigest()
        self.src_sha256 = sha256_cache[self.getArchiveName()]
        self.src_md5 = md5_cache[self.getArchiveName()]

    def getFolderName(self):
        return self.name.replace("-", "_") + "-" + str(self.version)

    def getArchiveName(self):
        if not self.archive_name:
            self.archive_name = self.tar_dir + "/" \
                + self.name.replace('-', '_') + '-' + str(self.version) \
                + '-' + self.distro + '.tar.gz'
        return self.archive_name

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
        if os.path.exists(self.getArchiveName()):
            info("using cached archive for package '%s'..." % self.name)
        else:
            info("downloading archive version for package '%s'..." % self.name)
            urlretrieve(self.src_uri, self.getArchiveName())

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

    def get_recipe_text(self, distributor, license_text):
        """
        Generate the Yocto Recipe, given the distributor line
        and the license text.
        """
        ret = "# Copyright " + strftime("%Y", gmtime()) + " "
        ret += distributor + "\n"
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
        # ROS distro
        ret += 'ROSDISTRO = "%s"\n' % (self.distro)
        self.get_license_line()
        if isinstance(self.license, str):
            ret += 'LICENSE = "%s"\n' % get_license(self.license)
        elif isinstance(self.license, list):
            ret += 'LICENSE = "'
            ret += ' & '.join([get_license(l) for l in self.license]) + '"\n'
        ret += 'LIC_FILES_CHKSUM = "file://package.xml;beginline='
        ret += str(self.license_line)
        ret += ';endline='
        ret += str(self.license_line)
        ret += ';md5='
        ret += str(self.license_md5)
        ret += '"\n\n'
        # check for catkin
        if self.name == 'catkin':
            ret += 'CATKIN_NO_BIN="True"\n\n'
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
        self.src_uri = self.src_uri.replace(self.name, '${PN}')
        ret += 'SRC_URI = "' + self.src_uri + ';'
        ret += 'downloadfilename=${ROS_SP}.tar.gz"\n\n'
        ret += 'SRC_URI[md5sum] = "' + self.src_md5 + '"\n'
        ret += 'SRC_URI[sha256sum] = "' + self.src_sha256 + '"\n'
        ret += 'S = "${WORKDIR}/'
        ret += self.get_src_location() + '"\n\n'
        ret += 'inherit catkin\n'
        return ret
