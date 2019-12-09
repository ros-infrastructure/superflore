# Copyright 2019 Open Source Robotics Foundation, Inc.
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

from superflore.repo_instance import RepoInstance
from superflore.utils import info
from superflore.utils import rand_ascii_str


class NixRosOverlay(object):
    def __init__(self, repo_dir, do_clone, org='lopsided98',
                 repo='nix-ros-overlay', from_branch='', new_branch=True):
        self.repo = RepoInstance(org, repo, repo_dir, do_clone,
            from_branch=from_branch)
        if new_branch:
            self.branch_name = 'nix-bot-%s' % rand_ascii_str()
            info('Creating new branch {0}...'.format(self.branch_name))
            self.repo.create_branch(self.branch_name)
        else:
            self.branch_name = None

    def commit_changes(self, distro):
        info('Adding changes...')
        if distro == 'all':
            commit_msg = 'regenerate all distros, {0}'
            self.repo.git.add('*/*/default.nix')
            self.repo.git.add('*/generated.nix')
        else:
            commit_msg = 'regenerate rosPackages.{1}, {0}'
            self.repo.git.add(distro)
        if self.repo.git.status('--porcelain') == '':
            info('Nothing changed; no commit done')
        else:
            timestamp = os.getenv(
                'SUPERFLORE_GENERATION_DATETIME',
                time.ctime())
            commit_msg = commit_msg.format(timestamp, distro)
            if self.branch_name:
                info('Committing to branch {0}...'.format(self.branch_name))
            else:
                info('Committing to current branch')
            self.repo.git.commit(m=commit_msg)

    def pull_request(self, message, distro=None, title=''):
        if not title:
            timestamp = os.getenv(
                'SUPERFLORE_GENERATION_DATETIME',
                time.ctime())
            title = 'rosdistro sync, {0}'.format(timestamp)
        self.repo.pull_request(message, title, branch=self.branch_name,
            fork=False)
