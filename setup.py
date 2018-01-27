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
    'docker',
    'pyyaml'
]

setup(
    name='superflore',
    version='0.2.1',
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
    data_files=[
        ('test_docker', ['tests/docker/Dockerfile']),
    ],
    include_package_data = True,
    entry_points={
        'console_scripts' : [
            'superflore-gen-ebuilds = superflore.generators.ebuild:main',
            'superflore-gen-meta-pkgs = superflore.generators.bitbake:main',
            'superflore-check-ebuilds = superflore.test_integration.gentoo:main',
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
