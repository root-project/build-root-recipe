# Building ROOT for ROOT developers, step by step

## 1. Forking the `root` and `roottest` repositories

You need to have your own forks of the repositories in order to propose
modifications in the form of GitHub PRs. In some cases the modifications will
need to go in `roottest`, so it's better to clone both. Go on the respective
websites:

* <https://github.com/root-project/root>
* <https://github.com/root-project/roottest>

And click on the `Fork` button in the top right of the web UI.

## 2. Clone the repositories and track the upstream git remote

You can now clone both repositories on your machine, e.g. via

```bash
git clone https://github.com/YOURUSERNAME/root.git
git clone https://github.com/YOURUSERNAME/roottest.git
```

To track changes in the main repositories, add the `upstream` remotes.

Inside the `root` directory:

```bash
git remote add upstream https://github.com/root-project/root.git
```

Inside the `roottest` directory:

```bash
git remote add upstream https://github.com/root-project/roottest.git
```

## 3. Create build and install directories

To keep things clean, it is suggested to create separate directories for the
builds and for the installations.

```bash
mkdir rootbuild rootinstall
```

## 4. Configure the CMake build

There are many [configuration options](https://root.cern/install/build_from_source/#all-build-options).
For the purposes of development and testing, the following configuration is
suggested:

```bash
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -Dtesting=ON -Droottest=ON -DCMAKE_INSTALL_PREFIX=rootinstall/myinstall -B rootbuild/mybuild -S root
```

The process of launching the Cmake build may be sped up by using the ccache package, if it is installed in the system. To activate it, add `-Dccache=ON` to variables.

## 5. Build and install

Finally, you can launch the CMake build via:

```bash
cmake --build rootbuild/mybuild --target install -jNPROC
```

where `NPROC` is the number of available cores you want to send in parallel for the build.
