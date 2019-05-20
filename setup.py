#!/usr/bin/env python

import sys
from setuptools import find_packages, setup

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
    'catkin_pkg >= 0.4.0',
    'bs4',
    'rospkg >= 1.1.8',
]

setup(
    name='superflore',
    version='0.2.1',
    packages=find_packages(exclude=['tests', 'tests.*']),
    author='Hunter L. Allen',
    author_email='hunter@openrobotics.org',
    url='https://github.com/ros-infrastructure/superflore',
    keywords=['ROS'],
    install_requires=install_requires,
    python_requires='>=3',
    classifiers=['Programming Language :: Python',
                 'License :: OSI Approved :: Apache Software License'],
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
