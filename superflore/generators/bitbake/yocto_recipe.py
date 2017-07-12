# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Open Source Robotics Foundation, Inc.
# Copyright (c) 2016 David Bensoussan, Synapticon GmbH
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


import xmltodict
import hashlib
import tarfile
import glob
import yaml
import sys
import re

from superflore.utils import get_license
from termcolor import colored


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


base_url = \
  "https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/base.yaml"
python_url = \
  "https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/python.yaml"
ruby_url = \
  "https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/ruby.yaml"

print(colored("Downloading latest base yml...", 'cyan'))
base_yml = yaml.load(get_http(base_url))
print(colored("Downloading latest python yml...", 'cyan'))
python_yml = yaml.load(get_http(python_url))
print(colored("Downloading latest ruby yml...", 'cyan'))
ruby_yml = yaml.load(get_http(ruby_url))


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

    def getLicenseMD5(self, license):
        if license == "BSD":
            return "d566ef916e9dedc494f5f793a6690ba5"
        elif license == "Mozilla Public License Version 1.1":
            return "e1b5a50d4dd59d8102e41a7a2254462d"
        elif license == "CC-BY-NC-SA-2.0":
            return "11e24f757f025b2cbebd5b14b4a7ca19"
        elif license == "LGPL-2.1":
            return "184dd1523b9a109aead3fbbe0b4262e0"
        elif license == "GPL":
            return "162b49cfbae9eadf37c9b89b2d2ac6be"
        elif license == "LGPL-2.1+":
            return "58d727014cda5ed405b7fb52666a1f97"
        elif license == "LGPLv2":
            return "46ee8693f40a89a31023e97ae17ecf19"
        elif license == "MIT":
            return "58e54c03ca7f821dd3967e2a2cd1596e"

    def getSrcMD5(self):
        return hashlib.md5(
            open("./" + self.getArchiveName(), 'rb').read()).hexdigest()

    def getSrcSha256(self):
        return hashlib.sha256(
            open("./" + self.getArchiveName(), 'rb').read()).hexdigest()

    def getURL(self):
        return "https://github.com/" + \
               self.repository + "/" + \
               self.name.replace("-", "_") + \
               "/archive/" + str(self.version) + \
               ".tar.gz"

    def getFolderName(self):
        return self.name.replace("-", "_") + "-" + str(self.version)

    def getArchiveName(self):
        return self.name.replace("-", "_") + \
               "-" + str(self.version) + \
               ".tar.gz"

    def get_license_line(self):
        f = self.pkg_xml
        self.license_line = ''
        self.license_md5 = ''
        i = 0
        for line in self.pkg_xml.split('\n'):
            i += 1
            if 'license' in line:
                self.license_line = str(i)
                md5 = hashlib.md5()
                md5.update(line)
                self.license_md5 = md5.hexdigest()
                break

    def downloadArchive(self):
        urllib.urlretrieve(self.src_uri, self.getArchiveName())

    def extractArchive(self):
        tar = tarfile.open(self.getArchiveName(), "r:gz")
        tar.extractall()
        tar.close()

    def add_depend(self, depend):
        if depend not in self.depends:
            self.depends.append(depend)

    def get_recipe_text(self, distributor, license_text, die_msg=None):
        """
        Generate the Yocto Recipe, given the distributor line
        and the license text.
        """
        ret = '# Copyright 2017 ' + distributor + '\n'
        ret += '# Distributed under the terms of the ' + license_text
        ret += ' license\n\n'

        py_ver = sys.version_info
        # description
        if self.description is not None:
            ret += 'DESCRIPTION = "' + self.description + '"\n'
        else:
            ret += 'DESCRIPTION = "None"\n'
        # author
        ret += 'AUTHOR = "' + self.author + '"\n'
        # section
        ret += 'SECTION = "devel"\n'
        if isinstance(self.license, str):
            ret += 'LICENSE = "' + self.license + '"\n'
        elif isinstance(self.license, list):
            ret += 'LICENSE = "'
            first = True
            for lic in self.license:
                if not first:
                    ret += ' '
                    first = False
                ret += lic
            ret += '"\n'
        ret += 'LIC_FILES_CHKSUM = "file://package.xml;beginline='
        self.get_license_line()
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
            ret += dep
            first = False
        ret += '"\n'

        # SRC_URI
        ret += 'SRC_URI = "' + self.src_uri + ';'
        ret += 'downloadfilename=${ROS_SP}.tar.gz"\n\n'
        ret += 'SRC_URI[md5sum] = "' + self.getSrcMD5() + '"\n'
        ret += 'SRC_URI[sha256sum] = "' + self.getSrcSha256() + '"\n'
        ret += 'S = "${WORKDIR}/${ROS_SP}"\n\n'
        ret += 'inherit catkin\n'
        return ret


class UnresolvedDependency(Exception):
    def __init__(self, message):
        self.message = message
