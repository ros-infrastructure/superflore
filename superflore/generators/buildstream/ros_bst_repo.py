# Copyright 2017 Open Source Robotics Foundation, Inc.
# Copyright 2024 Codethink
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

from superflore.repo_instance import RepoInstance
from superflore.utils import info


class RosBstRepo(object):
    def __init__(
        self, dir, do_clone, branch, org, repo,
        from_branch='', branch_name='', generated_elements_dir="elements/generated"
    ):
        self.repo = RepoInstance(
            org, repo, dir, do_clone, from_branch=from_branch)
        self.branch_name = branch
        self.generated_elements_dir = generated_elements_dir
        if branch:
            info('Creating new branch {0}...'.format(self.branch_name))
            self.repo.create_branch(self.branch_name)

    def clean_ros_element_dirs(self, distro):
        files = self.generated_elements_dir
        info('Cleaning up:\n{0}'.format(files))
        self.repo.git.rm('-rf', '--ignore-unmatch', files.split())

    def commit_changes(self, distro, commit_msg):
        info('Commit changes...')
        if self.repo.git.status('--porcelain') == '':
            info('Nothing changed; no commit done')
        else:
            if self.branch_name:
                info('Committing to branch {0}...'.format(self.branch_name))
            else:
                info('Committing to current branch')
            self.repo.git.commit(m=commit_msg)

    def pull_request(self, message, distro=None, title=''):
        self.repo.pull_request(message, title, branch=distro)

    def get_file_revision_logs(self, *file_path):
        return self.repo.git.log('--oneline', '--', *file_path)

    def add_generated_files(self, distro):
        info('Adding changes...')
        self.repo.git.add(self.generated_elements_dir)

    def get_change_summary(self, distro):
        sep = '-' * 5
        return '\n'.join([
            sep,
            self.repo.git.status('--porcelain'),
            sep,
            self.repo.git.diff(
                'HEAD',
                self.generated_elements_dir + '/'
            ),
        ]) + '\n'
