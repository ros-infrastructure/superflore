#!/usr/bin/python
from scripts.gen_packages import generate_installers
from scripts.overlay_instance import ros_overlay
import shutil
import sys
import os

all_mode = False

if len(sys.argv) == 2:
    arg1 = sys.argv[1]
    if arg1 == '--all':
        all_mode = True
    else:
        ros_overlay
# clone current repo
overlay = ros_overlay()
active_distros = [ 'ros-indigo', 'ros-kinetic', 'ros-lunar' ]

if all_mode:
    """
    Clean existing ros-* files
    """
    ros_overlay.warn('"All" mode detected... This may take a while!')
    overlay.clean_ros_ebuild_dirs()
    for x in active_distros:
        ros_overlay.info('Creating directory {0}/{1}...'.format(overlay.repo_dir, x))
        os.makedirs('{0}/{1}'.format(overlay.repo_dir, x))

def link_existing_files():
    global overlay
    for x in active_distros:
        ros_overlay.info('Symbolicly linking files from {0}/{1}...'.format(overlay.repo_dir, x))
        os.symlink(overlay.repo_dir + '/' + x, './' + x)

def clean_up():
    ros_overlay.info('Cleaning up temporary directory {0}...'.format(overlay.repo_dir))
    shutil.rmtree(overlay.repo_dir)
    ros_overlay.info('Cleaning up symbolic links...')

    for x in active_distros:
        os.remove(x)

try:
    link_existing_files()
except FileExistsError as fe:
    ros_overlay.warn('Detected existing rosdistro ebuild structure... Removing and overwriting.')
    for x in active_distros:
        os.remove(x)
    link_existing_files()

# generate installers for kinetic
indigo_installers, indigo_broken, indigo_changes = generate_installers("indigo")
kinetic_installers, kinetic_broken, kinetic_changes = generate_installers("kinetic")
lunar_installers, lunar_broken, lunar_changes = generate_installers("lunar")

if len(indigo_changes) + len(kinetic_changes) + len(lunar_changes) == 0:
    ros_overlay.info('ROS distro is up to date.')
    ros_overlay.info('Exiting...')
    clean_up()
    quit()

master_list = indigo_broken.copy()

for p in kinetic_broken.keys():
    if p not in master_list.keys():
        master_list[p] = kinetic_broken[p]

for p in lunar_broken.keys():
    if p not in master_list.keys():
        master_list[p] = lunar_broken[p]

inst_list = set()

for broken in master_list.keys():
    for pkg in master_list[broken]:
        inst_list.add(pkg)

# remove duplicates
inst_list = sorted(inst_list)

delta  = "Changes:\n"
delta += "========\n" 

if len(indigo_changes) > 0:
    delta += "Indigo Changes:\n"
    delta += "---------------\n"
    
    for d in sorted(indigo_changes):
        delta += '* {0}\n'.format(d)
    delta += "\n"

if len(kinetic_changes) > 0:
    delta += "Kinetic Changes:\n"
    delta += "----------------\n"

    for d in sorted(kinetic_changes):
        delta += '* {0}\n'.format(d)
    delta += "\n"

if len(lunar_changes) > 0:
    delta += "Lunar Changes:\n"
    delta += "--------------\n"

    for d in sorted(lunar_changes):
        delta += '* {0}\n'.format(d)
    delta += "\n"

if len(inst_list) > 0:
    missing_deps  ="Missing Dependencies:\n"
    missing_deps +="=====================\n"
    for pkg in inst_list:
        missing_deps += " * [ ] {0}\n".format(pkg)

"""
We don't need to remove files anymore.

overlay.clean_ros_ebuild_dirs()
"""

# Commit changes and file pull request
overlay.regenerate_manifests()
overlay.commit_changes()
try:
    overlay.pull_request('{0}\n{1}'.format(delta, missing_deps))
except Exception as e:
    overlay.error('Failed to file PR with ros/ros-overlay repo!')
    overlay.error('Exception: {0}'.format(e))

clean_up()
ros_overlay.happy('Successfully synchronized repositories!')
