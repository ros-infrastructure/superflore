# generates ebuilds from ros distribution data
import sys
import os
import xmltodict
from termcolor import colored

from rosinstall_generator.distro import get_distro, get_package_names, _generate_rosinstall
from rosdistro.dependency_walker import DependencyWalker, SourceDependencyWalker
from rosdistro.manifest_provider import get_release_tag
from rosdistro.rosdistro import RosPackage

from .ebuild import Ebuild
from .metadata_xml import metadata_xml

org = "Open Source Robotics Foundation"
org_license = "LGPL-v2"

def warn(string):
    print(colored(string, 'yellow'))

def ok(string):
    print(colored(string, 'green'))

def err(string):
    print(colored(string, 'red'))
    
def make_dir(dirname):
    try:
        os.makedirs(dirname)
    except:
        pass

def get_pkg_version(distro, pkg_name):
    pkg = distro.release_packages[pkg_name]
    repo = distro.repositories[pkg.repository_name].release_repository
    return repo.version.split('-')[0]
    
def generate_installers(distro_name):
    make_dir("ros-{}".format(distro_name))
    distro = get_distro(distro_name)
    pkg_names = get_package_names(distro)
    installers = []
    bad_installers = []
    succeeded = 0
    failed = 0

    for pkg in pkg_names[0]:
        try:
            current = gentoo_installer(distro, pkg)
            
            # make the directory
            make_dir("ros-{}/{}".format(distro_name, pkg))
            ebuild_text = current.ebuild_text()
            metadata_text = current.metadata_text()

            ok(">>>> Succesfully generated installer for package \"{}.\"".format(pkg))
            succeeded = succeeded + 1

            try:
                ebuild_file = open("ros-{}/{}/{}-{}.ebuild".format(distro_name, pkg, pkg, get_pkg_version(distro, pkg)), "w")
                metadata_file = open("ros-{}/{}/metadata.xml".format(distro_name, pkg), "w")
        
                ebuild_file.write(ebuild_text)
                metadata_file.write(metadata_text)
            except:
                err(">>>> Failed to write ebuild/metadata to disk!")
            installers.append(current)
        except:
            warn("!!!! Failed to generate gentoo installer for package {}!".format(pkg))
            bad_installers.append(current)
            failed = failed + 1

    print("------------------   Generated {} / {} installers for distro \"{}\"".format(succeeded, failed + succeeded, distro_name))
    return installers
    
def _gen_metadata_for_package(distro, pkg_name):
    pkg = distro.release_packages[pkg_name]
    repo = distro.repositories[pkg.repository_name].release_repository
    ros_pkg = RosPackage(pkg_name, repo)

    pkg_rosinstall = _generate_rosinstall(pkg_name, repo.url, get_release_tag(repo, pkg_name), True)
    pkg_xml = ros_pkg.get_package_xml(distro.name)
    pkg_fields = xmltodict.parse(pkg_xml)

    pkg_metadata_xml = metadata_xml()

    """
    @todo: upstream_maintainer
    @todo: upstream_name
    @todo: upstream_email
    @todo: upstream_bug_url
    @todo: longdescription
    """
    return pkg_metadata_xml

def _gen_ebuild_for_package(distro, pkg_name):
    pkg = distro.release_packages[pkg_name]
    repo = distro.repositories[pkg.repository_name].release_repository
    ros_pkg = RosPackage(pkg_name, repo)

    pkg_rosinstall = _generate_rosinstall(pkg_name, repo.url, get_release_tag(repo, pkg_name), True)
    pkg_ebuild = Ebuild()

    pkg_ebuild.distro = distro.name
    pkg_ebuild.src_uri = pkg_rosinstall[0]['tar']['uri']
    pkg_dep_walker = DependencyWalker(distro)

    pkg_build_deps = pkg_dep_walker.get_depends(pkg_name, "build")
    pkg_run_deps   = pkg_dep_walker.get_depends(pkg_name, "run")

    pkg_keywords = [ 'x86', 'amd64', 'arm', 'arm64' ]

    # add run dependencies
    for rdep in pkg_run_deps:
        pkg_ebuild.add_run_depend(rdep)

    # add build dependencies
    for bdep in pkg_build_deps:
        pkg_ebuild.add_build_depend(bdep)

    # add keywords
    for key in pkg_keywords:
        pkg_ebuild.add_keyword(key)

    # parse throught package xml
    pkg_xml = ros_pkg.get_package_xml(distro.name)
    pkg_fields = xmltodict.parse(pkg_xml)
    
    pkg_ebuild.upstream_license = pkg_fields['package']['license']

    try:
        pkg_ebuild.description = pkg_fields['package']['description']
    except:
        warn(">>>> failed to get description field for package {}".format(pkg_name))
    """
    @todo: homepage
    """
    return pkg_ebuild

class gentoo_installer(object):
    def __init__(self, distro, pkg_name):
        self.metadata_xml = _gen_metadata_for_package(distro, pkg_name)
        self.ebuild       = _gen_ebuild_for_package(distro, pkg_name)

    def metadata_text(self):
        return self.metadata_xml.get_metadata_text()

    def ebuild_text(self):
        return self.ebuild.get_ebuild_text(org, org_license)
