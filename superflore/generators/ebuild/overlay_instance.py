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

import docker
from superflore.docker import Docker
from superflore.repo_instance import RepoInstance
from superflore.utils import info
from superflore.utils import rand_ascii_str


class RosOverlay(object):
    def __init__(
        self, repo_dir, do_clone, org='ros', repo='ros-overlay',
        from_branch='', new_branch=True
    ):
        self.repo = RepoInstance(
            org, repo, repo_dir=repo_dir, do_clone=do_clone,
            from_branch=from_branch)
        if new_branch:
            self.branch_name = 'gentoo-bot-%s' % rand_ascii_str()
            info('Creating new branch {0}...'.format(self.branch_name))
            self.repo.create_branch(self.branch_name)
        else:
            self.branch_name = None

    def commit_changes(self, distro):
        info('Adding changes...')
        self.repo.git.add(self.repo.repo_dir)
        if self.repo.git.status('--porcelain') == '':
            info('Nothing changed; no commit done')
        else:
            if self.branch_name:
                info('Committing to branch {0}...'.format(self.branch_name))
            else:
                info('Committing to current branch')
            if distro == 'all':
                commit_msg = 'regenerate all distros, {0}'
            elif distro:
                commit_msg = 'regenerate ros-{1}, {0}'
            else:
                commit_msg = 'rosdistro sync, {0}'
            timestamp = os.getenv(
                'SUPERFLORE_GENERATION_DATETIME',
                time.ctime())
            commit_msg = commit_msg.format(timestamp, distro)
            self.repo.git.commit(m='{0}'.format(commit_msg))

    def regenerate_manifests(
        self, regen_dict, image_owner='allenh1', image_name='ros_gentoo_base'
    ):
        info(
            "Pulling docker image '%s/%s:latest'..." % (
                image_owner, image_name
            )
        )
        dock = Docker()
        dock.pull(image_owner, image_name)
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
        try:
            dock.run(show_cmd=True)
        except docker.errors.ContainerError:
            print(dock.log)
            raise

    def pull_request(self, message, overlay=None, title=''):
        if not title:
            timestamp = os.getenv(
                'SUPERFLORE_GENERATION_DATETIME',
                time.ctime())
            title = 'rosdistro sync, {0}'.format(timestamp)
        self.repo.pull_request(message, title)
