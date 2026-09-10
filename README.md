# OpenMSTOPP 1.0.0 experimental

Independent source package: 131 command-line tools. Requires the exact OpenMS core and OpenMSCLI commits in `dependencies.lock.json` installed in `CMAKE_PREFIX_PATH`. No parent source/build tree is used.

```sh
cmake -S . -B build -DCMAKE_PREFIX_PATH="/sdk/core;/sdk/cli" -DCMAKE_INSTALL_PREFIX=/products/topp
cmake --build build --parallel 4
ctest --test-dir build --output-on-failure
cmake --install build
```

Set `OPENMS_TOOL_PREFIX_PATH` to installation prefixes to discover independently installed tools. Scientific algorithms, including FLASH and OpenSWATH algorithms, remain in core; this package owns their executable front ends. Product version is independent of the core version. All existing numerical fixtures and the original suite are preserved in OpenMS4-test-data. Binary validation remains pending an authorized build. Adapters still require their documented external executables; those are not silently downloaded or bundled.
