# This generates Gentoo Linux ebuilds for ROS packages.
from termcolor import colored
import yaml
import sys
import re

try:
    import requests

    def get_http(url):
        return requests.get(url).text
except:
    from urllib.request import urlopen

    def get_http(url):
        response = urlopen(url)
        return response.read()

base_url = "https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/base.yaml"
python_url = "https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/python.yaml"
ruby_url = "https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/ruby.yaml"

print(colored("Downloading latest base yml...", 'cyan'))
base_yml = yaml.load(get_http(base_url))
print(colored("Downloading latest python yml...", 'cyan'))
python_yml = yaml.load(get_http(python_url))
print(colored("Downloading latest ruby yml...", 'cyan'))
ruby_yml = yaml.load(get_http(ruby_url))

def get_license(l):
    bsd_re = '^(BSD)((.)*([1234]))?'
    gpl_re = '^(GPL)((.)*([123]))?'
    lgpl_re = '^(LGPL)((.)*([23]|2\\.1))?'
    apache_re = '^(Apache)((.)*(1\\.0|1\\.1|2\\.0|2))?'
    none_re = '^(Public Domain)'
    cc_re = '^(Creative Commons)|'
    moz_re = '^(Mozilla)((.)*(1\\.1))?'
    mit_re = '^MIT'
    f = re.IGNORECASE

    if re.search(apache_re, l, f) is not None:
        version = re.search(apache_re, l, f).group(4)
        if version is not None:
            return 'Apache-{0}'.format(version)
        return 'Apache-1.0'
    elif re.search(bsd_re, l, f) is not None:
        version = re.search(bsd_re, l, f).group(4)
        if version is not None:
            return 'BSD-{0}'.format(version)
        return 'BSD'
    elif re.search(gpl_re, l, f) is not None:
        version = re.search(gpl_re, l, f).group(4)
        if version is not None:
            return 'GPL-{0}'.format(version)
        return 'GPL-1'
    elif re.search(lgpl_re, l, f) is not None:
        version = re.search(lgpl_re, l, f).group(4)
        if version is not None:
            return 'LGPL-{0}'.format(version)
        return 'LGPL-2'
    elif re.search(moz_re, l, f) is not None:
        version = re.search(moz_re, l, f).group(4)
        if version is not None:
            return 'MPL-{0}'.format(version)
        return 'MPL-2.0'
    elif re.search(mit_re, l, f) is not None:
        return 'MIT'
    elif re.search(cc_re, l, f) is not None:
        return 'CC-BY-SA-3.0'
    elif re.search(none_re, l, f) is not None:
        return ''
    else:
        print(colored('Could not find a match for license "{0}".'.format(l), 'red'))
        return l

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
        self.distro = None
        self.cmake_package = True
        self.base_yml = None
        self.unresolved_deps = list()
        self.name = None
        self.has_patches = False
        self.die_msg = None

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
        if internal:
            self.rdepends.append(rdepend)
        else:
            self.rdepends_external.append(rdepend)

    def add_keyword(self, keyword):
        self.keys.append(keyword)

    def get_ebuild_text(self, distributor, license_text, die_msg=None):
        """
        Generate the ebuild in text, given the distributor line
        and the license text.
    
        @todo: make the year dynamic
        """
        ret  = "# Copyright 2017 " + distributor + "\n"
        ret += "# Distributed under the terms of the " + license_text + " license\n\n"

        # EAPI=<eapi>
        ret += "EAPI=" + self.eapi + "\n\n"
        """
        @todo: don't hard code this
        """
        ret += "inherit cmake-utils eutils\n\n"

        # inherits
        # description, homepage, src_uri
        if isinstance(self.description, str):
            ret += "DESCRIPTION=\"" + self.description + "\"\n"
        elif sys.version_info <= (3, 0) and isinstance(self.description, unicode):
            ret += "DESCRIPTION=\"" + self.description + "\"\n"
        else:
            ret += "DESCRIPTION=\"\"\n"

        ret += "HOMEPAGE=\"" + self.homepage + "\"\n"
        ret += "SRC_URI=\"" + self.src_uri + " -> ${P}-${PV}.tar.gz\"\n\n"
        # license
        if isinstance(self.upstream_license, str):
            split = self.upstream_license.split(',')
            if len(split) > 1:
                # they did something like "BSD,GPL,blah"
                ret += 'LICENSE="|| ( '
                for l in split:
                    l = get_license(l.replace(' ', ''))
                    ret += '{0} '.format(l)
                ret += ')"\n'
            else:
                ret += "LICENSE=\"" + get_license(self.upstream_license) + "\"\n\n"
        elif sys.version_info <= (3, 0) and isinstance(self.upstream_license, unicode):
            self.upstream_license = self.upstream_license.decode()
            split = self.upstream_license.split(',')
            if len(split) > 1:
                # they did something like "BSD,GPL,blah"
                ret += 'LICENSE="|| ( '
                for l in split:
                    l = get_license(l.replace(' ', ''))
                    ret += '{0} '.format(l)
                ret += ')"\n'            
            else:
                ret += "LICENSE=\"" + get_license(self.upstream_license) + "\"\n\n"            
        elif isinstance(self.upstream_license, list):
            ret += "LICENSE=\"|| ( "
            for l in self.upstream_license:
                l = get_license(l)
                ret += '{0} '.format(l)
            ret += ")\"\n"
                
        # iterate through the keywords, adding to the KEYWORDS line.
        ret += "KEYWORDS=\""

        first = True
        for i in self.keys:
            if not first:
                ret += " "
            ret += i
            first = False

        ret += "\"\n"
        """
        @todo: uh... probably shouldn't force PYTHON 3.5
        """
        ret += "PYTHON_DEPEND=\"3::3.5\"\n\n"
        # RDEPEND
        ret += "RDEPEND=\"\n"
        for rdep in sorted(self.rdepends):
            ret += "    " + "ros-" + self.distro + "/" + rdep + "\n"
        for rdep in sorted(self.rdepends_external):
            try:
                ret += "    " + self.resolve(rdep) + "\n"
            except UnresolvedDependency as msg:
                self.unresolved_deps.append(rdep)
                
        ret += "\"\n"

        # DEPEND
        ret += "DEPEND=\"${RDEPEND}\n"
        for bdep in sorted(self.depends):
            ret += "    " + 'ros-{0}/{1}\n'.format(self.distro, bdep)
        for bdep in sorted(self.depends_external):
            try:
                ret += "    " + self.resolve(bdep) + "\n"
            except UnresolvedDependency as bad_dep:
                self.unresolved_deps.append(bdep)
        ret += "\"\n\n"

        # SLOT
        ret += "SLOT=\"0\"\n"
        # CMAKE_BUILD_TYPE
        ret += "CMAKE_BUILD_TYPE=RelWithDebInfo\n"
        ret += "ROS_PREFIX=\"opt/ros/{}\"\n\n".format(self.distro)

        ret += "src_unpack() {\n"
        ret += "    default\n"
        ret += "    mv *${P}* ${P}\n"
        # Patch source if needed.
        if self.has_patches:
            ret += "    cd ${P}\n"
            ret += "    EPATCH_SOURCE=\"${FILESDIR}\" EPATCH_SUFFIX=\"patch\" \\\n"
            ret += "                 EPATCH_FORCE=\"yes\" epatch\n"
        ret += "}\n\n"

        # If we're writing the ebuild for catkin, don't build in binary mode.
        binary_package = '0' if self.name == 'catkin' else '1'

        # source configuration
        ret += "src_configure() {\n"
        if self.name != 'stage':
            ret += "    append-cxxflags \"-std=c++11\"\n"
        ret += "    export DEST_SETUP_DIR=\"/${ROS_PREFIX}\"\n"
        ret += "    local mycmakeargs=(\n"
        ret += "        -DCMAKE_INSTALL_PREFIX=${D}${ROS_PREFIX}\n"
        ret += "        -DCMAKE_PREFIX_PATH=/${ROS_PREFIX}\n"
        ret += "        -DPYTHON_INSTALL_DIR=lib64/python3.5/site-packages\n"
        ret += "        -DCATKIN_ENABLE_TESTING=OFF\n"
        if self.name != 'catkin':
            ret += "        -DPYTHON_EXECUTABLE=/usr/bin/ros-python-{0}\n".format(self.distro)
        ret += "        -DCATKIN_BUILD_BINARY_PACKAGE={0}\n".format(binary_package)
        if self.name == 'opencv3':
            ret += "        -DCMAKE_CXX_FLAGS=\"-O2 -pipe\"\n"
            ret += "        -DCMAKE_C_FLAGS=\"-O2 -pipe\"\n"
        ret += "     )\n"
        ret += "    cmake-utils_src_configure\n"
        ret += "}\n\n"

        if self.name == 'catkin':
            ret += "src_compile() {\n"
            ret += "    gcc ${FILESDIR}/ros-python.c -o ${WORKDIR}/${P}/ros-python-"
            ret += "{0} || die 'could not compile ros-python!'\n".format(self.distro)
            ret += "    cmake-utils_src_compile\n"
            ret += "}\n\n"

        if self.die_msg is not None:
            self.die_msg = ' {0}'.format(die_msg)
        else:
            self.die_msg = ''

        ret += "src_install() {\n"
        if self.name == 'catkin':
            ret += "    cd ${WORKDIR}/${P}\n"
            ret += "    mkdir -p ${D}/usr/bin\n"
            ret += "    cp ros-python-{0} ".format(self.distro) + "${D}/usr/bin || die 'could not install ros-python!'\n"
        ret += "    cd ${WORKDIR}/${P}_build\n"
        ret += "    make install || die{0}\n".format(self.die_msg)
        ret += "}\n"

        if len(self.unresolved_deps) > 0:
            raise UnresolvedDependency("failed to satisfy dependencies!")

        return ret

    def get_unresolved(self):
        return self.unresolved_deps

    @staticmethod
    def resolve(pkg):
        if pkg not in base_yml:
            if pkg not in python_yml:
                if pkg not in ruby_yml:
                    raise UnresolvedDependency("could not resolve package {} for Gentoo.".format(pkg))
                elif 'gentoo'not in ruby_yml[pkg]:
                    raise UnresolvedDependency("could not resolve package {} for Gentoo.".format(pkg))
                elif 'portage' in ruby_yml[pkg]['gentoo']:                
                    resolution = ruby_yml[pkg]['gentoo']['portage']['packages'][0]
                    return resolution
                else:
                    resolution = ruby_yml[pkg]['gentoo'][0]
                    return resolution
            elif 'gentoo'not in python_yml[pkg]:
                raise UnresolvedDependency("could not resolve package {} for Gentoo.".format(pkg))
            elif 'portage' in python_yml[pkg]['gentoo']:                
                resolution = python_yml[pkg]['gentoo']['portage']['packages'][0]
                return resolution
            else:
                resolution = python_yml[pkg]['gentoo'][0]
                return resolution
        elif 'gentoo'not in base_yml[pkg]:
            raise UnresolvedDependency("could not resolve package {} for Gentoo.".format(pkg))
        elif 'portage' in base_yml[pkg]['gentoo']:
            resolution = base_yml[pkg]['gentoo']['portage']['packages'][0]
            return resolution
        else:
            resolution = base_yml[pkg]['gentoo'][0]
            return resolution 

class UnresolvedDependency(Exception):
    def __init__(self, message):
        self.message = message

class UnknownLicense(Exception):
    def __init__(self, message):
        self.message = message
