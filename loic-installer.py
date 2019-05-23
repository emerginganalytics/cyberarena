#!/usr/bin/env python3
# Script to automatically install Low Orbital Ion Cannon for educational and testing purposes on Debian 9
# Author: Chance Melby

import subprocess
import os

subprocess.call(["sudo", "apt-get", "update", "-y"], shell=False)
# upgrade = subprocess.call(["sudo", "apt-get", "upgrade", "-y"], shell=False)
# add Mono repository
subprocess.call(["sudo", "apt", "install", "apt-transport-https", "dirmngr", "gnupg", "ca-certificates"],
                shell=False)
subprocess.call(["sudo", "apt-key", "adv", "--keyserver", "hkp://keyserver.ubuntu.com:80", "--recv-keys",
                 "3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF"], shell=False)
subprocess.call(["echo", "'deb https://download.mono-project.com/repo/debian stable-stretch main'", "|", "sudo",
                 "tee", "/etc/apt/sources.list.d/mono-official-stable.list"], shell=False)
subprocess.call(["sudo", "apt-get", "update", "-y"], shell=False)
# install mono-devel and git
subprocess.call(["sudo", "apt-get", "install", "mono-devel"], shell=False)
subprocess.call(["sudo", "apt-get", "install", "git"], shell=False)
# create directory for loic
p = subprocess.Popen("mkdir loic", shell=True)
p.wait()
os.chdir("loic/")
# install and run loic
subprocess.call(["wget", "https://raw.github.com/nicolargo/loicinstaller/master/loic.sh"], shell=False)
subprocess.call(["sudo", "chmod", "a+x", "loic.sh"], shell=False)
subprocess.call(["./loic.sh", "install"], shell=False)
os.chdir("LOIC/")
subprocess.call(["./loic.sh", "run"], shell=False)
subprocess.call(["./loic.sh", "run"], shell=False)
