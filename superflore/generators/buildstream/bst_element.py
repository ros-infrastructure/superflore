# Copyright (c) 2016 David Bensoussan, Synapticon GmbH
# Copyright (c) 2017 Open Source Robotics Foundation, Inc.
# Copyright (c) 2024 Codethink
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

import os
import textwrap
import yaml

from superflore.exceptions import NoPkgXml
from superflore.exceptions import UnresolvedDependency
from superflore.PackageMetadata import PackageMetadata
from superflore.utils import err
from superflore.utils import get_pkg_version
from superflore.utils import info


class BstElement(object):
    def __init__(
        self, component_name, pkg_name, pkg_xml, rosdistro, src_uri,
        srcrev_cache, skip_keys, repo_dir, external_repos
    ):
        self.repo_dir = repo_dir
        self.external_repos = external_repos
        self.component = component_name
        self.name = pkg_name
        self.distro = rosdistro.name
        self.version = get_pkg_version(rosdistro, pkg_name, is_oe=True)
        self.src_uri = src_uri
        self.pkg_xml = pkg_xml
        self.author = None
        if self.pkg_xml:
            pkg_fields = PackageMetadata(pkg_xml)
            maintainer_name = pkg_fields.upstream_name
            maintainer_email = pkg_fields.upstream_email
            author_name = pkg_fields.author_name
            author_email = pkg_fields.author_email
            self.maintainer = maintainer_name + ' <' + maintainer_email + '>'
            if author_name or author_email:
                self.author = author_name + \
                    (' <' + author_email + '>' if author_email else '')
            self.license = pkg_fields.upstream_license
            self.description = pkg_fields.description
            self.homepage = pkg_fields.homepage
            pkg_build_type = pkg_fields.build_type
            self.build_type = pkg_build_type
        else:
            self.description = ''
            self.license = None
            self.homepage = None
            self.build_type = 'ament_cmake'
            self.maintainer = "OSRF"
        self.depends = set()
        self.depends_external = set()
        self.buildtool_depends = set()
        self.buildtool_depends_external = set()
        self.export_depends = set()
        self.export_depends_external = set()
        self.buildtool_export_depends = set()
        self.buildtool_export_depends_external = set()
        self.rdepends = set()
        self.rdepends_external = set()
        self.license_line = None
        if self.src_uri not in srcrev_cache:
            srcrev_cache[self.src_uri] = self.get_srcrev()
        self.srcrev = srcrev_cache[self.src_uri]
        self.skip_keys = skip_keys

    def get_license_line(self):
        self.license_line = ''
        i = 0
        if not self.pkg_xml:
            raise NoPkgXml('No package xml file!')
        for line in str(self.pkg_xml, 'utf-8').split('\n'):
            i += 1
            if 'license' in line:
                self.license_line = str(i)
                break

    def get_repo_src_uri(self):
        """
        Parse out the git repository SRC_URI out of github archive, e.g.
        github.com/ros2-gbp/ament_lint-release
        from
        https://github.com/ros2-gbp/ament_lint-release/archive/release/bouncy/ament_cmake_copyright/0.5.2-0.tar.gz
        """
        github_start = 'https://github.com/'
        structure = self.src_uri.replace(github_start, '')
        dirs = structure.split('/')
        return "github:%s/%s" % (dirs[0], dirs[1])

    def get_repo_branch_name(self):
        """
        Parse out the git branch name out of github archive SRC_URI, e.g.
        release/bouncy/ament_cmake_copyright
        from
        https://github.com/ros2-gbp/ament_lint-release/archive/release/bouncy/ament_cmake_copyright/0.5.2-0.tar.gz
        """
        github_start = 'https://github.com/'
        structure = self.src_uri.replace(github_start, '')
        dirs = structure.split('/')
        return '{0}/{1}/{2}'.format(
            dirs[3], dirs[4], dirs[5]).replace('.tar.gz', '')

    def get_repo_tag_name(self):
        """
        Parse out the git tag name out of github archive SRC_URI, e.g.
        release/bouncy/ament_cmake_copyright/0.5.2-0
        from
        https://github.com/ros2-gbp/ament_lint-release/archive/release/bouncy/ament_cmake_copyright/0.5.2-0.tar.gz
        """
        github_start = 'https://github.com/'
        structure = self.src_uri.replace(github_start, '')
        dirs = structure.split('/')
        return '{0}/{1}/{2}/{3}'.format(
            dirs[3], dirs[4], dirs[5], dirs[6]).replace('.tar.gz', '')

    def get_srcrev(self):
        # e.g. git ls-remote https://github.com/ros2-gbp/ament_lint-release \
        #                    release/bouncy/ament_cmake_copyright/0.5.2-0
        # 48bf1aa1cb083a884fbc8520ced00523255aeaed \
        #     refs/tags/release/bouncy/ament_cmake_copyright/0.5.2-0
        # from https://github.com/ros2-gbp/ament_lint-release/archive/ \
        #     release/bouncy/ament_cmake_copyright/0.5.2-0.tar.gz
        from git.cmd import Git

        g = Git()
        for ref in g.execute(["git",
                              "ls-remote",
                              self.get_repo_src_uri().replace("github:", "https://github.com/"),
                              "refs/tags/%s" % self.get_repo_tag_name()
                              ]).split('\n'):
            srcrev, tag = ref.split('\t')
            if tag == "refs/tags/%s" % self.get_repo_tag_name():
                return srcrev
        err("Cannot map refs/tags/%s to srcrev in https://%s repository with "
            "git ls-remote" % (self.get_repo_tag_name(),
                               self.get_repo_src_uri()))
        return "INVALID"

    def add_build_depend(self, bdepend, pkg):
        if bdepend not in self.skip_keys:
            if pkg:
                self.depends.add(pkg)
            else:
                self.depends_external.add(bdepend)

    def add_buildtool_depend(self, btdepend, pkg):
        if btdepend not in self.skip_keys:
            if pkg:
                self.buildtool_depends.add(pkg)
            else:
                self.buildtool_depends_external.add(btdepend)

    def add_export_depend(self, edepend, pkg):
        if edepend not in self.skip_keys:
            if pkg:
                self.export_depends.add(pkg)
            else:
                self.export_depends_external.add(edepend)

    def add_buildtool_export_depend(self, btedepend, pkg):
        if btedepend not in self.skip_keys:
            if pkg:
                self.buildtool_export_depends.add(pkg)
            else:
                self.buildtool_export_depends_external.add(btedepend)

    def add_run_depend(self, rdepend, pkg):
        if rdepend not in self.skip_keys:
            if pkg:
                self.rdepends.add(pkg)
            else:
                self.rdepends_external.add(rdepend)

    @staticmethod
    def convert_dep_name(dep):
        return dep.lower().replace('_', '-')

    @classmethod
    def convert_to_bst_name(cls, dep):
        return cls.convert_dep_name(dep) + ".bst"

    def get_dependencies(self, internal_depends, external_depends):
        dependencies = set()
        system_dependencies = set()
        for dep in internal_depends:
            element = self.convert_dep_name(dep.repository_name) + "/" + self.convert_to_bst_name(dep.name)
            dependencies.add("generated/" + element)
            info('Internal dependency add: ' + element)
        for dep in external_depends:
            resolved = False
            dep_bst = self.convert_to_bst_name(dep)
            for external_repo_name, external_repo_path in self.external_repos.items():
                if os.path.isfile(external_repo_path + '/' + dep_bst):
                    resolved = True
                    element = external_repo_name + dep_bst
                    dependencies.add(element)
                    system_dependencies.add(element)
                    info('External dependency add: ' + element)
                    break
            if not resolved:
                raise UnresolvedDependency("external dependency {} missing".format(dep))

        return dependencies, system_dependencies

    def get_element_text(self, distributor):
        """
        Generate the BuildStream element, given the distributor line
        and the license text.
        """
        header = "# Generated by superflore -- DO NOT EDIT\n#\n"
        header += "# Copyright " + distributor + "\n#\n"

        if self.description:
            self.description = self.description.replace('\n', ' ')
            header += textwrap.fill('Description: ' + self.description,
                                    width=80,
                                    initial_indent='# ',
                                    subsequent_indent='# ') + '\n'
        header += '# Maintainer: ' + self.maintainer + '\n'
        if self.author:
            header += '# Author: ' + self.author + '\n'
        if self.homepage:
            header += '# Homepage: ' + self.homepage + '\n'
        header += '# Source URI: ' + self.src_uri + '\n'
        if self.license:
            header += '# License: ' + " & ".join(self.license) + '\n'
        header += '\n'

        element = {}
        base = "base.bst"
        buildstack = [base]
        if self.build_type in {"ament_cmake", "cmake"}:
            element["kind"] = "cmake"
            buildstack.append("freedesktop-sdk.bst:public-stacks/buildsystem-cmake.bst")
        elif self.build_type == "ament_python":
            element["kind"] = "pyproject"
            buildstack.append("freedesktop-sdk.bst:public-stacks/buildsystem-python-setuptools.bst")

        # depends
        deps, sys_deps = self.get_dependencies(
            self.depends, self.depends_external)
        buildtool_native_deps, sys_deps = self.get_dependencies(
            self.buildtool_depends,
            self.buildtool_depends_external
        )
        native_deps = set(buildtool_native_deps)
        export_deps, sys_deps = self.get_dependencies(
            self.export_depends, self.export_depends_external)
        buildtool_export_native_deps, sys_deps = self.get_dependencies(
            self.buildtool_export_depends,
            self.buildtool_export_depends_external
        )
        native_deps |= buildtool_export_native_deps
        exec_deps, sys_deps = self.get_dependencies(
            self.rdepends, self.rdepends_external)

        element["build-depends"] = buildstack + sorted(deps | buildtool_native_deps)

        element["runtime-depends"] = [base] + sorted(deps | export_deps | buildtool_export_native_deps | exec_deps)

        variables = {}
        if self.build_type == "ament_cmake":
            variables["cmake-local"] = "-DBUILD_TESTING=OFF"
        if variables:
            element["variables"] = variables

        sources = []
        source = {}
        source["kind"] = "git_repo"
        source["url"] = self.get_repo_src_uri()
        source["track"] = self.get_repo_branch_name()
        source["ref"] = self.srcrev
        sources.append(source)
        element["sources"] = sources

        includepath = "includes/" + \
                      self.convert_dep_name(self.component) + "/" + \
                      self.convert_dep_name(self.name) + ".inc"
        fullincludepath = self.repo_dir + "/" + includepath
        if os.path.isfile(fullincludepath):
            with open(fullincludepath) as incfile:
                include = yaml.safe_load(incfile)
                for listkey in ["build-depends", "runtime-depends", "sources"]:
                    if listkey in include:
                        # Append generated list to list from include file
                        element[listkey] = {"(<)": element[listkey]}
                # BuildStream include directive
                element["(@)"] = includepath

        yamltext = yaml.dump(element, sort_keys=False)

        # Improve formatting
        for block in element.keys():
            yamltext = yamltext.replace("\n" + block + ":", "\n\n" + block + ":")

        return header + yamltext
