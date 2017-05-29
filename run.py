#!/usr/bin/python
from scripts.gen_packages import generate_installers

# generate installers for kinetic
# indigo_installers, indigo_broken = generate_installers("indigo")
# kinetic_installers, kinetic_broken = generate_installers("kinetic")
lunar_installers, lunar_broken = generate_installers("lunar")

master_list = lunar_broken.copy() # indigo_broken.copy()

"""
for p in kinetic_broken.keys():
    if p not in master_list.key():
        master_list[p] = kinetic_broken[p].copy()

for p in lunar_broken.keys():
    if p not in master_list.keys():
        master_list[p] = lunar_broken[p].copy()
"""
for broken in master_list.keys():
    print("{}:".format(broken))
    for pkg in master_list[broken]:
        print (" * [ ] {}".format(pkg))
    print()
