
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
            ret += "~" + keywords[i] + (i == len(self.keywords) - 1 ? " " : "")

        ret += "\"\n\n"

        """
        @todo: rdepend
        @todo: depend
        @todo: CMAKE_BUILD_TYPE
        """
        return ret
