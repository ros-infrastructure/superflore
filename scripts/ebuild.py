# This generates Gentoo Linux ebuilds for ROS packages.

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
        elif isinstance(self.description, unicode):
            ret += "DESCRIPTION=\"" + self.description + "\"\n"
        else:
            ret += "DESCRIPTION=\"\"\n"

        ret += "HOMEPAGE=\"" + self.homepage + "\"\n"
        ret += "SRC_URI=\"" + self.src_uri + "\"\n\n"
        # license
        if isinstance(self.upstream_license, str):
            ret += "LICENSE=\"" + self.upstream_license + "\"\n\n"
        elif isinstance(self.upstream_license, unicode):
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
            ret += "    " + rdep + "\n"
        ret += "\"\n"

        # DEPEND
        ret += "DEPEND=\"\n"
        for bdep in self.depends:
            ret += "    " + "ros-" + self.distro + "/" + bdep + "\n"
        for bdep in self.depends_external:
            ret += "    " + bdep + "\n"
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
