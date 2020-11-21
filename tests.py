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

from os import listdir
from os.path import isfile, join
import time

VM_USERNAME = "cdps"
VM_PASSWORD = "cdps"


def start_and_login(vm):
    call(["sudo", "virsh", "start", vm])
    # call(["sudo", "virsh", "console", vm])

    login_process = subprocess.Popen(["sudo", "virsh", "console" ,"s1"])
    print("Happens while running")
    login_process.communicate(input="\n" + VM_USERNAME + "\n" +  VM_PASSWORD + "\n")
    call(["\n"])
    time.sleep(7)
    call(["cdps"])
    #call([VM_USERNAME])
    #call([VM_PASSWORD])
    # call(["sudo", "halt", "-p"])

print(start_and_login("s1"))


# p = subprocess.Popen([data["om_points"], ">", diz['d']+"/points.xml"])
# print "Happens while running"
# p.communicate() #now wait plus that you can send commands to process