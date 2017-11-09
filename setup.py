#!/usr/bin/env python

import sys
from setuptools import find_packages, setup

install_requires = [
    'xmltodict',
    'termcolor',
    'setuptools',
    'rosinstall_generator',
    'rosdistro',
    'rosdep',
    'gitpython',
    'git-pull-request',
    'requests',
    'docker'
]

if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    install_requires.append('argparse')

setup(
    name='superflore',
    version='0.1.0',
    packages=find_packages(exclude=['tests']),
    author='Hunter L. Allen',
    author_email='hunter@openrobotics.org',
    url='https://github.com/ros-infrastructure/superflore',
    keywords=['ROS'],
    install_requires=install_requires,
    classifiers=['Programming Language :: Python',
                 'License :: OSI Approved :: Apache Software License'],
    description='Super Bloom',
    license='Apache 2.0',
    test_suite='tests',
    data_files=[('repoman_docker', ['repoman_docker/Dockerfile'])],
    include_package_data = True,
    entry_points={
        'console_scripts' : [
            'superflore-gen-ebuilds = superflore.generators.ebuild:main',
            'superflore-gen-meta-pkgs = superflore.generators.bitbake:main'
        ],
        'common' : [
            'repo_instance = superflore.repo_instance',
            'gen_packages = superflore.gen_packages'
        ],
        'generators' : [
            'portage = superflore.generators.ebuild',
            'yocto = superflore.generators.bitbake'
        ]
    }
)
