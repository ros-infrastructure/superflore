#!/usr/bin/python
from src.gen_packages import generate_installers
from src.overlay_instance import ros_overlay
import shutil
import sys
import os

# Modify if a new distro is added
active_distros = [ 'indigo', 'kinetic', 'lunar' ]
# just update packages, by default.
mode = 'update'

def link_existing_files():
    global overlay
    global mode
    if mode == 'all' or mode == 'update':
        for x in active_distros:
            ros_overlay.info('Symbolicly linking files from {0}/ros-{1}...'.format(overlay.repo_dir, x))
            os.symlink('{0}/ros-{1}'.format(overlay.repo_dir, x), './ros-' + x)
    else:
        # only link the relevant directory.
        ros_overlay.info('Symbolicly linking files from {0}/ros-{1}...'.format(overlay.repo_dir, mode))
        os.symlink('{0}/ros-{1}'.format(overlay.repo_dir, mode), './ros-' + mode)        

def clean_up():
    global mode
    ros_overlay.info('Cleaning up temporary directory {0}...'.format(overlay.repo_dir))
    shutil.rmtree(overlay.repo_dir)
    ros_overlay.info('Cleaning up symbolic links...')

    if mode != 'all' and mode != 'update':
        os.remove('ros-{0}'.format(mode))
    else:
        for x in active_distros:
            os.remove('ros-{0}'.format(x))

def print_usage():
    usage = 'Usage: {0} [ --all'.format(sys.argv[0])
    for distro in active_distros:
        usage += '| --{0}'.format(distro)
    usage += ' ]'
    ros_overlay.info(usage)
    
if len(sys.argv) == 2:
    arg1 = sys.argv[1].replace('--', '')

    if arg1 == 'all' or arg1 == 'update':
        mode = arg1
    else:
        if not arg1 in active_distros:
            ros_overlay.error('Unknown ros distro "{0}"'.format(arg1))
            ros_overlay.error('Exiting...')
            sys.exit(1)
        else:
            ros_overlay.info('Regenerating all packages for distro "{0}"'.format(arg1))
            mode = arg1
elif len(sys.argv) >= 2:
    ros_overlay.error('Invalid arguments!')
    print_usage()

# clone current repo
overlay = ros_overlay()
selected_targets = active_distros

if mode == 'all':
    """
    Clean existing ros-* files
    """
    ros_overlay.warn('"All" mode detected... This may take a while!')
    overlay.clean_ros_ebuild_dirs()
    for x in active_distros:
        ros_overlay.info('Creating directory {0}/ros-{1}...'.format(overlay.repo_dir, x))
        os.makedirs('{0}/ros-{1}'.format(overlay.repo_dir, x))
elif mode != 'update':
    """
    Clean ros-[mode] files
    """
    overlay.clean_ros_ebuild_dirs(mode)
    ros_overlay.info('Creating directory {0}/ros-{1}...'.format(overlay.repo_dir, mode))
    os.makedirs('{0}/ros-{1}'.format(overlay.repo_dir, mode))
    selected_targets = [ mode ]
try:
    link_existing_files()
except FileExistsError as fe:
    ros_overlay.warn('Detected existing rosdistro ebuild structure... Removing and overwriting.')
    for x in active_distros:
        os.remove('ros-{0}'.format(x))
    link_existing_files()

# generate installers
total_installers = dict()
total_broken = set()
total_changes = dict()

for distro in selected_targets:
    distro_installers, distro_broken, distro_changes = generate_installers(distro)
    for key in distro_broken.keys():
        for pkg in distro_broken[key]:
            total_broken.add(pkg)

    total_changes[distro] = distro_changes
    total_installers[distro] = distro_installers

num_changes = 0
for distro_name in total_changes:
    num_changes += len(total_changes[distro_name])

if num_changes == 0:
    ros_overlay.info('ROS distro is up to date.')
    ros_overlay.info('Exiting...')
    clean_up()
    sys.exit(0)

# remove duplicates
inst_list = total_broken

delta  = "Changes:\n"
delta += "========\n" 

if 'indigo' in total_changes and len(total_changes['indigo']) > 0:
    delta += "Indigo Changes:\n"
    delta += "---------------\n"
    
    for d in sorted(total_changes['indigo']):
        delta += '* {0}\n'.format(d)
    delta += "\n"

if 'kinetic' in total_changes and len(total_changes['kinetic']) > 0:
    delta += "Kinetic Changes:\n"
    delta += "----------------\n"

    for d in sorted(total_changes['kinetic']):
        delta += '* {0}\n'.format(d)
    delta += "\n"

if 'lunar' in total_changes and len(total_changes['lunar']) > 0:
    delta += "Lunar Changes:\n"
    delta += "--------------\n"

    for d in sorted(total_changes['lunar']):
        delta += '* {0}\n'.format(d)
    delta += "\n"

if len(inst_list) > 0:
    missing_deps  ="Missing Dependencies:\n"
    missing_deps +="=====================\n"
    for pkg in sorted(inst_list):
        missing_deps += " * [ ] {0}\n".format(pkg)

"""
We don't need to remove files anymore.

overlay.clean_ros_ebuild_dirs()
"""

# Commit changes and file pull request
overlay.regenerate_manifests(mode)
overlay.commit_changes(mode)
try:
    overlay.pull_request('{0}\n{1}'.format(delta, missing_deps))
except Exception as e:
    overlay.error('Failed to file PR with ros/ros-overlay repo!')
    overlay.error('Exception: {0}'.format(e))

clean_up()
ros_overlay.happy('Successfully synchronized repositories!')
