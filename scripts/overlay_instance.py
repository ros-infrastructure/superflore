# Instance of the ROS Overlay
from .repo_instance import repo_instance
import random
import string
import time
import os

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
        self.git.commit(m='{0}'.format(commit_msg))

    def regenerate_manifests(self):
        self.info('Generating manifests...')
        pid = os.fork()

        if pid == 0:
            os.chdir(self.repo_dir)
            self.info('child: changed work directory to {0}'.format(os.getcwd()))
            os.execlp('sudo', 'sudo', 'repoman', 'manifest')
            self.error('Failed to run repoman!')
            self.error('Do you have permissions?')
            quit()
        else:            
            if os.waitpid(pid, 0)[1] != 0:
                self.error('Manifest generation failed. Exiting...')
                quit()
            else:
                self.happy('Manifest generation succeeded.')

    def pull_request(self, message):
        self.info('Filing pull-request for ros/ros-overlay...')
        pr_title = 'rosdistro sync, {0}'.format(time.ctime())        
        self.git.pull_request(m='{0}'.format(message), title='{0}'.format(pr_title))
        self.happy('Successfully filed a pull request with the ros/ros-overlay repo.')
