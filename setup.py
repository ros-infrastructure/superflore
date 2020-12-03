#!/usr/bin/env python

import sys
from setuptools import find_packages, setup

"""
Returns <public_version> appended with a PEP-440 compliant local version label
(see https://www.python.org/dev/peps/pep-0440/#local-version-identifiers). The
local version label is based on the output from
"git describe --tags --dirty --broken". Nothing is appended if:
- Git is not available, or
- "git describe" might not be operating on a branch of superflore.git, or
- there is no tag for <public_version>, or
- the HEAD of the current branch is coincident with the tag for <public_version>.

NB. Not using https://pypi.org/project/setuptools-git-version/ because it passes
"--long" to "git describe" and doesn't pass "--broken".
"""
def append_local_version_label(public_version):
    try:
        from git import Repo
        from os import getcwd
        from os.path import join, samefile

        repo = Repo()
        """
        If we're been copied under the working dir of some other Git repo,
        "git describe" won't return what we're expecting, so don't append
        anything. The test for this case will also fail if, say, we try to
        invoke ../setup.py from a subdirectory, but it's better to err on the
        side of "least surprises".
        """
        if not samefile(repo.git_dir, join(getcwd(), '.git')):
            return public_version

        # The tags have a "v" prefix.
        val = repo.git.describe(
            '--match', 'v' + public_version, '--tags', '--dirty', '--broken')
        """
        Output from "git describe --tags --dirty --broken" is
            <TAG>[-<NR-OF-COMMITS>-g<ABBRE-HASH>][-dirty][-broken]
        Convert to a legal Python local version label, dropping the "v" prefix
        of the tag.
        """
        return val.replace('-', '+', 1).replace('-', '.')[1:]
    except:
        return public_version

if sys.version_info < (3, 0):
    sys.exit('Sorry, Python < 3.0 is not supported')

install_requires = [
    'xmltodict',
    'termcolor',
    'setuptools',
    'rosinstall_generator',
    'rosdistro >= 0.7.4',
    'rosdep >= 0.15.2',
    'gitpython',
    'requests',
    'docker',
    'pyyaml',
    'pygithub',
    'catkin_pkg >= 0.4.10',
    'rospkg >= 1.1.8',
]

setup(
    name='superflore',
    version=append_local_version_label('0.3.2'),
    packages=find_packages(exclude=['tests', 'tests.*']),
    author='Hunter L. Allen',
    author_email='hunterlallen@protonmail.com',
    url='https://github.com/ros-infrastructure/superflore',
    keywords=['ROS'],
    install_requires=install_requires,
    python_requires='>=3',
    classifiers=['Programming Language :: Python',
                 'License :: OSI Approved :: Apache Software License',
                 'License :: OSI Approved :: MIT License'
    ],
    description='Super Bloom',
    license='Apache 2.0',
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'superflore-gen-ebuilds = superflore.generators.ebuild:main',
            'superflore-gen-oe-recipes = superflore.generators.bitbake:main',
            'superflore-check-ebuilds = superflore.test_integration.gentoo:main',
        ]
    }
)
