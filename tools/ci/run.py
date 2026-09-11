#!/usr/bin/env python3
"""Build and test TOPP against installed, pinned Core and CLI packages."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time


def archive_install(prefix: Path, output: Path, name: str) -> Path:
    """Create a checksummed archive while preserving library symlinks."""
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{name}.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        stream.add(prefix, arcname=name)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix(".gz.sha256").write_text(
        f"{digest}  {archive.name}\n", encoding="utf-8")
    return archive


def core_prefix(extracted: Path) -> Path:
    """Find the single Core SDK root extracted by the workflow."""
    candidates = [path for path in extracted.iterdir()
                  if path.is_dir() and (path / "source-revision.txt").is_file()]
    if len(candidates) != 1:
        raise ValueError(f"Expected one extracted Core SDK, found {len(candidates)}")
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--core-dir", required=True, type=Path)
    parser.add_argument("--cli-source", required=True, type=Path)
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[2]
    work = args.work_dir.resolve()
    if args.jobs < 1 or (work.exists() and any(work.iterdir())):
        parser.error("--jobs must be positive and --work-dir must be empty")
    results = work / "results"
    results.mkdir(parents=True)
    core = core_prefix(args.core_dir.resolve())
    cli_build, cli_install = work / "cli-build", work / "cli"
    topp_build, topp_install = work / "topp-build", work / "topp"
    dependencies = Path(os.environ["CONDA_PREFIX"]).resolve()
    windows = sys.platform == "win32"
    dependency_prefix = dependencies / "Library" if windows else dependencies
    generator = "Visual Studio 17 2022" if windows else "Ninja"
    configuration = "Release"
    env = os.environ.copy()
    runtime_dirs = [dependency_prefix / "bin", core / "bin", cli_install / "bin"]
    env["PATH"] = os.pathsep.join(str(path) for path in runtime_dirs) + os.pathsep + env["PATH"]
    if sys.platform == "linux":
        env["LD_LIBRARY_PATH"] = os.pathsep.join(
            [str(dependency_prefix / "lib"), str(core / "lib"), str(cli_install / "lib")])
    elif sys.platform == "darwin":
        env["DYLD_FALLBACK_LIBRARY_PATH"] = os.pathsep.join(
            [str(dependency_prefix / "lib"), str(core / "lib"), str(cli_install / "lib")])
    commands = []

    def run(name: str, command: list[str], cwd: Path = source) -> None:
        started = time.monotonic()
        print(f"\n--- {name} ---", flush=True)
        log = results / f"{name}.log"
        with log.open("w", encoding="utf-8") as stream:
            process = subprocess.Popen(command, cwd=cwd, env=env, text=True,
                                       encoding="utf-8", errors="replace",
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in process.stdout:
                stream.write(line)
                print(line, end="", flush=True)
            code = process.wait()
        commands.append({"name": name, "command": command, "returncode": code,
                         "elapsed_seconds": round(time.monotonic() - started, 3)})
        (results / "commands.json").write_text(
            json.dumps(commands, indent=2) + "\n", encoding="utf-8")
        if code:
            raise subprocess.CalledProcessError(code, command)

    common = ["-G", generator, f"-DCMAKE_BUILD_TYPE={configuration}",
              "-DOPENMS4_REQUIRE_CLEAN_SOURCE=ON"]
    if windows:
        common += ["-A", "x64", "-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreadedDLL"]
    elif sys.platform == "darwin":
        common += [f"-DOpenMP_ROOT={dependency_prefix.as_posix()}",
                   f"-DCURL_ROOT={dependency_prefix.as_posix()}",
                   "-DCMAKE_FIND_FRAMEWORK=LAST"]
    run("driver-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tools/ci", "-v"])
    run("configure-cli", ["cmake", "-S", str(args.cli_source.resolve()), "-B", str(cli_build),
                           f"-DCMAKE_INSTALL_PREFIX={cli_install.as_posix()}",
                           f"-DCMAKE_PREFIX_PATH={core.as_posix()};{dependency_prefix.as_posix()}",
                           *common])
    run("build-cli", ["cmake", "--build", str(cli_build), "--config", configuration,
                       "--parallel", str(args.jobs)])
    run("test-cli", ["ctest", "--test-dir", str(cli_build), "-C", configuration,
                      "--output-on-failure", "--no-tests=error", "--parallel", str(args.jobs)])
    run("install-cli", ["cmake", "--install", str(cli_build), "--config", configuration])
    topp_prefixes = f"{core.as_posix()};{cli_install.as_posix()};{dependency_prefix.as_posix()}"
    run("configure-topp", ["cmake", "-S", str(source), "-B", str(topp_build),
                            f"-DCMAKE_INSTALL_PREFIX={topp_install.as_posix()}",
                            f"-DCMAKE_PREFIX_PATH={topp_prefixes}",
                            "-DOPENMS4_WARNINGS_AS_ERRORS=ON", *common])
    run("build-topp", ["cmake", "--build", str(topp_build), "--config", configuration,
                        "--parallel", str(args.jobs)])
    run("test-topp", ["ctest", "--test-dir", str(topp_build), "-C", configuration,
                       "--output-on-failure", "--no-tests=error", "--parallel", str(args.jobs)])
    run("install-topp", ["cmake", "--install", str(topp_build), "--config", configuration])
    installed_tools = sorted((topp_install / "bin").glob("*.exe" if windows else "*"))
    if len(installed_tools) < 120:
        raise ValueError(f"Expected at least 120 installed tools, found {len(installed_tools)}")
    env["OPENMS_TOOL_PREFIX_PATH"] = str(topp_install)
    run("installed-openms-info", [str(topp_install / "bin" / ("OpenMSInfo.exe" if windows else "OpenMSInfo")),
                                  "--help"])
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    shutil.copyfile(source / "dependencies.lock.json", topp_install / "dependencies.lock.json")
    (topp_install / "source-revision.txt").write_text(revision + "\n", encoding="utf-8")
    archive_install(topp_install, work / "dist",
                    f"OpenMS4-topp-{args.platform}-Release-{revision[:12]}")


if __name__ == "__main__":
    main()
