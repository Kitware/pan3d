# CHANGELOG


## v0.16.1 (2025-04-16)

### Bug Fixes

- **slice explorer**: Slice slider won't show with summary toolbar
  ([`5d03277`](https://github.com/Kitware/pan3d/commit/5d03277551aef5d2a8e9c82622212daca91d1888))


## v0.16.0 (2025-04-15)

### Bug Fixes

- **adding documentation**: Adding documentation to the methods
  ([`de356ec`](https://github.com/Kitware/pan3d/commit/de356ec1d224ea2db6a88929740fedd48bfdcd69))

- **analytics explorer**: Figure annotations updated to use long_name
  ([`671396f`](https://github.com/Kitware/pan3d/commit/671396ff65b40acd3f058dd07373221156917ed1))

- **analytics explorer**: Improvements to the app
  ([`00a6df4`](https://github.com/Kitware/pan3d/commit/00a6df42912eeee3dc849f8c164394e6761e75a3))

-- Refactor based on new explorer class -- Adding plot button to toolbar

- **broken import**: Report error if xcdat missing in analytics explorer
  ([`74c0e85`](https://github.com/Kitware/pan3d/commit/74c0e854e439d88a1aa7558d1491081173b38b1f))

- **config color map**: Changing default color map from config
  ([`5ec7b57`](https://github.com/Kitware/pan3d/commit/5ec7b57a7c759bd642aa0da588997a3bfc262c07))

The `esgf` color maps are no longer kept in pan3d

- **refactor**: Adding refactored changes for analytics explorer
  ([`73d3ef9`](https://github.com/Kitware/pan3d/commit/73d3ef9a748e150ca46134631cd4db65bb0b3545))

### Features

- **analytics explorer**: Adding half baked analytics explorer
  ([`da39235`](https://github.com/Kitware/pan3d/commit/da39235619ac8cd12128b6f8b25332df3dbaf5e5))

- **analytics explorer**: Adding plotting increment 2
  ([`952bfa8`](https://github.com/Kitware/pan3d/commit/952bfa8cdc8caa84e50e28b8e63fe4d11f91da29))


## v0.15.2 (2025-04-10)

### Bug Fixes

- **explorer update**: Fixing style issues for explorers
  ([`9e30793`](https://github.com/Kitware/pan3d/commit/9e307936958c762acac048b689798d0666a18d90))

This fix partly addresses https://github.com/Kitware/pan3d/issues/177


## v0.15.1 (2025-04-07)

### Bug Fixes

- **slice explorer update**: Slice Explorer won't load necessary data arrays
  ([`5eca91a`](https://github.com/Kitware/pan3d/commit/5eca91aedf7f1018d8d58a3ce15534e9b26f1648))

This fix addresses https://github.com/Kitware/pan3d/issues/177


## v0.15.0 (2025-03-07)

### Features

- **uniform exploreres**: Making explorers uniform
  ([`6f60e44`](https://github.com/Kitware/pan3d/commit/6f60e4472854d973f6a2e6b8741b568610b5b490))


## v0.14.1 (2025-01-17)

### Bug Fixes

- **deprecation**: Replace removed dimensions property
  ([`dba3f1e`](https://github.com/Kitware/pan3d/commit/dba3f1e1f97e446df10175f5875f1c26813deece))


## v0.14.0 (2025-01-06)

### Bug Fixes

- **contour explorere**: Adding contour explorer to the accessor
  ([`ac2aab6`](https://github.com/Kitware/pan3d/commit/ac2aab6638c49a85e2062d8d18f5072cfc7ac4f3))

- **missing varaible**: Adding missing class member variable to constructor
  ([`5bd326a`](https://github.com/Kitware/pan3d/commit/5bd326a3448f09a8d31053199009a27c86874653))

### Features

- **contour explorer**: Adding general countour explorer
  ([`715f8f1`](https://github.com/Kitware/pan3d/commit/715f8f1ae22ab50f73305dc450c18397bf563fba))


## v0.13.1 (2025-01-06)

### Bug Fixes

- **accessor**: Add .local/.remote option
  ([`a90d6f2`](https://github.com/Kitware/pan3d/commit/a90d6f250e8b53bc9ab2b16e0666d9c283acb02f))


## v0.13.0 (2024-12-20)

### Documentation

- **example**: Cleanup notebook
  ([`3a69c49`](https://github.com/Kitware/pan3d/commit/3a69c4941f07bc976a99fe773c7a65033a8f016c))

### Features

- **accessor**: Enable caching on viewer instantiation
  ([`8b554c9`](https://github.com/Kitware/pan3d/commit/8b554c9af9b3d600f0c7ad9f8b3b192a78257d02))

- **globe**: Enable globe as accessor
  ([`c8510f8`](https://github.com/Kitware/pan3d/commit/c8510f8f3f878daf1b2a0846a36d9ce3e363419a))

- **preview**: Preview can support xarray an input
  ([`7267aa6`](https://github.com/Kitware/pan3d/commit/7267aa6775e0e808e7632cd59427afd152b5a647))

- **slicer**: Explorer available as accessor
  ([`7058ade`](https://github.com/Kitware/pan3d/commit/7058ade8dc34fd10beb1f5104e7ff0db97534492))


## v0.12.2 (2024-12-18)

### Bug Fixes

- **globe explorer revision**: Adding updates to globe explorer
  ([`6fe397b`](https://github.com/Kitware/pan3d/commit/6fe397b2cf21c33c010140c46ff24a76f6f96558))

Adding to fix issue https://github.com/Kitware/pan3d/issues/142

- **rebase**: Rebasing over lookup table changes
  ([`f1ff447`](https://github.com/Kitware/pan3d/commit/f1ff447bbb8520b1f8890d1a74ad271a24eebacb))

- **review**: Adding changes from feedback
  ([`92f7c50`](https://github.com/Kitware/pan3d/commit/92f7c507a775a47f4f437068dabc9daf42cebf63))


## v0.12.1 (2024-12-17)

### Bug Fixes

- **lookup tables**: Adding lookup table changes to explorers
  ([`dad4830`](https://github.com/Kitware/pan3d/commit/dad4830a510a483b82aa9735a03c29009f54fe7c))

-- Adding to fix issue https://github.com/Kitware/pan3d/issues/143


## v0.12.0 (2024-12-09)

### Features

- **presets**: Use default ParaView color presets
  ([`75d7575`](https://github.com/Kitware/pan3d/commit/75d7575cea65b6de1637c0892c01995683988ddc))


## v0.11.2 (2024-12-09)

### Bug Fixes

- **preset**: Add x-margin for lut image
  ([`915baad`](https://github.com/Kitware/pan3d/commit/915baad93ca915a6a6ef2168d2dea9c2353370c6))


## v0.11.1 (2024-12-09)

### Bug Fixes

- **colors**: Better color preset helpers
  ([`37f352d`](https://github.com/Kitware/pan3d/commit/37f352d6471446114a0413273ad1d698849c8a9e))


## v0.11.0 (2024-12-06)

### Features

- **contour**: Add contour explorer
  ([`5608dc1`](https://github.com/Kitware/pan3d/commit/5608dc1d82ab3507fb6234f6986aaf0b925756a6))


## v0.10.4 (2024-11-27)

### Bug Fixes

- **scaling**: Wasm camera handling
  ([`4ca1922`](https://github.com/Kitware/pan3d/commit/4ca1922d16165e01d2a349f03ba042cfbde87d37))

- **scroll**: Remove scrollbar on linux
  ([`d311962`](https://github.com/Kitware/pan3d/commit/d311962fa47eb5ca11f8faa48c087720b3ae752d))

- **wasm**: Better conditional widget initialization
  ([`f93b143`](https://github.com/Kitware/pan3d/commit/f93b1430a93b5369165e64f58811c9eec7a690f7))

- **wasm**: Properly handle camera sync
  ([`272cb77`](https://github.com/Kitware/pan3d/commit/272cb7712e1371ed4fb2eb6af00be2d984c8104c))


## v0.10.3 (2024-11-22)

### Bug Fixes

- **binder**: Update XArrayViewer to check for gpu
  ([`12ab9c4`](https://github.com/Kitware/pan3d/commit/12ab9c43b62347982d0a21437e37ec1acc465c30))

Also fix typo in esgf notebook

### Documentation

- **examples**: Update esgf example - add markup cells, update config
  ([`c33fde6`](https://github.com/Kitware/pan3d/commit/c33fde6399feff0a22fe6640838609b2a6e31471))

- **examples**: Update pangeo example - add markup cells, update config
  ([`0965b0b`](https://github.com/Kitware/pan3d/commit/0965b0b35d2826660265f35e667d02998e2e2a6c))


## v0.10.2 (2024-11-16)

### Bug Fixes

- **vtk**: Use explicit import
  ([`628da61`](https://github.com/Kitware/pan3d/commit/628da61498e4bac0e55809ab3efb563e9cb99c59))

### Chores

- **binder**: Allow OSMesa to drive wasm
  ([`bceea41`](https://github.com/Kitware/pan3d/commit/bceea418e550a70ba7d8395494436c42e6a8417e))

- **binder**: Remove vtk-osmesa post script
  ([`1f6fe97`](https://github.com/Kitware/pan3d/commit/1f6fe977d2de1bba84420c69e91a67cd0247bf74))

- **binder**: Try to fix binder
  ([`8757967`](https://github.com/Kitware/pan3d/commit/87579675e274efce3105f1448e65b7040d848b78))

### Continuous Integration

- Push only if a release was triggered
  ([`bef1cb1`](https://github.com/Kitware/pan3d/commit/bef1cb135cec50fe707929758979baf244123c50))

### Documentation

- Fix readme links
  ([`5fc4726`](https://github.com/Kitware/pan3d/commit/5fc47263f37d89b59e5dd6e21021ace0c6b6564d))


## v0.10.1 (2024-11-15)

### Bug Fixes

- **api**: Remove disable rendering and add api doc
  ([`0d94995`](https://github.com/Kitware/pan3d/commit/0d949958bf0a392f064ff5bd5b4398e84a96d18e))

### Documentation

- Update names and tutorial images
  ([`38b0935`](https://github.com/Kitware/pan3d/commit/38b0935fe64e75566db995f94399771fd88d4c72))


## v0.10.0 (2024-11-15)

### Bug Fixes

- **algo**: Array listing
  ([`c823b16`](https://github.com/Kitware/pan3d/commit/c823b16024250a470bdd09c542e09a2bafc800f0))

- **algo**: Better print
  ([`47d9a05`](https://github.com/Kitware/pan3d/commit/47d9a05dca88f77ddf92759280958bd215c2902c))

- **dep**: Properly describe dependencies
  ([`0049e00`](https://github.com/Kitware/pan3d/commit/0049e002bdfd7ab90e72c54a3e65823ff6a8abd3))

- **examples**: Update config files
  ([`737e92c`](https://github.com/Kitware/pan3d/commit/737e92cdf1148ffc37c4b8776777db9d922a9589))

- **import/export**: Add cli handling too
  ([`239c661`](https://github.com/Kitware/pan3d/commit/239c6619e9ecc11f3032ceb29f334160dd55d708))

- **jupyter**: Update all notebooks
  ([`44fcffa`](https://github.com/Kitware/pan3d/commit/44fcffa508e0f21679a3695bc7859e4ac5eb1d9a))

- **load_dataset**: Rationalize data loading
  ([`f00be9f`](https://github.com/Kitware/pan3d/commit/f00be9f6329e9f5e00c5076804fc3ab810ee5515))

- **preview**: Data info and progress
  ([`39a4eeb`](https://github.com/Kitware/pan3d/commit/39a4eebe42beb3da9beb225e891e6750f5c72c0c))

- **pvxarray**: Remove invalid import
  ([`d7820e4`](https://github.com/Kitware/pan3d/commit/d7820e4b90d6a82ee2a62e461c7af927cc557e67))

- **rendering**: Disable rendering in testing
  ([`3ff5360`](https://github.com/Kitware/pan3d/commit/3ff5360465416dfd43d676fccba59e7465f8e593))

- **slice**: Make are required when no source
  ([`335daa0`](https://github.com/Kitware/pan3d/commit/335daa0cfbb9cd4901799ee80fb1ebc92e03750d))

- **slice-explorer**: Properly handling coloring
  ([`d379ce6`](https://github.com/Kitware/pan3d/commit/d379ce622ed53608601104af8dfffbb36483e8be))

- **Slicer**: Improve slice explorer
  ([`9c12281`](https://github.com/Kitware/pan3d/commit/9c12281db8825f649e494f7ecab26a4253d240ff))

- **slices**: Rename slicing and provide extents
  ([`a271aed`](https://github.com/Kitware/pan3d/commit/a271aeda97517a3ffa99abd1171f7d75c837397d))

- **xarray**: Add algo support
  ([`dfb767e`](https://github.com/Kitware/pan3d/commit/dfb767e018d8f8dc8dd852e065f2711b41fdf463))

### Code Style

- Format notebooks
  ([`2ce17b2`](https://github.com/Kitware/pan3d/commit/2ce17b24210a98a032302df35546f0088ba9df9b))

### Continuous Integration

- Disable rendering in viewer test
  ([`ab67641`](https://github.com/Kitware/pan3d/commit/ab6764147ab597d745b2741a1edc1ddd90ee413f))

- Fix test dependencies
  ([`8ae4b36`](https://github.com/Kitware/pan3d/commit/8ae4b36616bd7a09dd959b1dd3e217ce1ad00ee2))

- Install osmesa on linux
  ([`615c09d`](https://github.com/Kitware/pan3d/commit/615c09d3da30fb0fe9204d0e0fc542f7d02a2d7c))

- Remove js build
  ([`04b22cd`](https://github.com/Kitware/pan3d/commit/04b22cd1007ffd7ce0b6f6295143e789e9db6834))

- Remove viewer test on windows due to rendering
  ([`69b38d2`](https://github.com/Kitware/pan3d/commit/69b38d254274078427ccac5a7cd5cec73849c4db))

- Update testing and ci
  ([`e8f3b72`](https://github.com/Kitware/pan3d/commit/e8f3b72a8ae140272c37cd4666e820ba29a14776))

- **linux**: Install osmesa
  ([`0108aaf`](https://github.com/Kitware/pan3d/commit/0108aaf5eca135ce6383e427170d15950017850c))

- **testing**: Update py3.10 and fix accessor test
  ([`b7ad050`](https://github.com/Kitware/pan3d/commit/b7ad0502f077e4fb161a520b33614902548aca1d))

### Documentation

- Rtd update
  ([`cd200b2`](https://github.com/Kitware/pan3d/commit/cd200b271c28737aac33b38cc9cb8831f0c469d4))

- Update markdown with new images
  ([`1d31187`](https://github.com/Kitware/pan3d/commit/1d3118773ba8e94f673fe1261c858d716b11a3a1))

- **data**: Add real data descriptor
  ([`eedd9f0`](https://github.com/Kitware/pan3d/commit/eedd9f03ec8fd759342daa05ffe54fb5ab2bf1de))

### Features

- **catalog**: Add executable catalog browser
  ([`e99cdeb`](https://github.com/Kitware/pan3d/commit/e99cdeb08e83ee5e681c46a11251633cc5d8c00d))

- **import/export**: Add load/state on Xarrray source
  ([`939d87b`](https://github.com/Kitware/pan3d/commit/939d87ba3d1df3ce30dd6070c916aa1ef6d311ce))

- **NaN**: Add color picker for NaN
  ([`2356832`](https://github.com/Kitware/pan3d/commit/23568326ee96286ce24bd6419cbe7a572e287f72))

- **preview**: Add preview application
  ([`266df73`](https://github.com/Kitware/pan3d/commit/266df73aa44723a33f24dcca124765c535b8cbc2))

- **scalarbar**: Interactive scalarbar
  ([`6ffef93`](https://github.com/Kitware/pan3d/commit/6ffef93e685369f676883a3a0d2e0557139ab39a))

- **wasm**: Enable local rendering with wasm
  ([`90f0c32`](https://github.com/Kitware/pan3d/commit/90f0c329bc0ddc5ee400305a811460b5db202b91))

- **xarray**: Add slicing and compute in algo
  ([`d1fe31c`](https://github.com/Kitware/pan3d/commit/d1fe31cf32533ed57ffde8aa939d2bf26138e2b2))

- **xarray**: Porting pyvista-xarray to pure vtk
  ([`8fb49c4`](https://github.com/Kitware/pan3d/commit/8fb49c48e7728b55cf28943442833fbbdfb007ed))

### Refactoring

- Remove deprecated code
  ([`683beec`](https://github.com/Kitware/pan3d/commit/683beec3de2263c048073cd87e90de4ef27ea08c))

- **preview**: Break into independant ui pieces
  ([`35064fe`](https://github.com/Kitware/pan3d/commit/35064fe2c1180eca4098022d03fa443207af1e2f))

### Testing

- Fix data size
  ([`2a1f166`](https://github.com/Kitware/pan3d/commit/2a1f1663a987d5294fdb4747322321736c8f62e5))


## v0.9.2 (2024-10-22)

### Bug Fixes

- **import**: Correct import pattern
  ([`4d478bf`](https://github.com/Kitware/pan3d/commit/4d478bf4c8dc2e4e0f91272e6ab23016b3683021))

- **preset**: Centralize util methods
  ([`1f4eaf0`](https://github.com/Kitware/pan3d/commit/1f4eaf0139a33666cc5e8021a1c0d1f87d3fc772))


## v0.9.1 (2024-10-22)

### Bug Fixes

- **explorer**: Gui and code cleanup
  ([`8eb9ca4`](https://github.com/Kitware/pan3d/commit/8eb9ca43ae85f6e8c4a6d95329376d9c74ee8fb9))

### Continuous Integration

- **black**: Update pre-commit version
  ([`22f7dab`](https://github.com/Kitware/pan3d/commit/22f7dab272bcb934d610e30abafb1953f9c171db))


## v0.9.0 (2024-10-10)

### Documentation

- **contributing**: Update contributing guide
  ([`d5dc425`](https://github.com/Kitware/pan3d/commit/d5dc425e226e279a2888a9ecb0109f8fc5113a92))

### Features

- **Slice Explorer**: Adding inital version of the slice explorer
  ([`3147a46`](https://github.com/Kitware/pan3d/commit/3147a462368c00e44f0a0a33073b66681b601e03))

Adding Slice Explorer -- the main module in the `explorers` directory -- a driver example using
  python in `examples` -- a jupyter notebook demo example


## v0.8.9 (2024-08-15)

### Bug Fixes

- Close menus for bounds configure and render options when nearby drawer changes state
  ([`0396e36`](https://github.com/Kitware/pan3d/commit/0396e36c8289e481c2bb3e5200aa848af86b3b99))

- Update links to other tutorial pages
  ([`c3393b5`](https://github.com/Kitware/pan3d/commit/c3393b541971e2a26727d584fb02c3176da843e7))

### Code Style

- Add trailing comma
  ([`cdf7e21`](https://github.com/Kitware/pan3d/commit/cdf7e2153b513ccc8e992d782a5e96da25e322a7))

### Documentation

- Add preview bounds explanation for 2D data
  ([`1b49657`](https://github.com/Kitware/pan3d/commit/1b49657041d36dafb85c6f382e178d5bdc3bf292))

- First pass at updating documentation
  ([`3f97272`](https://github.com/Kitware/pan3d/commit/3f972722a9e5b2bf4f83f9f45ea830bd999d49cd))

- Fix Catalogs tutorial link in GeoTrame tutorial
  ([`ae2b38c`](https://github.com/Kitware/pan3d/commit/ae2b38c69dd718a389031746ad93b24e97437939))

- Update interactive preview descriptions for 3D data
  ([`87130cf`](https://github.com/Kitware/pan3d/commit/87130cf9a61fd4ea843d348defc62c7209fd9c5f))

### Refactoring

- Apply new name in example notebooks
  ([`31f78aa`](https://github.com/Kitware/pan3d/commit/31f78aaebe2f06716d4b7f17d20d53a16f290369))

- Apply new name in miscellaneous places
  ([`4caea8b`](https://github.com/Kitware/pan3d/commit/4caea8be4865ee6cbdea9ecfff7ba4787b7a70aa))

- Change name to GeoTrame in user-facing places
  ([`8141701`](https://github.com/Kitware/pan3d/commit/81417012556907aaddda034399fc3ce82011ae79))


## v0.8.8 (2024-07-01)

### Bug Fixes

- Ci ([`b7dbd2d`](https://github.com/Kitware/pan3d/commit/b7dbd2d03eaea60d0336e7b4f62d8f35518d55c4))


## v0.8.7 (2024-07-01)

### Bug Fixes

- Release step
  ([`1d4c277`](https://github.com/Kitware/pan3d/commit/1d4c277ef283cc709390d235855f1fb494942dbf))

- Release step
  ([`cf2a898`](https://github.com/Kitware/pan3d/commit/cf2a898d28e2265db6cea22569b0fa107c4a8035))


## v0.8.6 (2024-07-01)

### Bug Fixes

- **prune**: Remove unwanted files in packages
  ([`9d3a5d6`](https://github.com/Kitware/pan3d/commit/9d3a5d6a038210ab5c17a70893ed6747572465c7))

- **wheel**: Add wheel in build env
  ([`3365503`](https://github.com/Kitware/pan3d/commit/3365503d1fd33f6ffc91f48f738c04a8b84081de))


## v0.8.5 (2024-07-01)

### Bug Fixes

- Trigger a release
  ([`655f739`](https://github.com/Kitware/pan3d/commit/655f73912e923fa23cc59b7919c05a78e37cce38))

### Continuous Integration

- Register css
  ([`3398f1b`](https://github.com/Kitware/pan3d/commit/3398f1ba32265695cf30a27443a9e427add09a3d))

- Remove setuptool_scm
  ([`947f349`](https://github.com/Kitware/pan3d/commit/947f349fee587f5e3cb6083b77644973ea454b6d))


## v0.8.4 (2024-07-01)

### Bug Fixes

- **ci**: Hopefully get that js file
  ([`11d9482`](https://github.com/Kitware/pan3d/commit/11d94822ac82f84229c5b0028027589eec907a0d))

- **ci**: Try to bundle generated js
  ([`98a8f36`](https://github.com/Kitware/pan3d/commit/98a8f36522b98da3651dd67b13bc57a8eadd048c))

### Continuous Integration

- **semantic-release**: Publish built wheel
  ([`c5660da`](https://github.com/Kitware/pan3d/commit/c5660da84ff7fe1edc20cf6e1461b13ba00da10f))


## v0.8.3 (2024-07-01)

### Bug Fixes

- **dep**: Keep trying to get that js in bundle
  ([`981d617`](https://github.com/Kitware/pan3d/commit/981d61773a48c6605754c25864b9cac40d55f5a0))

### Continuous Integration

- Add missing file
  ([`fec5b9e`](https://github.com/Kitware/pan3d/commit/fec5b9e71450ad55d073cd2a0d1f863cb1af26d3))


## v0.8.2 (2024-07-01)

### Bug Fixes

- **js**: Add missing js file
  ([`3810ee1`](https://github.com/Kitware/pan3d/commit/3810ee1b6b54045f0836306583cd818d417bc932))


## v0.8.1 (2024-07-01)

### Bug Fixes

- **build**: Use hatch
  ([`3363daf`](https://github.com/Kitware/pan3d/commit/3363dafa98e267700c2847f32ec6ff097146b2f4))

- **pyproject**: Properly add required js files
  ([`6270a80`](https://github.com/Kitware/pan3d/commit/6270a80976a3b596122a711c1d7aafc3326d69a4))

### Continuous Integration

- Add missing dep
  ([`19e6239`](https://github.com/Kitware/pan3d/commit/19e6239b7ebc5288e4191c904c3ac1b2ee2acce5))


## v0.8.0 (2024-07-01)

### Bug Fixes

- Consistency for inclusive bounds max vs exclusive slicing stop
  ([`9d47789`](https://github.com/Kitware/pan3d/commit/9d4778902ec9164274a5540ee8500f5d52fd314a))

- Disable auto slicing during import
  ([`70ce50f`](https://github.com/Kitware/pan3d/commit/70ce50f60c0102a272678fc3fc062bd2ec09a0cb))

- Improve auto slicing behavior in `DatasetBuilder`
  ([`98a737e`](https://github.com/Kitware/pan3d/commit/98a737e26f021e18e17a33b946ee6d5a4084654a))

- Make bounds interactive preview work for data with flipped coordinates
  ([`ae54153`](https://github.com/Kitware/pan3d/commit/ae54153866590666562f849b263f19b6816a5c2e))

- Remove `ui_current_time_string`, use pregenerated labels list with datetime formatting
  ([`c1041ac`](https://github.com/Kitware/pan3d/commit/c1041ac9d9538103e63033bbc92bfe6823e959cd))

- Resolve test failures
  ([`186bf5f`](https://github.com/Kitware/pan3d/commit/186bf5f008e0bd052ac45e078a38db47ac84f4ea))

### Code Style

- Reformat with black
  ([`9e54fdf`](https://github.com/Kitware/pan3d/commit/9e54fdf13714c7d5ce5e96fcfac5240f704b51f1))

### Continuous Integration

- Update action version and ensure js bundle at release
  ([`063ffc9`](https://github.com/Kitware/pan3d/commit/063ffc971dc27908996d7f54b64822384b13ff6a))

### Features

- In preview image generation, compute gradients for small dimensions
  ([`68b3b9f`](https://github.com/Kitware/pan3d/commit/68b3b9f0d095ab1cb084691c2d67b9deed0c59fc))

- Make bounds configuration available in both axis drawer and bounds menu (rather than being mutally
  exclusive depending on `da_auto_slicing`)
  ([`8ec9c4a`](https://github.com/Kitware/pan3d/commit/8ec9c4a6ab8be78343300d33874b77554242930c))


## v0.7.0 (2024-06-25)

### Bug Fixes

- Change tag names
  ([`655daef`](https://github.com/Kitware/pan3d/commit/655daef682d3add13611767185f01a639dddf6a5))

- Move symlink command to entrypoint script
  ([`9f2db38`](https://github.com/Kitware/pan3d/commit/9f2db381773b1a6f04dad313e0d53d49f4a325c5))

- Remove `if` clauses from ci `jobs` spec (redundant after `on` spec)
  ([`f87ddf0`](https://github.com/Kitware/pan3d/commit/f87ddf04cdc2086ce11e20a1623089c11dac35ad))

- Remove jupyter server proxy command
  ([`50cfc3a`](https://github.com/Kitware/pan3d/commit/50cfc3a69ad96c33927309c6c922682d05fa5d98))

- Remove reference to jupyter.py in pyproject.toml
  ([`232cdc6`](https://github.com/Kitware/pan3d/commit/232cdc632e106d152594d907d35b73016a12e248))

- Rename docker images
  ([`0b4df24`](https://github.com/Kitware/pan3d/commit/0b4df2433eb29f66506287ae66a6022af4a5e5e0))

- Specify tags for each image
  ([`f93de95`](https://github.com/Kitware/pan3d/commit/f93de9534c386603f8a15f13f202d0b55daa7554))

- Use dockerhub registry instead of ghcr.io
  ([`f7e6cb2`](https://github.com/Kitware/pan3d/commit/f7e6cb2259b2ad8c1c335c725425cdb7584a836a))

### Continuous Integration

- Remove pull_request trigger for publish action
  ([`1751cc4`](https://github.com/Kitware/pan3d/commit/1751cc413aa3bd645da8bfd5b1c5b2f4d8495666))

### Features

- Add cloud dockerfile and add ci step to publish as pan3d-cloud
  ([`25794ea`](https://github.com/Kitware/pan3d/commit/25794eaa76b38e62b5c7b2da6cf49de14e831e09))

- Add entrypoint to create symlink to examples folder (suggested by Yuvi @ 2i2c)
  ([`29f6af5`](https://github.com/Kitware/pan3d/commit/29f6af52d2561c1f1b03ef609b79f43cb4be6634))

### Refactoring

- Simplify job names
  ([`6ae13a9`](https://github.com/Kitware/pan3d/commit/6ae13a965fe844934d933b723ec9b4d2026042c4))


## v0.6.2 (2024-06-25)

### Bug Fixes

- Add "pan3d.ui.pan3d_components" to packages list
  ([`8389496`](https://github.com/Kitware/pan3d/commit/8389496ac09e0b4988c4d733fd6ac0c91f34d3bf))

- Add catalogs folder to setuptools packages list
  ([`54722a6`](https://github.com/Kitware/pan3d/commit/54722a671d3d317b725e91f42bc78b12fa401f11))

- Add missing parenthesis in async callback
  ([`a2e7676`](https://github.com/Kitware/pan3d/commit/a2e76762a06c3f6870eb32374def6e6437fd7d23))

- Add new folders to packages list in pyproject.toml
  ([`3247611`](https://github.com/Kitware/pan3d/commit/32476117eebe3de18a9e7daecaac58632af1b374))

- Add npm installation steps to CI tests
  ([`ce688ed`](https://github.com/Kitware/pan3d/commit/ce688ed14488a793cbf1827f7db79ec84fd881fc))

- Always use `push_camera` instead of `reset_camera`
  ([`b3ce44f`](https://github.com/Kitware/pan3d/commit/b3ce44f3f20f61bd66c23d82b048c34c76fef747))

- Apply suggested usability changes
  ([`1532b5a`](https://github.com/Kitware/pan3d/commit/1532b5ae25084aa207ddd28c6b973344d596be07))

- Assign coordinates on implicitly indexed data arrays before sending to algorithm
  ([`087d04f`](https://github.com/Kitware/pan3d/commit/087d04fa544334d178eb442a8b52cf1f2c59c611))

- Asynchronous trame state updates
  ([`48bd1d7`](https://github.com/Kitware/pan3d/commit/48bd1d7779a735fa059d564296c734493964efc4))

- Cast keys and values in `da_vars_attrs` to strings
  ([`bc8c319`](https://github.com/Kitware/pan3d/commit/bc8c319a230bea29c5ac6332b4fc2f8e47fe40a5))

- Cast objects to strings in template code
  ([`c8c66ba`](https://github.com/Kitware/pan3d/commit/c8c66baae1c9ad796c9826bf9c77e4751908059f))

- Change pyvista StructuredGrid reference
  ([`5260a60`](https://github.com/Kitware/pan3d/commit/5260a60a04dc57412d8af2259edb8a699cdd0d36))

- Consolidate asynchronous viewer behavior with helper function `run_as_async`
  ([`a69f106`](https://github.com/Kitware/pan3d/commit/a69f106778f4645cb356d6455403cb49ba73b00c))

- Convert more directive attributes to tuple syntax
  ([`469c511`](https://github.com/Kitware/pan3d/commit/469c5113bcc12fcc61b04e0abe5f1b27f75e6a34))

- Correct various bugs and unexpected behavior
  ([`9c9ebf7`](https://github.com/Kitware/pan3d/commit/9c9ebf7862dfd93369bf7ea4b4ab46fef51cf902))

- Guard against a None `catalogs` value in `DatasetViewer` constructor
  ([`dc505e5`](https://github.com/Kitware/pan3d/commit/dc505e5e17682113ac537eb90be10585fae1ddb2))

- Improve compatibility with more pangeo datasets with timedelta dtypes
  ([`a80119e`](https://github.com/Kitware/pan3d/commit/a80119e19a25cd7aa383edbb580ec793a81ccda7))

- Improve usability of import via UI
  ([`22520fd`](https://github.com/Kitware/pan3d/commit/22520fd359f9e334f4bbb8be7e0e9f9c5a70c967))

- Include module and serve packages individusaly
  ([`c9b449f`](https://github.com/Kitware/pan3d/commit/c9b449ff6a54a8f50818b49d1ea15e0bab2ba22b))

- Loading and error states should be handled only by `run_as_async` method
  ([`1c488ff`](https://github.com/Kitware/pan3d/commit/1c488ff9de9ac2c503db0fbd4bd853b8d41b5853))

- Move default resolution value (cmd arg is None if not specified)
  ([`faabc39`](https://github.com/Kitware/pan3d/commit/faabc39df0ef5edbdb5caa69efb34dfcaa260876))

- Prevent "NoneType is not iterable" error in Pangeo search by ID
  ([`6b91079`](https://github.com/Kitware/pan3d/commit/6b91079cea8cc916a2909601f0cab9b5d68dbb6e))

- Prevent `auto_select_coordinates` from overwriting `set_data_array_axis_names` results
  ([`53f016e`](https://github.com/Kitware/pan3d/commit/53f016e492acdfdcd2bbe11adc50f7d0eaea930e))

- Prevent name conflict by renaming catalogs module import
  ([`806657f`](https://github.com/Kitware/pan3d/commit/806657fb4db006ae1e40c182563a5d4d3fe7db3c))

- Protect against NoSearchResults exceptions from intake_esgf
  ([`3654f48`](https://github.com/Kitware/pan3d/commit/3654f482ed44ee14236f8140ccd8cd016a2150d5))

- Reduce sleep time in `run_as_async`
  ([`50e568b`](https://github.com/Kitware/pan3d/commit/50e568b2af8b5f53a4d76be7366f2244b6d6fa40))

- Remove broken pangeo-forge links from catalog
  ([`9ea98f5`](https://github.com/Kitware/pan3d/commit/9ea98f5d75bb7efc2e7c1624f05ed83898a53abd))

- Remove cmdline arg shorthand notations to avoid conflicts
  ([`88d9810`](https://github.com/Kitware/pan3d/commit/88d9810f06f283fe66fa785f6e6bc71b211a9d78))

- Remove defaults on computed attribute values
  ([`fd024a7`](https://github.com/Kitware/pan3d/commit/fd024a7de971c856beb85e2d2828242038ae1a36))

- Remove unnecessary values from exported state
  ([`a6de08b`](https://github.com/Kitware/pan3d/commit/a6de08bbe070a17c5f614ee7e4639dd7d9b0155d))

- Reset search and message when catalog changes
  ([`5327dab`](https://github.com/Kitware/pan3d/commit/5327dab1b9cb83d460f3e0e11cddce0570bf4d16))

- Set DatasetBuilder slicing to None when DatasetViewer coordinates are blank
  ([`f53dc24`](https://github.com/Kitware/pan3d/commit/f53dc24e6106b1a247dae063b7c4689f20b09ed3))

- Show import loading bar during import
  ([`24821c4`](https://github.com/Kitware/pan3d/commit/24821c41d6427df69b6c0edd8fd4691a59917eed))

- Slice by index instead of value to allow slicing time coord
  ([`801735f`](https://github.com/Kitware/pan3d/commit/801735f3ef4296ffc292f1c3c5ba2ac7ec380b94))

- State synchronization between builder and viewer
  ([`e3ab71a`](https://github.com/Kitware/pan3d/commit/e3ab71ab1da2177da1ff3d5037c56ca1345a1534))

- Stringify axes list for VSelect component
  ([`e783699`](https://github.com/Kitware/pan3d/commit/e7836993bbfba19a29a2485d02c99fab1977b42d))

- Synchronize slicing state between builder and viewer
  ([`33b5404`](https://github.com/Kitware/pan3d/commit/33b54048b3a1cd0fc50aedd92a64d35d360b26a5))

- Update binder requirements.txt
  ([`26abc54`](https://github.com/Kitware/pan3d/commit/26abc54e9eab0af05f89845cee6dd3f07d8b9a5b))

- Update Builder and Viewer to use Pangeo module
  ([`b94e60e`](https://github.com/Kitware/pan3d/commit/b94e60eb552f57b1157210be8617fa6706d1e0ac))

- Update example config files
  ([`5cac70e`](https://github.com/Kitware/pan3d/commit/5cac70ea660dda2cc61fb6ecaa137ae3aec19b2f))

- Update files in `docker` folder
  ([`b1aae3f`](https://github.com/Kitware/pan3d/commit/b1aae3facf5a0df09823a4eebb422e7b4463881a))

- Update javscript path in CI for build step
  ([`7432328`](https://github.com/Kitware/pan3d/commit/743232879e4f4dab9fa9ffa4b19d2031c0d78889))

- Update test expected size for updated example file
  ([`c4acabe`](https://github.com/Kitware/pan3d/commit/c4acabef8045dbbda6c41d2069dc1a54dd9806a4))

- Use `push_camera` instead of `reset_camera` in cloud mode
  ([`41dde0c`](https://github.com/Kitware/pan3d/commit/41dde0ccb4cf794f9985bbbfe490dab49d096f9d))

- Use correct exception imports in `pangeo_forge.py`
  ([`a8fccca`](https://github.com/Kitware/pan3d/commit/a8fccca880988a7a257c1216e8102b08869bfc78))

- Use relative path for pangeo datasets JSON
  ([`e85e83e`](https://github.com/Kitware/pan3d/commit/e85e83e849b958e8070b84be7a6876a97f49484a))

- Use true min and max for default slicing
  ([`aa4d939`](https://github.com/Kitware/pan3d/commit/aa4d9394b2f4f2c40ef38df6f3489563de8a570f))

- Use try-catch for catalog module imports
  ([`a1a7e5a`](https://github.com/Kitware/pan3d/commit/a1a7e5ab0d10747095ed4e11f1546b00815b4f3d))

- Wait until server ready before enabling auto rendering
  ([`e02d159`](https://github.com/Kitware/pan3d/commit/e02d15922ee33e7bcc86094318527b54cf1ee258))

- **changelog**: Change misspelled word
  ([`e977de5`](https://github.com/Kitware/pan3d/commit/e977de5e5a0d458db95543bb578b3b89bde05151))

- **dataset_builder**: Update export_config and mesh_changed functions
  ([`40e1b17`](https://github.com/Kitware/pan3d/commit/40e1b17aa439f6c79efa6f1075bb6ae6c18b85ec))

- **DatasetBuilder**: Typing adjustments
  ([`0686dea`](https://github.com/Kitware/pan3d/commit/0686dea8889db3e8d1360d3c6e511abe2e6ad1a5))

- **docs**: Fix README badge rendering on GH
  ([`a6065d6`](https://github.com/Kitware/pan3d/commit/a6065d6326f49b4560375e6cf33775850482f011))

- **examples**: Update example notebooks with catalogs argument
  ([`f8c07d9`](https://github.com/Kitware/pan3d/commit/f8c07d9e69178fcb0ad8571acea76fd84083f09a))

- **examples**: Update notebooks and add requirements.txt
  ([`406c76b`](https://github.com/Kitware/pan3d/commit/406c76baf5ce99259ecbd949a11947928f43e565))

- **lint**: Run black
  ([`754d44d`](https://github.com/Kitware/pan3d/commit/754d44d955dc530a2203a3470fca7b2eaed836e4))

- **pyproject.toml**: Escape backslash characters in version pattern
  ([`66d8db9`](https://github.com/Kitware/pan3d/commit/66d8db9348b5ae07b2bab278fa4a3aada1ea89b8))

- **pyproject.toml**: Semantic-release v8 does not support setup.cfg
  ([`bda7a67`](https://github.com/Kitware/pan3d/commit/bda7a67b5cf9f7f0ac2d866b458ca9b767eb2353))

- **release**: Add a job to build dist folder
  ([`aa48f3a`](https://github.com/Kitware/pan3d/commit/aa48f3a58822ce00c6adde2969f9ea2259814061))

- **requirements**: Add trame-jupyter-extension to requirements.txt
  ([`91f253a`](https://github.com/Kitware/pan3d/commit/91f253a9e4860490bc1730ee11f4d183f4d2e4c7))

- **setup**: Add setuptools_scm to pyproject.toml; use git tag for version in build step
  ([`9c2789d`](https://github.com/Kitware/pan3d/commit/9c2789d0427ebd12d5d9398d4f4d51e21b804beb))

- **setup**: Add vtk-osmesa to examples requirements for binder
  ([`5abfa59`](https://github.com/Kitware/pan3d/commit/5abfa5948f2caddd19dc4ff0d2f450c0af857dd0))

- **setup**: Specify packages list to override automatic packages discovery
  ([`a0f7941`](https://github.com/Kitware/pan3d/commit/a0f7941cc3a1ad230240deabc8bd0bca682ad756))

- **setup**: Use Dockerfile to specify uninstall of default vtk before install of vtk-osmesa
  ([`34c459d`](https://github.com/Kitware/pan3d/commit/34c459d20de43abe428ed968c3de44e79c6f5757))

- **test**: Add a flag to disable render in `set_render_options`; geovista GeoPlotter raises
  exception when no GPU found
  ([`2fd86ca`](https://github.com/Kitware/pan3d/commit/2fd86ca6c2a39e92961ccd74b0f5b13f674c3fba))

- **test**: Allow non-numeric slicing values (for time axis)
  ([`822427e`](https://github.com/Kitware/pan3d/commit/822427ef31eae93c7c321243bd98bc386b82e4e3))

- **test**: Don't enable cartographic mode on 4D test data
  ([`b632ad9`](https://github.com/Kitware/pan3d/commit/b632ad99d5bb93aab1d54efb3e12a1fbdc6276aa))

- **threading**: Use `call_soon_threadsafe` for plotting mesh
  ([`28930fb`](https://github.com/Kitware/pan3d/commit/28930fb372a4cc6d5fbfadaf3d966d67994e202b))

### Build System

- Add binder start script from pyvista docs
  ([`51318d1`](https://github.com/Kitware/pan3d/commit/51318d150170a74e13b46cc09b3bd03cfb261e4e))

- Add more dependencies to Dockerfile
  ([`808d421`](https://github.com/Kitware/pan3d/commit/808d421aa4b049acd611af6a712784ca0a3b93f8))

- Add xvfb to system requirements
  ([`6a961e9`](https://github.com/Kitware/pan3d/commit/6a961e9d8625d15748c9b004e5f483655e878dca))

- Move binder configuration to .binder, use postBuild script instead of start
  ([`8f166c9`](https://github.com/Kitware/pan3d/commit/8f166c9c37f8aa82b062625bdf99840c7c2864f0))

- Move configuration files to top-level binder folder
  ([`1f388d9`](https://github.com/Kitware/pan3d/commit/1f388d91df04dbd2709596b1ecf0d5efb9cb2940))

- Reformat requirements.txt
  ([`513399b`](https://github.com/Kitware/pan3d/commit/513399b36c01ad0d128042ddb769c962880daf34))

- Remove apt.txt
  ([`1b4c176`](https://github.com/Kitware/pan3d/commit/1b4c176bd9a4822fd43a4ccc305c003c424a322e))

- Remove setuptools-scm, use __version__ in setup.py
  ([`bf63e56`](https://github.com/Kitware/pan3d/commit/bf63e560096c72a5d3fd73460b04a47deb324cad))

- Remove vtk-osmesa installation, use xvfb
  ([`6efab66`](https://github.com/Kitware/pan3d/commit/6efab66704ccba153cd7a90c872cf2653ab2c28d))

- Remove which Xvfb command
  ([`081f5cb`](https://github.com/Kitware/pan3d/commit/081f5cba49f406fd74b907cf2b07b31951704b55))

Co-authored-by: Zach Mullen <zach.mullen@kitware.com>

- Require trame-vtk>=2.6.3
  ([`be9a4ce`](https://github.com/Kitware/pan3d/commit/be9a4ced0e9bebf5265b301edb0146e1b05c090e))

- Switch user back to NB_USER after installation
  ([`f4e8893`](https://github.com/Kitware/pan3d/commit/f4e8893baa28fd1855faf1aad887d2494dcb72d0))

- Try binder build without Dockerfile
  ([`27f038f`](https://github.com/Kitware/pan3d/commit/27f038f7e7c7f0f0e6693e23fd162a7f51b300b7))

- Try without xvfb, use vtk-osmesa
  ([`850dc15`](https://github.com/Kitware/pan3d/commit/850dc15b78f4ec66cfe9b3e5231d707fe549f439))

- Update Dockerfile in examples/jupyter
  ([`dd5961a`](https://github.com/Kitware/pan3d/commit/dd5961aa34c94a8f1b04e1ee3de10225dcb025ff))

- Use BINDER_REQUEST instead of JUPYTERHUB_BASE_URL to determine whether env is in Binder
  ([`bd9c5e2`](https://github.com/Kitware/pan3d/commit/bd9c5e2f960dff6964e8d54e346fe6cd1f323d2b))

- **binder**: Try local pan3d install
  ([`404c2ab`](https://github.com/Kitware/pan3d/commit/404c2abd3ebd6998d230ae98a58026030ee61bc5))

- **setup**: Add MANIFEST.in and include package data
  ([`efb8cd0`](https://github.com/Kitware/pan3d/commit/efb8cd0b722dbe410d459242f043bddad60f9c63))

### Code Style

- Add trailing comma
  ([`5ac37cd`](https://github.com/Kitware/pan3d/commit/5ac37cdcd4955f8613e020e3e41baed113cb288c))

- Apply changes from black
  ([`0d06d82`](https://github.com/Kitware/pan3d/commit/0d06d82d638438a25c4953cfddf10a8a3f78d608))

- Fix automatic formatting of list by removing comma
  ([`b28f444`](https://github.com/Kitware/pan3d/commit/b28f444fa48edf94560a37aab0d1f2f02c38641c))

- Fix formatting
  ([`599c1e2`](https://github.com/Kitware/pan3d/commit/599c1e2b525a0ec39435dca5a0e3786f7996e4e5))

- Fix formatting
  ([`a698eca`](https://github.com/Kitware/pan3d/commit/a698ecad3bcba57b261321a8c7e69dd9840e7f14))

- Fix formatting
  ([`39cae23`](https://github.com/Kitware/pan3d/commit/39cae2386a7a9f9e4a3e58edd5a44193823429a6))

- Prefer double-quotes
  ([`d77d630`](https://github.com/Kitware/pan3d/commit/d77d630b15da084f4d9fff4353e530c66f1f787f))

- Reformat with black
  ([`cfa631b`](https://github.com/Kitware/pan3d/commit/cfa631b8296dbcd019945a956ea10f513c3a9410))

- Reformat with black
  ([`ffce418`](https://github.com/Kitware/pan3d/commit/ffce418ddbb34f58d37a9c60ecb96f27cee3b7c0))

- Reformat with black
  ([`2860427`](https://github.com/Kitware/pan3d/commit/28604277b68a9aaf5b02fe59cf670b2882304653))

- Reformat with black
  ([`78efd90`](https://github.com/Kitware/pan3d/commit/78efd90fc218953f19c5c364b9a7b305fb443a89))

- Reformat with black
  ([`fb36747`](https://github.com/Kitware/pan3d/commit/fb3674706e080ef32c956a1ea6eaeb7098ccae81))

- Reformatting with black
  ([`687e370`](https://github.com/Kitware/pan3d/commit/687e370703920fba3d29267fadb3c56207e7633d))

- Remove print statement
  ([`cca89e1`](https://github.com/Kitware/pan3d/commit/cca89e170f8b6eae33737b2274b296f3feeeb8c5))

- Replace 2 tutorial images with rotated worlds
  ([`b6abe09`](https://github.com/Kitware/pan3d/commit/b6abe092a821d6709b45bddc89bf7642a137b109))

- Switch cover image in README
  ([`d7db238`](https://github.com/Kitware/pan3d/commit/d7db2382369c7a0d004a4d0f142dd3862d282a39))

- Update style via black
  ([`de58bfd`](https://github.com/Kitware/pan3d/commit/de58bfd95002d387a1afe55e2a8085a63f43ea26))

- Use black to fix styling
  ([`cd61185`](https://github.com/Kitware/pan3d/commit/cd611853756376747815dffa1311c9a4a7819b83))

- Use black to fix styling
  ([`26708bd`](https://github.com/Kitware/pan3d/commit/26708bdc9fa6dfeb222486a04fca1fcf5a6eca4c))

- Use black to fix styling
  ([`a8cbaab`](https://github.com/Kitware/pan3d/commit/a8cbaabebc940836ca84f139c84883850531831f))

- Use double quotes
  ([`bf128ba`](https://github.com/Kitware/pan3d/commit/bf128ba380135ed2b2a90b34fea5288843b799a4))

- **css**: Hide scroll bar by default
  ([`d55c2ac`](https://github.com/Kitware/pan3d/commit/d55c2acc374f63c1d898b94dd31c655085934e61))

### Continuous Integration

- Add `contents:write` to permissions in release job
  ([`c4ef618`](https://github.com/Kitware/pan3d/commit/c4ef618af7820403688abdf745d01c0181076b40))

- Combine build, release, publish jobs into one release job with 3 steps
  ([`0a61ae3`](https://github.com/Kitware/pan3d/commit/0a61ae322c72ea7df32220f12b169480c653f7c1))

- Rebuild before PyPI publish
  ([`34432d2`](https://github.com/Kitware/pan3d/commit/34432d253f051cd9fcabc387a177647f4baed5c6))

- **pyproject.toml**: Bump python requirement to 3.7
  ([`e7217a4`](https://github.com/Kitware/pan3d/commit/e7217a490e011bdfb8dd27378073ad022a5570c7))

### Documentation

- Add `site` to .gitignore
  ([`0f30478`](https://github.com/Kitware/pan3d/commit/0f30478b0be577b271d0d26e1ee755f7c198528e))

- Add comment to `.binder/requirements.txt`
  ([`9a1dfbe`](https://github.com/Kitware/pan3d/commit/9a1dfbe65d231c93153ca878a4d6fe810cb0dec3))

- Add configuration for readthedocs
  ([`4ee93de`](https://github.com/Kitware/pan3d/commit/4ee93de21679f98d33920fbcbcd3a1d671eacff5))

- Add descriptors for what each axis represents
  ([`908b9b4`](https://github.com/Kitware/pan3d/commit/908b9b4e4703d9e4c1a62524e651cc9cd4a3d8ba))

- Add example config file with ESGF dataset
  ([`c4c9dae`](https://github.com/Kitware/pan3d/commit/c4c9daef6d5e6a376dce738113c192143c0c6f14))

- Add mesh edges screenshot to viewer tutorial
  ([`d2ac60c`](https://github.com/Kitware/pan3d/commit/d2ac60cc567766affdf8ef1342e6ee8968bcc745))

- Add new tutorial page for catalog search dialog
  ([`0421f9e`](https://github.com/Kitware/pan3d/commit/0421f9e97033fceb59a6284aab24d5f3d01d60bf))

- Add two new example jupyter notebooks
  ([`8efdbfb`](https://github.com/Kitware/pan3d/commit/8efdbfb85cb09b85fac7e3ed636a59aeb7bb836f))

- Add typing and docstrings to dataset_builder.py
  ([`40d6e95`](https://github.com/Kitware/pan3d/commit/40d6e95a7e29031ee6147a4f50960613cc573f6b))

- Adjust existing pages to catalogs changes
  ([`bece99d`](https://github.com/Kitware/pan3d/commit/bece99d268ed10f22bad2a8278ffb1f6850bc923))

- Fill API documentation pages
  ([`d50027d`](https://github.com/Kitware/pan3d/commit/d50027d0e9da0519923861c07e73539fb0d3b28d))

- Improve language in tutorial pages
  ([`9149c5b`](https://github.com/Kitware/pan3d/commit/9149c5b1328f8ce024e80deff13f6557ad7e6093))

Co-authored by: @johnkit

- Improve Pangeo Forge examples
  ([`5f1be01`](https://github.com/Kitware/pan3d/commit/5f1be0130514d176e8142da6385e0fa26e8f3634))

- Replace "active" with "name" in config schema
  ([`787a0e9`](https://github.com/Kitware/pan3d/commit/787a0e925681dedd2a89cbfd7b62bf1eed6b1033))

- Update current time in description for updated screenshot
  ([`2f0a0ae`](https://github.com/Kitware/pan3d/commit/2f0a0ae87ccff9e4d4bce860ad584290dde5995c))

- Update docs images
  ([`1e070ca`](https://github.com/Kitware/pan3d/commit/1e070caf994db8d0ac03d80aec24d5a74956363f))

- Update docstrings for API docs pages
  ([`c006332`](https://github.com/Kitware/pan3d/commit/c0063322f10543b3a48716c0427254f404ae5fde))

- Update examples
  ([`37314ca`](https://github.com/Kitware/pan3d/commit/37314ca990a720891278a1c1b756cd657464413b))

- Update existing jupyter notebook examples
  ([`96cb22a`](https://github.com/Kitware/pan3d/commit/96cb22a27ca16c5938f53a8ef86d107d31244a8e))

- Update image folder (stored with lfs)
  ([`9caaa06`](https://github.com/Kitware/pan3d/commit/9caaa067ef7e4e27576330f4ba890554c78b1de6))

- Update tutorials and other descriptive documentation
  ([`34d41cf`](https://github.com/Kitware/pan3d/commit/34d41cf1f0432fb783d11e716ed16623d6ac45d1))

- **cli**: Rename `dataset_path` arg to `dataset`
  ([`1dd1c30`](https://github.com/Kitware/pan3d/commit/1dd1c30d98b794f897aa9097b9a3324e7ba5de1f))

- **setup**: Update pyproject.toml and MANIFEST.in with README location
  ([`94638cd`](https://github.com/Kitware/pan3d/commit/94638cd0e211b5465567c6a8215b6e5a56ec6da4))

- **tutorials**: Create basic docs navigation and add tutorials
  ([`c6fb974`](https://github.com/Kitware/pan3d/commit/c6fb97446efdaee0b4f5f32634bb5e73d5b36537))

- **version**: Use dynamic version in pyproject.toml
  ([`b7db351`](https://github.com/Kitware/pan3d/commit/b7db351604038bdb5b3eb6cf3802c50b47e0a463))

### Features

- Add "render_cartographic" state var and relevant management/docs
  ([`294bc7f`](https://github.com/Kitware/pan3d/commit/294bc7f42bf7ba4a01aaa559d0dfeca1fc2a2738))

- Add `--esgf` argument to `pan3d-viewer`
  ([`1b1f0ba`](https://github.com/Kitware/pan3d/commit/1b1f0ba2f51f01481623a574d78f1981c8d685fe))

- Add `resolution` CLI arg and disable auto slicing when <= 1
  ([`24c97ad`](https://github.com/Kitware/pan3d/commit/24c97adc8af68f8ed3f9b6be6b381bb98ec48977))

- Add `viewer` kwarg to Builder constructor to instantiate Viewer
  ([`4927a9c`](https://github.com/Kitware/pan3d/commit/4927a9cdfbe85a33c096ebf1133dd59312ee9783))

- Add a catalog search dialog
  ([`210afb1`](https://github.com/Kitware/pan3d/commit/210afb187b682b5d05ea04785c21799ff24eb525))

- Add automatic rendering, enabled by default
  ([`644e1fa`](https://github.com/Kitware/pan3d/commit/644e1fa101bcb6fae3b522943758d2f38aaf42ae))

- Add BoundsConfigure component within render area
  ([`73653e9`](https://github.com/Kitware/pan3d/commit/73653e9c3a0c5d9d185e0b103b54e88c9bc6f330))

- Add camera positioning to cartographic rendering
  ([`c860d08`](https://github.com/Kitware/pan3d/commit/c860d08ef708ddec06917d2b1260d962fcc00cc4))

- Add esgf module, which uses intake-esgf
  ([`6be5401`](https://github.com/Kitware/pan3d/commit/6be54014f19df79d5acad0b44d2ee2c73b673dac))

- Add group selector to UI in `main_drawer`
  ([`30f3063`](https://github.com/Kitware/pan3d/commit/30f3063fbeb10989f802ef672b855e699ce9a602))

- Add more xarray examples to default dataset list
  ([`af6586e`](https://github.com/Kitware/pan3d/commit/af6586eaeb0102c2a04052a0a97603152f4a54d8))

- Add PreviewBounds component, written with Vue
  ([`1d9c898`](https://github.com/Kitware/pan3d/commit/1d9c89892df76ee0d505218c563c52a1e36423ec))

- Add value checking on DatasetBuilder setters
  ([`ecfe374`](https://github.com/Kitware/pan3d/commit/ecfe374df2fd2e41602254913ab36f3b325d7182))

- Generate cube face preview images and set up cube mode state vars
  ([`ad2fcdc`](https://github.com/Kitware/pan3d/commit/ad2fcdc14b202ba548433db69705827af90a8a10))

- Implement Pangeo module functions using intake
  ([`3bcbf2e`](https://github.com/Kitware/pan3d/commit/3bcbf2edcc5515a7fdd3f7977c596801cbb22970))

- More extensive automatic coordinate selection
  ([`01de7c1`](https://github.com/Kitware/pan3d/commit/01de7c1500c55e6a887ba6ee4e8d2c120d1e258c))

- Set rendering mode to client in known cloud jupyter environments
  ([`32641fe`](https://github.com/Kitware/pan3d/commit/32641feab747f5edd9a38debd5fbf0c54ed3a55f))

- Use GeoVista to map data onto earth sphere
  ([`3bb7b2f`](https://github.com/Kitware/pan3d/commit/3bb7b2f4bba20128a660d2b70c15c8c79db12f5a))

- **examples**: Add notebook demonstrating use of `builder.mesh` with pyvista rendering
  ([`7f9d88c`](https://github.com/Kitware/pan3d/commit/7f9d88cc84506211b492b02dc4fa70a0572e0000))

### Refactoring

- Add lfs images
  ([`deb30ff`](https://github.com/Kitware/pan3d/commit/deb30ff4d09b5c880f1e2487634fdaea3c51077a))

- Apply suggested change from review
  ([`6d4f3ac`](https://github.com/Kitware/pan3d/commit/6d4f3ac37a73d5c099950e6241d197017b4d4c1d))

- Apply suggestions
  ([`c891b38`](https://github.com/Kitware/pan3d/commit/c891b387ed64989eaf1dda385f5cb3f26991d3c2))

- Enable module in widgets, not dataset_viewer
  ([`1c4d30c`](https://github.com/Kitware/pan3d/commit/1c4d30cbab102623c7c4be0aaf73ef4fe768da1f))

- Move `call_catalog_function` to `pan3d.catalogs.__init__.py`
  ([`01aee20`](https://github.com/Kitware/pan3d/commit/01aee20e85f86c707a5d465765ea128d35fefb6b))

- Move `serve` directory within `module` directory
  ([`06bc8bd`](https://github.com/Kitware/pan3d/commit/06bc8bd0840bba4f662dbd1d16ac0d9180d69190))

- Move catalog modules to new `pan3d/catalogs` folder
  ([`8a25e85`](https://github.com/Kitware/pan3d/commit/8a25e85d9f75fa7fa78ab2a19b9a7155f130a090))

- Move javascript code to its own top-level directory
  ([`7aa8ea9`](https://github.com/Kitware/pan3d/commit/7aa8ea9977829c1df43fce06c586b67cdb4e7ad3))

- Move module and serve dirs back into python package
  ([`73d24a4`](https://github.com/Kitware/pan3d/commit/73d24a45b0485502819862ba8a2f779595ef2f7f))

- Move widgets.py into pan3d_components
  ([`a28e308`](https://github.com/Kitware/pan3d/commit/a28e3083212c6c2dd0556228951f85d9f62a15d9))

- Remove class-checking for specific pangeo catalog errors (avoid importing auxiliary libraries
  directly)
  ([`9456ca6`](https://github.com/Kitware/pan3d/commit/9456ca6931e60ad6dbd7ecc122ef3c49525d83af))

- Remove docs images (to be stored with git-lfs)
  ([`beb1b2a`](https://github.com/Kitware/pan3d/commit/beb1b2a18d451bbe7b5eb378115af35b6d436e81))

- Rename `_cloud` to `_force_local_rendering`
  ([`2b1c5a7`](https://github.com/Kitware/pan3d/commit/2b1c5a7ce89fc36c42eeb21607491d760feb905d))

- Rename `force_local_rendering` to `has_gpu_rendering` and negate result
  ([`2a39eda`](https://github.com/Kitware/pan3d/commit/2a39eda68490e7f2eed0ebe6d1625b45c95e4123))

- Replace `dataset_path` with `dataset_info`; value for `source` can determine which `load_dataset`
  method to use
  ([`ae545ae`](https://github.com/Kitware/pan3d/commit/ae545ae05acbb27d56f3a6404d127e375d19638f))

- Replace branching if logic for catalogs with `builder._call_catalog_function`
  ([`ce02dd4`](https://github.com/Kitware/pan3d/commit/ce02dd403eb078d3fdedec2aa896c84be9aec2d9))

- Separate default load dataset function for paths and urls
  ([`92b0845`](https://github.com/Kitware/pan3d/commit/92b084538db0d86cc2134c361fd1cdf7dc33549e))

- Store docs images with git-lfs
  ([`c12e0c3`](https://github.com/Kitware/pan3d/commit/c12e0c30e481b7c985ff3c25ef7132da6f40b137))

- Suggested changes from @jourdain
  ([`3423103`](https://github.com/Kitware/pan3d/commit/34231038ac197dada66a74b1ac371be3654900d4))

- Use catalogs list kwarg instead of multiple boolean catalog flags
  ([`0b48175`](https://github.com/Kitware/pan3d/commit/0b48175a66348edf70a9d8da7ff438227a753ab7))

- **catalogs**: Create base methods in catalogs module that dynamically import relevant submodules
  ([`633918d`](https://github.com/Kitware/pan3d/commit/633918d858ee32d476c7d76acbf2ceece309a87e))

- **dataset_builder**: Separate trame and plotting from data configuration
  ([`4ea790a`](https://github.com/Kitware/pan3d/commit/4ea790a54ceec8e94a0df58b00d97ed70dfc8416))

- **pangeo**: Use methods similar to esgf module
  ([`3ed0b29`](https://github.com/Kitware/pan3d/commit/3ed0b29ece034dc1ad7788a3e12a3eac231c682f))

- **setup**: Delete setup.cfg
  ([`f68cd65`](https://github.com/Kitware/pan3d/commit/f68cd65ad75fe1ca5f43e770aa8c7fe8de0fa32e))

### Testing

- Add tests for builder and viewer
  ([`deae267`](https://github.com/Kitware/pan3d/commit/deae26704d2448f81e9266e8649dd11bec52069d))

- Disable `DatasetViewer` automatic render in tests
  ([`203569a`](https://github.com/Kitware/pan3d/commit/203569ab48f4aef409090c4748de895113345d79))

- Update expected state with new default expanded coordinates
  ([`87e073c`](https://github.com/Kitware/pan3d/commit/87e073cf94bf2e4a51b73ed837a75ab42e0712c3))

- Update expected state with new drawer defaults
  ([`954969f`](https://github.com/Kitware/pan3d/commit/954969f56dfa705429b80f867b18e9161d9f62fb))

- Update expected values in tests
  ([`e08af6b`](https://github.com/Kitware/pan3d/commit/e08af6b40fb2a17f689071a8b484e69b9157c97b))

- Update main testing workflow
  ([`39eb6b1`](https://github.com/Kitware/pan3d/commit/39eb6b1537ae44e2fcd349ec13cee486bcee3a5f))

- Update tests with `dataset_info` values instead of `dataset_path` values
  ([`15cf1d0`](https://github.com/Kitware/pan3d/commit/15cf1d03ea021a1600c34090705774b62b20ed4a))

- **builder**: Add test to cover invalid values to DatasetBuilder setters
  ([`93326fd`](https://github.com/Kitware/pan3d/commit/93326fd26fe195e7c853860fe751963ba47439e3))

- **export**: Re-export `example_config_xarray.json`
  ([`7f6be7c`](https://github.com/Kitware/pan3d/commit/7f6be7cfc84ec5b387b6ce06cf7028193d79c26b))

- **export**: Remove time slicing to match exported config
  ([`cb08b41`](https://github.com/Kitware/pan3d/commit/cb08b417535654cd549892c30be41ccfbd58a78e))

- **pre-commit**: Omit changelog from codespell
  ([`38efb4f`](https://github.com/Kitware/pan3d/commit/38efb4f29bcf9d1710557a16f749865191247dc7))
