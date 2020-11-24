#!/usr/bin/env python
import os
import sys
import subprocess
from subprocess import PIPE
from subprocess import call
import argparse
from lxml import etree
import logging
import sys
import tempfile

from os import listdir
from os.path import isfile, join
import time
import shutil

VM_USERNAME = "cdps"
VM_PASSWORD = "cdps"

current_path = os.getcwd()

BASE_ADRESS_LAN1 = "10.0.1.2"
LAN1 = {
    "network": "10.0.1.0",
    "netmask": "255.255.255.0",
    "gateway": "10.0.1.1"
}
CLIENT_IP = ""


BASE_ADRESS_LAN2 = "10.0.2.11"
LAN2 = {
  "network": "10.0.2.0",
  "netmask": "255.255.255.0",
  "gateway": "10.0.2.1"
}

SERVER_IPs = ["10.0.2.11", "10.0.2.12", "10.0.2.13", "10.0.2.14", "10.0.2.15"]

#print("The current directory is:\n" + current_path)

def get_VM_config_files(vm_name):
    current_path = os.getcwd()
    TMP_DIR_NAME = "tmp_config_files"
    TMP_DIR_PATH= current_path + '/' + TMP_DIR_NAME

    try:
        os.mkdir(TMP_DIR_PATH)

        # /etc/hostname config file creation
        hostname_file = open(TMP_DIR_PATH + '/hostname', 'w')
        hostname_file.write(vm_name)
        hostname_file.close()
        # copy hostname file into the VM /etc/hostname path
        call(["sudo", "virt-copy-in", "-a", vm_name + ".qcow2", TMP_DIR_PATH + "/hostname", "/etc"])
        #/etc/network/interfaces config file creation
        interfaces_file = open(TMP_DIR_PATH + '/interfaces', 'w')

        # write interfaces file
        LINES_TO_WRITE = ["# auto lo\n"
                        , "# iface lo inet loopback\n"
                        , "# iface eth0 inet static\n"
                        , "#     address " + SERVER_IPs.pop(0) + "\n"
                        , "#     network " + LAN2['network']  + "\n"
                        , "#     netmask " + LAN2['netmask']  + "\n"
                        , "#     gateway " + LAN2['gateway']  + "\n"]

        interfaces_file.writelines(LINES_TO_WRITE)
        interfaces_file.close()
        # copy interfaces file into the VM /etc/network/inteface path
        call(["sudo", "virt-copy-in", "-a", vm_name + ".qcow2", TMP_DIR_PATH + "/interfaces", "/etc/network"])

        print(vm_name + " /etc/hostname config file:")
        call(["sudo", "virt-cat", "-a", vm_name + ".qcow2", "/etc/hostname"])
        print("\n" + vm_name + " /etc/network/interfaces config file: ")
        call(["sudo", "virt-cat", "-a", vm_name + ".qcow2","/etc/network/interfaces"])
        print("")
        
        shutil.rmtree(TMP_DIR_PATH)

    except OSError:
        print("Fail while creating the temporal VM config files")
    else:
        print("Server hostname and interfaces successfullly configured")

get_VM_config_files('s1')
get_VM_config_files('s2')

