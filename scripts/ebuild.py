
class Ebuild(object):
    """
    Basic definition of an ebuild.
    This is where any necessary variables will be filled.
    """
    def __init__(self):
        self.eapi = 6
        self.description = None
        self.homepage = None
        self.src_uri = None
        self.upstream_license = None
        self.keywords = None
        self.rdepends = None
        self.depends = None
        self.cmake_package = True

    def add_build_depend(self, depend):
        self.depends.append(depend)
        
    def add_run_rdepend(self, rdepend):
        self.rdepends.append(rdepend)

    def add_keyword(self, keyword):
        self.keywords.append(keyword)

    def get_ebuild_text(self, distributor, license_text):
        """
        Generate the ebuild in text, given the distributor line
        and the license text.
    
        @todo: make the year dynamic
        @todo: raise an exception if the distributor/license is invalid
        """

        ret  = "# Copyright 2017 " + distributor + "\n"
        ret += "# Distributed under the terms of the " + license_text + "\n\n"

        # EAPI=<eapi>
        ret += "EAPI=" + self.eapi + "\n\n"
        # inherits
        ret += "inherit cmake-utils\n\n"
        # description, homepage, src_uri
        ret += "DESCRIPTION=\"" + self.description + "\"\n"
        ret += "HOMEPAGE=\"" + self.homepage + "\"\n"
        ret += "SRC_URI=\"" + self.src_uri + "\"\n\n"
        # license
        ret += "LICENSE=\"" + self.upstream_license + "\n\n"

        # iterate through the keywords, adding to the KEYWORDS line.
        ret += "KEYWORDS=\""
        x = 0

        for i in range(len(self.keywords)):
            ret += "~" + keywords[i]
            if i != len(self.keywords) - 1:
                ret += " "

        # RDEPEND
        ret += "RDEPEND=\"\n"

        for rdep in self.rdepends:
            ret += "    " + rdep + "\n"

        ret += "\n\"\n"

        # DEPEND
        ret += "DEPEND=\"${RDEPEND}\n"

        for bdep in self.depends:
            ret += "    " + bdep + "\n"

        ret += "\n\"\n\n"

        # CMAKE_BUILD_TYPE
        ret += "CMAKE_BUILD_TYPE=RelWithDebInfo\n\n"

        # source configuration
        ret += "src_configure() {\n"
        ret += "    append-cxxflags -std=c++14" # because people don't add it as it is default now
        ret += "    cmake-utils_src_configure"
        ret += "}"
        
        return ret
