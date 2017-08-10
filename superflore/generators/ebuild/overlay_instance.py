# Instance of the ROS Overlay
from superflore.repo_instance import RepoInstance
from superflore.docker import Docker
import random
import string
import time
import os


def get_random_tmp_dir():
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(10))
    return '/tmp/{0}'.format(rand_str)


def get_random_branch_name():
    rand_str = ''.join(random.choice(string.ascii_letters) for x in range(10))
    return 'gentoo-bot-{0}'.format(rand_str)


class RosOverlay(object):
    def __init__(self, repo_dir=None):
        # clone repo into a random tmp directory.
        do_clone = True
        if repo_dir:
            do_clone = not os.path.exists(os.path.realpath(repo_dir))
        self.repo = RepoInstance(
            'ros', 'ros-overlay',
            repo_dir or get_random_tmp_dir(),
            do_clone
        )
        self.branch_name = get_random_branch_name()
        if do_clone:
            self.repo.clone()
        branch_msg = 'Creating new branch {0}...'.format(self.branch_name)
        self.repo.info(branch_msg)
        self.repo.create_branch(self.branch_name)

    def clean_ros_ebuild_dirs(self, distro=None):
        if distro is not None:
            self.repo.info('Cleaning up ros-{0} directory...'.format(distro))
            self.repo.git.rm('-rf', 'ros-{0}'.format(distro))
        else:
            self.repo.info('Cleaning up ros-* directories...')
            self.repo.git.rm('-rf', 'ros-*')

    def commit_changes(self, distro):
        self.repo.info('Adding changes...')
        if not distro:
            self.repo.git.add('ros-*')
        else:
            self.repo.git.add('ros-{0}'.format(distro))
        if not distro:
            distro = 'update'
        commit_msg = {
            'update': 'rosdistro sync, {0}',
            'all': 'regenerate all distros, {0}',
            'lunar': 'regenerate ros-lunar, {0}',
            'indigo': 'regenerate ros-indigo, {0}',
            'kinetic': 'regenerate ros-kinetic, {0}',
        }[distro].format(time.ctime())
        self.repo.info('Committing to branch {0}...'.format(self.branch_name))
        self.repo.git.commit(m='{0}'.format(commit_msg))

    def regenerate_manifests(self, mode):
        self.repo.info('Building docker image...')
        dock = Docker('repoman_docker', 'gentoo_repoman')
        dock.build()
        self.repo.info('Running docker image...')
        self.repo.info('Generating manifests...')
        dock.map_directory(
            '/home/%s/.gnupg' % os.getenv('USER'),
            '/root/.gnupg'
        )
        if mode == 'all' or not mode:
            dock.map_directory(self.repo.repo_dir, '/tmp/ros-overlay')
        else:
            ros_dir = '{0}/ros-{1}'.format(self.repo.repo_dir, mode)
            dock.map_directory(ros_dir, '/tmp/ros-overlay')
        dock.add_bash_command('cd {0}'.format('/tmp/ros-overlay'))
        dock.add_bash_command('repoman manifest')
        dock.run(show_cmd=True)

    def pull_request(self, message):
        pr_title = 'rosdistro sync, {0}'.format(time.ctime())
        self.repo.pull_request(message, pr_title)
