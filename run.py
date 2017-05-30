#!/usr/bin/python
from scripts.gen_packages import generate_installers

# generate installers for kinetic
indigo_installers, indigo_broken = generate_installers("indigo")
kinetic_installers, kinetic_broken = generate_installers("kinetic")
lunar_installers, lunar_broken = generate_installers("lunar")

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

for pkg in inst_list:
    print(" * [ ] {}".format(pkg))
