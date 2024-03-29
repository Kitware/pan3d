# CHANGELOG



## v0.5.1 (2024-03-22)

### Fix

* fix(examples): Update example notebooks with catalogs argument ([`8d21be7`](https://github.com/Kitware/pan3d/commit/8d21be779c19da8c9c176f4f97842e0a585093a2))

### Unknown

* Merge pull request #71 from Kitware/fix-examples

Update example notebooks with catalogs argument ([`01ee2be`](https://github.com/Kitware/pan3d/commit/01ee2bec06cda8a18c5f11870a7b7a41932b82be))


## v0.5.0 (2024-03-20)

### Feature

* feat: Add value checking on DatasetBuilder setters ([`fb97573`](https://github.com/Kitware/pan3d/commit/fb97573b154d718a533c55f979807aa7f4bb2172))

### Fix

* fix: Set DatasetBuilder slicing to None when DatasetViewer coordinates are blank ([`38de031`](https://github.com/Kitware/pan3d/commit/38de03182da22932b1b838737459652bee7a752a))

### Refactor

* refactor: apply suggested change from review ([`5f50f0f`](https://github.com/Kitware/pan3d/commit/5f50f0fc6933a64ba02249514e0150bf121d2acf))

### Test

* test(builder): Add test to cover invalid values to DatasetBuilder setters ([`b08eff2`](https://github.com/Kitware/pan3d/commit/b08eff2a800d4f8264f201d367d647889301071f))

### Unknown

* Merge pull request #70 from Kitware/builder-unexpected-inputs

Validate inputs to DatasetBuilder setters ([`977d1c0`](https://github.com/Kitware/pan3d/commit/977d1c034141736992677ed9e2c3e00e992c597e))


## v0.4.1 (2024-03-15)

### Documentation

* docs: update docs images ([`3ad51b6`](https://github.com/Kitware/pan3d/commit/3ad51b6f0cc17b1de906333f2b5a8d6527a9315a))

* docs: add new tutorial page for catalog search dialog ([`8f00699`](https://github.com/Kitware/pan3d/commit/8f006996817d6ddc775c8e4db518b58fb0df4e6c))

* docs: adjust existing pages to catalogs changes ([`94f1f77`](https://github.com/Kitware/pan3d/commit/94f1f773c6b57f4648d16364b0f55e2b811d1612))

### Fix

* fix: prevent name conflict by renaming catalogs module import ([`72ca343`](https://github.com/Kitware/pan3d/commit/72ca343c90132105a8d0885578f03d3840205999))

* fix: add catalogs folder to setuptools packages list ([`4edb6c3`](https://github.com/Kitware/pan3d/commit/4edb6c3c281a4f357e877215f6d75b4980308e45))

* fix: prevent &#34;NoneType is not iterable&#34; error in Pangeo search by ID ([`27873e8`](https://github.com/Kitware/pan3d/commit/27873e8f14f43821c68ef56be6fbf8a5acd1f68b))

### Refactor

* refactor(catalogs): create base methods in catalogs module that dynamically import relevant submodules ([`9bb4cfd`](https://github.com/Kitware/pan3d/commit/9bb4cfdb065ac676a7ac12cb9777706161b56794))

* refactor: move `call_catalog_function` to `pan3d.catalogs.__init__.py` ([`0cc5c57`](https://github.com/Kitware/pan3d/commit/0cc5c578b33a48fbe4968f9f147e61f81cb0152f))

* refactor: move catalog modules to new `pan3d/catalogs` folder ([`75a1deb`](https://github.com/Kitware/pan3d/commit/75a1debdd4e1497e97c9c429662736fc96076f28))

### Style

* style: reformat with black ([`627c41a`](https://github.com/Kitware/pan3d/commit/627c41a29b31cbf55cc94a04ef1d75d23305cadb))

### Unknown

* Merge pull request #69 from Kitware/catalog-docs

Catalog Docs ([`6f946b1`](https://github.com/Kitware/pan3d/commit/6f946b14c02c2334c327fbb278cc36f5ddca79e2))

* setup(install): add `all` requirements group ([`86d19d1`](https://github.com/Kitware/pan3d/commit/86d19d129439582f084e4f4305591a5730b28d62))


## v0.4.0 (2024-03-08)

### Feature

* feat: add `viewer` kwarg to Builder constructor to instantiate Viewer ([`a2ed1f4`](https://github.com/Kitware/pan3d/commit/a2ed1f4423e5a78c798ab5668d4c4148efd700d3))

### Fix

* fix: guard against a None `catalogs` value in `DatasetViewer` constructor ([`6898faf`](https://github.com/Kitware/pan3d/commit/6898fafaa88cf61401bf3a206ba15feaf505d59c))

* fix: reset search and message when catalog changes ([`9c65ad3`](https://github.com/Kitware/pan3d/commit/9c65ad3fb074e0b556fbe50b84d9afb51229b367))

* fix: reduce sleep time in `run_as_async` ([`a1d0904`](https://github.com/Kitware/pan3d/commit/a1d09044bc3c9be0dafccfff09e9f0dd58f83606))

* fix: Use try-catch for catalog module imports ([`e820d80`](https://github.com/Kitware/pan3d/commit/e820d8084596b80c231f817b3938518f229a2783))

### Refactor

* refactor: remove class-checking for specific pangeo catalog errors (avoid importing auxiliary libraries directly) ([`066f8e6`](https://github.com/Kitware/pan3d/commit/066f8e6ef584573ab52139a169d357eaf9c48e72))

* refactor: replace branching if logic for catalogs with `builder._call_catalog_function` ([`0d37c51`](https://github.com/Kitware/pan3d/commit/0d37c5161ba190afdd20a7231e70ae105c758d83))

* refactor: use catalogs list kwarg instead of multiple boolean catalog flags ([`36683c2`](https://github.com/Kitware/pan3d/commit/36683c226871adcb2d6da6dc9792177390ac21f8))

* refactor: separate default load dataset function for paths and urls ([`de7da40`](https://github.com/Kitware/pan3d/commit/de7da401c1168aab528270ca75cbcdadf9db192c))

### Style

* style: reformat with black ([`84e2ffd`](https://github.com/Kitware/pan3d/commit/84e2ffd51da3fac58cae3d808ffb65858ea600f4))

* style: remove print statement ([`9c893a1`](https://github.com/Kitware/pan3d/commit/9c893a1abd4812320770177ac71c7d98ab45da5d))

* style: fix automatic formatting of list by removing comma ([`2be407c`](https://github.com/Kitware/pan3d/commit/2be407cd60a2818d990443271416b24aee94f34c))

### Unknown

* Merge pull request #67 from Kitware/esgf-data

Catalog modules: Pangeo &amp; ESGF data ([`0208640`](https://github.com/Kitware/pan3d/commit/0208640315e0e34ef0d366b033871b8dd2d39fb1))

* Merge branch &#39;main&#39; into esgf-data ([`23d5474`](https://github.com/Kitware/pan3d/commit/23d547442daed98013fe1b3d76ccac4ceae67e5d))


## v0.3.1 (2024-03-01)

### Documentation

* docs: update examples ([`ed3f200`](https://github.com/Kitware/pan3d/commit/ed3f200cf7713c834a6d1b5acc2eb450531d65e2))

### Feature

* feat: implement Pangeo module functions using intake ([`6dd201f`](https://github.com/Kitware/pan3d/commit/6dd201f99e4c67c02f8fa0a507f3242b4d50a90f))

* feat: add a catalog search dialog ([`3bd0d95`](https://github.com/Kitware/pan3d/commit/3bd0d955edea731afa6de30657079e4214aa0bc1))

### Fix

* fix: update binder requirements.txt ([`aaa890d`](https://github.com/Kitware/pan3d/commit/aaa890d6a6d9ec0d4cda8e4398346f830869e68e))

* fix: use correct exception imports in `pangeo_forge.py` ([`395ff46`](https://github.com/Kitware/pan3d/commit/395ff465712261a00b5e1eaae96ffbf943a7070b))

* fix: remove unnecessary values from exported state ([`6a86276`](https://github.com/Kitware/pan3d/commit/6a862763abb9eefb4778c7b65efd25fb681848d5))

* fix: loading and error states should be handled only by `run_as_async` method ([`56f36a6`](https://github.com/Kitware/pan3d/commit/56f36a6dacb1d54118be7c8d27e3945cf4a2c623))

* fix: improve compatibility with more pangeo datasets with timedelta dtypes ([`b94a0fd`](https://github.com/Kitware/pan3d/commit/b94a0fda08ca2b93a0888adfa4d45283ceeaf1c0))

* fix: consolidate asynchronous viewer behavior with helper function `run_as_async` ([`adfe751`](https://github.com/Kitware/pan3d/commit/adfe75171393d9c1c211209fc9421ab4d93fa1c4))

* fix: Update Builder and Viewer to use Pangeo module ([`4171046`](https://github.com/Kitware/pan3d/commit/41710461fb5c5393db2b03dfa696f1288fbf830f))

* fix: add missing parenthesis in async callback ([`0cebdd5`](https://github.com/Kitware/pan3d/commit/0cebdd5c1d644b123c724bbedc3a88d061a9d794))

### Style

* style: reformatting with black ([`b1cf493`](https://github.com/Kitware/pan3d/commit/b1cf493d3f21b641f09c5952b8160a86f6796136))

* style: update style via black ([`6ba5d00`](https://github.com/Kitware/pan3d/commit/6ba5d00b4b8e899e540b8c46b04dd632da9f4606))

### Unknown

* Merge pull request #68 from Kitware/binder-reqs

Update Binder Requirements ([`f10dec3`](https://github.com/Kitware/pan3d/commit/f10dec33249228db876aad86c283465f9104b50c))

* tests: remove check for loading state in export ([`0fd8a8d`](https://github.com/Kitware/pan3d/commit/0fd8a8d4c70be117caedaa79b7db35ef5ba56ffe))

* ui: Adjustments to main drawer and catalog search components ([`b8c63b1`](https://github.com/Kitware/pan3d/commit/b8c63b187ca86f6674427290605653fbd3b71f20))

* setup: Add Pangeo section to optional dependencies ([`0eb185b`](https://github.com/Kitware/pan3d/commit/0eb185b42fa576f543f4684cdffcb1db27f56e32))

* wip: update Pangeo module with congruent API to ESGF module; functions still need implementation ([`b825f70`](https://github.com/Kitware/pan3d/commit/b825f70dcdf7c6031389725061bf186203c6bcbe))

* wip: update Pangeo module; needs catalog search functions ([`4b82c45`](https://github.com/Kitware/pan3d/commit/4b82c451c130c9eaf857f37fc37644716e2f8e19))


## v0.3.0 (2024-02-21)

### Documentation

* docs: add example config file with ESGF dataset ([`6adc7f5`](https://github.com/Kitware/pan3d/commit/6adc7f5ea7a6ff473d43fd81965b3b867857f4df))

* docs: Add `site` to .gitignore ([`cafc96e`](https://github.com/Kitware/pan3d/commit/cafc96ef76f0b303cf14e60df7423baa41d6e4a9))

* docs: Improve language in tutorial pages

Co-authored by: @johnkit ([`effbc94`](https://github.com/Kitware/pan3d/commit/effbc944d613a80c17e2db5ac66e831123339759))

* docs: update tutorials and other descriptive documentation ([`11e5ec7`](https://github.com/Kitware/pan3d/commit/11e5ec72fab28da9cf646e8477effa546213d02b))

* docs: update image folder (stored with lfs) ([`c63ec8e`](https://github.com/Kitware/pan3d/commit/c63ec8ea7300c81c7d56c92fad464a94071c7023))

* docs: update docstrings for API docs pages ([`7332c35`](https://github.com/Kitware/pan3d/commit/7332c352827bcceda542fbe066b7cb4bd2443913))

* docs: Add two new example jupyter notebooks ([`c09fd06`](https://github.com/Kitware/pan3d/commit/c09fd068c2481f7e40c7571d9fdca71996c33e29))

* docs: update existing jupyter notebook examples ([`63ae602`](https://github.com/Kitware/pan3d/commit/63ae6021142fd53958b113ee0c346f43fd010164))

* docs: replace &#34;active&#34; with &#34;name&#34; in config schema ([`e9758d7`](https://github.com/Kitware/pan3d/commit/e9758d773c6ff12d6e417b739a9cf0b71a4b7c58))

### Feature

* feat: add group selector to UI in `main_drawer` ([`7b580b5`](https://github.com/Kitware/pan3d/commit/7b580b5008055cdb107bbfed7ff9570940605ef8))

* feat: add `--esgf` argument to `pan3d-viewer` ([`78cf8df`](https://github.com/Kitware/pan3d/commit/78cf8df89027ff2703a216f374fc55645ddb3001))

* feat: add esgf module, which uses intake-esgf ([`b57b0a4`](https://github.com/Kitware/pan3d/commit/b57b0a49027ce091a5b45c0cb636e7021c42434f))

* feat: add automatic rendering, enabled by default ([`4f20e39`](https://github.com/Kitware/pan3d/commit/4f20e397fa83838f301fb1e95a16cfbf6fbf1ea4))

* feat: more extensive automatic coordinate selection ([`e3a54cc`](https://github.com/Kitware/pan3d/commit/e3a54ccd2968bcdda706a22e7b7babdee485e50d))

* feat: add more xarray examples to default dataset list ([`f533334`](https://github.com/Kitware/pan3d/commit/f5333343e3d1388c13e1cf00dacdff7fd58283ad))

### Fix

* fix: protect against NoSearchResults exceptions from intake_esgf ([`09687f7`](https://github.com/Kitware/pan3d/commit/09687f75b4895975bf5f06f0e00dc5378222f9c6))

* fix: remove broken pangeo-forge links from catalog ([`bcec69e`](https://github.com/Kitware/pan3d/commit/bcec69e66e7bdcd6f70a76b6c73cdedc110b6fa3))

* fix: improve usability of import via UI ([`7eea64b`](https://github.com/Kitware/pan3d/commit/7eea64ba8f6d135781732cfdbf91f066de6fc8ca))

* fix: wait until server ready before enabling auto rendering ([`2bceade`](https://github.com/Kitware/pan3d/commit/2bceade7c915f2f6b553f0442559268a0e112f5a))

* fix: synchronize slicing state between builder and viewer ([`e6e6421`](https://github.com/Kitware/pan3d/commit/e6e6421b40ff85026a9f1ee85fd1db29ebe98b82))

* fix: assign coordinates on implicitly indexed data arrays before sending to algorithm ([`b554d4d`](https://github.com/Kitware/pan3d/commit/b554d4de39e26065fd48f6c26b24c78a0e33dc6f))

* fix: asynchronous trame state updates ([`7152037`](https://github.com/Kitware/pan3d/commit/7152037c383711a144e7121482b73cd7b515835e))

* fix: state synchronization between builder and viewer ([`68bdfae`](https://github.com/Kitware/pan3d/commit/68bdfaebaed0001524452ae5274094ea802d4713))

* fix(threading): use `call_soon_threadsafe` for plotting mesh ([`9b2d652`](https://github.com/Kitware/pan3d/commit/9b2d652cdce75be01067effde36a3512b036d1c1))

### Refactor

* refactor: replace `dataset_path` with `dataset_info`;  value for `source` can determine which `load_dataset` method to use ([`c324ba4`](https://github.com/Kitware/pan3d/commit/c324ba41b175d6c74523d1e2ddf0b8ea514d1d53))

* refactor(pangeo): use methods similar to esgf module ([`bbd6b84`](https://github.com/Kitware/pan3d/commit/bbd6b8495c8aa7bb35718be9f89b486612ba0748))

* refactor: suggested changes from @jourdain ([`b87a945`](https://github.com/Kitware/pan3d/commit/b87a9450a989c0c672d41afe7d852b030323d219))

* refactor(dataset_builder): separate trame and plotting from data configuration ([`bfb64be`](https://github.com/Kitware/pan3d/commit/bfb64bee8cfe34b2ee32a21e4dbadde302f63f85))

### Style

* style: Reformat with black ([`9a83c4f`](https://github.com/Kitware/pan3d/commit/9a83c4faeb2000dd5822546ab0b2fcaa8243b783))

* style: Reformat with black ([`42ecfd4`](https://github.com/Kitware/pan3d/commit/42ecfd4fab7b929fa9ba37d2ac388aaa03773f26))

* style: fix formatting ([`27fd178`](https://github.com/Kitware/pan3d/commit/27fd1784190bff1f6274372315673640b8ffbb23))

* style: fix formatting ([`068865d`](https://github.com/Kitware/pan3d/commit/068865d22e1eae780bd31287707f6b4d7a816e01))

* style: fix formatting ([`8a45de4`](https://github.com/Kitware/pan3d/commit/8a45de4b7d1d3b66c4b33c13d89fcd5c791c76dc))

* style(css): hide scroll bar by default ([`e4d32e9`](https://github.com/Kitware/pan3d/commit/e4d32e9a0827b4e28cd2440f9085e5edccd90b8e))

### Test

* test: update tests with `dataset_info` values instead of `dataset_path` values ([`68bf50b`](https://github.com/Kitware/pan3d/commit/68bf50bca28abacc34d6a3d6e19bb57a562af250))

* test: update expected state with new default expanded coordinates ([`61bcff5`](https://github.com/Kitware/pan3d/commit/61bcff51ee2c0414e7013dead5ba975d98773d06))

* test: update expected state with new drawer defaults ([`7e5c5c7`](https://github.com/Kitware/pan3d/commit/7e5c5c7898f58b179926376635de9a880846b519))

* test: disable `DatasetViewer` automatic render in tests ([`dee418e`](https://github.com/Kitware/pan3d/commit/dee418e3aebe68727ba8cb81075773349e3b3863))

* test: update main testing workflow ([`de68b49`](https://github.com/Kitware/pan3d/commit/de68b4901681ce61c2e3829be0807954ae2bb396))

* test: add tests for builder and viewer ([`9e305d4`](https://github.com/Kitware/pan3d/commit/9e305d427de2b6ba72cd6f26428fb0efe4a19a34))

### Unknown

* Merge pull request #59 from Kitware/separate-viewer

Separate DatasetViewer from DatasetBuilder ([`f89d2b0`](https://github.com/Kitware/pan3d/commit/f89d2b0feaf2a4a7888a3fbc5a2d7551ebb2d27c))

* More doc changes

* Change title from &#34;local server to a more general &#34;command line&#34;
* Change pip instruction to include [viewer]
* Show more code in jupyter_notebook.md
* Also fix mkdocs warning in dataset_viewer.py ([`f74dada`](https://github.com/Kitware/pan3d/commit/f74dadacfd407afbbff172b3c0a352079fb4a162))

* setup: specify minimum versions for requirements in pyproject.toml ([`612d42d`](https://github.com/Kitware/pan3d/commit/612d42ddecdeb770c43e872d3dbaf5454fc1a807))

* ui: change loading widget style ([`32b4a2b`](https://github.com/Kitware/pan3d/commit/32b4a2b65d4bc4bcfb17ce372f939b949d14c310))

* ui: Differentiate between icons for menus and drawers on the left and right sides ([`50bfd92`](https://github.com/Kitware/pan3d/commit/50bfd92ab5867cc9689cb40c3d2167d9ea1317f6))

* setup: move trame dependencies to [viewer] option ([`b243779`](https://github.com/Kitware/pan3d/commit/b2437794f4bbd41193af618fa656547fcf2ef9f5))


## v0.2.3 (2024-01-17)

### Fix

* fix(docs): fix README badge rendering on GH ([`6a65a49`](https://github.com/Kitware/pan3d/commit/6a65a49e85e994a54e9fd2e026d9ff0ad9a04514))


## v0.2.2 (2024-01-16)

### Documentation

* docs: Add mesh edges screenshot to viewer tutorial ([`88be0ce`](https://github.com/Kitware/pan3d/commit/88be0cedd4454909b6a58938288f5b21fb972c5f))

* docs: improve Pangeo Forge examples ([`15d0c4e`](https://github.com/Kitware/pan3d/commit/15d0c4ec55a859b982d93151ba1cf503e3bf8f40))

* docs: Update current time in description for updated screenshot ([`9b5814a`](https://github.com/Kitware/pan3d/commit/9b5814a546a7bf41b93e4898e02feed1502ebc65))

* docs: Add descriptors for what each axis represents ([`61ee428`](https://github.com/Kitware/pan3d/commit/61ee4282f4b4d2f3c30216cdc2fd030236fb230f))

* docs: Add configuration for readthedocs ([`c2c1e37`](https://github.com/Kitware/pan3d/commit/c2c1e379518c974b3bef2eb1144249f51b46942d))

* docs: fill API documentation pages ([`b261649`](https://github.com/Kitware/pan3d/commit/b261649996cae25695d910dee915ff4cf3432055))

* docs: Add typing and docstrings to dataset_builder.py ([`d6d8855`](https://github.com/Kitware/pan3d/commit/d6d88556e9272588e5f99cebf1c25b5e29347087))

### Fix

* fix: use true min and max for default slicing ([`8965827`](https://github.com/Kitware/pan3d/commit/8965827b591de491144617c41c78e66c48796c07))

* fix: use relative path for pangeo datasets JSON ([`6d9d9e9`](https://github.com/Kitware/pan3d/commit/6d9d9e9bdd46bc03261784081cb5c5b7e5034679))

* fix: update test expected size for updated example file ([`81d4601`](https://github.com/Kitware/pan3d/commit/81d460128cf7a5a79195cd5a817328eee3c581a4))

* fix: change pyvista StructuredGrid reference ([`d917fd0`](https://github.com/Kitware/pan3d/commit/d917fd07754ab7480eec48ece58e001a7bd92d17))

* fix(DatasetBuilder): typing adjustments ([`aa5dbc8`](https://github.com/Kitware/pan3d/commit/aa5dbc87edb31c90529218b433aa876d09299801))

### Refactor

* refactor: add lfs images ([`0256f52`](https://github.com/Kitware/pan3d/commit/0256f52e420412685cadba41e5fea280e07c8f5d))

* refactor: store docs images with git-lfs ([`7d0d776`](https://github.com/Kitware/pan3d/commit/7d0d77676527b5131e2c81c325a3d378b297b33c))

* refactor: remove docs images (to be stored with git-lfs) ([`b63799d`](https://github.com/Kitware/pan3d/commit/b63799d88d70fdc76ecdbe697d0a7a9d907c25f6))

### Style

* style: Use black to fix styling ([`fd4f265`](https://github.com/Kitware/pan3d/commit/fd4f265d4882d36f373de1b5932bcea3d2f64d31))

* style: replace 2 tutorial images with rotated worlds ([`872d693`](https://github.com/Kitware/pan3d/commit/872d693130e9d795d7c185d38ebf7b818d8ccc32))

* style: Use black to fix styling ([`07ce042`](https://github.com/Kitware/pan3d/commit/07ce042b86d55698aaf85b6f765f923f1db6edbe))

* style: switch cover image in README ([`ef01699`](https://github.com/Kitware/pan3d/commit/ef01699b22b30885426ec3bf6f7a4eaf725e252a))

* style: Use black to fix styling ([`965c11c`](https://github.com/Kitware/pan3d/commit/965c11c731021abcbf7f19f1acf73e5dd4980317))

### Unknown

* Merge pull request #47 from Kitware/docs-and-tutorials

Docs and tutorials ([`b33ae78`](https://github.com/Kitware/pan3d/commit/b33ae784ad8abfeaa19ead97441239ce646669c5))

* Merge branch &#39;main&#39; into docs-and-tutorials ([`4876d7c`](https://github.com/Kitware/pan3d/commit/4876d7c8ad0ba17b4bfe280eb78f6c99049dc8ec))


## v0.2.1 (2023-12-14)

### Build

* build: require trame-vtk&gt;=2.6.3 ([`8a117b5`](https://github.com/Kitware/pan3d/commit/8a117b56d4866385f5f3f12e5ccb52556a73e861))

### Fix

* fix: always use `push_camera` instead of `reset_camera` ([`8f963ff`](https://github.com/Kitware/pan3d/commit/8f963ff9c11a68d51ffbf87a287ecb88eed754a6))

* fix: use `push_camera` instead of `reset_camera` in cloud mode ([`780c9d5`](https://github.com/Kitware/pan3d/commit/780c9d547ab9e8cf09f98d6923948de781585ba9))

### Refactor

* refactor: rename `force_local_rendering` to `has_gpu_rendering` and negate result ([`094c3bc`](https://github.com/Kitware/pan3d/commit/094c3bc80ec74777fbd3ec35a92a6299f575a126))

* refactor: rename `_cloud` to `_force_local_rendering` ([`033505b`](https://github.com/Kitware/pan3d/commit/033505bd41f1a3067cf3c42cc846c271ea3baaa5))

### Unknown

* Merge pull request #48 from Kitware/client-rendering-fixes

Client rendering fixes ([`8f13280`](https://github.com/Kitware/pan3d/commit/8f13280c6f34229257b21fa2b847f42283599b76))


## v0.2.0 (2023-12-13)

### Build

* build: use BINDER_REQUEST instead of JUPYTERHUB_BASE_URL to determine whether env is in Binder ([`de5317c`](https://github.com/Kitware/pan3d/commit/de5317c91f5f5418709456678e4710f997ea7414))

* build(binder): try local pan3d install ([`29e6af3`](https://github.com/Kitware/pan3d/commit/29e6af311e2561b2db77c83b841f6f550b873dea))

* build: remove apt.txt ([`3fa4217`](https://github.com/Kitware/pan3d/commit/3fa4217d7520c311de66d1efdc1254a6828bbeeb))

* build: move binder configuration to .binder, use postBuild script instead of start ([`efcfd2e`](https://github.com/Kitware/pan3d/commit/efcfd2ece7256bf303d9f555f93fccfbc3fae622))

* build: try without xvfb, use vtk-osmesa ([`caead90`](https://github.com/Kitware/pan3d/commit/caead90d56072139987af5157e441fb73c0502d8))

* build: remove vtk-osmesa installation, use xvfb ([`1b9c1b8`](https://github.com/Kitware/pan3d/commit/1b9c1b87583e9b2e3ac477a957daab02ffb8a336))

* build: remove which Xvfb command

Co-authored-by: Zach Mullen &lt;zach.mullen@kitware.com&gt; ([`99da410`](https://github.com/Kitware/pan3d/commit/99da4103640bbdc544705506e02dd3787cf9168a))

* build: add binder start script from pyvista docs ([`ab51a64`](https://github.com/Kitware/pan3d/commit/ab51a64756c59ec92cf9d17e2ccb914eacbd4c65))

* build: add xvfb to system requirements ([`e79653e`](https://github.com/Kitware/pan3d/commit/e79653e7a72c21a8622eb4df10ac142e37f06a18))

* build: reformat requirements.txt ([`00a075f`](https://github.com/Kitware/pan3d/commit/00a075f032114a54ff21f96b985f191137e886a0))

* build: move configuration files to top-level binder folder ([`52f2dfe`](https://github.com/Kitware/pan3d/commit/52f2dfe1dbcb3ad2d36b9001ec807be7de74558b))

* build: try binder build without Dockerfile ([`299eb6b`](https://github.com/Kitware/pan3d/commit/299eb6b057aba4d1fc04cb5c2cd40153b96ce697))

* build: add more dependencies to Dockerfile ([`af1ccb5`](https://github.com/Kitware/pan3d/commit/af1ccb504a564e6f862a0171ed14d0adff02f6fd))

* build: switch user back to NB_USER after installation ([`da0a89d`](https://github.com/Kitware/pan3d/commit/da0a89dd09cf529dd41454a05f7a7edd7501407c))

* build: update Dockerfile in examples/jupyter ([`5167759`](https://github.com/Kitware/pan3d/commit/5167759f8e0378a873da733d2f700771dd9391d5))

### Documentation

* docs: add comment to `.binder/requirements.txt` ([`7cff7b0`](https://github.com/Kitware/pan3d/commit/7cff7b0f7742679ac108e3ee91f1cc630d5c8d11))

### Feature

* feat: set rendering mode to client in known cloud jupyter environments ([`10dd413`](https://github.com/Kitware/pan3d/commit/10dd41387fbc830079c8131cf615693b011639e3))

### Fix

* fix: remove defaults on computed attribute values ([`05b0e44`](https://github.com/Kitware/pan3d/commit/05b0e44e9c716299b1b6d831c207f6716ee7e028))

* fix: prevent `auto_select_coordinates` from overwriting `set_data_array_axis_names` results ([`8de4f4a`](https://github.com/Kitware/pan3d/commit/8de4f4a6a2ede0c34a27cf42269ac9f701cb3acf))

* fix: convert more directive attributes to tuple syntax ([`035e229`](https://github.com/Kitware/pan3d/commit/035e229b46fd324cf0d40802d0f150d2442250b6))

* fix: cast keys and values in `da_vars_attrs` to strings ([`a2c1c4b`](https://github.com/Kitware/pan3d/commit/a2c1c4bc6d3690c9bc56ab9f24cc34615b3e5622))

* fix: cast objects to strings in template code ([`0ff5e0b`](https://github.com/Kitware/pan3d/commit/0ff5e0b930a7d56b220e369921365385259a0637))

* fix: stringify axes list for VSelect component ([`615eaed`](https://github.com/Kitware/pan3d/commit/615eaed020e91403828c1348c52e5009eebd4d5e))

### Style

* style: apply changes from black ([`d80f10e`](https://github.com/Kitware/pan3d/commit/d80f10efaab0f1c58621b44368af03cda9bdd842))

### Unknown

* Merge pull request #46 from Kitware/binder-test

More binder configuration improvements ([`f119ffb`](https://github.com/Kitware/pan3d/commit/f119ffb3017343b6935c23a02bcb543fafd7510f))

* ui: collapse pyvista plotter toolbar by default; avoid looking cramped in notebook output ([`e8a6ea2`](https://github.com/Kitware/pan3d/commit/e8a6ea21d414eb481b502d05930a46c8bbef74f1))

* launch: allow --debug argument passed through to server ([`7cf2282`](https://github.com/Kitware/pan3d/commit/7cf22829505d5010ab0f3669bbbeccf64f83b204))

* debug: Add print statement for select component ([`5e8c309`](https://github.com/Kitware/pan3d/commit/5e8c309e151ee0215bc2a6656520983bb094b6f6))

* Merge pull request #45 from Kitware/binder-dockerfile

Binder configuration ([`d8cad54`](https://github.com/Kitware/pan3d/commit/d8cad54c95c85c63b70ae746147effaaf7e82f9f))


## v0.1.2 (2023-12-05)

### Build

* build: remove setuptools-scm, use __version__ in setup.py ([`5da2edf`](https://github.com/Kitware/pan3d/commit/5da2edf0a6a6411359b73c78e84b8c6b17cf034f))

### Ci

* ci: add `contents:write` to permissions in release job ([`a1b2a11`](https://github.com/Kitware/pan3d/commit/a1b2a118e65f87e2f2e386f0dca08545cd4c9046))

* ci: combine build, release, publish jobs into one release job with 3 steps ([`43bfff8`](https://github.com/Kitware/pan3d/commit/43bfff81ca595b69aaadc2e287ba2bdda9041cb6))

* ci: rebuild before PyPI publish ([`4ef460e`](https://github.com/Kitware/pan3d/commit/4ef460e296187d668893b6749a18c56598a7c960))

### Documentation

* docs(setup): update pyproject.toml and MANIFEST.in with README location ([`37deecc`](https://github.com/Kitware/pan3d/commit/37deecca74ba381cb6444fabe76efd30aab57976))

* docs(tutorials): create basic docs navigation and add tutorials ([`e72fd03`](https://github.com/Kitware/pan3d/commit/e72fd03f78ca7bdf69293e8b1f64113909cfdaba))

### Fix

* fix(setup): Add setuptools_scm to pyproject.toml; use git tag for version in build step ([`1cb09a4`](https://github.com/Kitware/pan3d/commit/1cb09a48e9e0ad817f998b658e8681182674ba62))

### Style

* style: prefer double-quotes ([`9dcb236`](https://github.com/Kitware/pan3d/commit/9dcb23601323d2bca4df841978b39ea2d08294d5))

### Unknown

* Merge pull request #44 from Kitware/publish-permissions

Release job permissions ([`132ddb9`](https://github.com/Kitware/pan3d/commit/132ddb98a3b87f78b659e3e3102de15ad430802f))

* Merge pull request #43 from Kitware/build-version

Fix build versioning ([`7429fb3`](https://github.com/Kitware/pan3d/commit/7429fb33568932a164164e5925aa24038bc1b92d))


## v0.1.1 (2023-12-04)

### Documentation

* docs(version): use dynamic version in pyproject.toml ([`3a64c19`](https://github.com/Kitware/pan3d/commit/3a64c198f9d2b075bd0beff22b81065545566902))

### Fix

* fix(requirements): add trame-jupyter-extension to requirements.txt ([`52a38b4`](https://github.com/Kitware/pan3d/commit/52a38b44f95d6cc523eb5cf856e5cad5fa9c7fe6))

* fix(setup): use Dockerfile to specify uninstall of default vtk before install of vtk-osmesa ([`0577cf4`](https://github.com/Kitware/pan3d/commit/0577cf4c5f14dd73bec25bd9162cc09e857d1ffb))

* fix(setup): add vtk-osmesa to examples requirements for binder ([`6cfe167`](https://github.com/Kitware/pan3d/commit/6cfe167d01fedf842bff5b1207d9bd584e8e69fb))

### Unknown

* Merge pull request #42 from Kitware/vtk-osmesa

Add `vtk-osmesa` to requirements for binder ([`7fd6657`](https://github.com/Kitware/pan3d/commit/7fd6657c55ad65d3d12fc03b6593b24ad1894833))

* Merge pull request #41 from Kitware/dynamic-version

Use dynamic version in pyproject.toml ([`8e2be28`](https://github.com/Kitware/pan3d/commit/8e2be28a40a76da1a1c032341e18042d9bcfbe0d))


## v0.1.0 (2023-11-27)

### Build

* build(setup): add MANIFEST.in and include package data ([`ab1bcea`](https://github.com/Kitware/pan3d/commit/ab1bcea571fe23c862b6ad8e045277cc22d6930f))

### Documentation

* docs(cli): Rename `dataset_path` arg to `dataset` ([`35fb509`](https://github.com/Kitware/pan3d/commit/35fb509cd7b63a1bec54927c85597eca20727410))

### Feature

* feat(examples): add notebook demonstrating use of `builder.mesh` with pyvista rendering ([`e7d6d74`](https://github.com/Kitware/pan3d/commit/e7d6d7427fd60c91e8ea69be04e15cbcfa7608a8))

### Fix

* fix(lint): run black ([`9fd1b99`](https://github.com/Kitware/pan3d/commit/9fd1b99510f16b27fd2aacb2268a7e62665453a8))

* fix(examples): update notebooks and add requirements.txt ([`1469cb6`](https://github.com/Kitware/pan3d/commit/1469cb60ced0f2ab7849d7b95c22048195647a79))

* fix(dataset_builder): update export_config and mesh_changed functions ([`340a55f`](https://github.com/Kitware/pan3d/commit/340a55f1ac788e52c0fc67234c71014d55b794fb))

### Test

* test(export): re-export `example_config_xarray.json` ([`3c76898`](https://github.com/Kitware/pan3d/commit/3c76898afb56019c7d81c7e97dde8976377f3c45))

* test(pre-commit): omit changelog from codespell ([`b1e79f8`](https://github.com/Kitware/pan3d/commit/b1e79f87e5598ff6d426a3305d498732bffd7f45))

* test(export): remove time slicing to match exported config ([`84bc6a3`](https://github.com/Kitware/pan3d/commit/84bc6a387b50e4eb0978fdf1001490ceb9425de9))

### Unknown

* Merge pull request #40 from Kitware/packaging

Examples &amp; Packaging ([`762748e`](https://github.com/Kitware/pan3d/commit/762748e0350c883671ab6a26bf26724b14a2218b))


## v0.0.1 (2023-11-17)

### Ci

* ci(pyproject.toml): bump python requirement to 3.7 ([`bffff73`](https://github.com/Kitware/pan3d/commit/bffff73681a051707ed5a100e8e86bebec4a030b))

### Fix

* fix(setup): specify packages list to override automatic packages discovery ([`b6c3c73`](https://github.com/Kitware/pan3d/commit/b6c3c73fed0b6844946aa6882c7d54e2ebb2e724))

* fix(pyproject.toml): escape backslash characters in version pattern ([`8ab1963`](https://github.com/Kitware/pan3d/commit/8ab1963197968eb5d90a154c5ff66adb2bdeb6a1))

* fix(release): add a job to build dist folder ([`f3c1e1d`](https://github.com/Kitware/pan3d/commit/f3c1e1d878402cdcd85a49407c1c12f8e1303b82))

* fix(pyproject.toml): semantic-release v8 does not support setup.cfg ([`67c121b`](https://github.com/Kitware/pan3d/commit/67c121ba049b9e02f668ac51becd24c7fb60a60f))

* fix(changelog): change misspelled word ([`bc772a0`](https://github.com/Kitware/pan3d/commit/bc772a0d14feb5d7690eefccd6b94e3d0670e6cf))

### Refactor

* refactor(setup): delete setup.cfg ([`a59ef67`](https://github.com/Kitware/pan3d/commit/a59ef6764bde3426dae90feee312d18fc22c6927))

### Unknown

* Merge pull request #39 from Kitware/fix-release-job

Fix release job ([`b082319`](https://github.com/Kitware/pan3d/commit/b082319dc6acfaae57f3155c3f33283482dd42cc))


## v0.0.0 (2023-11-16)

### Unknown

* Merge pull request #38 from Kitware/pypi-2

Fix PyPI publishing step in CI ([`81e30bf`](https://github.com/Kitware/pan3d/commit/81e30bf1a7472aaab37695fa90901efbdc2e2b9b))

* Separate PyPI publish from semantic release job ([`31eaf55`](https://github.com/Kitware/pan3d/commit/31eaf55e8f2cb4e38e42c7b27026c70b071c6c9f))

* Merge pull request #35 from Kitware/pypi

Update PyPI publishing ([`aea55d4`](https://github.com/Kitware/pan3d/commit/aea55d4a80af78eaef00b692984498f461fa818e))

* Merge pull request #37 from Kitware/pangeo-compatibility

Pangeo datasets compatibility ([`f8867fe`](https://github.com/Kitware/pan3d/commit/f8867fea55d3c30568226767659755c8a4098bbe))

* Rename mesh-&gt;_mesh, pv_mesh-&gt;mesh ([`75bd691`](https://github.com/Kitware/pan3d/commit/75bd691633ff50bc43447f25c5c53d2475e6cdcd))

* Merge pull request #36 from Kitware/render-options

Add UI panel to change render options ([`d78d110`](https://github.com/Kitware/pan3d/commit/d78d1109424853aa267c22eaf499c597ec591836))

* Merge pull request #34 from Kitware/loading-optimization

Loading optimization ([`aaa7374`](https://github.com/Kitware/pan3d/commit/aaa737456bd444a35a0d633ab9e6c11bcbfd5cbf))

* Remove unused import of `get_catalog` ([`a8ef34f`](https://github.com/Kitware/pan3d/commit/a8ef34f3e3b92d692acfa449341a6e4c6138259d))

* Reformatting by Black ([`a828d05`](https://github.com/Kitware/pan3d/commit/a828d0539ad0d2334202042b0075e0473993fc7e))

* Allow user to view attributes for available arrays ([`fa5e145`](https://github.com/Kitware/pan3d/commit/fa5e1458d7d4c0c04fa8aceb588edbcd75ff18d2))

* Create static list of compatible pangeo forge datasets ([`b8613fa`](https://github.com/Kitware/pan3d/commit/b8613fafdfe77436b000ee6daadc146cafdfc98b))

* Compatibility with more date types ([`398206e`](https://github.com/Kitware/pan3d/commit/398206e2fe822cecee5fa4c06019bc48d876a0d2))

* Fix coordinate and slicing assignments ([`e886dee`](https://github.com/Kitware/pan3d/commit/e886dee96171e10b6b5ae733b53c383c3f54a3f0))

* Move Dataset Attributes to a dialog (sidebar too narrow) ([`bbefcf5`](https://github.com/Kitware/pan3d/commit/bbefcf5c809773fd1350810e05254fc05c470b6b))

* Make time indexing compatible with datetime64 dtypes and more human-readable ([`6237b16`](https://github.com/Kitware/pan3d/commit/6237b16d6ed6e3dbab2bee345db1ed1f8f52b02e))

* Use controller functions instead to reset view ([`d2f8baf`](https://github.com/Kitware/pan3d/commit/d2f8baf773c9a5e68836f96cc45348f1ce20ed0a))

* Lint fixes via Black ([`20cfbf6`](https://github.com/Kitware/pan3d/commit/20cfbf6e81ad7127a9714f37dde40f60b4f7598d))

* Add reset camera call to `plot_mesh` function ([`b3db360`](https://github.com/Kitware/pan3d/commit/b3db3606953ccc9b27191fe9b133b4761476720e))

* Fix imports ([`e5ecb0b`](https://github.com/Kitware/pan3d/commit/e5ecb0ba4acc8524508fee87409e04128464e4a0))

* Black Lint fixes ([`94d320f`](https://github.com/Kitware/pan3d/commit/94d320f1d52ec7c43c3f830714bc960df07965ed))

* Add UI panel to change render options ([`2384b13`](https://github.com/Kitware/pan3d/commit/2384b1361fb24fd4977ed42ceb836c8f0c96def0))

* Fix edge case bugs ([`ef980ec`](https://github.com/Kitware/pan3d/commit/ef980ec0ed3cdaab04409c59dc49ed42130c9752))

* Update CI action to publish on PyPI ([`63899be`](https://github.com/Kitware/pan3d/commit/63899be9a3f0c993d7825bb94809f8f4957e25bf))

* Change expected size for sliced array in test_import_config ([`65ceb6f`](https://github.com/Kitware/pan3d/commit/65ceb6f0c3a4cc3a4b6daf33dceab9923194fb50))

* Reduce redundant algorithm modifications (&amp; therefore repeated slice computations) ([`49a05ea`](https://github.com/Kitware/pan3d/commit/49a05ea936d765ffcf58ae29c681cb0ba7c9b4c7))

* Remove time printouts ([`bbe639d`](https://github.com/Kitware/pan3d/commit/bbe639df168ee626e05ab6b29e2eb04ad212dd44))

* Access mesh by property on algorithm, not compute function ([`b21ca1a`](https://github.com/Kitware/pan3d/commit/b21ca1ab50adaa3aafbcd4eb055c3fe6acae1378))

* Add back data array property ([`5c5b5fe`](https://github.com/Kitware/pan3d/commit/5c5b5fe63d9dc84f5a7aaa1fd8fb43dd72e68da5))

* Fix example file names in testing ([`22fc920`](https://github.com/Kitware/pan3d/commit/22fc920891353fc6171b45fb2803a13bbfb1b9ad))

* Use new Pvyista-Xarray Algorithm capabilities ([`5eda594`](https://github.com/Kitware/pan3d/commit/5eda594f45cdf6ef75698fe796674f48d34224fb))

* Small UI fixes for smaller window sizes ([`996abbc`](https://github.com/Kitware/pan3d/commit/996abbc2f446689d283eade1cd3ab7d339137bd9))

* Auto assign axes for i-j-k ([`0dd7c5f`](https://github.com/Kitware/pan3d/commit/0dd7c5fb34845527500aac1f32c4032abbc5e514))

* Add new example config and rename old ones ([`b220878`](https://github.com/Kitware/pan3d/commit/b2208784e7c97975c4d6fee8decffc6ba399994a))

* Merge pull request #33 from Kitware/import-export

Add Import and Export buttons ([`ada08d9`](https://github.com/Kitware/pan3d/commit/ada08d963a56d582d0a2ec6a069d2e4b1dc07cdd))

* Add immediate side effect for da_active, too ([`d7c9f9b`](https://github.com/Kitware/pan3d/commit/d7c9f9b1f4e40cdcab1944d59a872a27ef1d718e))

* Add example notebook using user-accesible state-setting functions ([`f0cdf7d`](https://github.com/Kitware/pan3d/commit/f0cdf7d8e67bd72647c048eae06ac8d6b8ee6fa0))

* Immediate callback during set_dataset_path ([`4a4c2f9`](https://github.com/Kitware/pan3d/commit/4a4c2f9818fd6961538c7a996c80b644c3db8c11))

* Allow &#34;pangeo&#34; arg to determine whether to fetch pangeo forge datasets ([`81037ba`](https://github.com/Kitware/pan3d/commit/81037baef828a8ebbf9f814f931c1645da96777a))

* Separate user-accesible state change functions and rename dialog-relevant state vars ([`24da1f6`](https://github.com/Kitware/pan3d/commit/24da1f6064ddfaccac9a32077f45595efa8764f3))

* Use pathlib read_text and write_text ([`b816852`](https://github.com/Kitware/pan3d/commit/b81685249babc1f58e001ca34c9f7d61bc8db8ea))

* Combine functions for da_[axis] state change ([`41e3c22`](https://github.com/Kitware/pan3d/commit/41e3c224749c308565d13cd4bc51f0e5e62d7423))

* Change default value for step to 1 ([`817bc5e`](https://github.com/Kitware/pan3d/commit/817bc5edce5cb29684f1bf6047e58cce5cf16111))

* Change pangeo forge example to use import, allow passing dict to import function ([`9de793b`](https://github.com/Kitware/pan3d/commit/9de793bd8ed42ab40b131a60aff9cb24f1ab4a59))

* Manage drawer states manually, use VAppLayout instead of SinglePageWithDrawerLayout ([`255dd7e`](https://github.com/Kitware/pan3d/commit/255dd7e95e21816404aaf70ce83e9ce10465a477))

* Change state variable names to group &#34;ui&#34; and &#34;da&#34; relevant vars ([`6f497a9`](https://github.com/Kitware/pan3d/commit/6f497a9be4f3e7e817c6b87aa61a51dcd2ea71bf))

* Remove redundant state modifications ([`ad725e2`](https://github.com/Kitware/pan3d/commit/ad725e2a63525dc5eb16b2779d48f51ec72d9cae))

* Shorten property lists where mapping does not require tuples ([`6088389`](https://github.com/Kitware/pan3d/commit/608838948dfe0dc7ae087a8bad66d8cdfe9a7aa9))

* Prefer f-strings where possible ([`28561cb`](https://github.com/Kitware/pan3d/commit/28561cb331878bed9f5131df5a01d8307360c41e))

* Fix example config files for tests ([`03eca36`](https://github.com/Kitware/pan3d/commit/03eca3680adf83b858c0d1d1f1274ec2a45f38d1))

* Fix modifying expanded_coordinates in UI ([`6d01c5d`](https://github.com/Kitware/pan3d/commit/6d01c5d6a61f1f5e3ef943ea6c716ced06393ddd))

* Fix values in example config files ([`72c4fc7`](https://github.com/Kitware/pan3d/commit/72c4fc7a42246b8070ccad94f0aaecb41352a363))

* Fix display of slicing values, allow slicing for t axis ([`0dd63f5`](https://github.com/Kitware/pan3d/commit/0dd63f51cd884ed6260cfb9666fc1c17fd7ad0dd))

* Reorganize import/export file format ([`8077584`](https://github.com/Kitware/pan3d/commit/80775844e4fc0ffa877faa67013729ac0fe262c8))

* Remove unused/redundant state vars ([`5d13025`](https://github.com/Kitware/pan3d/commit/5d13025a213b2dbe973c21558101ab134dc155ce))

* Fix updating coordinates after import ([`571bd1a`](https://github.com/Kitware/pan3d/commit/571bd1a782fcb09c8f6616983ab2695959fa1932))

* Protect against edge cases ([`d6bf03f`](https://github.com/Kitware/pan3d/commit/d6bf03fa6aa436f995cc36374ccdc925f474599d))

* Reduce calls to `data_array` ([`fafb4c9`](https://github.com/Kitware/pan3d/commit/fafb4c99479ab6c5b8d6f43c908f9815a3027dd7))

* Switch lon/lat in example config ([`ff73a20`](https://github.com/Kitware/pan3d/commit/ff73a20532d28a8f72043e5fa1979a9ebc80ec38))

* Add a new test to compare import &amp; export ([`e7d0775`](https://github.com/Kitware/pan3d/commit/e7d0775384876c701c6822855e16db14fcdf2c2d))

* Add download support for browsers without File System API ([`e89b3fa`](https://github.com/Kitware/pan3d/commit/e89b3fa0317dc2bff80b4bf774df92516edb543a))

* Update config examples ([`6eb0445`](https://github.com/Kitware/pan3d/commit/6eb044511b71fce465601c52daf46f04a2fca7cd))

* Add export functionality ([`7a03d5f`](https://github.com/Kitware/pan3d/commit/7a03d5f0aa043c9e7ee96ed2c8a7dbe70ae152aa))

* Fix switching between active arrays ([`b2d6a04`](https://github.com/Kitware/pan3d/commit/b2d6a0491b24d745869ab9298cbba75972d3870c))

* Add import and export buttons to the toolbar ([`01f32f2`](https://github.com/Kitware/pan3d/commit/01f32f21ee54c2d24c15c70d047f267e3f09ebf6))

* Allow specifying expanded_coordinates in config ([`3d11e15`](https://github.com/Kitware/pan3d/commit/3d11e1592ba127ba22e6f821669fe7474575989a))

* Accept coordinate config from import file ([`8278db7`](https://github.com/Kitware/pan3d/commit/8278db7a0c9d481330487c1a52c8a8ee89e304a9))

* Update example config ([`74d098a`](https://github.com/Kitware/pan3d/commit/74d098ae677f8b733280f3bad53ac37fc2e8450e))

* Merge pull request #29 from Kitware/axis-selector

Axis selector redesign ([`be706a1`](https://github.com/Kitware/pan3d/commit/be706a175e0a538eb035747c175f3f1a0062e918))

* Use bracket notation instead of setattr ([`5304ceb`](https://github.com/Kitware/pan3d/commit/5304ceb985f12378e6a2afde69136a19ba95a165))

* Add `dirty` statement in `on_set_array_active` ([`910fe0c`](https://github.com/Kitware/pan3d/commit/910fe0c13c7e97599837f028138bcb959a66f4dc))

* Remove `.keys()` from `len` calculations ([`b670a16`](https://github.com/Kitware/pan3d/commit/b670a16a70e27b9de13458af5130bb75ee8c1f0f))

* Manage expanded panels in state; otherwise all open on state change ([`3eadb7a`](https://github.com/Kitware/pan3d/commit/3eadb7aae842b3870b304f7e5a45c75bb83064b9))

* Make sure coordinate start, stop, and step changes are reflected in client ([`616347b`](https://github.com/Kitware/pan3d/commit/616347b1f81460bb62bdfbb0d5635476d1e623c3))

* Change step maximum to array size ([`d2e0ec7`](https://github.com/Kitware/pan3d/commit/d2e0ec7b9e14cf4f0e38bb6b4c172330b7ed41fd))

* Use a slider to select index instead of start, stop, and step for coords assigned to T ([`cc50bf8`](https://github.com/Kitware/pan3d/commit/cc50bf8c42975a70722f227c431f43a2360283e6))

* Add range to coordinate attrs table ([`a6e297c`](https://github.com/Kitware/pan3d/commit/a6e297c83af13f4fde5bd032e632e700678c210a))

* Fix axis Select slot, only show assigned value ([`b1a9852`](https://github.com/Kitware/pan3d/commit/b1a9852228917b9340c1591e88266379124921c1))

* Remove dividers (visual clutter) ([`ddb40cc`](https://github.com/Kitware/pan3d/commit/ddb40cc6776a37a328264dfce8c2adaa6e4133fc))

* Add coordinate attributes tables ([`c6a285e`](https://github.com/Kitware/pan3d/commit/c6a285e8a9255dcb9b75e12c9634f485f6d3f7c3))

* Change appearance of apply button ([`36d3eed`](https://github.com/Kitware/pan3d/commit/36d3eed4fd4bf94bd346b2dc68daf88972376aaf))

* Switch lon/lat default axis assignment ([`1b91759`](https://github.com/Kitware/pan3d/commit/1b917598e008cb17407c2d68abccd2d557c6f158))

* Remove all references to resolution as a state variable ([`dc88d5f`](https://github.com/Kitware/pan3d/commit/dc88d5ff724870547c5f62727c3432fef449c064))

* Implement changing data_array with coordinate starts, stops, and steps ([`21f3f85`](https://github.com/Kitware/pan3d/commit/21f3f852b15b661df87189ac8a278131e6d0acff))

* Change display of axis placeholder card (when no coordinate assigned) ([`4601e45`](https://github.com/Kitware/pan3d/commit/4601e454f5c9b594daca18944b438b3c951573e5))

* Change width of righthand drawer ([`e8b7c92`](https://github.com/Kitware/pan3d/commit/e8b7c92eabd501d57d27a106689ceadd01c1b234))

* Fix display of selected axis ([`289aacf`](https://github.com/Kitware/pan3d/commit/289aacf192e1adcecdba51d1cb2f71a5fd999a35))

* Switch back to VTextField, specify mapping of min and max attrs ([`2578c59`](https://github.com/Kitware/pan3d/commit/2578c592d57f4135631fce8f996f64f77b298feb))

* Store coordinate slices on state.coordinates and edit in coordinate configuration ([`2bb5bfa`](https://github.com/Kitware/pan3d/commit/2bb5bfa16bf94269671408324fa1f10f23ccb249))

* Refactor AxisConfigure -&gt; CoordinateConfigure ([`587681a`](https://github.com/Kitware/pan3d/commit/587681afc3df14b314f287a602a935cfb2f1cfad))

* Merge pull request #32 from Kitware/other-engines

Allow other xarray engines for other file types ([`97821b7`](https://github.com/Kitware/pan3d/commit/97821b7534f44741324fc28f77fd8e4f94f50d3c))

* Add coordinate auto-selection ([`708bb39`](https://github.com/Kitware/pan3d/commit/708bb39f123196c0f15bb78d66925e014300656a))

* Use uppercase arg shortcuts (avoid conflict with &#34;-d/--debug&#34;) ([`d8e391e`](https://github.com/Kitware/pan3d/commit/d8e391e4eaab9435a9bfffe46b0946c167c58a1c))

* Allow other xarray engines for other file types ([`c65eeda`](https://github.com/Kitware/pan3d/commit/c65eedacc9c8ece852a110fe9ad7f91379766b57))

* Merge pull request #30 from Kitware/vue3-migration

Vue 3 migration ([`5553583`](https://github.com/Kitware/pan3d/commit/55535834764314c065029e4fe959b6ba4d0d249b))

* Use better code for accessing custom style file ([`81ab442`](https://github.com/Kitware/pan3d/commit/81ab442f8daba987d66b386289633fd0e4a6699c))

* Condense axis state reset ([`1cb2197`](https://github.com/Kitware/pan3d/commit/1cb21978c4018dc1f92cc2e468f5ab332190ce7a))

* Use pathlib.Path for accessing custom style file ([`5a9afe7`](https://github.com/Kitware/pan3d/commit/5a9afe7a1acb29ba0eba8e9effcc89cb4677609f))

* Resolve merge conflicts ([`d8bfdc0`](https://github.com/Kitware/pan3d/commit/d8bfdc058da58086811a5070560f2e4db6069b0b))

* Merge remote-tracking branch &#39;origin/main&#39; into vue3-migration ([`75deac3`](https://github.com/Kitware/pan3d/commit/75deac38da9d4b5c265345f8347efbd5d7b92157))

* Merge pull request #31 from Kitware/console-scripts

Fix `pan3d-viewer` console script ([`0a80b2f`](https://github.com/Kitware/pan3d/commit/0a80b2f31b23d93a5c11921193a428a128dc4335))

* Fix `pan3d-viewer` console script ([`5f94c5b`](https://github.com/Kitware/pan3d/commit/5f94c5bfaacc0a99404d267e4cd8903ce16c0a01))

* Minor spacing fix ([`3e6acfc`](https://github.com/Kitware/pan3d/commit/3e6acfc529c7937790c58518a335222de67aa052))

* Fix custom css file reference ([`40944d5`](https://github.com/Kitware/pan3d/commit/40944d58318fff105652284acdce3899adb9f073))

* Use vuetify 3 API ([`aa7c297`](https://github.com/Kitware/pan3d/commit/aa7c29708bd226a50b2adbb91af446b8073d2d3d))

* Prevent axis select input from changing on select event ([`e15331a`](https://github.com/Kitware/pan3d/commit/e15331a6b4f799d4ac14944ed7e96286c825d1a1))

* New layout of Axis Selection component with basic assignment only ([`c2f0954`](https://github.com/Kitware/pan3d/commit/c2f09541c71390b2c60fb35fdaebb263bebdb0bf))

* Shift axis selector component placement ([`c8b40fd`](https://github.com/Kitware/pan3d/commit/c8b40fd319837c143ecf8e5bc3dec2d77a7d3aba))

* Allow --server arg to main ([`fff5f80`](https://github.com/Kitware/pan3d/commit/fff5f80a1fae7758f84529d9efdb2953dacad571))

* Merge pull request #28 from Kitware/viewer-class

Refactor to create Pan3DViewer class ([`b2ea683`](https://github.com/Kitware/pan3d/commit/b2ea68328da1115327c63144d9083dbd4b8488ee))

* Invoke viewer prop in server start ([`0a844e2`](https://github.com/Kitware/pan3d/commit/0a844e2c9791ffe7cf23a5b37e165d91ba1bf8b4))

* UI macro components accept state var names as parameters, but with expected values as defaults ([`5b7331b`](https://github.com/Kitware/pan3d/commit/5b7331b4dadd55dcaaa3d2650ee192bb603740af))

* Make layout an internal variable ([`22189b3`](https://github.com/Kitware/pan3d/commit/22189b3b88626686da170e8f0800b1d68a444c9c))

* Dissolve RenderArea component into main class ([`0c36b45`](https://github.com/Kitware/pan3d/commit/0c36b45c413e22cc2a0963dde8eb4f875d848413))

* Call viewer in main so lazy load occurs ([`de8843e`](https://github.com/Kitware/pan3d/commit/de8843e846d0f7474300c043d01657073dcd219d))

* Remove the word &#34;bookmark&#34; from notebook examples ([`d65129e`](https://github.com/Kitware/pan3d/commit/d65129e719ede4e0114ca7b3be73100391ff2017))

* Start with layout = None ([`81ad9ab`](https://github.com/Kitware/pan3d/commit/81ad9ab1d7b6feb8e00d1c9c7a0a8b954f260e1c))

* Lazy-load layout ([`a13307f`](https://github.com/Kitware/pan3d/commit/a13307f4fb78d9a4a6d0b29dda9d3cac963df7f1))

* Remove reference to main class as `viewer` ([`478af46`](https://github.com/Kitware/pan3d/commit/478af46b55a1d8e87be39ade88fadfcab4cee527))

* Add a print line to example notebook, showing access to vtk data array ([`1db0aec`](https://github.com/Kitware/pan3d/commit/1db0aecc95ad586737f6cbaa12923a4dc06c0e3c))

* Fix test config ([`233bde8`](https://github.com/Kitware/pan3d/commit/233bde8c25294f514a01826f2923962322ec2d9d))

* Rename feature bookmark -&gt; config ([`20d9c40`](https://github.com/Kitware/pan3d/commit/20d9c4058bde149269257bad194313ce6dfba1b9))

* More UI component refactoring ([`e7d71a2`](https://github.com/Kitware/pan3d/commit/e7d71a29c3a842792e5093bfb23986bcc6ec4d80))

* Rename property gui -&gt; viewer ([`c53fb7d`](https://github.com/Kitware/pan3d/commit/c53fb7ddf788d3ea9c4dda6ab1d9a25f87c533c5))

* Don&#39;t pass layout to components ([`efadb82`](https://github.com/Kitware/pan3d/commit/efadb82ee393bff375315d2d9901484079aff153))

* Break ui file into macro components ([`c74ba60`](https://github.com/Kitware/pan3d/commit/c74ba609ea89d20a301d01cf4dab12c5a5f61f9a))

* Class rename Pan3DViewer -&gt; DatasetBuilder ([`555710c`](https://github.com/Kitware/pan3d/commit/555710c4ac0d9d750499e8e2e6f283ea0bbcd3f3))

* Remove some redundant lines ([`258ea4a`](https://github.com/Kitware/pan3d/commit/258ea4ab9fbff5ebe131fc566247fb6396b3c683))

* Update tests ([`4038352`](https://github.com/Kitware/pan3d/commit/4038352df87b86bb1fb6d6790180e95c95161a7c))

* Adjust ui function for changing active array ([`6dd7acb`](https://github.com/Kitware/pan3d/commit/6dd7acbad2d1af70f400b970e1c5031562741d8b))

* Allow specifying dataset_path or bookmark_path via cli ([`dba930d`](https://github.com/Kitware/pan3d/commit/dba930d9dc1d982e824b59bc9c93c72db36f130f))

* Update jupyter example ([`5694506`](https://github.com/Kitware/pan3d/commit/56945060b1059d9a818ce9bad304786812c74a93))

* Refactor to Pan3DViewer class structure ([`ae86188`](https://github.com/Kitware/pan3d/commit/ae8618856e24a0b38e9a3afdaae3271a50f1ca58))

* Update gitignore ([`28cd54e`](https://github.com/Kitware/pan3d/commit/28cd54e02de22bf5dd574186d8b0ed9f10210265))

* Merge pull request #24 from Kitware/pangeo-forge-data

Incorporate Pangeo Forge data ([`c589f69`](https://github.com/Kitware/pan3d/commit/c589f69d1dad1e00e21e62ec90225bd0164ea932))

* Add back clim arg to add_mesh ([`0320014`](https://github.com/Kitware/pan3d/commit/03200141050985c9845c4d77666c53f5364cc234))

* Apply button shows data array size ([`a8a0207`](https://github.com/Kitware/pan3d/commit/a8a0207a6a64eea430486bb8d90582307ee14756))

* Adjust slider controls ([`c61798e`](https://github.com/Kitware/pan3d/commit/c61798ee5bf2f3da2b40f81f2b4915385d4f815e))

* Use resolution in data_array getter ([`85866f4`](https://github.com/Kitware/pan3d/commit/85866f4e8eb45e52d89fc4b3d0ef6f1f08d8c02a))

* Use separate thread and event loop for mesh tasks ([`7d82a5c`](https://github.com/Kitware/pan3d/commit/7d82a5cb1fa0842620490944b036df2a0e1e6cc9))

* Remove reset on state change, perfect state will render pangeo forge data ([`3b0e8e4`](https://github.com/Kitware/pan3d/commit/3b0e8e4ac1ba8135b142b1a4fc5597c8b9bd77b2))

* Update pvxarray and add necessary deps ([`b55d6bb`](https://github.com/Kitware/pan3d/commit/b55d6bb68416a7345c0bb79fbca746cc25c910c0))

* Run mesh update asynchronously in reset function ([`4021631`](https://github.com/Kitware/pan3d/commit/4021631fb4b096339ac78b40f0d1763cf2e193a1))

* Clear plotter on reset ([`da773c7`](https://github.com/Kitware/pan3d/commit/da773c776929e1e63dea3e4558efde4f39715e76))

* Add dataset dimensions to data atrributes table ([`31c7136`](https://github.com/Kitware/pan3d/commit/31c713608dcd2400d6fa7ec7e4e3089acfed1245))

* Correct label on Xarray examples ([`a5896fc`](https://github.com/Kitware/pan3d/commit/a5896fc634940e2468b6caab668e65da52aef9a2))

* Fetch available datasets from pangeo forge ([`4cef392`](https://github.com/Kitware/pan3d/commit/4cef392d3d338c1873b75730388a70ceeaae68a5))

* Merge pull request #23 from Kitware/ui-redesign

UI redesign ([`f67c0a8`](https://github.com/Kitware/pan3d/commit/f67c0a8a900c108236ce2801b69ba3ebb5053cf1))

* Change label for time slider ([`5d03aa4`](https://github.com/Kitware/pan3d/commit/5d03aa4fb800903f03b8c002bb82e2c48e83c327))

* Call `validate_mesh` before algorithm `Update` to avoid vtk warnings ([`0bb1bf9`](https://github.com/Kitware/pan3d/commit/0bb1bf92a19fb84e24b2783295577c6ffcbcf8a9))

* Add time indexing in validate mesh function ([`7b56cf0`](https://github.com/Kitware/pan3d/commit/7b56cf004cdcc38542aa03d9f660ae09011ba37e))

* Use `mesh` method to check data validity instead of `RequestData` ([`837fdc5`](https://github.com/Kitware/pan3d/commit/837fdc5bf0c70a6030b8f158fff21c9e60c680e9))

* Add trame-vuetify and trame-vtk to dependencies to comply with trame@3 ([`d4f8e63`](https://github.com/Kitware/pan3d/commit/d4f8e6315f0a40fbd75a8a3f360b8d657b050218))

* Use plotter_ui from pyvista.trame.ui ([`08db4f5`](https://github.com/Kitware/pan3d/commit/08db4f5c93448598b8bf9e360f7f2b2ec60e083a))

* Auto reset and display any error messages ([`8ec1ea0`](https://github.com/Kitware/pan3d/commit/8ec1ea05ff8d0e40fb35f9ef1316526e5dad72a2))

* Rearrange UI and auto-select first available array ([`ba11ebe`](https://github.com/Kitware/pan3d/commit/ba11ebe6e65a6c8e9e4f2c3d33421ec1f4f4ab57))

* Merge pull request #26 from Kitware/refactor

Promote src contents to top-level, delete other modules ([`ea8c153`](https://github.com/Kitware/pan3d/commit/ea8c153ed97984d2427ca38f2b62f8dc3dd9bb5b))

* Promote src contents to top-level, delete other modules ([`82ff1b5`](https://github.com/Kitware/pan3d/commit/82ff1b562f20f7ab8078ff9fe534e4208b49456a))

* Merge pull request #25 from Kitware/fix-ci

Fix Github actions ([`2791cae`](https://github.com/Kitware/pan3d/commit/2791cae4177464c8ae200dd5a35bcda4721eaad9))

* Use single dockerfile for build (following example from trame/examples/deploy/docker/SingleFile) ([`377dbb9`](https://github.com/Kitware/pan3d/commit/377dbb96b6a654d7faae44fa37e487cf92a29032))

* Put the second dockerfile back ([`2d41f8c`](https://github.com/Kitware/pan3d/commit/2d41f8c5f9f3db2330d31bfb43e012c0768ccde9))

* Remove git install from dockerfile ([`46943b0`](https://github.com/Kitware/pan3d/commit/46943b000034de32534e682eeb8d2321665f9737))

* Add back cases for pushing docker image ([`f46dd70`](https://github.com/Kitware/pan3d/commit/f46dd7065b01f2d3042c5c1264f675fd80060040))

* Fix pyvista requirement (feature has been merged) ([`403dea7`](https://github.com/Kitware/pan3d/commit/403dea75c6830ef7264425e68bb9fbf0a241b7af))

* Fix spelling errors ([`4cd9ca2`](https://github.com/Kitware/pan3d/commit/4cd9ca295a314e5acd26246b546d801ac6ee8ede))

* Fix dockerfile ([`db3a063`](https://github.com/Kitware/pan3d/commit/db3a0633a48c98b402c29d1130ef785df737d53b))

* Fix format errors ([`42798c5`](https://github.com/Kitware/pan3d/commit/42798c5ac7f91a8d35cc01d871e5e58f97873ab7))

* Fix Github actions ([`071c252`](https://github.com/Kitware/pan3d/commit/071c2527a804b47e9d33100232f88726ac13f0ee))

* Add Docker build/publish GHA (#21)

* Add Docker build/publish GHA

* fix working-directory

* Fix

* Fix image name ([`8829614`](https://github.com/Kitware/pan3d/commit/8829614ff4e67c70b8f8218039711a50d86c644d))

* Fix build ([`4f542ea`](https://github.com/Kitware/pan3d/commit/4f542eaabf21ed0605c20f146f0cd5a4e6d4894e))

* Remove unneeded styling ([`98d9ce5`](https://github.com/Kitware/pan3d/commit/98d9ce5b83b60ce17739f3a7f373a29d1070bae0))

* Fix dependencies ([`34ba1c7`](https://github.com/Kitware/pan3d/commit/34ba1c707e026fc76d6b1d80066efe392518be53))

* Update gitignore ([`acb9c5a`](https://github.com/Kitware/pan3d/commit/acb9c5aeff82341e31666c6299b81a6c4c7b5435))

* Add VTK 9.2.2 OSMesa and EGL wheels ([`ee71c9e`](https://github.com/Kitware/pan3d/commit/ee71c9e1a7fbe104cc4585318b2eff63b227fa82))

* streamline deployment ([`a548c89`](https://github.com/Kitware/pan3d/commit/a548c89d5a0f2a2768385e255a63956ea6b21046))

* Add deployable docker infrastructure ([`5ca88f5`](https://github.com/Kitware/pan3d/commit/5ca88f5a658e3674c840fd5cced87eb44cfc3943))

* Fix dependencies ([`53db291`](https://github.com/Kitware/pan3d/commit/53db291107cea91ed60a2098a8249f08e5ce7c56))

* Refactoring viewer to focus on Xarray (#14)

* Cleanup

* Move main

* Remove ImageData support

* Switch viewer to PyVista

* Only support RectilinearGrids

* Switch to using pyvista-xarray

* Add notes about required upstream changes

* Add time and scale sliders

* Add resolution dropdown

* Add dataset path UI text field

* Fix repo config

* Move things around

* Cleanup

* Clean up view_update

* Cleanup

* Cleanup

* clenaup

* fix

* Add dropdown choices for dataset selection ([`ff321e3`](https://github.com/Kitware/pan3d/commit/ff321e312e3dbb422164a385783f526afd25751a))

* update layout ([`d77de84`](https://github.com/Kitware/pan3d/commit/d77de845f0431d6cc81ed48617e2132b2f2241f7))

* small cleanup ([`b225f4b`](https://github.com/Kitware/pan3d/commit/b225f4bac1d7446bd177fd2509bed9cb01cb4052))

* update readme to reflect data need ([`d8dd65e`](https://github.com/Kitware/pan3d/commit/d8dd65e30dbd30875022cbf2b92885fb02f7318d))

* allow to delete individual cell data ([`9f3ec50`](https://github.com/Kitware/pan3d/commit/9f3ec50303700d15cb6683d97390bff8bb02777a))

* Most of the viewer available ([`3757fae`](https://github.com/Kitware/pan3d/commit/3757fae4b0593c7a9384e4e1840911c878c69ae1))

* bind reset fields and camera ([`eea474b`](https://github.com/Kitware/pan3d/commit/eea474be2c46c9635b29fb03dfe803f37c02c30a))

* getting array binding with viz ([`f4237e2`](https://github.com/Kitware/pan3d/commit/f4237e24c7ca6880320096e9c265fe90f1f48f2b))

* Merge pull request #6 from Kitware/john-update-mockup1

Add code to extend the mockup to include display and interaction ([`aba31e5`](https://github.com/Kitware/pan3d/commit/aba31e51b561de0a9b53e3d26b64e3a73944e9bd))

* Add code to extend the mockup to include display and interaction ([`ff8c0c1`](https://github.com/Kitware/pan3d/commit/ff8c0c1cce53822cb9fcd99c28d3d656c521175a))

* Merge pull request #5 from Kitware/strawman-notebook

Add strawman notebook suggesting some basic pan3d functionality ([`230d568`](https://github.com/Kitware/pan3d/commit/230d568458471a0412b7750c066b468966d0cbd9))

* Add strawman notebook suggesting some basic pan3d functionality ([`ea3a6ea`](https://github.com/Kitware/pan3d/commit/ea3a6eac44176b77144898d2a6a8030658e93e08))

* demo: pyvista + trame ([`cf222af`](https://github.com/Kitware/pan3d/commit/cf222afbbf165d74fbc609eac983318440815b2c))

* Initial commit ([`323cae0`](https://github.com/Kitware/pan3d/commit/323cae0b1248adb53ef59bd854e99da2ef99d1bc))
