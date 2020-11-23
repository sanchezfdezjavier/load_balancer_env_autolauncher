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

#print("The current directory is:\n" + current_path)

def get_VM_config_files(vm_name):
    current_path = os.getcwd()
    TMP_DIR_NAME = "tmp_config_files"
    TMP_DIR_PATH= current_path + '/' + TMP_DIR_NAME

    try:
        print(TMP_DIR_PATH + '/' + 'hostname')
        os.mkdir(TMP_DIR_PATH)
        config_file = open(TMP_DIR_PATH + '/' + 'hostname', 'w')
        config_file.write(vm_name)
        config_file.close()
    except OSError:
        print("Fail while creating the temporal VM config files")
    else:
        print("Files successfully created")


get_VM_config_files('s1')