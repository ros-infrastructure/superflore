#!/usr/bin/python
from scripts.gen_packages import generate_installers
from scripts.overlay_instance import ros_overlay
import shutil
import os

# clone current repo
overlay = ros_overlay()

def link_existing_files():
    global overlay
    ros_overlay.info('Symbolicly linking files from {0}...'.format(overlay.repo_dir + '/ros-indigo'))
    os.symlink(overlay.repo_dir + '/ros-indigo', './ros-indigo')
    ros_overlay.info('Symbolicly linking files from {0}...'.format(overlay.repo_dir + '/ros-kinetic'))
    os.symlink(overlay.repo_dir + '/ros-kinetic', './ros-kinetic')
    ros_overlay.info('Symbolicly linking files from {0}...'.format(overlay.repo_dir + '/ros-lunar'))
    os.symlink(overlay.repo_dir + '/ros-lunar', './ros-lunar')

try:
    link_existing_files()
except FileExistsError as fe:
    ros_overlay.warn('Detected existing rosdistro ebuil structure... Removing and overwriting.')
    for x in [ 'ros-lunar', 'ros-kinetic', 'ros-indigo' ]:
        os.remove(x)
        os.symlink(overlay.repo_dir + '/' + x, './' + x) 

# generate installers for kinetic
indigo_installers, indigo_broken = generate_installers("indigo")
kinetic_installers, kinetic_broken = generate_installers("kinetic")
lunar_installers, lunar_broken = generate_installers("lunar")

master_list = lunar_broken.copy()

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

missing_deps  ="Missing Dependencies:"
missing_deps +="---------------------"
for pkg in inst_list:
    missing_deps += " * [ ] {}".format(pkg)

# Clone repo
overlay.clean_ros_ebuild_dirs()

# Copy ros-* to ebuild directory
# shutil.copytree('ros-indigo', overlay.repo_dir)
# shutil.copytree('ros-kinetic', overlay.repo_dir)
# shutil.copytree('ros-lunar', overlay.repo_dir)

# Commit changes and file pull request
overlay.commit_changes()
overlay.pull_request(missing_deps)
