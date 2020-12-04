#!/usr/bin/env python

import os
import sys
import subprocess
from subprocess import call

LOAD_BALANCER_NAME = "lb"

def virsh_lb_forwarding_setup():
    current_path = os.getcwd()
    TMP_DIR_NAME = "forwarding_tmp"
    TMP_DIR_PATH = current_path + '/' + TMP_DIR_NAME

    os.mkdir(TMP_DIR_PATH)

    # /etc/hostname config file creation
    forwarding_file = open(TMP_DIR_PATH + '/sysctl.conf', 'w')
    forwarding_file.write("net.ipv4.ip_forward=1")
    forwarding_file.close()
    # copy hostname file into the VM /etc/hostname path
    call(["sudo", "virt-copy-in", "-a", LOAD_BALANCER_NAME + ".qcow2", TMP_DIR_PATH + "/sysctl.conf", "/etc"])

virsh_lb_forwarding_setup()