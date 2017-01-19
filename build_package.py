#!/usr/bin/python

import argparse
import os
import shutil
import subprocess

parser = argparse.ArgumentParser(description="Build a Raspbian .deb package for the Emunah Menorah")
parser.add_argument("-d", "--tempdir", dest="tempdir", required=True, help="Temporary working directory for building the package; the directory must not exist")
args = parser.parse_args()

# Check that the temp working directory is clean
if os.path.exists(args.tempdir):
    raise Exception("The temp directory must be empty or not exist")

# Copy files to the temp directory
shutil.copytree("package_files", args.tempdir, symlinks=True)

# Build the package
os.chdir(args.tempdir)
subprocess.check_call(["dpkg-buildpackage", "-A", "-us", "-uc"])
