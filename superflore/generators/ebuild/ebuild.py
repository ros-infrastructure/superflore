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

from time import gmtime, strftime

from superflore.exceptions import UnresolvedDependency
from superflore.utils import get_license
from superflore.utils import resolve_dep
from superflore.utils import sanitize_string
from superflore.utils import trim_string

# TODO(allenh1): is there a better way to get these?
depend_only_pkgs = [
    'dev-util/gperf',
    'app-doc/doxygen',
    'virtual/pkgconfig'
]


class ebuild_keyword(object):
    def __init__(self, arch, stable):
        self.arch = arch
        self.stable = stable

    def to_string(self):
        if self.stable:
            return self.arch
        else:
            return '~{0}'.format(self.arch)

    def __eq__(self, other):
        return self.to_string() == other.to_string()


class Ebuild(object):
    """
    Basic definition of an ebuild.
    This is where any necessary variables will be filled.
    """
    def __init__(self):
        self.eapi = str(6)
        self.description = ""
        self.homepage = "https://wiki.ros.org"
        self.src_uri = None
        self.upstream_license = "LGPL-2"
        self.keys = list()
        self.rdepends = list()
        self.rdepends_external = list()
        self.depends = list()
        self.depends_external = list()
        self.tdepends = list()
        self.tdepends_external = list()
        self.distro = None
        self.cmake_package = True
        self.base_yml = None
        self.unresolved_deps = list()
        self.name = None
        self.has_patches = False
        self.python_3 = True
        self.illegal_desc_chars = '()[]{}|^$\\#\t\n\r\v\f\'\"\`'

    def add_build_depend(self, depend, internal=True):
        if depend in self.rdepends:
            return
        elif depend in self.rdepends_external:
            return
        elif internal:
            self.depends.append(depend)
        else:
            self.depends_external.append(depend)

    def add_run_depend(self, rdepend, internal=True):
        if rdepend in depend_only_pkgs and not internal:
            self.depends_external.append(rdepend)
        elif internal:
            self.rdepends.append(rdepend)
        else:
            self.rdepends_external.append(rdepend)

    def add_test_depend(self, tdepend, internal=True):
        if not internal:
            self.tdepends_external.append(tdepend)
        else:
            self.tdepends.append(tdepend)

    def add_keyword(self, keyword, stable=False):
        self.keys.append(ebuild_keyword(keyword, stable))

    def get_ebuild_text(self, distributor, license_text):
        """
        Generate the ebuild in text, given the distributor line
        and the license text.
        """
        ret = "# Copyright " + strftime("%Y", gmtime()) + " "
        ret += distributor + "\n"
        ret += "# Distributed under the terms of the " + license_text
        ret += " license\n\n"

        # EAPI=<eapi>
        ret += "EAPI=" + self.eapi + "\n"
        if self.python_3:
            ret += "PYTHON_COMPAT=( python{2_7,3_5} )\n\n"
        else:
            ret += "PYTHON_COMPAT=( python2_7 )\n\n"
        # inherits
        ret += "inherit ros-cmake\n\n"

        # description, homepage, src_uri
        self.description =\
            sanitize_string(self.description, self.illegal_desc_chars)
        self.description = trim_string(self.description)
        ret += "DESCRIPTION=\"" + self.description + "\"\n"
        ret += "HOMEPAGE=\"" + self.homepage + "\"\n"
        self.src_uri = self.src_uri.replace(self.name, '${PN}')
        ret += "SRC_URI=\"" + self.src_uri
        ret += " -> ${PN}-" + self.distro + "-release-${PV}.tar.gz\"\n\n"
        # license -- only add if valid
        if isinstance(self.upstream_license, str):
            split = self.upstream_license.split(',')
            if len(split) > 1:
                # they did something like "BSD,GPL,blah"
                ret += 'LICENSE="( '
                ret += ' '.join([get_license(l.strip()) for l in split])
                ret += ' )"\n'
            else:
                ret += "LICENSE=\""
                ret += get_license(self.upstream_license) + "\"\n\n"
        elif isinstance(self.upstream_license, list):
            ret += "LICENSE=\"( "
            ret += ' '.join(
                [get_license(ul) for ul in self.upstream_license]
            )
            ret += " )\"\n"
        # iterate through the keywords, adding to the KEYWORDS line.
        ret += "KEYWORDS=\""
        ret += ' '.join([key.to_string() for key in self.keys])
        ret += "\"\n"
        if len(self.tdepends) or len(self.tdepends_external):
            ret += 'IUSE="test"\n'
        # RDEPEND
        ret += "RDEPEND=\"\n"
        for rdep in sorted(self.rdepends):
            ret += "    " + "ros-" + self.distro + "/" + rdep + "\n"
        # internal test dependencies
        for tdep in sorted(self.tdepends):
            ret += "    " + "test? ( ros-" + self.distro + "/" + tdep + " )\n"
        for rdep in sorted(self.rdepends_external):
            try:
                for res in resolve_dep(rdep, 'gentoo')[0]:
                    if res in depend_only_pkgs:
                        self.depends_external.append(rdep)
                        break
                    else:
                        ret += "    " + res + "\n"
            except UnresolvedDependency:
                self.unresolved_deps.append(rdep)
        # external test dependencies
        for tdep in sorted(self.tdepends_external):
            try:
                for res in resolve_dep(tdep, 'gentoo')[0]:
                    ret += "    test? ( " + res + " )\n"
            except UnresolvedDependency:
                self.unresolved_deps.append(tdep)
        ret += "\"\n"
        # DEPEND
        ret += "DEPEND=\"${RDEPEND}\n"
        for bdep in sorted(self.depends):
            ret += "    " + 'ros-{0}/{1}\n'.format(self.distro, bdep)
        for bdep in sorted(self.depends_external):
            try:
                for res in resolve_dep(bdep, 'gentoo')[0]:
                    ret += "    " + res + "\n"
            except UnresolvedDependency:
                self.unresolved_deps.append(bdep)
        ret += "\"\n\n"

        # SLOT
        ret += "SLOT=\"0\"\n"
        # CMAKE_BUILD_TYPE
        if self.name == "catkin":
            ret += "BUILD_BINARY=\"0\"\n"
        ret += "ROS_DISTRO=\"{0}\"\n".format(self.distro)
        ret += "ROS_PREFIX=\"opt/ros/${ROS_DISTRO}\"\n"

        # Patch source if needed.
        if self.has_patches:
            ret += "\nsrc_prepare() {\n"
            ret += "    cd ${P}\n"
            ret += "    EPATCH_SOURCE=\"${FILESDIR}\""
            ret += " EPATCH_SUFFIX=\"patch\" \\\n"
            ret += "    EPATCH_FORCE=\"yes\" epatch\n"
            ret += "    ros-cmake_src_prepare\n"
            ret += "}\n"

        # source configuration
        if self.name == 'opencv3':
            ret += "\nsrc_configure() {\n"
            ret += "    filter-flags '-march=*' '-mcpu=*' '-mtune=*'\n"
            ret += "    if [[ $(gcc-major-version) -gt 4 ]]; then\n"
            ret += "        local mycmakeargs=(\n"
            ret += "            -DWITH_CUDA=OFF\n"
            ret += "        )\n"
            ret += '        ewarn "Cuda does not support GCC > 4, so cuda'
            ret += ' has been disabled."\n'
            ret += "    fi\n"
            ret += "    ros-cmake_src_configure\n"
            ret += "}\n"
        elif self.name == 'stage':
            ret += "\nsrc_configure() {\n"
            ret += "    filter-flags '-std=*'\n"
            ret += "    ros-cmake_src_configure\n"
            ret += "}\n"

        if len(self.unresolved_deps) > 0:
            raise UnresolvedDependency("failed to satisfy dependencies!")

        return ret.replace('    ', '\t')

    def get_unresolved(self):
        return self.unresolved_deps
