# This generates Gentoo Linux ebuilds for ROS packages.
import sys
import yaml
try:
    from urllib2 import open as get_http
except:
    from urllib.request import urlopen

    def get_http(url):
        response = urlopen(url)
        return response.read()

base_url = "https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/base.yaml"
python_url = "https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/python.yaml"

print("Downloading latest base yml...")
base_yml = yaml.load(get_http(base_url))
print("Downloading latest python yml...")
python_yml = yaml.load(get_http(python_url))

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
        self.upstream_license = "LGPL-v2"
        self.keys = list()
        self.rdepends = list()
        self.rdepends_external = list()
        self.depends = list()
        self.depends_external = list()
        self.distro = None
        self.cmake_package = True
        self.base_yml = None


    def add_build_depend(self, depend, internal=True):
        if internal:
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

    def get_ebuild_text(self, distributor, license_text):
        """
        Generate the ebuild in text, given the distributor line
        and the license text.
    
        @todo: make the year dynamic
        @todo: raise an exception if the distributor/license is invalid
        """

        ret  = "# Copyright 2017 " + distributor + "\n"
        ret += "# Distributed under the terms of the " + license_text + " license\n\n"

        # EAPI=<eapi>
        ret += "EAPI=" + self.eapi + "\n\n"
        # inherits
        # description, homepage, src_uri
        if isinstance(self.description, str):
            ret += "DESCRIPTION=\"" + self.description + "\"\n"
        elif sys.version_info <= (3, 0) and isinstance(self.description, unicode):
            ret += "DESCRIPTION=\"" + self.description + "\"\n"
        else:
            ret += "DESCRIPTION=\"\"\n"

        ret += "HOMEPAGE=\"" + self.homepage + "\"\n"
        ret += "SRC_URI=\"" + self.src_uri + "\"\n\n"
        # license
        if isinstance(self.upstream_license, str):
            ret += "LICENSE=\"" + self.upstream_license + "\"\n\n"
        elif sys.version_info <= (3, 0) and isinstance(self.upstream_license, unicode):
            ret += "LICENSE=\"" + self.upstream_license + "\"\n\n"
        else:
            ret += "LICENSE=\"UNKNOWN\"\n"
        # iterate through the keywords, adding to the KEYWORDS line.
        ret += "KEYWORDS=\""

        first = True
        for i in self.keys:
            if not first:
                ret += " "
            ret += "~" + i
            first = False

        ret += "\"\n\n"

        # RDEPEND
        ret += "RDEPEND=\"\n"

        for rdep in self.rdepends:
            ret += "    " + "ros-" + self.distro + "/" + rdep + "\n"
        for rdep in self.rdepends_external:
            ret += "    " + self.resolve(rdep) + "\n"
        ret += "\"\n"

        # DEPEND
        ret += "DEPEND=\"\n"
        for bdep in self.depends:
            ret += "    " + "ros-" + self.distro + "/" + bdep + "\n"
        for bdep in self.depends_external:
            ret += "    " + self.resolve(bdep) + "\n"
        ret += "\"\n\n"

        # SLOT
        ret += "SLOT=\"0/0\"\n"
        # CMAKE_BUILD_TYPE
        ret += "CMAKE_BUILD_TYPE=RelWithDebInfo\n\n"

        ret += "src_unpack() {\n"
        ret += "    wget -O ${P}.tar.gz ${SRC_URI}\n"
        ret += "    tar -xf ${P}.tar.gz\n"
        ret += "    rm -f ${P}.tar.gz\n"
        ret += "    mv *${P}* ${P}\n"
        ret += "}\n\n"
        
        # source configuration
        ret += "src_configure() {\n"
        ret += "    mkdir ${WORKDIR}/src\n"
        ret += "    cp -R ${WORKDIR}/${P} ${WORKDIR}/src/${P}\n"
        ret += "}\n\n"

        ret += "src_compile() {\n"
        ret += "    echo \"\"\n"
        ret += "}\n\n"

        ret += "src_install() {\n"
        ret += "    echo \"\"\n"
        ret += "}\n\n"

        ret += "pkg_postinst() {\n"
        ret += "    cd ../work\n"
        ret += "    source /opt/ros/" + self.distro + "/setup.bash\n"
        ret += "    catkin_make_isolated --install --install-space=\"/opt/ros/" + self.distro + "\" || die\n"
        ret += "}\n"        

        """
        @todo: is there really not a way to do it not in pkg_postinst?
        """        
        return ret

    @staticmethod
    def resolve(pkg):
        if pkg == 'libopenni-dev':
            return "dev-libs/OpenNI"
        elif pkg == "linux-headers-generic":
            return "sys-kernel/linux-headers"
        elif pkg == "liburdfdom-tools":
            return "dev-libs/urdfdom"
        elif pkg == "python-lxml":
            return "dev-python/lxml"
        elif pkg == "python-yaml":
            return "dev-python/pyyaml"
        elif pkg == "python-pyassimp":
            return "dev-libs/assimp"
        elif pkg == "libfcl-dev":
            return "sci-libs/fcl"
        elif pkg == "tinyxml2":
            return "dev-libs/tinyxml2"
        elif pkg == "python-future":
            return "dev-python/future"
        elif pkg == "python":
            return "dev-lang/python\ndev-lang/python-exec"
        elif pkg == "libqglviewer-qt4":
            return "x11-libs/libQGLViewer"
        elif pkg == "libqglviewer-qt4-dev":
            return "x11-libs/libQGLViewer"
        elif pkg == "python-setuptools":
            return "dev-python/setuptools"
        elif pkg == "ffmpeg":
            return "virtual/ffmpeg"
        elif pkg == "libv4l-dev":
            return "media-libs/libv4l"
        elif pkg == "libwebp-dev":
            return "media-libs/libwebp"
        elif pkg == "muparser":
            return "dev-cpp/muParser"
        elif pkg == "python-pyproj":
            return "dev-python/pyproj"
        elif pkg == "libxi-dev":
            return "x11-libs/libXi"
        elif pkg == "libxmu-dev":
            return "x11-libs/libXmu"
        elif pkg == "util-linux":
            return "sys-apps/util-linux"
        elif pkg == "uuid":
            return "sys-apps/util-linux"
        elif pkg == "python-argparse":
            return "dev-lang/python\ndev-lang/python-exec"
        elif pkg == "python-qt5-bindings-webkit":
            return "dev-python/PyQt5"
        elif pkg not in base_yml:
            if pkg not in python_yml:
                raise UnresolvedDependency("unknown dependency {}".format(pkg))
            elif 'gentoo'not in python_yml[pkg]:
                raise UnresolvedDependency("could not resolve package {} for Gentoo.".format(pkg))
            elif 'portage' in python_yml[pkg]['gentoo']:
                resolution = python_yml[pkg]['gentoo']['portage']['packages'][0]
                print("resolved: {} --> {}".format(pkg, resolution))
                return resolution
            else:
                resolution = python_yml[pkg]['gentoo'][0]
                print("resolved: {} --> {}".format(pkg, resolution))
                return resolution
        elif 'gentoo'not in base_yml[pkg]:
            raise UnresolvedDependency("could not resolve package {} for Gentoo.".format(pkg))
        elif 'portage' in base_yml[pkg]['gentoo']:
            resolution = base_yml[pkg]['gentoo']['portage']['packages'][0]
            print("resolved: {} --> {}".format(pkg, resolution))
            return resolution
        else:
            resolution = base_yml[pkg]['gentoo'][0]
            print("resolved: {} --> {}".format(pkg, resolution))
            return resolution 

class UnresolvedDependency(Exception):
    def __init__(self, message):
        self.message = message
