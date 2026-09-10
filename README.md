# OpenMSTOPP 1.0.0 experimental

Independent source package: 131 command-line tools. Requires the exact OpenMS core and OpenMSCLI commits in `dependencies.lock.json` installed in `CMAKE_PREFIX_PATH`. No parent source/build tree is used.

```sh
cmake -S . -B build -DCMAKE_PREFIX_PATH=/sdk/openms4 -DCMAKE_INSTALL_PREFIX=/sdk/openms4
cmake --build build --parallel 4
ctest --test-dir build --output-on-failure
cmake --install build
```

Set `OPENMS_TOOL_PREFIX_PATH` to installation prefixes to discover independently installed tools. Scientific algorithms, including FLASH and OpenSWATH algorithms, remain in core; this package owns their executable front ends. Product version is independent of the core version. All existing numerical fixtures and the original suite are preserved in OpenMS4-test-data. Adapters still require their documented external executables; those are not silently downloaded or bundled.

## Installation and source identity

The example co-locates independently built packages in one install prefix.
Unix executables and libraries use relative loader paths to its library directory;
Windows deployments place the Core/CLI and dependency DLLs beside the executables
in `bin`. For deliberately separate Unix prefixes, supply their library paths in
`CMAKE_INSTALL_RPATH`; this is a fixed-prefix deployment rather than a relocatable
combined bundle. `OPENMS_TOOL_PREFIX_PATH` controls tool discovery, not native
library loading. Package external native dependencies when creating a bundle.

`OPENMS4_REQUIRE_CLEAN_SOURCE=ON` rejects uncommitted source inputs for published
builds. Source archives must provide `OPENMS4_SOURCE_REVISION` and explicitly
assert `OPENMS4_SOURCE_DIRTY`; Git checkouts derive both from the checkout.
The consumer helper is generated from the parent experiment's canonical CMake
source; standalone builds do not require the parent checkout.

TOPP always requires Core's optional `TestSupport` component to build FuzzyDiff,
even when `BUILD_TESTING=OFF`. This does not make fixture files a dependency of
every installed TOPP executable. `tools.json` owns executable registration and
categories; FeatureLinkerWNet is enabled only with the SDK's WNet feature.
