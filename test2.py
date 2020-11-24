#!/usr/bin/env python
import subprocess
from subprocess import call

def undefine_all():
    ps = subprocess.Popen(["sudo", "virsh", "list", "--inactive", "--name"], stdout=subprocess.PIPE)
    output = subprocess.check_output(["xargs", "-r", "-n", "1", "virsh","undefine"], stdin=ps.stdout)
    ps.wait()

undefine_all()

# ps = subprocess.Popen(('ps', '-A'), stdout=subprocess.PIPE)
# output = subprocess.check_output(('grep', 'process_name'), stdin=ps.stdout)
# ps.wait()