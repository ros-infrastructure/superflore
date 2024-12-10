from textwrap import dedent
from time import gmtime, strftime
from typing import Iterable

from superflore.generators.nix.nix_package import NixPackage


class NixPackageSet:
    """
    Code generator for Nix overlay package set. Each package in the set must
    be defined as a function in a default.nix file within a directory named
    after the package. The package functions are called with callPackage.
    """

    def __init__(self, pkg_names: Iterable[str]):
        self.pkg_names = pkg_names

    def get_text(self, distributor: str, license_name: str) -> str:
        ret = []
        ret += dedent('''
        # Copyright {} {}
        # Distributed under the terms of the {} license

        self: super: {{

        ''').format(strftime("%Y", gmtime()), distributor, license_name)
        ret.extend((" {0} = self.callPackage ./{0} {{}};\n\n"
                   .format(NixPackage.normalize_name(pkg_name))
                    for pkg_name in self.pkg_names))
        ret += "}\n"
        return ''.join(ret)
