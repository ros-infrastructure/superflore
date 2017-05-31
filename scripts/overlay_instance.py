# Instance of the ROS Overlay
from .repo_instance import repo_instance
import random
import string
import time

def get_random_tmp_dir():
    return '/tmp/{0}'.format(''.join(random.choice(string.ascii_letters) for x in range(10)))

def get_random_branch_name():
    return 'gentoo-bot-{0}'.format(''.join(random.choice(string.ascii_letters) for x in range(10)))

class ros_overlay(repo_instance):
    def __init__(self):
        # clone repo into a random tmp directory.
        repo_instance.__init__(self, 'ros', 'ros-overlay', get_random_tmp_dir())
        self.branch_name = get_random_branch_name()        
        self.clone()
        repo_instance.info('Creating new branch {0}...'.format(self.branch_name))
        self.create_branch(self.branch_name)

    def clean_ros_ebuild_dirs(self):
        self.git.rm('-rf', 'ros-*')

    def commit_changes(self):
        self.info('Adding changes...')
        self.git.add('ros-*')
        commit_msg = 'rosdistro sync, {0}'.format(time.ctime())
        self.info('Committing to branch {0}...'.format(self.branch_name))
        self.git.commit(m='"{0}"'.format(commit_msg))

    def pull_request(self, message):
        self.info('Filing pull-request for ros/ros-overlay...')
        self.git.pull_request(m=message)
        self.happy('Successfully filed a pull request with the ros/ros-overlay repo.')
