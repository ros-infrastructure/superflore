# Change Log

## [v0.3.0](https://github.com/ros-infrastructure/superflore/tree/v0.3.0) (2019-06-11)
[Full Changelog](https://github.com/ros-infrastructure/superflore/compare/v0.1.0...v0.3.0)

**Implemented enhancements:**

- Commit Message for Updates Reads ROS-'None' [\#195](https://github.com/ros-infrastructure/superflore/issues/195)
- Option args.all doesn't add all modified files to the commit/PR [\#183](https://github.com/ros-infrastructure/superflore/issues/183)
- Centralize skip keys option for dropping dependencies [\#170](https://github.com/ros-infrastructure/superflore/issues/170)
- Extending OpenEmbedded support [\#167](https://github.com/ros-infrastructure/superflore/issues/167)
- Remove ROS 2 index [\#162](https://github.com/ros-infrastructure/superflore/issues/162)
- Docker Container Output [\#146](https://github.com/ros-infrastructure/superflore/issues/146)
- Re-Imagining Open Embedded [\#95](https://github.com/ros-infrastructure/superflore/issues/95)
- Move some packages to DEPEND [\#83](https://github.com/ros-infrastructure/superflore/issues/83)
- Gentoo Build CI [\#82](https://github.com/ros-infrastructure/superflore/issues/82)
- Clean up .tar files for OpenEmbedded [\#80](https://github.com/ros-infrastructure/superflore/issues/80)
- Replace custom Docker class with upstream docker library [\#66](https://github.com/ros-infrastructure/superflore/issues/66)
- Update bitbake generator to not use symlinks [\#62](https://github.com/ros-infrastructure/superflore/issues/62)
- Refactor [\#27](https://github.com/ros-infrastructure/superflore/issues/27)
- Fix ros-None in Gentoo Commit Messages [\#196](https://github.com/ros-infrastructure/superflore/pull/196) ([allenh1](https://github.com/allenh1))
- Check missing dependencies before checking preserve\_existing [\#194](https://github.com/ros-infrastructure/superflore/pull/194) ([andre-rosa](https://github.com/andre-rosa))
- Fix gen\_pkg\_func failure not being recorded by generate\_installers [\#187](https://github.com/ros-infrastructure/superflore/pull/187) ([andre-rosa](https://github.com/andre-rosa))
- Fix args.all handling [\#182](https://github.com/ros-infrastructure/superflore/pull/182) ([andre-rosa](https://github.com/andre-rosa))
- Fix assorted typos [\#181](https://github.com/ros-infrastructure/superflore/pull/181) ([andre-rosa](https://github.com/andre-rosa))
- Add `--upstream-branch` option [\#180](https://github.com/ros-infrastructure/superflore/pull/180) ([andre-rosa](https://github.com/andre-rosa))
- Add `--skip-keys` option [\#175](https://github.com/ros-infrastructure/superflore/pull/175) ([andre-rosa](https://github.com/andre-rosa))
- Small cleanups [\#169](https://github.com/ros-infrastructure/superflore/pull/169) ([andre-rosa](https://github.com/andre-rosa))
- Initial OpenEmbedded Support for ROS 2 [\#168](https://github.com/ros-infrastructure/superflore/pull/168) ([andre-rosa](https://github.com/andre-rosa))
- Remove ROS 2 index, since it is now part of the conventional one. [\#165](https://github.com/ros-infrastructure/superflore/pull/165) ([allenh1](https://github.com/allenh1))
- Fix maintainer email [\#161](https://github.com/ros-infrastructure/superflore/pull/161) ([allenh1](https://github.com/allenh1))
- Add Crystal Distribution [\#158](https://github.com/ros-infrastructure/superflore/pull/158) ([allenh1](https://github.com/allenh1))
- Support python3\_6 for ROS 1 [\#157](https://github.com/ros-infrastructure/superflore/pull/157) ([concavegit](https://github.com/concavegit))
- Add bionic to stdeb.cfg. [\#156](https://github.com/ros-infrastructure/superflore/pull/156) ([allenh1](https://github.com/allenh1))
- Add bouncy [\#155](https://github.com/ros-infrastructure/superflore/pull/155) ([allenh1](https://github.com/allenh1))
- Add Melodic to list [\#149](https://github.com/ros-infrastructure/superflore/pull/149) ([allenh1](https://github.com/allenh1))
- Even more utils tests [\#148](https://github.com/ros-infrastructure/superflore/pull/148) ([allenh1](https://github.com/allenh1))
- Create a way to get the log from the docker container. [\#147](https://github.com/ros-infrastructure/superflore/pull/147) ([allenh1](https://github.com/allenh1))
- Add CacheManager tests. [\#145](https://github.com/ros-infrastructure/superflore/pull/145) ([allenh1](https://github.com/allenh1))
- Adding coverage for exceptions.py [\#144](https://github.com/ros-infrastructure/superflore/pull/144) ([shaneallcroft](https://github.com/shaneallcroft))
- Add tests for PackageMetadata.py. [\#143](https://github.com/ros-infrastructure/superflore/pull/143) ([allenh1](https://github.com/allenh1))
- Add tests for TempfileManager [\#142](https://github.com/ros-infrastructure/superflore/pull/142) ([allenh1](https://github.com/allenh1))
- Added tests for parser.py. [\#140](https://github.com/ros-infrastructure/superflore/pull/140) ([allenh1](https://github.com/allenh1))
- Added tests for generate\_installers function. [\#136](https://github.com/ros-infrastructure/superflore/pull/136) ([allenh1](https://github.com/allenh1))
- Be My Ardent-tine [\#135](https://github.com/ros-infrastructure/superflore/pull/135) ([allenh1](https://github.com/allenh1))
- Centralize Duplicate Code [\#134](https://github.com/ros-infrastructure/superflore/pull/134) ([allenh1](https://github.com/allenh1))
- Add stdeb.cfg [\#133](https://github.com/ros-infrastructure/superflore/pull/133) ([allenh1](https://github.com/allenh1))
- Use GitHub api instead of the Git Pull Request module [\#132](https://github.com/ros-infrastructure/superflore/pull/132) ([allenh1](https://github.com/allenh1))
- Add --dry-run and --pr-only to Open Embedded [\#131](https://github.com/ros-infrastructure/superflore/pull/131) ([allenh1](https://github.com/allenh1))
- Adding patch file support for Open Embedded. [\#129](https://github.com/ros-infrastructure/superflore/pull/129) ([allenh1](https://github.com/allenh1))
- Add `--upstream-repo` argument [\#128](https://github.com/ros-infrastructure/superflore/pull/128) ([allenh1](https://github.com/allenh1))

**Fixed bugs:**

- Commit Message for Updates Reads ROS-'None' [\#195](https://github.com/ros-infrastructure/superflore/issues/195)
- generate\_installers\(\) may record a failure in gen\_pkg\_func\(\) as success [\#186](https://github.com/ros-infrastructure/superflore/issues/186)
- Option args.all doesn't add all modified files to the commit/PR [\#183](https://github.com/ros-infrastructure/superflore/issues/183)
- Multi-License Line Fix [\#117](https://github.com/ros-infrastructure/superflore/issues/117)
- Regression: --only flag without --output-repository-path [\#85](https://github.com/ros-infrastructure/superflore/issues/85)
- Docker First Run Behavior [\#68](https://github.com/ros-infrastructure/superflore/issues/68)
- Fix ros-None in Gentoo Commit Messages [\#196](https://github.com/ros-infrastructure/superflore/pull/196) ([allenh1](https://github.com/allenh1))
- Check missing dependencies before checking preserve\\_existing [\#194](https://github.com/ros-infrastructure/superflore/pull/194) ([andre-rosa](https://github.com/andre-rosa))
- Fix gen\\_pkg\\_func failure not being recorded by generate\\_installers [\#187](https://github.com/ros-infrastructure/superflore/pull/187) ([andre-rosa](https://github.com/andre-rosa))
- Fix args.all handling [\#182](https://github.com/ros-infrastructure/superflore/pull/182) ([andre-rosa](https://github.com/andre-rosa))
- Fix small syntax issue [\#174](https://github.com/ros-infrastructure/superflore/pull/174) ([allenh1](https://github.com/allenh1))
- Fix lack of command text in PR's. [\#150](https://github.com/ros-infrastructure/superflore/pull/150) ([allenh1](https://github.com/allenh1))
- Even more utils tests [\#148](https://github.com/ros-infrastructure/superflore/pull/148) ([allenh1](https://github.com/allenh1))
- Fix a typo blocking the Gentoo ebuild from working appropriately. [\#139](https://github.com/ros-infrastructure/superflore/pull/139) ([allenh1](https://github.com/allenh1))
- Add test for ros-infrastructure/superflore\\#117. [\#118](https://github.com/ros-infrastructure/superflore/pull/118) ([allenh1](https://github.com/allenh1))
- Fix existing version detection. [\#103](https://github.com/ros-infrastructure/superflore/pull/103) ([allenh1](https://github.com/allenh1))
- Fix an issue with the dockerfile. [\#101](https://github.com/ros-infrastructure/superflore/pull/101) ([allenh1](https://github.com/allenh1))
- Add public domain license [\#87](https://github.com/ros-infrastructure/superflore/pull/87) ([allenh1](https://github.com/allenh1))

**Closed issues:**

- Recent Gentoo generations aren't listing missing dependencies [\#193](https://github.com/ros-infrastructure/superflore/issues/193)
- Sometimes a transient XML download failure aborts generation [\#188](https://github.com/ros-infrastructure/superflore/issues/188)
- Melodic qt\_metapackages cannot be generated [\#184](https://github.com/ros-infrastructure/superflore/issues/184)
- Add `--dry-run` and `--pr-only` to Open Embedded [\#130](https://github.com/ros-infrastructure/superflore/issues/130)
- Patch file support OpenEmbedded [\#110](https://github.com/ros-infrastructure/superflore/issues/110)

**Merged pull requests:**

- Retry XML downloads [\#189](https://github.com/ros-infrastructure/superflore/pull/189) ([andre-rosa](https://github.com/andre-rosa))
- Pass along unknown licenses unclassified [\#185](https://github.com/ros-infrastructure/superflore/pull/185) ([andre-rosa](https://github.com/andre-rosa))
- Inform that --only option also requires setting --ros-distro [\#179](https://github.com/ros-infrastructure/superflore/pull/179) ([andre-rosa](https://github.com/andre-rosa))
- Rename superflore-gen-meta-pkgs to superflore-gen-oe-recipes [\#178](https://github.com/ros-infrastructure/superflore/pull/178) ([andre-rosa](https://github.com/andre-rosa))
- Rename regenerate\_installer to regenerate\_pkg [\#177](https://github.com/ros-infrastructure/superflore/pull/177) ([andre-rosa](https://github.com/andre-rosa))
- Pass distro to generate\_installer [\#176](https://github.com/ros-infrastructure/superflore/pull/176) ([andre-rosa](https://github.com/andre-rosa))
- Add distro parameter to resolve\_dep [\#173](https://github.com/ros-infrastructure/superflore/pull/173) ([andre-rosa](https://github.com/andre-rosa))
- Reduce distro hardcoding [\#172](https://github.com/ros-infrastructure/superflore/pull/172) ([nuclearsandwich](https://github.com/nuclearsandwich))
- Use index for querying distro information [\#171](https://github.com/ros-infrastructure/superflore/pull/171) ([andre-rosa](https://github.com/andre-rosa))
- Enforce python 3 requirement [\#160](https://github.com/ros-infrastructure/superflore/pull/160) ([cottsay](https://github.com/cottsay))
- Remove shebang and +x from a non-executable [\#159](https://github.com/ros-infrastructure/superflore/pull/159) ([cottsay](https://github.com/cottsay))

## [v0.2.1](https://github.com/ros-infrastructure/superflore/tree/v0.2.1) (2018-01-26)
[Full Changelog](https://github.com/ros-infrastructure/superflore/compare/v0.2.0...v0.2.1)

**Implemented enhancements:**

- Fix CI [\#125](https://github.com/ros-infrastructure/superflore/pull/125) ([allenh1](https://github.com/allenh1))
- Strip the path from the executable name. [\#124](https://github.com/ros-infrastructure/superflore/pull/124) ([allenh1](https://github.com/allenh1))
- Add in test dependencies, enabled by the use flag 'test' [\#123](https://github.com/ros-infrastructure/superflore/pull/123) ([allenh1](https://github.com/allenh1))
- Use allenh1/ros\_gentoo\_base for Docker [\#122](https://github.com/ros-infrastructure/superflore/pull/122) ([allenh1](https://github.com/allenh1))
- More Explicit PRs [\#120](https://github.com/ros-infrastructure/superflore/pull/120) ([allenh1](https://github.com/allenh1))
- Add command line arguments to the PR text. [\#119](https://github.com/ros-infrastructure/superflore/pull/119) ([allenh1](https://github.com/allenh1))
- Add test for ros-infrastructure/superflore\#117. [\#118](https://github.com/ros-infrastructure/superflore/pull/118) ([allenh1](https://github.com/allenh1))
- Gentoo Integration Tests [\#115](https://github.com/ros-infrastructure/superflore/pull/115) ([allenh1](https://github.com/allenh1))
- Add opencv3 check [\#114](https://github.com/ros-infrastructure/superflore/pull/114) ([allenh1](https://github.com/allenh1))
- More utils tests [\#113](https://github.com/ros-infrastructure/superflore/pull/113) ([allenh1](https://github.com/allenh1))
- Add metadata.xml tests. [\#112](https://github.com/ros-infrastructure/superflore/pull/112) ([allenh1](https://github.com/allenh1))
- Docker tests [\#111](https://github.com/ros-infrastructure/superflore/pull/111) ([allenh1](https://github.com/allenh1))
- Add `--only \[pkg\_1\] \[pkg\_2\] ... \[pkg\_n\]` [\#109](https://github.com/ros-infrastructure/superflore/pull/109) ([allenh1](https://github.com/allenh1))

**Fixed bugs:**

- Multi-License Line Fix [\#117](https://github.com/ros-infrastructure/superflore/issues/117)
- Add test for ros-infrastructure/superflore\\#117. [\#118](https://github.com/ros-infrastructure/superflore/pull/118) ([allenh1](https://github.com/allenh1))

## [v0.2.0](https://github.com/ros-infrastructure/superflore/tree/v0.2.0) (2017-12-28)
[Full Changelog](https://github.com/ros-infrastructure/superflore/compare/v0.1.0...v0.2.0)

**Implemented enhancements:**

- Move some packages to DEPEND [\#83](https://github.com/ros-infrastructure/superflore/issues/83)
- Create a `tar-archive-dir` to clean up the `.tar` files downloaded for Open Embedded [\#80](https://github.com/ros-infrastructure/superflore/issues/80)
- Replace custom Docker class with upstream docker library [\#66](https://github.com/ros-infrastructure/superflore/issues/66)
- ROS-distribution specific branches for Open Embedded [\#107](https://github.com/ros-infrastructure/superflore/pull/107) ([allenh1](https://github.com/allenh1))
- Add checksum cache for Open Embedded [\#102](https://github.com/ros-infrastructure/superflore/pull/102) ([allenh1](https://github.com/allenh1))
- Dynamically update copyright year & handle multiple licenses for Open Embedded [\#100](https://github.com/ros-infrastructure/superflore/pull/100) ([shaneallcroft](https://github.com/shaneallcroft))
- Add `--only PKG` option [\#76](https://github.com/ros-infrastructure/superflore/pull/76) ([allenh1](https://github.com/allenh1))

**Fixed bugs:**

- Regression: --only flag without --output-repository-path [\#85](https://github.com/ros-infrastructure/superflore/issues/85)
- Fix existing version detection. [\#103](https://github.com/ros-infrastructure/superflore/pull/103) ([allenh1](https://github.com/allenh1))
- Fix an issue with the dockerfile. [\#101](https://github.com/ros-infrastructure/superflore/pull/101) ([allenh1](https://github.com/allenh1))
- Add public domain license [\#87](https://github.com/ros-infrastructure/superflore/pull/87) ([allenh1](https://github.com/allenh1))

**Merged pull requests:**

- Make generated ebuild copyright dynamic [\#91](https://github.com/ros-infrastructure/superflore/pull/91) ([shaneallcroft](https://github.com/shaneallcroft))
- Drop python 2 support [\#90](https://github.com/ros-infrastructure/superflore/pull/90) ([allenh1](https://github.com/allenh1))



\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*
