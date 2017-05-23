
class Ebuild(object):
    """
    Basic definition of an ebuild.
    This is where any necessary variables will be filled.
    """
    def __init__(self):
        self.eapi = str(6)
        self.description = None
        self.homepage = None
        self.src_uri = None
        self.upstream_license = None
        self.keys = list()
        self.rdepends = list()
        self.depends = list()
        self.distro = None
        self.cmake_package = True

    def add_build_depend(self, depend):
        self.depends.append(depend)
        
    def add_run_rdepend(self, rdepend):
        self.rdepends.append(rdepend)

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
        ret += "inherit cmake-utils\n\n"
        # description, homepage, src_uri
        ret += "DESCRIPTION=\"" + self.description + "\"\n"
        ret += "HOMEPAGE=\"" + self.homepage + "\"\n"
        ret += "SRC_URI=\"" + self.src_uri + "\"\n\n"
        # license
        ret += "LICENSE=\"" + self.upstream_license + "\"\n\n"

        # iterate through the keywords, adding to the KEYWORDS line.
        ret += "KEYWORDS=\""

        for i in self.keys:
            ret += "~" + i + " "

        ret += "\"\n\n"

        # RDEPEND
        ret += "RDEPEND=\"\n"

        for rdep in self.rdepends:
            ret += "    " + "ros-" + self.distro + "/" + rdep + "\n"

        ret += "\n\"\n"

        # DEPEND
        ret += "DEPEND=\"${RDEPEND}\n"

        for bdep in self.depends:
            ret += "    " + "ros-" + distro + "/" + bdep + "\n"

        ret += "\n\"\n\n"

        # CMAKE_BUILD_TYPE
        ret += "CMAKE_BUILD_TYPE=RelWithDebInfo\n\n"

        ret += "src_prepare() {\n"
        ret += "    mv *${P}* ${P}\n"
        ret += "}\n\n"
        
        # source configuration
        ret += "src_configure() {\n"
        ret += "    append-cxxflags \"-std=c++14\"\n" # because people don't add it as it is default now
        ret += "    mkdir ${WORKDIR}/src\n"
        ret += "    cp -R ${WORKDIR}/${P} ${WORKDIR}/src/${P}\n"
        ret += "}\n\n"

        ret += "src_install() {\n"
        ret += "    cd ../"
        ret += "    source /opt/ros/" + self.distro + "/setup.bash"
        ret += "    catkin_make_isolated --install --install-space=\"/opt/ros/" + self.distro + "\" || die"
        ret += "}\n\n"

        ret += "src_install() {\n"
        ret += "    echo \"\"\n"
        ret += "}\n"
        
        return ret
