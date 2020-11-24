#!/usr/bin/env python
import subprocess
from subprocess import call

ps = subprocess.Popen(["sudo", "virsh", "list", "--inactive", "--name"], stdout=subprocess.PIPE)
output = subprocess.check_output(["xargs", "-r", "-n", "1", "virsh","undefine"], stdin=ps.stdout)
ps.wait()