#!/usr/bin/env python

import sys
from setuptools import find_packages, setup

install_requires = [
    'xmltodict',
    'termcolor',
    'setuptools',    
    'rosinstall_generator',    
    'rosdistro',
    'gitpython',
    'git-pull-request',
]

if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    install_requires.append('argparse')

if sys.version_info[0] == 3:
    install_requires.append('urllib')
else:
    install_requires.append('requests')

setup(
    name='ebuild_generator',
    version='0.0.0',
    packages=find_packages(exclude=['tests']),
    author='Hunter L. Allen',
    author_email='hunter@openrobotics.org',
    url='https://github.com/allenh1/ebuild-generator',
    keywords=['ROS'],
    install_requires=install_requires,
    classifiers=['Programming Language :: Python',
                 'License :: Apache 2.0'],
    description='ROS release automation tool for Gentoo',
    license='Apache 2.0',
    test_suite='tests',
    entry_points={
        'console_scripts' : [
            'gen-ros-ebuilds = ebuild_generator.generators.ebuild:main'
        ],
        'ebuild_generator.common' : [
            'repo_instance = ebuild_generator.repo_instance',
            'gen_packages = ebuild_generator.gen_packages'
        ],
        'ebuild_generator.generators' : [
            'portage = ebuild_generator.generators.ebuild'
        ]
    }
)
