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

from termcolor import colored
from git import Repo
from git.exc import GitCommandError as GitGotGot
import shutil


class repo_instance(object):
    def __init__(self, repo_owner, repo_name, repo_dir=None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        repo_url = 'https://github.com/{0}/{1}'
        self.repo_url = repo_url.format(self.repo_owner, self.repo_name)
        if repo_dir is not None:
            self.repo_dir = repo_dir
        else:
            self.repo_dir = self.repo_name
        self.repo = Repo.clone_from(self.repo_url, self.repo_dir)
        self.git = self.repo.git

    def clone(self, branch=None):
        shutil.rmtree(self.repo_dir)
        msg = 'Cloning repo {0}/{1}'.format(self.repo_owner, self.repo_name)
        if self.repo_dir != self.repo_name:
            msg += (' into directory {0}'.format(self.repo_dir))
        msg += '...'
        repo_instance.info(msg)
        self.repo = Repo.clone_from(self.repo_url, self.repo_dir)
        if branch is not None:
            self.git.checkout(branch)

    def remove_file(self, filename, ignore_fail=False):
        try:
            self.git.rm('-f', filename)
        except GitGotGot as g:
            if ignore_fail:
                return
            fail_msg = 'Failed to remove file {0}'.format(filename)
            fail_msg += 'from source control.'
            self.error(fail_msg)
            self.error(' Exception: {0}'.format(g))

    def create_branch(self, branch_name):
        """
        @todo: error checking
        """
        repo_instance.info(self.git.checkout('HEAD', b=branch_name))

    def remove_branch(self, branch_name):
        """
        @todo: error checking
        """
        self.git.branch('-D', branch_name)

    def change_branch(self, branch_name):
        """
        @todo: error checking
        """
        self.git.checkout(branch_name)

    def rebase(self, target):
        """
        @todo: error checking
        """
        self.git.rebase(i=target)

    @staticmethod
    def info(string):
        print(colored(string, 'cyan'))

    @staticmethod
    def error(string):
        print(colored(string, 'red'))

    @staticmethod
    def warn(string):
        print(colored(string, 'yellow'))

    @staticmethod
    def happy(string):
        print(colored(string, 'green'))


class CloneException(Exception):
    def __init__(self, message):
        self.message = message


class BranchException(Exception):
    def __init__(self, message):
        self.message = message