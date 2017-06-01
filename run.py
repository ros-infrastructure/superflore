#!/usr/bin/python
from scripts.gen_packages import generate_installers
from scripts.overlay_instance import ros_overlay
import shutil

# clone current repo
overlay = ros_overlay()

# generate installers for kinetic
indigo_installers, indigo_broken = generate_installers("indigo")
kinetic_installers, kinetic_broken = generate_installers("kinetic")
lunar_installers, lunar_broken = generate_installers("lunar")

master_list = lunar_broken.copy()

ros_overlay.info('Copying files from {0}...'.format(overlay.repo_dir + '/ros-indigo'))
shutil.copytree(overlay.repo_dir + '/ros-indigo', './')
ros_overlay.info('Copying files from {0}...'.format(overlay.repo_dir + '/ros-kinetic'))
shutil.copytree(overlay.repo_dir + '/ros-kinetic', './')
ros_overlay.info('Copying files from {0}...'.format(overlay.repo_dir + '/ros-lunar'))
shutil.copytree(overlay.repo_dir + '/ros-lunar', './')

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
shutil.copytree('ros-indigo', overlay.repo_dir)
shutil.copytree('ros-kinetic', overlay.repo_dir)
shutil.copytree('ros-lunar', overlay.repo_dir)

# Commit changes and file pull request
overlay.commit_changes()
overlay.pull_request()
