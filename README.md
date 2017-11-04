Super Flore:
=================
Latin for "Super Bloom", this is an extended release manager for
ROS.

Supported Platforms:
--------------------
 * Gentoo
 * Open Embedded

Installation:
=============

Dependencies:
--------------
 * Python 3
 * Docker
 * Git

Instructions:
-------------

```
 $ sudo python3 ./setup.py install
```

Usage:
======

```
$ superflore-gen-ebuilds --help
usage: Deploy ROS packages into Gentoo Linux [-h] [--ros-distro ROS_DISTRO]
                                             [--all] [--dry-run] [--pr-only]
                                             [--output-repository-path OUTPUT_REPOSITORY_PATH]
                                             [--only ONLY [ONLY ...]]

optional arguments:
  -h, --help            show this help message and exit
  --ros-distro ROS_DISTRO
                        regenerate packages for the specified distro
  --all                 regenerate all packages in all distros
  --dry-run             run without filing a PR to remote
  --pr-only             ONLY file a PR to remote
  --output-repository-path OUTPUT_REPOSITORY_PATH
                        location of the Git repo
  --only ONLY [ONLY ...]
                        generate only the specified packages
```

Common Usage:
--------------
To update the gentoo ebuilds, run the following:

```
$ superflore-gen-ebuilds
```

This command will clone the `ros/ros-overlay` repo into
a subfolder within `/tmp`. This can be thought of as an
update mode. *Note: this mode will file a PR with ros/ros-overlay.*

If you don't want to file a PR with ros/ros-overlay, you should add
the `--dry-run` flag. You can later decide to file the PR after inspection
by using the `--pr-only` flag.

To regenerate only the specified packages, use the `--only [pkg1] [pkg2] ... [pkgn]` flag (**note:** you will need to also use the `--ros-distro [distro]` flag.

*If you want to use an existing repo instead of cloning one,
add `--output-repository-path [path]`.*

Regenerating:
--------------
In the case that you wish to regenerate an entire rosdistro, you may do
so by adding the `--ros-distro [distro name]` flag. *Note: this is very
time consuming.*

If you wish to regenerate _all_ installers for _all_ ros distros, you
should pass the `--all` flag in place of the `--ros-distro` flag. *Note:
this takes an _extremely_ long amount of time.*
