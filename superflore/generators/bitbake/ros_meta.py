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

from superflore.generators.bitbake.yocto_recipe import yoctoRecipe
from superflore.repo_instance import RepoInstance
from superflore.utils import info


class RosMeta(object):
    def __init__(
        self, dir, do_clone, branch, org='ros', repo='meta-ros',
        from_branch='', branch_name=''
    ):
        self.repo = RepoInstance(
            org, repo, dir, do_clone, from_branch=from_branch)
        self.branch_name = branch
        if branch:
            info('Creating new branch {0}...'.format(self.branch_name))
            self.repo.create_branch(self.branch_name)

    def clean_ros_recipe_dirs(self, distro):
        # superflore-change-summary.txt is no longer being generated since:
        # https://github.com/ros-infrastructure/superflore/pull/273
        # but remove it here to make sure it gets deleted when new distro
        # release is being generated
        files = 'meta-ros{0}-{1}/generated-recipes '\
                'meta-ros{0}-{1}/conf/ros-distro/include/{1}/generated '\
                'meta-ros{0}-{1}/files/{1}/generated/'\
                'newer-platform-components.list '\
                'meta-ros{0}-{1}/files/{1}/generated/rosdep-resolve.yaml '\
                'meta-ros{0}-{1}/files/{1}/generated/'\
                'superflore-change-summary.txt '.format(
                    yoctoRecipe._get_ros_version(distro), distro)
        info(
            'Cleaning up:\n{0}'
            .format(files))
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
        self.repo.git.add('meta-ros{0}-{1}/generated-recipes'.format(
            yoctoRecipe._get_ros_version(distro), distro))
        self.repo.git.add('meta-ros{0}-{1}/conf/ros-distro/include/{1}/'
                          'generated/*.inc'.format(
                              yoctoRecipe._get_ros_version(distro), distro))
        self.repo.git.add('meta-ros{0}-{1}/files/{1}/generated/'
                          'rosdep-resolve.yaml'.format(
                              yoctoRecipe._get_ros_version(distro), distro))
        self.repo.git.add('meta-ros{0}-{1}/files/{1}/generated/'
                          'newer-platform-components.list'.format(
                              yoctoRecipe._get_ros_version(distro), distro))

    def get_change_summary(self, distro):
        sep = '-' * 5
        return '\n'.join([
            sep,
            self.repo.git.status('--porcelain'),
            sep,
            self.repo.git.diff(
                'HEAD',
                'meta-ros{0}-{1}/conf/ros-distro/include/{1}/'
                'generated/*.inc'.format(
                    yoctoRecipe._get_ros_version(distro), distro)),
            sep,
            self.repo.git.diff(
                'HEAD',
                'meta-ros{0}-{1}/files/{1}/generated/'
                'newer-platform-components.list'.format(
                    yoctoRecipe._get_ros_version(distro), distro),
                'meta-ros{0}-{1}/files/{1}/generated/'
                'rosdep-resolve.yaml'.format(
                    yoctoRecipe._get_ros_version(distro), distro)
            ),
        ]) + '\n'
