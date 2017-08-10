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


# TODO(allenh1): remove inheritance like the RosOverlay class.
from superflore import RepoInstance as repo_instance
import random
import string
import time


def get_random_tmp_dir():
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(10))
    return '/tmp/{0}'.format(rand_str)


def get_random_branch_name():
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(10))
    return 'gentoo-bot-{0}'.format(rand_str)


class ros_meta(repo_instance):
    def __init__(self):
        # clone repo into a random tmp directory.
        repo_instance.__init__(self, 'allenh1',
                               'meta-ros', get_random_tmp_dir())
        self.branch_name = get_random_branch_name()
        self.clone()
        branch_msg = 'Creating new branch {0}...'.format(self.branch_name)
        repo_instance.info(branch_msg)
        self.create_branch(self.branch_name)

    def clean_ros_ebuild_dirs(self, distro=None):
        if distro is not None:
            self.info(
                'Cleaning up recipes-ros-{0} directory...'.format(distro)
            )
            self.git.rm('-rf', 'recipes-ros-{0}'.format(distro))
        else:
            self.info('Cleaning up recipes-ros-* directories...')
            self.git.rm('-rf', 'recipes-ros-*')

    def commit_changes(self, distro):
        self.info('Adding changes...')
        if distro == 'all' or distro == 'update':
            self.git.add('recipes-ros-*')
        else:
            self.git.add('recipes-ros-{0}'.format(distro))
        commit_msg = {
            'update': 'rosdistro sync, {0}',
            'all': 'regenerate all distros, {0}',
            'lunar': 'regenerate ros-lunar, {0}',
            'indigo': 'regenerate ros-indigo, {0}',
            'kinetic': 'regenerate ros-kinetic, {0}',
        }[distro].format(time.ctime())
        self.info('Committing to branch {0}...'.format(self.branch_name))
        self.git.commit(m='{0}'.format(commit_msg))

    def pull_request(self, message):
        self.info('Filing pull-request for allenh1/meta-ros...')
        pr_title = 'rosdistro sync, {0}'.format(time.ctime())
        self.git.pull_request(m='{0}'.format(message),
                              title='{0}'.format(pr_title))
        good_msg = 'Successfully filed a pull request with the {0} repo.'
        good_msg = good_msg.format('allenh1/meta-ros')
        self.happy(good_msg)
