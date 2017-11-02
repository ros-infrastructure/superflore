# Copyright 2017 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time

from superflore.docker import Docker

from superflore.repo_instance import RepoInstance

from superflore.utils import info
from superflore.utils import rand_ascii_str


class RosOverlay(object):
    def __init__(self, repo_dir, do_clone, org='ros', repo='ros-overlay'):
        self.repo = RepoInstance(org, repo, repo_dir, do_clone)
        self.branch_name = 'gentoo-bot-%s' % rand_ascii_str()
        info('Creating new branch {0}...'.format(self.branch_name))
        self.repo.create_branch(self.branch_name)

    def clean_ros_ebuild_dirs(self, distro=None):
        if distro:
            info('Cleaning up ros-{0} directory...'.format(distro))
            self.repo.git.rm('-rf', 'ros-{0}'.format(distro))
        else:
            info('Cleaning up ros-* directories...')
            self.repo.git.rm('-rf', 'ros-*')

    def commit_changes(self, distro):
        info('Adding changes...')
        if distro:
            self.repo.git.add('ros-{0}'.format(distro))
        else:
            self.repo.git.add('ros-*')
            distro = 'update'
        commit_msg = {
            'update': 'rosdistro sync, {0}',
            'all': 'regenerate all distros, {0}',
            'lunar': 'regenerate ros-lunar, {0}',
            'indigo': 'regenerate ros-indigo, {0}',
            'kinetic': 'regenerate ros-kinetic, {0}',
        }[distro].format(time.ctime())
        info('Committing to branch {0}...'.format(self.branch_name))
        self.repo.git.commit(m='{0}'.format(commit_msg))

    def regenerate_manifests(self, regen_dict):
        info('Building docker image...')
        dock = Docker('repoman_docker', 'gentoo_repoman')
        dock.build()
        info('Running docker image...')
        info('Generating manifests...')
        dock.map_directory(
            '/home/%s/.gnupg' % os.getenv('USER'),
            '/root/.gnupg'
        )
        dock.map_directory(self.repo.repo_dir, '/tmp/ros-overlay')
        for key in regen_dict.keys():
            for pkg in regen_dict[key]:
                pkg_dir = '/tmp/ros-overlay/ros-{0}/{1}'.format(key, pkg)
                dock.add_bash_command('cd {0}'.format(pkg_dir))
                dock.add_bash_command('repoman manifest')
                dock.add_bash_command('cd /tmp/ros-overlay')
        dock.run(show_cmd=True)

    def pull_request(self, message):
        pr_title = 'rosdistro sync, {0}'.format(time.ctime())
        self.repo.pull_request(message, pr_title)
