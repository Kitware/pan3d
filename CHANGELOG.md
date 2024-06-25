# CHANGELOG

## v0.7.0 (2024-06-25)

### Ci

* ci: remove pull_request trigger for publish action ([`1751cc4`](https://github.com/Kitware/pan3d/commit/1751cc413aa3bd645da8bfd5b1c5b2f4d8495666))

### Feature

* feat: Add entrypoint to create symlink to examples folder (suggested by Yuvi @ 2i2c) ([`29f6af5`](https://github.com/Kitware/pan3d/commit/29f6af52d2561c1f1b03ef609b79f43cb4be6634))

* feat: add cloud dockerfile and add ci step to publish as pan3d-cloud ([`25794ea`](https://github.com/Kitware/pan3d/commit/25794eaa76b38e62b5c7b2da6cf49de14e831e09))

### Fix

* fix: Remove reference to jupyter.py in pyproject.toml ([`232cdc6`](https://github.com/Kitware/pan3d/commit/232cdc632e106d152594d907d35b73016a12e248))

* fix: move symlink command to entrypoint script ([`9f2db38`](https://github.com/Kitware/pan3d/commit/9f2db381773b1a6f04dad313e0d53d49f4a325c5))

* fix: rename docker images ([`0b4df24`](https://github.com/Kitware/pan3d/commit/0b4df2433eb29f66506287ae66a6022af4a5e5e0))

* fix: remove jupyter server proxy command ([`50cfc3a`](https://github.com/Kitware/pan3d/commit/50cfc3a69ad96c33927309c6c922682d05fa5d98))

* fix: change tag names ([`655daef`](https://github.com/Kitware/pan3d/commit/655daef682d3add13611767185f01a639dddf6a5))

* fix: specify tags for each image ([`f93de95`](https://github.com/Kitware/pan3d/commit/f93de9534c386603f8a15f13f202d0b55daa7554))

* fix: use dockerhub registry instead of ghcr.io ([`f7e6cb2`](https://github.com/Kitware/pan3d/commit/f7e6cb2259b2ad8c1c335c725425cdb7584a836a))

* fix: remove `if` clauses from ci `jobs` spec (redundant after `on` spec) ([`f87ddf0`](https://github.com/Kitware/pan3d/commit/f87ddf04cdc2086ce11e20a1623089c11dac35ad))

### Refactor

* refactor: simplify job names ([`6ae13a9`](https://github.com/Kitware/pan3d/commit/6ae13a965fe844934d933b723ec9b4d2026042c4))

### Unknown

* Merge pull request #77 from Kitware/cloud-docker-image

Create pan3d-cloud docker image ([`268b7b9`](https://github.com/Kitware/pan3d/commit/268b7b97d9c5220141b2e03bda01523762cf7766))

## v0.6.2 (2024-06-25)

### Build

* build: require trame-vtk&gt;=2.6.3 ([`be9a4ce`](https://github.com/Kitware/pan3d/commit/be9a4ced0e9bebf5265b301edb0146e1b05c090e))

* build: use BINDER_REQUEST instead of JUPYTERHUB_BASE_URL to determine whether env is in Binder ([`bd9c5e2`](https://github.com/Kitware/pan3d/commit/bd9c5e2f960dff6964e8d54e346fe6cd1f323d2b))

* build(binder): try local pan3d install ([`404c2ab`](https://github.com/Kitware/pan3d/commit/404c2abd3ebd6998d230ae98a58026030ee61bc5))

* build: remove apt.txt ([`1b4c176`](https://github.com/Kitware/pan3d/commit/1b4c176bd9a4822fd43a4ccc305c003c424a322e))

* build: move binder configuration to .binder, use postBuild script instead of start ([`8f166c9`](https://github.com/Kitware/pan3d/commit/8f166c9c37f8aa82b062625bdf99840c7c2864f0))

* build: try without xvfb, use vtk-osmesa ([`850dc15`](https://github.com/Kitware/pan3d/commit/850dc15b78f4ec66cfe9b3e5231d707fe549f439))

* build: remove vtk-osmesa installation, use xvfb ([`6efab66`](https://github.com/Kitware/pan3d/commit/6efab66704ccba153cd7a90c872cf2653ab2c28d))

* build: remove which Xvfb command

Co-authored-by: Zach Mullen &lt;zach.mullen@kitware.com&gt; ([`081f5cb`](https://github.com/Kitware/pan3d/commit/081f5cba49f406fd74b907cf2b07b31951704b55))

* build: add binder start script from pyvista docs ([`51318d1`](https://github.com/Kitware/pan3d/commit/51318d150170a74e13b46cc09b3bd03cfb261e4e))

* build: add xvfb to system requirements ([`6a961e9`](https://github.com/Kitware/pan3d/commit/6a961e9d8625d15748c9b004e5f483655e878dca))

* build: reformat requirements.txt ([`513399b`](https://github.com/Kitware/pan3d/commit/513399b36c01ad0d128042ddb769c962880daf34))

* build: move configuration files to top-level binder folder ([`1f388d9`](https://github.com/Kitware/pan3d/commit/1f388d91df04dbd2709596b1ecf0d5efb9cb2940))

* build: try binder build without Dockerfile ([`27f038f`](https://github.com/Kitware/pan3d/commit/27f038f7e7c7f0f0e6693e23fd162a7f51b300b7))

* build: add more dependencies to Dockerfile ([`808d421`](https://github.com/Kitware/pan3d/commit/808d421aa4b049acd611af6a712784ca0a3b93f8))

* build: switch user back to NB_USER after installation ([`f4e8893`](https://github.com/Kitware/pan3d/commit/f4e8893baa28fd1855faf1aad887d2494dcb72d0))

* build: update Dockerfile in examples/jupyter ([`dd5961a`](https://github.com/Kitware/pan3d/commit/dd5961aa34c94a8f1b04e1ee3de10225dcb025ff))

* build: remove setuptools-scm, use __version__ in setup.py ([`bf63e56`](https://github.com/Kitware/pan3d/commit/bf63e560096c72a5d3fd73460b04a47deb324cad))

* build(setup): add MANIFEST.in and include package data ([`efb8cd0`](https://github.com/Kitware/pan3d/commit/efb8cd0b722dbe410d459242f043bddad60f9c63))

### Ci

* ci: add `contents:write` to permissions in release job ([`c4ef618`](https://github.com/Kitware/pan3d/commit/c4ef618af7820403688abdf745d01c0181076b40))

* ci: combine build, release, publish jobs into one release job with 3 steps ([`0a61ae3`](https://github.com/Kitware/pan3d/commit/0a61ae322c72ea7df32220f12b169480c653f7c1))

* ci: rebuild before PyPI publish ([`34432d2`](https://github.com/Kitware/pan3d/commit/34432d253f051cd9fcabc387a177647f4baed5c6))

* ci(pyproject.toml): bump python requirement to 3.7 ([`e7217a4`](https://github.com/Kitware/pan3d/commit/e7217a490e011bdfb8dd27378073ad022a5570c7))

### Documentation

* docs: update docs images ([`1e070ca`](https://github.com/Kitware/pan3d/commit/1e070caf994db8d0ac03d80aec24d5a74956363f))

* docs: add new tutorial page for catalog search dialog ([`0421f9e`](https://github.com/Kitware/pan3d/commit/0421f9e97033fceb59a6284aab24d5f3d01d60bf))

* docs: adjust existing pages to catalogs changes ([`bece99d`](https://github.com/Kitware/pan3d/commit/bece99d268ed10f22bad2a8278ffb1f6850bc923))

* docs: update examples ([`37314ca`](https://github.com/Kitware/pan3d/commit/37314ca990a720891278a1c1b756cd657464413b))

* docs: add example config file with ESGF dataset ([`c4c9dae`](https://github.com/Kitware/pan3d/commit/c4c9daef6d5e6a376dce738113c192143c0c6f14))

* docs: Add `site` to .gitignore ([`0f30478`](https://github.com/Kitware/pan3d/commit/0f30478b0be577b271d0d26e1ee755f7c198528e))

* docs: Improve language in tutorial pages

Co-authored by: @johnkit ([`9149c5b`](https://github.com/Kitware/pan3d/commit/9149c5b1328f8ce024e80deff13f6557ad7e6093))

* docs: update tutorials and other descriptive documentation ([`34d41cf`](https://github.com/Kitware/pan3d/commit/34d41cf1f0432fb783d11e716ed16623d6ac45d1))

* docs: update image folder (stored with lfs) ([`9caaa06`](https://github.com/Kitware/pan3d/commit/9caaa067ef7e4e27576330f4ba890554c78b1de6))

* docs: update docstrings for API docs pages ([`c006332`](https://github.com/Kitware/pan3d/commit/c0063322f10543b3a48716c0427254f404ae5fde))

* docs: Add two new example jupyter notebooks ([`8efdbfb`](https://github.com/Kitware/pan3d/commit/8efdbfb85cb09b85fac7e3ed636a59aeb7bb836f))

* docs: update existing jupyter notebook examples ([`96cb22a`](https://github.com/Kitware/pan3d/commit/96cb22a27ca16c5938f53a8ef86d107d31244a8e))

* docs: replace &#34;active&#34; with &#34;name&#34; in config schema ([`787a0e9`](https://github.com/Kitware/pan3d/commit/787a0e925681dedd2a89cbfd7b62bf1eed6b1033))

* docs: Add mesh edges screenshot to viewer tutorial ([`d2ac60c`](https://github.com/Kitware/pan3d/commit/d2ac60cc567766affdf8ef1342e6ee8968bcc745))

* docs: improve Pangeo Forge examples ([`5f1be01`](https://github.com/Kitware/pan3d/commit/5f1be0130514d176e8142da6385e0fa26e8f3634))

* docs: Update current time in description for updated screenshot ([`2f0a0ae`](https://github.com/Kitware/pan3d/commit/2f0a0ae87ccff9e4d4bce860ad584290dde5995c))

* docs: Add descriptors for what each axis represents ([`908b9b4`](https://github.com/Kitware/pan3d/commit/908b9b4e4703d9e4c1a62524e651cc9cd4a3d8ba))

* docs: add comment to `.binder/requirements.txt` ([`9a1dfbe`](https://github.com/Kitware/pan3d/commit/9a1dfbe65d231c93153ca878a4d6fe810cb0dec3))

* docs: Add configuration for readthedocs ([`4ee93de`](https://github.com/Kitware/pan3d/commit/4ee93de21679f98d33920fbcbcd3a1d671eacff5))

* docs: fill API documentation pages ([`d50027d`](https://github.com/Kitware/pan3d/commit/d50027d0e9da0519923861c07e73539fb0d3b28d))

* docs: Add typing and docstrings to dataset_builder.py ([`40d6e95`](https://github.com/Kitware/pan3d/commit/40d6e95a7e29031ee6147a4f50960613cc573f6b))

* docs(setup): update pyproject.toml and MANIFEST.in with README location ([`94638cd`](https://github.com/Kitware/pan3d/commit/94638cd0e211b5465567c6a8215b6e5a56ec6da4))

* docs(tutorials): create basic docs navigation and add tutorials ([`c6fb974`](https://github.com/Kitware/pan3d/commit/c6fb97446efdaee0b4f5f32634bb5e73d5b36537))

* docs(version): use dynamic version in pyproject.toml ([`b7db351`](https://github.com/Kitware/pan3d/commit/b7db351604038bdb5b3eb6cf3802c50b47e0a463))

* docs(cli): Rename `dataset_path` arg to `dataset` ([`1dd1c30`](https://github.com/Kitware/pan3d/commit/1dd1c30d98b794f897aa9097b9a3324e7ba5de1f))

### Feature

* feat: Add PreviewBounds component, written with Vue ([`1d9c898`](https://github.com/Kitware/pan3d/commit/1d9c89892df76ee0d505218c563c52a1e36423ec))

* feat: Generate cube face preview images and set up cube mode state vars ([`ad2fcdc`](https://github.com/Kitware/pan3d/commit/ad2fcdc14b202ba548433db69705827af90a8a10))

* feat: Add `resolution` CLI arg and disable auto slicing when &lt;= 1 ([`24c97ad`](https://github.com/Kitware/pan3d/commit/24c97adc8af68f8ed3f9b6be6b381bb98ec48977))

* feat: Add BoundsConfigure component within render area ([`73653e9`](https://github.com/Kitware/pan3d/commit/73653e9c3a0c5d9d185e0b103b54e88c9bc6f330))

* feat: add camera positioning to cartographic rendering ([`c860d08`](https://github.com/Kitware/pan3d/commit/c860d08ef708ddec06917d2b1260d962fcc00cc4))

* feat: Use GeoVista to map data onto earth sphere ([`3bb7b2f`](https://github.com/Kitware/pan3d/commit/3bb7b2f4bba20128a660d2b70c15c8c79db12f5a))

* feat: Add &#34;render_cartographic&#34; state var and relevant management/docs ([`294bc7f`](https://github.com/Kitware/pan3d/commit/294bc7f42bf7ba4a01aaa559d0dfeca1fc2a2738))

* feat: Add value checking on DatasetBuilder setters ([`ecfe374`](https://github.com/Kitware/pan3d/commit/ecfe374df2fd2e41602254913ab36f3b325d7182))

* feat: add `viewer` kwarg to Builder constructor to instantiate Viewer ([`4927a9c`](https://github.com/Kitware/pan3d/commit/4927a9cdfbe85a33c096ebf1133dd59312ee9783))

* feat: implement Pangeo module functions using intake ([`3bcbf2e`](https://github.com/Kitware/pan3d/commit/3bcbf2edcc5515a7fdd3f7977c596801cbb22970))

* feat: add a catalog search dialog ([`210afb1`](https://github.com/Kitware/pan3d/commit/210afb187b682b5d05ea04785c21799ff24eb525))

* feat: add group selector to UI in `main_drawer` ([`30f3063`](https://github.com/Kitware/pan3d/commit/30f3063fbeb10989f802ef672b855e699ce9a602))

* feat: add `--esgf` argument to `pan3d-viewer` ([`1b1f0ba`](https://github.com/Kitware/pan3d/commit/1b1f0ba2f51f01481623a574d78f1981c8d685fe))

* feat: add esgf module, which uses intake-esgf ([`6be5401`](https://github.com/Kitware/pan3d/commit/6be54014f19df79d5acad0b44d2ee2c73b673dac))

* feat: add automatic rendering, enabled by default ([`644e1fa`](https://github.com/Kitware/pan3d/commit/644e1fa101bcb6fae3b522943758d2f38aaf42ae))

* feat: more extensive automatic coordinate selection ([`01de7c1`](https://github.com/Kitware/pan3d/commit/01de7c1500c55e6a887ba6ee4e8d2c120d1e258c))

* feat: add more xarray examples to default dataset list ([`af6586e`](https://github.com/Kitware/pan3d/commit/af6586eaeb0102c2a04052a0a97603152f4a54d8))

* feat: set rendering mode to client in known cloud jupyter environments ([`32641fe`](https://github.com/Kitware/pan3d/commit/32641feab747f5edd9a38debd5fbf0c54ed3a55f))

* feat(examples): add notebook demonstrating use of `builder.mesh` with pyvista rendering ([`7f9d88c`](https://github.com/Kitware/pan3d/commit/7f9d88cc84506211b492b02dc4fa70a0572e0000))

### Fix

* fix: Add &#34;pan3d.ui.pan3d_components&#34; to packages list ([`8389496`](https://github.com/Kitware/pan3d/commit/8389496ac09e0b4988c4d733fd6ac0c91f34d3bf))

* fix: include module and serve packages individusaly ([`c9b449f`](https://github.com/Kitware/pan3d/commit/c9b449ff6a54a8f50818b49d1ea15e0bab2ba22b))

* fix: update javscript path in CI for build step ([`7432328`](https://github.com/Kitware/pan3d/commit/743232879e4f4dab9fa9ffa4b19d2031c0d78889))

* fix: add new folders to packages list in pyproject.toml ([`3247611`](https://github.com/Kitware/pan3d/commit/32476117eebe3de18a9e7daecaac58632af1b374))

* fix: apply suggested usability changes ([`1532b5a`](https://github.com/Kitware/pan3d/commit/1532b5ae25084aa207ddd28c6b973344d596be07))

* fix: Add npm installation steps to CI tests ([`ce688ed`](https://github.com/Kitware/pan3d/commit/ce688ed14488a793cbf1827f7db79ec84fd881fc))

* fix: Move default resolution value (cmd arg is None if not specified) ([`faabc39`](https://github.com/Kitware/pan3d/commit/faabc39df0ef5edbdb5caa69efb34dfcaa260876))

* fix: Correct various bugs and unexpected behavior ([`9c9ebf7`](https://github.com/Kitware/pan3d/commit/9c9ebf7862dfd93369bf7ea4b4ab46fef51cf902))

* fix: Update example config files ([`5cac70e`](https://github.com/Kitware/pan3d/commit/5cac70ea660dda2cc61fb6ecaa137ae3aec19b2f))

* fix: slice by index instead of value to allow slicing time coord ([`801735f`](https://github.com/Kitware/pan3d/commit/801735f3ef4296ffc292f1c3c5ba2ac7ec380b94))

* fix: remove cmdline arg shorthand notations to avoid conflicts ([`88d9810`](https://github.com/Kitware/pan3d/commit/88d9810f06f283fe66fa785f6e6bc71b211a9d78))

* fix: update files in `docker` folder ([`b1aae3f`](https://github.com/Kitware/pan3d/commit/b1aae3facf5a0df09823a4eebb422e7b4463881a))

* fix: show import loading bar during import ([`24821c4`](https://github.com/Kitware/pan3d/commit/24821c41d6427df69b6c0edd8fd4691a59917eed))

* fix(test): add a flag to disable render in `set_render_options`; geovista GeoPlotter raises exception when no GPU found ([`2fd86ca`](https://github.com/Kitware/pan3d/commit/2fd86ca6c2a39e92961ccd74b0f5b13f674c3fba))

* fix(test): allow non-numeric slicing values (for time axis) ([`822427e`](https://github.com/Kitware/pan3d/commit/822427ef31eae93c7c321243bd98bc386b82e4e3))

* fix(test): don&#39;t enable cartographic mode on 4D test data ([`b632ad9`](https://github.com/Kitware/pan3d/commit/b632ad99d5bb93aab1d54efb3e12a1fbdc6276aa))

* fix(examples): Update example notebooks with catalogs argument ([`f8c07d9`](https://github.com/Kitware/pan3d/commit/f8c07d9e69178fcb0ad8571acea76fd84083f09a))

* fix: Set DatasetBuilder slicing to None when DatasetViewer coordinates are blank ([`f53dc24`](https://github.com/Kitware/pan3d/commit/f53dc24e6106b1a247dae063b7c4689f20b09ed3))

* fix: prevent name conflict by renaming catalogs module import ([`806657f`](https://github.com/Kitware/pan3d/commit/806657fb4db006ae1e40c182563a5d4d3fe7db3c))

* fix: add catalogs folder to setuptools packages list ([`54722a6`](https://github.com/Kitware/pan3d/commit/54722a671d3d317b725e91f42bc78b12fa401f11))

* fix: prevent &#34;NoneType is not iterable&#34; error in Pangeo search by ID ([`6b91079`](https://github.com/Kitware/pan3d/commit/6b91079cea8cc916a2909601f0cab9b5d68dbb6e))

* fix: guard against a None `catalogs` value in `DatasetViewer` constructor ([`dc505e5`](https://github.com/Kitware/pan3d/commit/dc505e5e17682113ac537eb90be10585fae1ddb2))

* fix: reset search and message when catalog changes ([`5327dab`](https://github.com/Kitware/pan3d/commit/5327dab1b9cb83d460f3e0e11cddce0570bf4d16))

* fix: reduce sleep time in `run_as_async` ([`50e568b`](https://github.com/Kitware/pan3d/commit/50e568b2af8b5f53a4d76be7366f2244b6d6fa40))

* fix: update binder requirements.txt ([`26abc54`](https://github.com/Kitware/pan3d/commit/26abc54e9eab0af05f89845cee6dd3f07d8b9a5b))

* fix: Use try-catch for catalog module imports ([`a1a7e5a`](https://github.com/Kitware/pan3d/commit/a1a7e5ab0d10747095ed4e11f1546b00815b4f3d))

* fix: use correct exception imports in `pangeo_forge.py` ([`a8fccca`](https://github.com/Kitware/pan3d/commit/a8fccca880988a7a257c1216e8102b08869bfc78))

* fix: remove unnecessary values from exported state ([`a6de08b`](https://github.com/Kitware/pan3d/commit/a6de08bbe070a17c5f614ee7e4639dd7d9b0155d))

* fix: loading and error states should be handled only by `run_as_async` method ([`1c488ff`](https://github.com/Kitware/pan3d/commit/1c488ff9de9ac2c503db0fbd4bd853b8d41b5853))

* fix: improve compatibility with more pangeo datasets with timedelta dtypes ([`a80119e`](https://github.com/Kitware/pan3d/commit/a80119e19a25cd7aa383edbb580ec793a81ccda7))

* fix: consolidate asynchronous viewer behavior with helper function `run_as_async` ([`a69f106`](https://github.com/Kitware/pan3d/commit/a69f106778f4645cb356d6455403cb49ba73b00c))

* fix: Update Builder and Viewer to use Pangeo module ([`b94e60e`](https://github.com/Kitware/pan3d/commit/b94e60eb552f57b1157210be8617fa6706d1e0ac))

* fix: add missing parenthesis in async callback ([`a2e7676`](https://github.com/Kitware/pan3d/commit/a2e76762a06c3f6870eb32374def6e6437fd7d23))

* fix: protect against NoSearchResults exceptions from intake_esgf ([`3654f48`](https://github.com/Kitware/pan3d/commit/3654f482ed44ee14236f8140ccd8cd016a2150d5))

* fix: remove broken pangeo-forge links from catalog ([`9ea98f5`](https://github.com/Kitware/pan3d/commit/9ea98f5d75bb7efc2e7c1624f05ed83898a53abd))

* fix: improve usability of import via UI ([`22520fd`](https://github.com/Kitware/pan3d/commit/22520fd359f9e334f4bbb8be7e0e9f9c5a70c967))

* fix: wait until server ready before enabling auto rendering ([`e02d159`](https://github.com/Kitware/pan3d/commit/e02d15922ee33e7bcc86094318527b54cf1ee258))

* fix: synchronize slicing state between builder and viewer ([`33b5404`](https://github.com/Kitware/pan3d/commit/33b54048b3a1cd0fc50aedd92a64d35d360b26a5))

* fix: assign coordinates on implicitly indexed data arrays before sending to algorithm ([`087d04f`](https://github.com/Kitware/pan3d/commit/087d04fa544334d178eb442a8b52cf1f2c59c611))

* fix: asynchronous trame state updates ([`48bd1d7`](https://github.com/Kitware/pan3d/commit/48bd1d7779a735fa059d564296c734493964efc4))

* fix: state synchronization between builder and viewer ([`e3ab71a`](https://github.com/Kitware/pan3d/commit/e3ab71ab1da2177da1ff3d5037c56ca1345a1534))

* fix(threading): use `call_soon_threadsafe` for plotting mesh ([`28930fb`](https://github.com/Kitware/pan3d/commit/28930fb372a4cc6d5fbfadaf3d966d67994e202b))

* fix(docs): fix README badge rendering on GH ([`a6065d6`](https://github.com/Kitware/pan3d/commit/a6065d6326f49b4560375e6cf33775850482f011))

* fix: use true min and max for default slicing ([`aa4d939`](https://github.com/Kitware/pan3d/commit/aa4d9394b2f4f2c40ef38df6f3489563de8a570f))

* fix: use relative path for pangeo datasets JSON ([`e85e83e`](https://github.com/Kitware/pan3d/commit/e85e83e849b958e8070b84be7a6876a97f49484a))

* fix: update test expected size for updated example file ([`c4acabe`](https://github.com/Kitware/pan3d/commit/c4acabef8045dbbda6c41d2069dc1a54dd9806a4))

* fix: change pyvista StructuredGrid reference ([`5260a60`](https://github.com/Kitware/pan3d/commit/5260a60a04dc57412d8af2259edb8a699cdd0d36))

* fix(DatasetBuilder): typing adjustments ([`0686dea`](https://github.com/Kitware/pan3d/commit/0686dea8889db3e8d1360d3c6e511abe2e6ad1a5))

* fix: always use `push_camera` instead of `reset_camera` ([`b3ce44f`](https://github.com/Kitware/pan3d/commit/b3ce44f3f20f61bd66c23d82b048c34c76fef747))

* fix: use `push_camera` instead of `reset_camera` in cloud mode ([`41dde0c`](https://github.com/Kitware/pan3d/commit/41dde0ccb4cf794f9985bbbfe490dab49d096f9d))

* fix: remove defaults on computed attribute values ([`fd024a7`](https://github.com/Kitware/pan3d/commit/fd024a7de971c856beb85e2d2828242038ae1a36))

* fix: prevent `auto_select_coordinates` from overwriting `set_data_array_axis_names` results ([`53f016e`](https://github.com/Kitware/pan3d/commit/53f016e492acdfdcd2bbe11adc50f7d0eaea930e))

* fix: convert more directive attributes to tuple syntax ([`469c511`](https://github.com/Kitware/pan3d/commit/469c5113bcc12fcc61b04e0abe5f1b27f75e6a34))

* fix: cast keys and values in `da_vars_attrs` to strings ([`bc8c319`](https://github.com/Kitware/pan3d/commit/bc8c319a230bea29c5ac6332b4fc2f8e47fe40a5))

* fix: cast objects to strings in template code ([`c8c66ba`](https://github.com/Kitware/pan3d/commit/c8c66baae1c9ad796c9826bf9c77e4751908059f))

* fix: stringify axes list for VSelect component ([`e783699`](https://github.com/Kitware/pan3d/commit/e7836993bbfba19a29a2485d02c99fab1977b42d))

* fix(setup): Add setuptools_scm to pyproject.toml; use git tag for version in build step ([`9c2789d`](https://github.com/Kitware/pan3d/commit/9c2789d0427ebd12d5d9398d4f4d51e21b804beb))

* fix(requirements): add trame-jupyter-extension to requirements.txt ([`91f253a`](https://github.com/Kitware/pan3d/commit/91f253a9e4860490bc1730ee11f4d183f4d2e4c7))

* fix(setup): use Dockerfile to specify uninstall of default vtk before install of vtk-osmesa ([`34c459d`](https://github.com/Kitware/pan3d/commit/34c459d20de43abe428ed968c3de44e79c6f5757))

* fix(setup): add vtk-osmesa to examples requirements for binder ([`5abfa59`](https://github.com/Kitware/pan3d/commit/5abfa5948f2caddd19dc4ff0d2f450c0af857dd0))

* fix(lint): run black ([`754d44d`](https://github.com/Kitware/pan3d/commit/754d44d955dc530a2203a3470fca7b2eaed836e4))

* fix(examples): update notebooks and add requirements.txt ([`406c76b`](https://github.com/Kitware/pan3d/commit/406c76baf5ce99259ecbd949a11947928f43e565))

* fix(dataset_builder): update export_config and mesh_changed functions ([`40e1b17`](https://github.com/Kitware/pan3d/commit/40e1b17aa439f6c79efa6f1075bb6ae6c18b85ec))

* fix(setup): specify packages list to override automatic packages discovery ([`a0f7941`](https://github.com/Kitware/pan3d/commit/a0f7941cc3a1ad230240deabc8bd0bca682ad756))

* fix(pyproject.toml): escape backslash characters in version pattern ([`66d8db9`](https://github.com/Kitware/pan3d/commit/66d8db9348b5ae07b2bab278fa4a3aada1ea89b8))

* fix(release): add a job to build dist folder ([`aa48f3a`](https://github.com/Kitware/pan3d/commit/aa48f3a58822ce00c6adde2969f9ea2259814061))

* fix(pyproject.toml): semantic-release v8 does not support setup.cfg ([`bda7a67`](https://github.com/Kitware/pan3d/commit/bda7a67b5cf9f7f0ac2d866b458ca9b767eb2353))

* fix(changelog): change misspelled word ([`e977de5`](https://github.com/Kitware/pan3d/commit/e977de5e5a0d458db95543bb578b3b89bde05151))

### Refactor

* refactor: Enable module in widgets, not dataset_viewer ([`1c4d30c`](https://github.com/Kitware/pan3d/commit/1c4d30cbab102623c7c4be0aaf73ef4fe768da1f))

* refactor: move widgets.py into pan3d_components ([`a28e308`](https://github.com/Kitware/pan3d/commit/a28e3083212c6c2dd0556228951f85d9f62a15d9))

* refactor: move `serve` directory within `module` directory ([`06bc8bd`](https://github.com/Kitware/pan3d/commit/06bc8bd0840bba4f662dbd1d16ac0d9180d69190))

* refactor: apply suggestions ([`c891b38`](https://github.com/Kitware/pan3d/commit/c891b387ed64989eaf1dda385f5cb3f26991d3c2))

* refactor: move module and serve dirs back into python package ([`73d24a4`](https://github.com/Kitware/pan3d/commit/73d24a45b0485502819862ba8a2f779595ef2f7f))

* refactor: move javascript code to its own top-level directory ([`7aa8ea9`](https://github.com/Kitware/pan3d/commit/7aa8ea9977829c1df43fce06c586b67cdb4e7ad3))

* refactor: apply suggested change from review ([`6d4f3ac`](https://github.com/Kitware/pan3d/commit/6d4f3ac37a73d5c099950e6241d197017b4d4c1d))

* refactor(catalogs): create base methods in catalogs module that dynamically import relevant submodules ([`633918d`](https://github.com/Kitware/pan3d/commit/633918d858ee32d476c7d76acbf2ceece309a87e))

* refactor: move `call_catalog_function` to `pan3d.catalogs.__init__.py` ([`01aee20`](https://github.com/Kitware/pan3d/commit/01aee20e85f86c707a5d465765ea128d35fefb6b))

* refactor: move catalog modules to new `pan3d/catalogs` folder ([`8a25e85`](https://github.com/Kitware/pan3d/commit/8a25e85d9f75fa7fa78ab2a19b9a7155f130a090))

* refactor: remove class-checking for specific pangeo catalog errors (avoid importing auxiliary libraries directly) ([`9456ca6`](https://github.com/Kitware/pan3d/commit/9456ca6931e60ad6dbd7ecc122ef3c49525d83af))

* refactor: replace branching if logic for catalogs with `builder._call_catalog_function` ([`ce02dd4`](https://github.com/Kitware/pan3d/commit/ce02dd403eb078d3fdedec2aa896c84be9aec2d9))

* refactor: use catalogs list kwarg instead of multiple boolean catalog flags ([`0b48175`](https://github.com/Kitware/pan3d/commit/0b48175a66348edf70a9d8da7ff438227a753ab7))

* refactor: separate default load dataset function for paths and urls ([`92b0845`](https://github.com/Kitware/pan3d/commit/92b084538db0d86cc2134c361fd1cdf7dc33549e))

* refactor: replace `dataset_path` with `dataset_info`;  value for `source` can determine which `load_dataset` method to use ([`ae545ae`](https://github.com/Kitware/pan3d/commit/ae545ae05acbb27d56f3a6404d127e375d19638f))

* refactor(pangeo): use methods similar to esgf module ([`3ed0b29`](https://github.com/Kitware/pan3d/commit/3ed0b29ece034dc1ad7788a3e12a3eac231c682f))

* refactor: suggested changes from @jourdain ([`3423103`](https://github.com/Kitware/pan3d/commit/34231038ac197dada66a74b1ac371be3654900d4))

* refactor(dataset_builder): separate trame and plotting from data configuration ([`4ea790a`](https://github.com/Kitware/pan3d/commit/4ea790a54ceec8e94a0df58b00d97ed70dfc8416))

* refactor: add lfs images ([`deb30ff`](https://github.com/Kitware/pan3d/commit/deb30ff4d09b5c880f1e2487634fdaea3c51077a))

* refactor: store docs images with git-lfs ([`c12e0c3`](https://github.com/Kitware/pan3d/commit/c12e0c30e481b7c985ff3c25ef7132da6f40b137))

* refactor: remove docs images (to be stored with git-lfs) ([`beb1b2a`](https://github.com/Kitware/pan3d/commit/beb1b2a18d451bbe7b5eb378115af35b6d436e81))

* refactor: rename `force_local_rendering` to `has_gpu_rendering` and negate result ([`2a39eda`](https://github.com/Kitware/pan3d/commit/2a39eda68490e7f2eed0ebe6d1625b45c95e4123))

* refactor: rename `_cloud` to `_force_local_rendering` ([`2b1c5a7`](https://github.com/Kitware/pan3d/commit/2b1c5a7ce89fc36c42eeb21607491d760feb905d))

* refactor(setup): delete setup.cfg ([`f68cd65`](https://github.com/Kitware/pan3d/commit/f68cd65ad75fe1ca5f43e770aa8c7fe8de0fa32e))

### Style

* style: Use double quotes ([`bf128ba`](https://github.com/Kitware/pan3d/commit/bf128ba380135ed2b2a90b34fea5288843b799a4))

* style: reformat with black ([`cfa631b`](https://github.com/Kitware/pan3d/commit/cfa631b8296dbcd019945a956ea10f513c3a9410))

* style: add trailing comma ([`5ac37cd`](https://github.com/Kitware/pan3d/commit/5ac37cdcd4955f8613e020e3e41baed113cb288c))

* style: reformat with black ([`ffce418`](https://github.com/Kitware/pan3d/commit/ffce418ddbb34f58d37a9c60ecb96f27cee3b7c0))

* style: reformat with black ([`2860427`](https://github.com/Kitware/pan3d/commit/28604277b68a9aaf5b02fe59cf670b2882304653))

* style: remove print statement ([`cca89e1`](https://github.com/Kitware/pan3d/commit/cca89e170f8b6eae33737b2274b296f3feeeb8c5))

* style: fix automatic formatting of list by removing comma ([`b28f444`](https://github.com/Kitware/pan3d/commit/b28f444fa48edf94560a37aab0d1f2f02c38641c))

* style: reformatting with black ([`687e370`](https://github.com/Kitware/pan3d/commit/687e370703920fba3d29267fadb3c56207e7633d))

* style: update style via black ([`de58bfd`](https://github.com/Kitware/pan3d/commit/de58bfd95002d387a1afe55e2a8085a63f43ea26))

* style: Reformat with black ([`78efd90`](https://github.com/Kitware/pan3d/commit/78efd90fc218953f19c5c364b9a7b305fb443a89))

* style: Reformat with black ([`fb36747`](https://github.com/Kitware/pan3d/commit/fb3674706e080ef32c956a1ea6eaeb7098ccae81))

* style: fix formatting ([`599c1e2`](https://github.com/Kitware/pan3d/commit/599c1e2b525a0ec39435dca5a0e3786f7996e4e5))

* style: fix formatting ([`a698eca`](https://github.com/Kitware/pan3d/commit/a698ecad3bcba57b261321a8c7e69dd9840e7f14))

* style: fix formatting ([`39cae23`](https://github.com/Kitware/pan3d/commit/39cae2386a7a9f9e4a3e58edd5a44193823429a6))

* style(css): hide scroll bar by default ([`d55c2ac`](https://github.com/Kitware/pan3d/commit/d55c2acc374f63c1d898b94dd31c655085934e61))

* style: Use black to fix styling ([`cd61185`](https://github.com/Kitware/pan3d/commit/cd611853756376747815dffa1311c9a4a7819b83))

* style: replace 2 tutorial images with rotated worlds ([`b6abe09`](https://github.com/Kitware/pan3d/commit/b6abe092a821d6709b45bddc89bf7642a137b109))

* style: Use black to fix styling ([`26708bd`](https://github.com/Kitware/pan3d/commit/26708bdc9fa6dfeb222486a04fca1fcf5a6eca4c))

* style: switch cover image in README ([`d7db238`](https://github.com/Kitware/pan3d/commit/d7db2382369c7a0d004a4d0f142dd3862d282a39))

* style: Use black to fix styling ([`a8cbaab`](https://github.com/Kitware/pan3d/commit/a8cbaabebc940836ca84f139c84883850531831f))

* style: apply changes from black ([`0d06d82`](https://github.com/Kitware/pan3d/commit/0d06d82d638438a25c4953cfddf10a8a3f78d608))

* style: prefer double-quotes ([`d77d630`](https://github.com/Kitware/pan3d/commit/d77d630b15da084f4d9fff4353e530c66f1f787f))

### Test

* test: Update expected values in tests ([`e08af6b`](https://github.com/Kitware/pan3d/commit/e08af6b40fb2a17f689071a8b484e69b9157c97b))

* test(builder): Add test to cover invalid values to DatasetBuilder setters ([`93326fd`](https://github.com/Kitware/pan3d/commit/93326fd26fe195e7c853860fe751963ba47439e3))

* test: update tests with `dataset_info` values instead of `dataset_path` values ([`15cf1d0`](https://github.com/Kitware/pan3d/commit/15cf1d03ea021a1600c34090705774b62b20ed4a))

* test: update expected state with new default expanded coordinates ([`87e073c`](https://github.com/Kitware/pan3d/commit/87e073cf94bf2e4a51b73ed837a75ab42e0712c3))

* test: update expected state with new drawer defaults ([`954969f`](https://github.com/Kitware/pan3d/commit/954969f56dfa705429b80f867b18e9161d9f62fb))

* test: disable `DatasetViewer` automatic render in tests ([`203569a`](https://github.com/Kitware/pan3d/commit/203569ab48f4aef409090c4748de895113345d79))

* test: update main testing workflow ([`39eb6b1`](https://github.com/Kitware/pan3d/commit/39eb6b1537ae44e2fcd349ec13cee486bcee3a5f))

* test: add tests for builder and viewer ([`deae267`](https://github.com/Kitware/pan3d/commit/deae26704d2448f81e9266e8649dd11bec52069d))

* test(export): re-export `example_config_xarray.json` ([`7f6be7c`](https://github.com/Kitware/pan3d/commit/7f6be7cfc84ec5b387b6ce06cf7028193d79c26b))

* test(pre-commit): omit changelog from codespell ([`38efb4f`](https://github.com/Kitware/pan3d/commit/38efb4f29bcf9d1710557a16f749865191247dc7))

* test(export): remove time slicing to match exported config ([`cb08b41`](https://github.com/Kitware/pan3d/commit/cb08b417535654cd549892c30be41ccfbd58a78e))

### Unknown

* Merge pull request #78 from Kitware/auto-slicing

Improve Coordinate Indexing &amp; Slicing ([`c17d6b7`](https://github.com/Kitware/pan3d/commit/c17d6b76dd04d7f2f36b85c1ee0d87a1c85b8133))

* examples: add cartographic mode to noaa example ([`54d90ad`](https://github.com/Kitware/pan3d/commit/54d90ad6965256484b8d2dd5571cb48e739f03d9))

* setup(install): add `all` requirements group ([`8aa8780`](https://github.com/Kitware/pan3d/commit/8aa878078516f1645f511a7f14d91ff2125758fa))

* More doc changes

* Change title from &#34;local server to a more general &#34;command line&#34;
* Change pip instruction to include [viewer]
* Show more code in jupyter_notebook.md
* Also fix mkdocs warning in dataset_viewer.py ([`6607718`](https://github.com/Kitware/pan3d/commit/66077188ea579a54cbbe244133114c123ca5b985))

* tests: remove check for loading state in export ([`ecb36bc`](https://github.com/Kitware/pan3d/commit/ecb36bc1d7280162a2bb9c426d4678afbe907e1b))

* ui: Adjustments to main drawer and catalog search components ([`ace8d3c`](https://github.com/Kitware/pan3d/commit/ace8d3c85086a9641c863a2691a81d6cedbc2607))

* setup: Add Pangeo section to optional dependencies ([`be4e617`](https://github.com/Kitware/pan3d/commit/be4e6173e0fab965f3bea61aa95cadb996ab8821))

* wip: update Pangeo module with congruent API to ESGF module; functions still need implementation ([`84a2406`](https://github.com/Kitware/pan3d/commit/84a2406830d37ff156f01b83e392de311b4b5d1d))

* wip: update Pangeo module; needs catalog search functions ([`231fed5`](https://github.com/Kitware/pan3d/commit/231fed50c7b684c60af46e7725688a2a60c1e043))

* setup: specify minimum versions for requirements in pyproject.toml ([`bdbfcc0`](https://github.com/Kitware/pan3d/commit/bdbfcc0ef435363436c9162e3c48517157c90073))

* ui: change loading widget style ([`5aeec3c`](https://github.com/Kitware/pan3d/commit/5aeec3c0baea229aa3ae4f4df33dbe5c973f42cf))

* ui: Differentiate between icons for menus and drawers on the left and right sides ([`4f98d1d`](https://github.com/Kitware/pan3d/commit/4f98d1ddabc2f74bea0b6d44495c2b61e95ad2f9))

* setup: move trame dependencies to [viewer] option ([`854a6c2`](https://github.com/Kitware/pan3d/commit/854a6c23a85e1304fc00e75ede39f3ff66990a51))

* ui: collapse pyvista plotter toolbar by default; avoid looking cramped in notebook output ([`9ed0161`](https://github.com/Kitware/pan3d/commit/9ed01618c57ad1b8ac0d530297a9077535b4d657))

* launch: allow --debug argument passed through to server ([`1b0c60c`](https://github.com/Kitware/pan3d/commit/1b0c60c8903796a209692c6646f3bf246a3ffffc))

* debug: Add print statement for select component ([`53ca0b2`](https://github.com/Kitware/pan3d/commit/53ca0b266fc6d60fb5c22151939e942669760fa1))

* Separate PyPI publish from semantic release job ([`c436655`](https://github.com/Kitware/pan3d/commit/c4366558f1e277d98f904bb930e6090e25a6b532))

* Update CI action to publish on PyPI ([`104f81a`](https://github.com/Kitware/pan3d/commit/104f81a34f0b727ac9062561bd968e1fa1a38b6a))

* Rename mesh-&gt;_mesh, pv_mesh-&gt;mesh ([`03792a5`](https://github.com/Kitware/pan3d/commit/03792a5e1d6283eb99c0da562d93f8073ff9d645))

* Remove unused import of `get_catalog` ([`877d9dd`](https://github.com/Kitware/pan3d/commit/877d9dd88ed9392218235cdeaef14f230a202278))

* Reformatting by Black ([`722195f`](https://github.com/Kitware/pan3d/commit/722195f89ab0a47fa6612650183c6db32f255689))

* Allow user to view attributes for available arrays ([`cf905a5`](https://github.com/Kitware/pan3d/commit/cf905a5bb0e9c00f012aa57cc34b45c5943fdf9e))

* Create static list of compatible pangeo forge datasets ([`075c390`](https://github.com/Kitware/pan3d/commit/075c3907358e04fb6908f9b4229d639edd02c720))

* Compatibility with more date types ([`125103d`](https://github.com/Kitware/pan3d/commit/125103d6d42962195e86c7d4f6177a350dc0c4e1))

* Fix coordinate and slicing assignments ([`ab5e135`](https://github.com/Kitware/pan3d/commit/ab5e13521577d842dfac10d41e675a3dab565032))

* Move Dataset Attributes to a dialog (sidebar too narrow) ([`af1b703`](https://github.com/Kitware/pan3d/commit/af1b703606f12bd52200a8fa69987785d88a9cf4))

* Make time indexing compatible with datetime64 dtypes and more human-readable ([`8459ccc`](https://github.com/Kitware/pan3d/commit/8459ccc4bd763a76137ad6390abfde9afa6c1afa))

* Use controller functions instead to reset view ([`81cf17b`](https://github.com/Kitware/pan3d/commit/81cf17b643b3fc4e6b5899044324afbe9695849e))

* Add reset camera call to `plot_mesh` function ([`99c399e`](https://github.com/Kitware/pan3d/commit/99c399e38d35da080374eed346745fe5c2423e6c))

* Fix imports ([`d1f792f`](https://github.com/Kitware/pan3d/commit/d1f792fffbd8e7537910e03261fbdf3b226b4835))

* Black Lint fixes ([`5529a0a`](https://github.com/Kitware/pan3d/commit/5529a0ac4f117cd9bc555911eb2ed4da51751b12))

* Add UI panel to change render options ([`2444d94`](https://github.com/Kitware/pan3d/commit/2444d94055a69006f1d5c8558662c57794ecacd4))

* Lint fixes via Black ([`41a71d2`](https://github.com/Kitware/pan3d/commit/41a71d2c4ebcfd791bdaa813108629626d4440c2))

* Fix edge case bugs ([`b0ea813`](https://github.com/Kitware/pan3d/commit/b0ea813bbdb13ecb456379dffe434dc5400fe6d5))

* Change expected size for sliced array in test_import_config ([`ad1af03`](https://github.com/Kitware/pan3d/commit/ad1af031daedf28a6cad21128b315696dfac54c7))

* Reduce redundant algorithm modifications (&amp; therefore repeated slice computations) ([`7436c03`](https://github.com/Kitware/pan3d/commit/7436c0346fa343706e78e5b03fc517f8e8361c29))

* Remove time printouts ([`9a118ab`](https://github.com/Kitware/pan3d/commit/9a118abda17550f50d9e880ea4f770517992da7d))

* Access mesh by property on algorithm, not compute function ([`f262f06`](https://github.com/Kitware/pan3d/commit/f262f067737887cf3cddb80a78b97548904660a7))

* Add back data array property ([`fb48a4a`](https://github.com/Kitware/pan3d/commit/fb48a4ac675e4897b15117d018f7ce7a7a2c9653))

* Fix example file names in testing ([`6d32950`](https://github.com/Kitware/pan3d/commit/6d329503e9dfa99a9117c64ef7c08ffb1d533772))

* Use new Pvyista-Xarray Algorithm capabilities ([`ff5b1a5`](https://github.com/Kitware/pan3d/commit/ff5b1a5498e69e1453c431625ae2622296980ee8))

* Small UI fixes for smaller window sizes ([`de7ae7c`](https://github.com/Kitware/pan3d/commit/de7ae7cc251c95a9df1ca495261a407d1ed5ad75))

* Auto assign axes for i-j-k ([`280c968`](https://github.com/Kitware/pan3d/commit/280c9686d93e95a72522b9420b417dae3ffc74ce))

* Add new example config and rename old ones ([`f259004`](https://github.com/Kitware/pan3d/commit/f259004bb26c82a9ce4df0abbd689d9cf8bb2e4d))

* Add immediate side effect for da_active, too ([`401b914`](https://github.com/Kitware/pan3d/commit/401b9148047affbf14a76a076d2c2adf5ced16a7))

* Add example notebook using user-accesible state-setting functions ([`de2a7b2`](https://github.com/Kitware/pan3d/commit/de2a7b23ba08fcc7d124b6ebf913621a73ca1ebf))

* Immediate callback during set_dataset_path ([`e77cd5f`](https://github.com/Kitware/pan3d/commit/e77cd5ff13d131282e9de2622b55f14c0ff65325))

* Allow &#34;pangeo&#34; arg to determine whether to fetch pangeo forge datasets ([`af077f2`](https://github.com/Kitware/pan3d/commit/af077f2debc48644ee06100e888e8155066466d1))

* Separate user-accesible state change functions and rename dialog-relevant state vars ([`3dbf538`](https://github.com/Kitware/pan3d/commit/3dbf53847c7047f7f722597d1ebfa350a8c8cff4))

* Use pathlib read_text and write_text ([`c1caef4`](https://github.com/Kitware/pan3d/commit/c1caef45e9cebb0bcfcd968e943704592e606c92))

* Combine functions for da_[axis] state change ([`6ba41e8`](https://github.com/Kitware/pan3d/commit/6ba41e8eec4874df050afe443eed06f66c9113b5))

* Change default value for step to 1 ([`546dea4`](https://github.com/Kitware/pan3d/commit/546dea4c7586304344d2a3cc7a45972db65d3ae7))

* Change pangeo forge example to use import, allow passing dict to import function ([`8927485`](https://github.com/Kitware/pan3d/commit/89274855484137dd8f8ef59cacc649a583b67ee7))

* Manage drawer states manually, use VAppLayout instead of SinglePageWithDrawerLayout ([`72c5353`](https://github.com/Kitware/pan3d/commit/72c535344eae0e1ce1e6f7a129157977c9dff81e))

* Change state variable names to group &#34;ui&#34; and &#34;da&#34; relevant vars ([`6437fe8`](https://github.com/Kitware/pan3d/commit/6437fe88f8885f7d371c009020b0f56ff70a39f8))

* Remove redundant state modifications ([`2e53021`](https://github.com/Kitware/pan3d/commit/2e530218abf07d11947f12a0bf213a2d1e191aba))

* Shorten property lists where mapping does not require tuples ([`99ea334`](https://github.com/Kitware/pan3d/commit/99ea334da548947049425c98756b0a573982756c))

* Prefer f-strings where possible ([`b74cd66`](https://github.com/Kitware/pan3d/commit/b74cd669f442aa18c10bceab8f4f87327760f902))

* Fix example config files for tests ([`a349d79`](https://github.com/Kitware/pan3d/commit/a349d7968e06617d2a8e832ef76326110f58891e))

* Fix modifying expanded_coordinates in UI ([`a39bc9a`](https://github.com/Kitware/pan3d/commit/a39bc9a16c075a833e28007b6616d0859be61bd8))

* Fix values in example config files ([`e675365`](https://github.com/Kitware/pan3d/commit/e675365dd5c8e30d1379ed9c4826c69100e3e1fa))

* Fix display of slicing values, allow slicing for t axis ([`4f452d1`](https://github.com/Kitware/pan3d/commit/4f452d16d2f6e8b6400418c404ce62c5e5dd0d48))

* Reorganize import/export file format ([`fcf0a49`](https://github.com/Kitware/pan3d/commit/fcf0a49bd116bac5d072cc5ad6e5b9cd63c4183a))

* Remove unused/redundant state vars ([`a3c91ee`](https://github.com/Kitware/pan3d/commit/a3c91eeed7da489f9533120187e823511e971d3a))

* Fix updating coordinates after import ([`a085a5b`](https://github.com/Kitware/pan3d/commit/a085a5b87bf9689d246f28b4ff7f9a14aa014f17))

* Protect against edge cases ([`637a242`](https://github.com/Kitware/pan3d/commit/637a242c6d917d109d04bc1183e745ab04b216c7))

* Reduce calls to `data_array` ([`8d8f379`](https://github.com/Kitware/pan3d/commit/8d8f379fd100eece5f44a60b4b5930252ff8aa3d))

* Switch lon/lat in example config ([`06c5291`](https://github.com/Kitware/pan3d/commit/06c529127cdd876ec27dcf3efca6d840399556e1))

* Add a new test to compare import &amp; export ([`d54cdcc`](https://github.com/Kitware/pan3d/commit/d54cdcc722b12be16b6769380dab34e8aad9b380))

* Add download support for browsers without File System API ([`bb7cccf`](https://github.com/Kitware/pan3d/commit/bb7cccfa9d93392abd4b9fb8ba81eff0fb23c2f6))

* Update config examples ([`f8d2d0b`](https://github.com/Kitware/pan3d/commit/f8d2d0b0579013976fb5521aa595d29aa11dae0b))

* Add export functionality ([`9556d34`](https://github.com/Kitware/pan3d/commit/9556d34c5e5822eb302957cab6611a850a870df1))

* Fix switching between active arrays ([`8e3fe83`](https://github.com/Kitware/pan3d/commit/8e3fe83e50575850a722f15546dad893784c56fc))

* Add import and export buttons to the toolbar ([`8da1f08`](https://github.com/Kitware/pan3d/commit/8da1f08961ce8fcfc63dd5eff45493a66a17ddb6))

* Allow specifying expanded_coordinates in config ([`7dce23f`](https://github.com/Kitware/pan3d/commit/7dce23f02b682c4f54f40966279a949f6f8c0078))

* Accept coordinate config from import file ([`ff80bda`](https://github.com/Kitware/pan3d/commit/ff80bda113b7c1751ef9dc552ce8610421e53f1e))

* Update example config ([`ed09cf0`](https://github.com/Kitware/pan3d/commit/ed09cf0fe1c03f43e71369a558859a8e91c9cc6e))

* Use bracket notation instead of setattr ([`ee9b6ea`](https://github.com/Kitware/pan3d/commit/ee9b6ea45af72f0e54b2be91eb8712bc48948daa))

* Add `dirty` statement in `on_set_array_active` ([`9a90808`](https://github.com/Kitware/pan3d/commit/9a9080848b4d2ca755ec29f1fd3b04b00d976f45))

* Remove `.keys()` from `len` calculations ([`576307c`](https://github.com/Kitware/pan3d/commit/576307cb89034b7b286d5b84cffcfd4ba31e51c2))

* Manage expanded panels in state; otherwise all open on state change ([`8139fcb`](https://github.com/Kitware/pan3d/commit/8139fcb5e1d1b055fe2a72f3e8bbac69eef35aa7))

* Make sure coordinate start, stop, and step changes are reflected in client ([`0d22afa`](https://github.com/Kitware/pan3d/commit/0d22afa0060ec4936bb9d1173a1a4a091fb26b85))

* Change step maximum to array size ([`759c749`](https://github.com/Kitware/pan3d/commit/759c749a1431fadbf1d2377dfe5d8a2c903b6342))

* Use a slider to select index instead of start, stop, and step for coords assigned to T ([`4fb20e6`](https://github.com/Kitware/pan3d/commit/4fb20e6c8246e41a37c9469ff07e2b6b30054bce))

* Add range to coordinate attrs table ([`03cc460`](https://github.com/Kitware/pan3d/commit/03cc460aa38b45f263d55b766913fc7f27487669))

* Fix axis Select slot, only show assigned value ([`d86b4bb`](https://github.com/Kitware/pan3d/commit/d86b4bb38499270dd62b64bb611d5527ed52e742))

* Remove dividers (visual clutter) ([`58aaffd`](https://github.com/Kitware/pan3d/commit/58aaffdc4d162fefccb943f2abdc6f2ac97186ea))

* Add coordinate attributes tables ([`383a567`](https://github.com/Kitware/pan3d/commit/383a567f9fb24b7623c0027a16dc5ea51f35d4f0))

* Change appearance of apply button ([`e60439e`](https://github.com/Kitware/pan3d/commit/e60439e013b4b207145031f3477dce6d82a659ce))

* Switch lon/lat default axis assignment ([`685ca42`](https://github.com/Kitware/pan3d/commit/685ca428c0afa8c330f3e7c4fe21fce07aacb295))

* Remove all references to resolution as a state variable ([`ad1ef18`](https://github.com/Kitware/pan3d/commit/ad1ef1846fe73ad816fda1e405f2a15529395977))

* Implement changing data_array with coordinate starts, stops, and steps ([`f61adcb`](https://github.com/Kitware/pan3d/commit/f61adcbf3285edb28901501f3b19452c114b20c0))

* Change display of axis placeholder card (when no coordinate assigned) ([`6b7d97a`](https://github.com/Kitware/pan3d/commit/6b7d97aa326cb720a221c8d864c593efe4740aec))

* Change width of righthand drawer ([`32aa38f`](https://github.com/Kitware/pan3d/commit/32aa38f3dc8e7d936b08508cf8cd72af5b87d124))

* Fix display of selected axis ([`a9e5454`](https://github.com/Kitware/pan3d/commit/a9e54549be9a25b04d3a07a2f4d84fd15f44bc02))

* Switch back to VTextField, specify mapping of min and max attrs ([`e067bbe`](https://github.com/Kitware/pan3d/commit/e067bbef66e1b1f99e31ede04134ea752e509be8))

* Store coordinate slices on state.coordinates and edit in coordinate configuration ([`54ef006`](https://github.com/Kitware/pan3d/commit/54ef006a42cbc058de0f7ed3c02da2ea82d2662d))

* Refactor AxisConfigure -&gt; CoordinateConfigure ([`65fa5d5`](https://github.com/Kitware/pan3d/commit/65fa5d521c8fe115d306fccf1c924b11d1d71ef8))

* Add coordinate auto-selection ([`fbb19d4`](https://github.com/Kitware/pan3d/commit/fbb19d470b7e5c681edac05c7cd40aedb6520728))

* Use uppercase arg shortcuts (avoid conflict with &#34;-d/--debug&#34;) ([`0e2a30d`](https://github.com/Kitware/pan3d/commit/0e2a30db7a538c4f791591231c0c0880a99e98e5))

* Use better code for accessing custom style file ([`41fe985`](https://github.com/Kitware/pan3d/commit/41fe985bd7eb6ba16877d6685668b381decc2ed4))

* Condense axis state reset ([`797499f`](https://github.com/Kitware/pan3d/commit/797499f07ffbf8db50d8039d76a118fe1f34412c))

* Use pathlib.Path for accessing custom style file ([`de8774e`](https://github.com/Kitware/pan3d/commit/de8774e25c2bb46d30d4de57119ac78c28abdb02))

* Resolve merge conflicts ([`7286d61`](https://github.com/Kitware/pan3d/commit/7286d610c5f604839cdc884fa0a1a3d446bf7885))

* Minor spacing fix ([`d94d9ed`](https://github.com/Kitware/pan3d/commit/d94d9ed29e48f888e0b45d1b5a23d9b3711ec875))

* Fix custom css file reference ([`d7bb4b5`](https://github.com/Kitware/pan3d/commit/d7bb4b567c4994dc42c48f14ff4c96750eab878e))

* Use vuetify 3 API ([`4512d63`](https://github.com/Kitware/pan3d/commit/4512d63c640de71f15666fc94bd3554a59a02b35))

* Prevent axis select input from changing on select event ([`8c3729e`](https://github.com/Kitware/pan3d/commit/8c3729e69de00399cfe76eb572eb11d8fdc9eab0))

* New layout of Axis Selection component with basic assignment only ([`5a31dd2`](https://github.com/Kitware/pan3d/commit/5a31dd203613a79f87377f1f55f4f0fbb5aa2edf))

* Shift axis selector component placement ([`ad379f3`](https://github.com/Kitware/pan3d/commit/ad379f3f0823805817423bb90eeeadf47153b9cc))

* Allow --server arg to main ([`44a4dfc`](https://github.com/Kitware/pan3d/commit/44a4dfc42d4514acab00f1f7c83dcc0c386d6058))

* Allow other xarray engines for other file types ([`aff7763`](https://github.com/Kitware/pan3d/commit/aff7763f02ace9a7fad8e07c78a51ac5c11ba0fb))

* Fix `pan3d-viewer` console script ([`0fe727e`](https://github.com/Kitware/pan3d/commit/0fe727ed03b44935fc2812d175f3e368f0cfb767))

* Invoke viewer prop in server start ([`1980b56`](https://github.com/Kitware/pan3d/commit/1980b5657dd6925e04a0d778f0ebe01084414020))

* UI macro components accept state var names as parameters, but with expected values as defaults ([`c59a8ad`](https://github.com/Kitware/pan3d/commit/c59a8ad3355969cfaa8774378d1793052ccad580))

* Make layout an internal variable ([`ba93490`](https://github.com/Kitware/pan3d/commit/ba9349050363b9faff64acf2d35c7ef578984c4c))

* Dissolve RenderArea component into main class ([`0344356`](https://github.com/Kitware/pan3d/commit/03443569f54640632f13b48b046e4dbcf3349605))

* Call viewer in main so lazy load occurs ([`6a0a29a`](https://github.com/Kitware/pan3d/commit/6a0a29a9e427791337cb865f64ff519f7e4681e2))

* Remove the word &#34;bookmark&#34; from notebook examples ([`c6d42ed`](https://github.com/Kitware/pan3d/commit/c6d42ed6a72888170d9b2705bf768a518a0f9ac2))

* Start with layout = None ([`6bd1381`](https://github.com/Kitware/pan3d/commit/6bd1381e80225172c6429cb1d4a1398a0d8d2626))

* Lazy-load layout ([`b261f91`](https://github.com/Kitware/pan3d/commit/b261f91d9de5c817f3c22110abca4ed78e0ba9ef))

* Remove reference to main class as `viewer` ([`28026cd`](https://github.com/Kitware/pan3d/commit/28026cdca86503e5e3377c80a9ff606cd86bf30b))

* Add a print line to example notebook, showing access to vtk data array ([`fcf9a50`](https://github.com/Kitware/pan3d/commit/fcf9a501a6be336a3710a4387886b919b1a54c06))

* Fix test config ([`76e8780`](https://github.com/Kitware/pan3d/commit/76e878076c4036b679af670361aa2a17bdc7d9df))

* Rename feature bookmark -&gt; config ([`27604b1`](https://github.com/Kitware/pan3d/commit/27604b135a0df3b1528046ca659724fabf8f17ee))

* More UI component refactoring ([`790a57d`](https://github.com/Kitware/pan3d/commit/790a57d07cead815fc412d7d48e18875bb8e84e8))

* Rename property gui -&gt; viewer ([`53c8397`](https://github.com/Kitware/pan3d/commit/53c839707e4235aedfe6c69b716814fbcd058bb4))

* Don&#39;t pass layout to components ([`9f2acb7`](https://github.com/Kitware/pan3d/commit/9f2acb7ba64e9a7579a50d0cdb0cbbee9644beb1))

* Break ui file into macro components ([`d10da4c`](https://github.com/Kitware/pan3d/commit/d10da4c221cf78208c17add486756b680a72f91c))

* Class rename Pan3DViewer -&gt; DatasetBuilder ([`371fe1a`](https://github.com/Kitware/pan3d/commit/371fe1a7e2c17abf4f66507789a7095b104d62df))

* Remove some redundant lines ([`8860b8a`](https://github.com/Kitware/pan3d/commit/8860b8a7567ee5bc34d51641e0ac834ee2e6164d))

* Update tests ([`6a4791d`](https://github.com/Kitware/pan3d/commit/6a4791d261f7bd539b09cbe2792cc60f00e04082))

* Adjust ui function for changing active array ([`f8e1a0e`](https://github.com/Kitware/pan3d/commit/f8e1a0eeb0e9d576c2bc5f105a2bab9c5ea097d5))

* Allow specifying dataset_path or bookmark_path via cli ([`bc1ef44`](https://github.com/Kitware/pan3d/commit/bc1ef445fceda601af433180a5de4da8e39b2a67))

* Update jupyter example ([`6fed2f7`](https://github.com/Kitware/pan3d/commit/6fed2f77ea24d0f3171ce523c2c86407e6ed1d54))

* Refactor to Pan3DViewer class structure ([`e52756c`](https://github.com/Kitware/pan3d/commit/e52756c1015edca9d9968fdf14e79975fbdd9d03))

* Update gitignore ([`b2ba771`](https://github.com/Kitware/pan3d/commit/b2ba77114f8e3d5ddd8e2197d1a3a1d0ce14a511))

* Add back clim arg to add_mesh ([`14eed86`](https://github.com/Kitware/pan3d/commit/14eed869205516a495c50d4591ba521c5de1ea5b))

* Apply button shows data array size ([`6c248ee`](https://github.com/Kitware/pan3d/commit/6c248ee64054836f226b1445973fc0f7868dc29b))

* Adjust slider controls ([`0767c37`](https://github.com/Kitware/pan3d/commit/0767c37f24de11fb177017656229a7d6948f78fb))

* Use resolution in data_array getter ([`31b7510`](https://github.com/Kitware/pan3d/commit/31b751065f543cbd5e7a19e741a3e08fa947e46f))

* Use separate thread and event loop for mesh tasks ([`c301dca`](https://github.com/Kitware/pan3d/commit/c301dca77adbed6b6109f530d58aa7b76bcc5237))

* Remove reset on state change, perfect state will render pangeo forge data ([`af48099`](https://github.com/Kitware/pan3d/commit/af480993d3eba1ea248d4501b2c06ac40b264ebe))

* Update pvxarray and add necessary deps ([`94c308c`](https://github.com/Kitware/pan3d/commit/94c308cf75779b08100115c3e8320746add76c83))

* Run mesh update asynchronously in reset function ([`bd3a7dc`](https://github.com/Kitware/pan3d/commit/bd3a7dc33a5f7fd1318fd5e60d801828282461d0))

* Clear plotter on reset ([`a29dff6`](https://github.com/Kitware/pan3d/commit/a29dff6b8dbe39ec0b88a8b73edcb7e310c8605f))

* Add dataset dimensions to data atrributes table ([`efbe7fe`](https://github.com/Kitware/pan3d/commit/efbe7fec7baad4bd0cbce515582a3236219aff39))

* Correct label on Xarray examples ([`f8678eb`](https://github.com/Kitware/pan3d/commit/f8678eb5a5ffa1015cf0f6a8a92b6e0af38bbe5f))

* Fetch available datasets from pangeo forge ([`e81c501`](https://github.com/Kitware/pan3d/commit/e81c50111cecf1b3b40ed07324dcb4ffee11b327))

* Change label for time slider ([`c91393b`](https://github.com/Kitware/pan3d/commit/c91393b648122c60772f7fc75a36648529cc9797))

* Call `validate_mesh` before algorithm `Update` to avoid vtk warnings ([`d0d6703`](https://github.com/Kitware/pan3d/commit/d0d6703246658e9f5996ce66223e923c3cfd273e))

* Add time indexing in validate mesh function ([`54dde27`](https://github.com/Kitware/pan3d/commit/54dde27e8b84a9452b213498461fb9b26d25d1ee))

* Use `mesh` method to check data validity instead of `RequestData` ([`a1f510b`](https://github.com/Kitware/pan3d/commit/a1f510b93434684af99e430dd567a0d1ed2f95cd))

* Add trame-vuetify and trame-vtk to dependencies to comply with trame@3 ([`4d72465`](https://github.com/Kitware/pan3d/commit/4d72465db4c087a0e8523e048a4b05a9727b59c0))

* Use plotter_ui from pyvista.trame.ui ([`a3be7ab`](https://github.com/Kitware/pan3d/commit/a3be7ab8f126045d7a5d6fe788ac9c9bf2e8c251))

* Auto reset and display any error messages ([`ed63e94`](https://github.com/Kitware/pan3d/commit/ed63e9497f4139fb955a36e090f30ea527eb6052))

* Rearrange UI and auto-select first available array ([`f23a11c`](https://github.com/Kitware/pan3d/commit/f23a11c89701df8e13672ef0b0b1ad304ffc59b0))

* Promote src contents to top-level, delete other modules ([`7c885cb`](https://github.com/Kitware/pan3d/commit/7c885cbf8bd0e562b1aec24091ba1923d19e6a18))

* Use single dockerfile for build (following example from trame/examples/deploy/docker/SingleFile) ([`07469d8`](https://github.com/Kitware/pan3d/commit/07469d849f28ad3c678426f72492dfcea2c8fbfd))

* Put the second dockerfile back ([`0f6700c`](https://github.com/Kitware/pan3d/commit/0f6700ccdf23a008904840d570693798920cd94f))

* Remove git install from dockerfile ([`82b42b9`](https://github.com/Kitware/pan3d/commit/82b42b957d2255c3375c02cbcae1d1156ae9bc8e))

* Add back cases for pushing docker image ([`c0cd3ad`](https://github.com/Kitware/pan3d/commit/c0cd3ad29e1d81a2db25fe1668af782e097e451d))

* Fix pyvista requirement (feature has been merged) ([`26f447a`](https://github.com/Kitware/pan3d/commit/26f447a26b9d93910b0c25378bba4ff86606fdd1))

* Fix spelling errors ([`3cb0e24`](https://github.com/Kitware/pan3d/commit/3cb0e24b8d285f670085e98e0efd242b347cd6b5))

* Fix dockerfile ([`271c8cf`](https://github.com/Kitware/pan3d/commit/271c8cfe1d9e88620f42394f3b96c042fd70ff32))

* Fix format errors ([`1289b44`](https://github.com/Kitware/pan3d/commit/1289b448c7caeb4bb5fe7e1b150bbab380cec2f2))

* Fix Github actions ([`875a6bf`](https://github.com/Kitware/pan3d/commit/875a6bfb717e7173f480411a5d035437193cfc4a))

* Add Docker build/publish GHA (#21)

* Add Docker build/publish GHA

* fix working-directory

* Fix

* Fix image name ([`128441f`](https://github.com/Kitware/pan3d/commit/128441f266f9895dbf69de98e9d906f0d4d2114e))

* Fix build ([`2172675`](https://github.com/Kitware/pan3d/commit/217267584d56599a0d62112d946d91aea11ef679))

* Remove unneeded styling ([`e294a1d`](https://github.com/Kitware/pan3d/commit/e294a1dd1d8a6eec56b1d6818a157e8d8bae75d2))

* Fix dependencies ([`8157980`](https://github.com/Kitware/pan3d/commit/81579806384a377728e0dccaef78f90a8b5c6a63))

* Update gitignore ([`22e818e`](https://github.com/Kitware/pan3d/commit/22e818ef06d7f1d10d1c25c843fbf7ba63a23bad))

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
