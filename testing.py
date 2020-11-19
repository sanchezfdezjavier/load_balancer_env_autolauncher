import os
import sys
from subprocess import call
import argparse
from lxml import etree


def qemu_create_cow(nservers):
     for i in range(1, nservers + 1):
     	call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", "s{}.qcow2".format(i)])
     
     call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", "lb.qcow2"])
     call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", "c1.qcow2"])
     print("cow images successfully created2")

qemu_create_cow(3)
