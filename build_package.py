#!/usr/bin/python

import argparse
import os
import shutil
import subprocess

parser = argparse.ArgumentParser(description="Build a Raspbian .deb package for the Emunah Menorah")
parser.add_argument("-d", "--tempdir", dest="tempdir", required=True, help="Temporary working directory for building the package; the directory must be empty or not exist")
args = parser.parse_args()

# Check that the temp working directory is clean
if os.path.exists(args.tempdir):
    if (not os.path.isdir(args.tempdir)) or (len(os.listdir(args.tempdir)) > 0):
        raise Exception("The temp directory must be empty or not exist")
else:
    os.makedirs(args.tempdir)

# Copy files
shutil.copytree("package_files/DEBIAN", os.path.join(args.tempdir, "DEBIAN"))
shutil.copytree("package_files/etc", os.path.join(args.tempdir, "etc"), symlinks=True)

bin_dir = os.path.join(args.tempdir, "usr/local/bin/emunah-menorah")
os.makedirs(bin_dir)
shutil.copy2("dimmer_control.py", bin_dir)

html_dir = os.path.join(args.tempdir, "var/www/html/menorah")
os.makedirs(html_dir)
shutil.copy2("board_cleanup.py", html_dir)
shutil.copy2("board_init.sh", html_dir)
shutil.copy2("menorah_page.py", html_dir)
os.chmod(os.path.join(html_dir, "board_cleanup.py"), 0o700)
os.chmod(os.path.join(html_dir, "board_init.sh"), 0o700)

light_state_dir = os.path.join(args.tempdir, "var/www/html/menorah/light_state")
os.mkdir(light_state_dir)
os.chmod(light_state_dir, 0o777)

module_dir = os.path.join(args.tempdir, "usr/lib/python2.7/dist-packages")
os.makedirs(module_dir)
shutil.copy2("menorah_functions.py", module_dir)

# Build the package
subprocess.check_call(["dpkg-deb", "--build", args.tempdir])
