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
    'requests'
]

if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    install_requires.append('argparse')

setup(
    name='superflore',
    version='0.0.0',
    packages=find_packages(exclude=['tests']),
    author='Hunter L. Allen',
    author_email='hunter@openrobotics.org',
    url='https://github.com/allenh1/superflore',
    keywords=['ROS'],
    install_requires=install_requires,
    classifiers=['Programming Language :: Python',
                 'License :: Apache 2.0'],
    description='Super Bloom',
    license='Apache 2.0',
    test_suite='tests',
    entry_points={
        'console_scripts' : [
            'superflore-gen-ebuilds = superflore.generators.ebuild:main'
        ],
        'common' : [
            'repo_instance = superflore.repo_instance',
            'gen_packages = superflore.gen_packages'
        ],
        'generators' : [
            'portage = superflore.generators.ebuild'
        ]
    }
)
