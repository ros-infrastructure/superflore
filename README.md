Super Flore:
=================
Latin for "Super Bloom", this is an extended release manager for
ROS.

Supported Platforms:
--------------------
 * Gentoo
 * OpenEmbedded

Installation:
=============

Dependencies:
--------------
 * Python 3
 * Docker
 * Git

Instructions:
-------------
Generate an [OAuth token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) for this applicaiton.

After you have created the token, place it in the
environment variable `SUPERFLORE_GITHUB_TOKEN`.

Then install and run the application.

```
 $ sudo python3 ./setup.py install
```

Usage:
======

### Generating Gentoo Ebuilds
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
  --pr-comment PR_COMMENT
                        comment to add to the PR
  --upstream-repo UPSTREAM_REPO
                        location of the upstream repository as in
                        https://github.com/<owner>/<repository>
  --upstream-branch UPSTREAM_BRANCH
                        branch of the upstream repository
  --skip-keys SKIP_KEYS
                        packages to skip during regeneration
```

### Testing Gentoo Ebuilds
```
$ superflore-check-ebuilds -h
usage: Check if ROS packages are building for Gentoo Linux [-h]
                                                           [--ros-distro ROS_DISTRO [ROS_DISTRO ...]]
                                                           [--pkgs PKGS [PKGS ...]]
                                                           [-f F] [-v]
                                                           [--log-file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --ros-distro ROS_DISTRO [ROS_DISTRO ...]
                        distro(s) to check
  --pkgs PKGS [PKGS ...]
                        packages to build
  -f F                  build packages specified by the input file
  -v, --verbose         show output from docker
  --log-file LOG_FILE   location to store the log file
```

If a file is to be passed as input, it is expected to be in proper yaml format, such as the below.

```
indigo:
  - catkin
  - p2os_msgs
kinetic:
  - catkin
lunar:
  - catkin
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


F.A.Q.:
=========
Here are some specific use cases for Superflore.

Gentoo:
--------

**Q**: _I need to patch this package. What are the steps involved here?_

**A**: It's relatively simple to generate a patch for a package. From a 
contributor standpoint, superflore does most of the heavy lifting for you.

We'll assume you have already patched your source code, and your patch is
named `fix-pkg.patch`. Also, we'll assume you're patching the package `foo`,
and that you have a fork of ros/ros-overlay on its master branch within
you home directory.

```
$ cd ${HOME}/ros-overlay/ros-[distro]/foo
$ mkdir files
$ cp /path/to/patch/fix-pkg.patch ./files
$ git add files
$ git commit -m "Add patch to fix package [foo] in [distro]."
```

Next, use Superflore to regenerate the package.

```
$ superflore-gen-ebuilds --only [foo] --ros-distro [distro] --output-repository-path ~/ros-overlay
```

After that command runs, a pull request will be filed on your behalf into
the ROS overlay repository. **Note:** If you don't want a pull request to be
filed, add the `--dry-run` flag to the above command, and, after you are ready
to file the pr, run `superflore-gen-ebuilds --pr-only`.
