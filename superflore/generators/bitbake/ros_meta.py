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

import time

from superflore.repo_instance import RepoInstance
from superflore.utils import info
from superflore.utils import rand_ascii_str


class RosMeta(object):
    def __init__(self, repo_dir, do_clone, org='allenh1', repo='meta-ros'):
        self.repo = RepoInstance(org, repo, repo_dir, do_clone)
        self.branch_name = 'yocto-bot-%s' % rand_ascii_str()
        info('Creating new branch {0}...'.format(self.branch_name))
        self.repo.create_branch(self.branch_name)

    def clean_ros_recipe_dirs(self, distro=None):
        if distro:
            info('Cleaning up recipes-ros-{0} directory...'.format(distro))
            self.repo.git.rm('-rf', 'recipes-ros-{0}'.format(distro))
        else:
            info('Cleaning up recipes-ros-* directories...')
            self.repo.git.rm('-rf', 'recipes-ros-*')

    def commit_changes(self, distro):
        info('Adding changes...')
        if distro == 'all' or distro == 'update':
            self.repo.git.add('recipes-ros-*')
        else:
            self.repo.git.add('recipes-ros-{0}'.format(distro))
        commit_msg = {
            'update': 'rosdistro sync, {0}',
            'all': 'regenerate all distros, {0}',
            'lunar': 'regenerate ros-lunar, {0}',
            'indigo': 'regenerate ros-indigo, {0}',
            'kinetic': 'regenerate ros-kinetic, {0}',
        }[distro].format(time.ctime())
        info('Committing to branch {0}...'.format(self.branch_name))
        self.repo.git.commit(m='{0}'.format(commit_msg))

    def pull_request(self, message, distro):
        pr_title = 'rosdistro sync, {0}'.format(time.ctime())
        self.repo.pull_request(message, pr_title, branch=distro)
