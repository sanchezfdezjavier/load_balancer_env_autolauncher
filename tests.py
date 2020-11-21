#!/usr/bin/env python
import os
import sys
from subprocess import call
import argparse
from lxml import etree
import logging
import sys

from os import listdir
from os.path import isfile, join

current_path = os.path.dirname(os.path.abspath(__file__))
XML_TEMPLATE = "plantilla-vm-p3.xml"
IMAGE_NAME = "cdps-vm-base-p3.qcow2"


def get_files_to_delete(my_path):
    # Get a list containing all file names in the directory
    to_return = [f for f in listdir(my_path) if isfile(join(my_path, f))]
    
    files_to_preserve = ["script1.py", ".gitignore", "tests.py", "cp1.cfg", "dudas.txt", "README.md"]
    for file_name in files_to_preserve:
        to_return.remove(file_name)

    # Get all .qcow images file names except the source, IMAGE_NAME
    for file_name in to_return:
        if (file_name.endswith(".qcow2") and (file_name == IMAGE_NAME)):
            to_return.remove(file_name)

    # Get all .xml config files, except the template, XML_TEMPLATE
    for file_name in to_return:
        if(file_name.endswith(".xml") and (file_name == XML_TEMPLATE)):
            to_return.remove(file_name)

    return to_return

print(get_files_to_delete(current_path))