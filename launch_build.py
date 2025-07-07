import argparse
import os
import re
import shlex
import subprocess
import textwrap
from typing import Iterable


def create_directories_if_necessary() -> Iterable[str]:
    cwd = os.getcwd()
    root_home = os.path.join(cwd, "root")
    if not os.path.exists(root_home):
        subprocess.run(
            shlex.split(
                "git clone -o upstream https://github.com/root-project/root.git"
            ),
            check=True,
        )
    root_build = os.path.join(cwd, "rootbuild")
    if not os.path.exists(root_build):
        os.mkdir(root_build)
    root_install = os.path.join(cwd, "rootinstall")
    if not os.path.exists(root_install):
        os.mkdir(root_install)

    return root_home, root_build, root_install


# builtin_glew is necessary on latest CMake versions https://gitlab.kitware.com/cmake/cmake/-/issues/19662
build_config = {
    "default": "-DCMAKE_BUILD_TYPE=RelWithDebInfo -Dbuiltin_glew=ON",
    "debug": (
        "-DCMAKE_BUILD_TYPE=Debug -Dtesting=ON -Droottest=ON "
        "-Dtest_distrdf_pyspark=ON -Dtest_distrdf_dask=ON -Dbuiltin_glew=ON"
    ),
    "relwithdebinfo": (
        "-DCMAKE_BUILD_TYPE=RelWithDebInfo -Dtesting=ON -Droottest=ON "
        "-Dtest_distrdf_pyspark=ON -Dtest_distrdf_dask=ON -Dbuiltin_glew=ON"
    ),
    "minimal": ("-DCMAKE_BUILD_TYPE=RelWithDebInfo -Dminimal=ON"),
}

parser = argparse.ArgumentParser()
parser.add_argument(
    "-j", help="As in 'cmake -jNJOBS'", default=os.cpu_count(), type=int, dest="njobs"
)
parser.add_argument(
    "-n",
    help=(
        "The name of this build. If specified, it takes "
        "precedence over the automatic choice for a name"
    ),
    dest="name",
)
group = parser.add_argument_group(
    "CMake configuration [required]",
    textwrap.dedent("""
    The 'mode' option allows to choose one of the predefined CMake configuration
    strings. Otherwise, specify a custom string via the 'config' option
    """),
)
exclusive_group = group.add_mutually_exclusive_group(required=False)
exclusive_group.add_argument(
    "-m",
    help="One of the predefined CMake configuration modes",
    choices=list(build_config.keys()),
    default="default",
    dest="mode",
)
exclusive_group.add_argument(
    "-c",
    help=(
        textwrap.dedent("""
    Custom list of CMake options. Specify this option with an equal sign and
    quoted, as in: '-c=\"-DOpt1=ON -DOpt2=OFF\"'
    """)
    ),
    nargs="*",
    dest="config",
)
parser.add_argument(
    "--install", help="Also install ROOT to the install directory", action="store_true"
)
parser.add_argument(
    "-g",
    help='Specify a CMake generator for the build, e.g. "Unix MakeFiles", "Ninja" etc.',
    dest="generator",
)
parser.add_argument(
    "--print-configs",
    help="Print the available CMake configurations and exit",
    action="store_true",
)
args = parser.parse_args()


def launch_build():
    if args.print_configs:
        from pprint import pprint

        print("Available CMake configurations:")
        pprint(build_config)
        return

    root_home, root_build, root_install = create_directories_if_necessary()

    if args.name is None:
        # Figure out a sensible name to give to the build/install directories
        p = subprocess.run(
            ["git", "status"], cwd=root_home, check=True, capture_output=True
        )
        gitstatus = p.stdout.decode()
        pattern = re.compile("^On branch (?P<branch>.*)")
        branch = pattern.match(gitstatus).groupdict()["branch"]

        if branch == "master":
            # Further specify builds on the master branch with the commit SHA
            p = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=root_home,
                check=True,
                capture_output=True,
            )
            sha = p.stdout.decode().rstrip()
            branch += "-" + sha

        dirname = branch + "-" + args.mode if args.mode else branch + "-custom"
    else:
        dirname = args.name

    # Check if we are using a conda environment
    dirname = dirname + (
        f"-conda-{os.environ['CONDA_DEFAULT_ENV']}"
        if os.environ.get("CONDA_DEFAULT_ENV", "")
        else ""
    )

    build_dir = os.path.join(root_build, dirname)
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    install_dir = os.path.join(root_install, dirname)
    if not os.path.exists(install_dir):
        os.mkdir(install_dir)

    if not os.path.exists(os.path.join(build_dir, "CMakeCache.txt")):
        base_config = "cmake -Dccache=ON"
        if args.generator is not None:
            base_config += f' -G"{args.generator}"'
        base_config = shlex.split(base_config)
        mode_config = args.config[0] if args.config else build_config[args.mode]
        mode_config = shlex.split(mode_config)
        dirs_config = shlex.split(
            f"-DCMAKE_INSTALL_PREFIX={install_dir} -B {build_dir} -S {root_home}"
        )
        configure_command = base_config + mode_config + dirs_config
        subprocess.run(configure_command, check=True)

    njobs = args.njobs
    build_command = f"cmake --build {build_dir} -j{njobs}"
    if args.install:
        build_command += " --target install"
    subprocess.run(shlex.split(build_command), check=True)


if __name__ == "__main__":
    launch_build()
