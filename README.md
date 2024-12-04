# General guidelines and recipes to create a development environment with ROOT

Developing ROOT requires being able to build the project from source and knowing
which components to configure depending on one's needs. See the following
sections to set up your coding environment with ROOT.

## Prerequisites

ROOT depends on other libraries, some of them are necessary also in the build
process. You can find a list dependencies [on our website](https://root.cern/install/dependencies/).
Follow the instructions to install the dependencies on your system.

There are also some Python optional runtime dependencies which are nonetheless
useful in a development environment. You can find them listed in [requirements.txt](https://raw.githubusercontent.com/root-project/root/master/requirements.txt).

## Building ROOT

The ROOT source code is built via [CMake](https://cmake.org/). Usually in a
development environment one would need a build of ROOT with debug symbols, i.e.
`-DCMAKE_BUILD_TYPE=RelWithDebInfo` or `-DCMAKE_BUILD_TYPE=Debug`. Detailed
instructions on how to build ROOT from source are available [on our website](https://root.cern/install/build_from_source/).

## Recipes for installation

### Step-by-step instructions

Detailed instructions are available in the document [step_by_step_instructions.md](step_by_step_instructions.md)
which is a walkthrough of all the steps required to build ROOT and things to
look out for.

### The build script

Alternatively, an automated [Python build script](launch_build.py) is available.
This can help you streamline the building process:

```bash
python launch_build.py -h
```
```text
usage: launch_build.py [-h] [-j NJOBS] [-n NAME] (-m {default,debug,relwithdebinfo,minimal} | -c [CONFIG ...])

options:
  -h, --help            show this help message and exit
  -j NJOBS              As in 'cmake -jNJOBS'
  -n NAME               The name of this build. If specified, it takes precedence over the automatic choice for a name

CMake configuration [required]:
  The 'mode' option allows to choose one of the predefined CMake configuration strings. Otherwise, specify a custom string via the 'config' option

  -m {default,debug,relwithdebinfo,minimal}
                        One of the predefined CMake configuration modes
  -c [CONFIG ...]       Custom list of CMake options. Specify this option with an equal sign and quoted, as in: '-c="-DOpt1=ON -DOpt2=OFF"'
```

It creates the following directories in the current working directory:

```text
- root/
- roottest/
- rootbuild/
- rootinstall/
```

* `root` is the directory where the ROOT source resides. If not already
  present, it will be downloaded.
* `roottest` is the directory where the separate testing repository roottest
  source resides. If not already present, it will be downloaded.
* `rootbuild` and `rootinstall` store respectively build and install directories
  produced by CMake. Every time the `launch_build.py` script is launched, it
  creates two separate sub-directories for the current build and installation,
  for example:

  ```text
  - rootbuild/
    --> build1/
    --> build2/
  - rootinstall/
    --> install1/
    --> install2/
  ```

The script launches a CMake build with the appropriate flags, depending on
either one of the already available modes (see the `m` option) or the flags
passed via the `c` option. For example:

```bash
python launch_build.py -m relwithdebinfo
python launch_build.py -n mybuild -c="-Dminimal=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo"
```

### Activating ROOT in your environment after installation

After the CMake build has finished without errors, you can set up your environment
to use the ROOT installation you just created via a `thisroot` script, for
example on a Unix system with the bash shell:

```sh
source <build_or_install_dir>/bin/thisroot.sh
```

