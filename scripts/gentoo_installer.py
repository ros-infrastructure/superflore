# generate a gentoo package instance

from .gen_packages import _gen_metadata_for_package, _gen_ebuild_for_package

org = "Open Source Robotics Foundation"
org_license = "LGPL-v2"

class gentoo_installer:
    def __init__(object, distro_name, pkg_name):
        self.metadata_xml = _gen_metadata_for_package(distro_name, pkg_name)
        self.ebuild       = _gen_ebuild_for_package(distro_name, pkg_name)

        self.metadata_txt = self.metadata_xml.get_metadata_text()
        self.ebuild_txt   = self.ebuild.get_ebuild_text(org, org_license)
