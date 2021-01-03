"""A script which downloads, compiles, and installs the dependencies needed to
install and run pyMode.

Based on https://github.com/anstmichaels/emopt

WGMS3D depends on 2 core open source software packages:

- PETSc -- solving large Ax=b problems, parallel computing
- SLEPc -- solving large eigenvalue problems in parallel

To run this script, simply call:

    $ python install.py

By default, this will create the directory ~/.pymode and install all of the
libraries there. If you want to install these files elsewhere, you can use the
prefix flag:

    $ python install.py --prefix=/custom/install/path

For example, for a system-wide install, we might use:

    $ python install.py --prefix=/opt/local

where /opt/local is an existing directory.

If this script fails for any reason, read through the output and check the
install.log file which should be created. This should give you some indication
of what went wrong. In most cases, the issue will be related to not having the
appropriate prerequisite software packages installed.
"""

import os, sys, shutil, glob, requests
from subprocess import call
from argparse import ArgumentParser

# pymode parameters
pymode_deps = ".pymode_deps"

# Package Parameters
PETSC_VERSION = "3.12.1"
SLEPC_VERSION = "3.12.1"


class Logger(object):
    """Setup log file."""

    def __init__(self, log_fname):
        self.terminal = sys.stdout

        # clean up old log
        if os.path.isfile(log_fname):
            os.remove(log_fname)

        self.log = open(log_fname, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


def write_deps_file(home_dir, include_dir, install_dir):
    """Generate the dependency file.

    The dependency file, which is stored at ~/.emopt_deps, contains the paths
    of the installed dependencies. This is loaded by the setup.py script used
    to install EMopt.
    """
    dep_fname = home_dir + "/" + pymode_deps
    with open(dep_fname, "w") as fdep:
        fdep.write("PETSC_DIR=" + install_dir + "\n")
        fdep.write("PETSC_ARCH=\n")
        fdep.write("SLEPC_DIR=" + install_dir + "\n")


def print_message(s):
    """Define custom print message which adds color."""
    print("".join(["\033[92m", s, "\033[0m"]))


def install_petsc(install_dir):
    """Compile and install PETSc."""
    # Clean up environment variables. If these are set the PETSc compilation will
    # fail
    if "PETSC_DIR" in os.environ:
        del os.environ["PETSC_DIR"]
    if "PETSC_ARCH" in os.environ:
        del os.environ["PETSC_ARCH"]

    # get PETSc
    print_message("Downloading PETSc...")
    petsc_url = (
        "http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-"
        + PETSC_VERSION
        + ".tar.gz"
    )
    petsc_fname = "petsc-" + PETSC_VERSION + ".tar.gz"
    r = requests.get(petsc_url, allow_redirects=True)
    with open(petsc_fname, "wb") as fsave:
        fsave.write(r.content)

    # unzip package
    call(["tar", "xvzf", petsc_fname])

    petsc_folder = "petsc-" + PETSC_VERSION
    os.chdir(petsc_folder)

    # compile
    print_message("Compiling PETSc...")
    call(
        [
            "./configure",
            "--with-scalar-type=complex",
            "--with-mpi=1",
            "--COPTFLAGS='-O3'",
            "--FOPTFLAGS='-O3'",
            "--CXXOPTFLAGS='-O3'",
            "--with-debugging=0",
            "--prefix=" + install_dir,
            "--download-scalapack",
            "--download-mumps",
            "--download-openblas",
        ]
    )
    call(["make", "all", "test"])

    print_message("Installing PETSc...")
    call(["make", "install"])
    os.environ["PETSC_DIR"] = install_dir

    # cleanup
    print_message("Cleaning up working directory...")
    os.chdir("../")
    shutil.rmtree(petsc_folder)


def install_slepc(install_dir):
    """Compile and install SLEPc."""
    # SLEPC_DIR environment var cant be set
    if "SLEPC_DIR" in os.environ:
        del os.environ["SLEPC_DIR"]

    # get the SLEPc source
    print_message("Downloading SLEPc source...")
    slepc_url = (
        "http://slepc.upv.es/download/distrib/slepc-" + SLEPC_VERSION + ".tar.gz"
    )
    slepc_fname = "slepc-" + SLEPC_VERSION + ".tar.gz"
    r = requests.get(slepc_url, allow_redirects=True)
    with open(slepc_fname, "wb") as fsave:
        fsave.write(r.content)

    # unzip package
    call(["tar", "xvzf", slepc_fname])

    # compile and install
    print_message("Compiling SLEPc...")
    slepc_folder = "slepc-" + SLEPC_VERSION
    os.chdir(slepc_folder)
    call(["./configure", "--prefix=" + install_dir])
    call(["make", "all"])
    call(["make", "install"])
    call(["make", "test"])

    # cleanup
    os.chdir("../")
    shutil.rmtree(slepc_folder)
    os.remove(slepc_fname)


def install_begin(build_dir):
    """Prepare for building dependencies.
    This primarily involves moving into the build directory.
    """
    os.chdir(build_dir)


def install_end(start_dir, build_dir):
    """Cleanup post installation, i.e. delete build dir."""
    os.chdir(start_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)


def install_deps():
    # setup logging
    sys.stdout = Logger("install.log")

    # Do Argument parsing
    parser = ArgumentParser()
    parser.add_argument(
        "--prefix=",
        metavar="filepath",
        type=str,
        dest="prefix",
        help="Set the installation directory for dependencies",
    )

    args = parser.parse_args()

    # setup install directory
    home_dir = os.path.expanduser("~")
    if args.prefix == None:
        install_dir = home_dir + "/.pymode/"
    else:
        install_dir = args.prefix
        print(install_dir)

    if not os.path.exists(install_dir):
        os.makedirs(install_dir)

    # setup installation subdirs
    include_dir = install_dir + "include/"
    lib_dir = install_dir + "lib/"

    if not os.path.exists(include_dir):
        os.makedirs(include_dir)

    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)

    # setup working directory
    current_dir = os.getcwd()
    build_dir = "./build/"
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    # save file to user's home directory which will tell pymode where to look for the
    # dependencies

    # install dependencies
    install_begin(build_dir)
    try:
        install_petsc(install_dir)
        install_slepc(install_dir)
        # install_end(current_dir, build_dir)
        write_deps_file(home_dir, include_dir, install_dir)
    except Exception as e:
        print(e)
        install_end(current_dir, build_dir)

    print_message("Finished installing pymode dependencies!")


if __name__ == "__main__":
    install_deps()
