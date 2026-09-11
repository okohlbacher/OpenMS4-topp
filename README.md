# TOPP after standalone tool extraction

OpenNuXL, ProSE, NucleicAcidSearchEngine, CometAdapter, MascotAdapterOnline,
DatabaseSuitability, ProteomicsLFQ and ParquetDiff now have separate source
repositories and manifests. The remaining package owns 123 potential tools
(122 when optional FeatureLinkerWNet is disabled), preserving executable names.
Install the separate products beside TOPP for the complete historical suite.
File-format support remains in the Core SDK. Numerical fixtures remain TestData.

# OpenMSTOPP 1.0.0 experimental

Independent source package: 122 command-line tools, plus FeatureLinkerWNet when enabled in the SDK. Requires the exact OpenMS core and OpenMSCLI commits in `dependencies.lock.json` installed in `CMAKE_PREFIX_PATH`. No parent source/build tree is used.

First build and install the pinned Core SDK with `OPENMS_BUILD_TEST_SUPPORT=ON`,
then build and install the pinned OpenMSCLI package against that SDK. TOPP links
their imported `OpenMS::Core` and `OpenMS::CLI` targets; FuzzyDiff also links
`OpenMS::TestFramework` from Core's TestSupport component. Use the same compiler,
architecture and build configuration as those SDKs. For a Debug SDK installed at
`/sdk/openms4`:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH=/sdk/openms4 -DCMAKE_INSTALL_PREFIX=/sdk/openms4
cmake --build build --parallel 4
ctest --test-dir build --output-on-failure
cmake --install build
```

Use a Core+CLI dependency prefix without an existing TOPP installation while
running build-tree tests, and test before installing TOPP. The registry rejects
duplicate tool names when it discovers both a build-tree TOPP registry and a
separate installed TOPP registry beside CLI. Once installed, test the installed
executables with the OpenMS4-test-data harness.

Set `OPENMS_TOOL_PREFIX_PATH` to installation prefixes to discover independently installed tools. Scientific algorithms remain in core; this package owns the TOPP executable front ends. FLASH and OpenSWATH executable front ends belong to the separate OpenMS4-flash and OpenMS4-openswath packages. Product version is independent of the core version. All existing numerical fixtures and the original suite are preserved in OpenMS4-test-data. Adapters still require their documented external executables; those are not silently downloaded or bundled.

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

## CI and packages

GitHub Actions builds TOPP against the exact Core and CLI revisions in
`dependencies.lock.json` on Linux x64/ARM64, macOS x64/ARM64 and Windows x64.
The jobs test CLI, compile TOPP with warnings treated as errors, run every TOPP
metadata test, install the tools, and start the installed `OpenMSInfo` binary.
Each native archive contains only this TOPP product and its dependency lock.
The private CLI source is checked out with a read-only deploy key stored as the
`OPENMS4_CLI_DEPLOY_KEY` repository secret; jobs never receive write access to
that dependency.

Two additional macOS jobs build the pinned Core Homebrew formula, CLI and TOPP
with Homebrew dependencies. The cask depends on the Core formula and contains
CLI and all TOPP executables. Tags beginning with `topp-v` publish only
artifacts from a successful branch CI run for the same commit.

On macOS, install the tested tools and their Core formula dependency from the
repository tap:

```sh
brew tap okohlbacher/openms4-topp https://github.com/okohlbacher/OpenMS4-topp
brew install --cask okohlbacher/openms4-topp/openms4-topp
```

The OpenMS `FileInfo` executable is installed as `OpenMSFileInfo` to avoid a
name collision with Leptonica's image utility on case-insensitive macOS file
systems.
