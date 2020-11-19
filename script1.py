#!/usr/bin/env python

import os
import sys
from subprocess import call
import argparse
from lxml import etree
import logging
import sys

# WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!111
# This code does not work if you don't have installed the following dependecies:
#  lxml                 --> sudo apt-get install python3-lxml
#  qemu images support  --> sudo apt-get install qemu

#Constat definitions
ORDER_MODES = ["create", "start", "stop", "release"]
MIN_SERVERS = 1
MAX_SERVERS = 5
XML_TEMPLATE = "plantilla-vm-p3.xml"

def parse_Arguments():
    parser = argparse.ArgumentParser()

    # Positional mandatory argument
    parser.add_argument("order", help="possible values create/start/stop/release", type=str)
    # Optional arguments
    parser.add_argument("-sn", "--serversNumber", help="Help placeholder", type=int, default=2)
    # Parse arguments
    return parser.parse_args()

def check_order_input_value(order):
    if order in ORDER_MODES:
        return order
    else:
        print("Wrong order. The available order modes are: create, start, stop, release")

def check_servers_input_value(servers_number):
    if(MIN_SERVERS <= servers_number <= MAX_SERVERS):
        return servers_number
    else:
        print("Unsupported servers number, must be in 1 - 5 range")
    
def optional_without_create():
    if ((ARGS['order'] != "create") and (ARGS['serversNumber'] == 2)):
        print("Wrong input. Server number on create option not expected")
        quit()

def qemu_create_cow(nservers):
     for i in range(1, nservers + 1):
        sx_image_name = "s%i.qcow2" % i
     	call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", sx_image_name])

     call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", "lb.qcow2"])
     call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", "c1.qcow2"])

     print("cow images successfully created")

def create_xml_template(xml_template, nservers=1):
    for i in range(1, nservers+1):
        sx_xml_template_name = "s%i.xml" % i
        call(["cp", xml_template, sx_xml_template_name])

def setup_xml(xml_file):
    # Load xml file
    file = etree.parse(xml_file)
    # Finds the root tag
    root = file.getroot()

    # Change VM name tag: takes the xml_file name without the extension
    name_tag = root.find("name")
    name_tag.text = xml_file.split('.')[0]

    # Change brige type of source tag to 'virbr0'
    source_tag = root.find("./devices/interface/source")
    source_tag.set("bridge", "virbr0")
    
    # Save the changes
    file_saved = open(xml_file, 'w')
    file_saved.write(etree.tostring(root, pretty_print=True))
    file_saved.close()


def create():
    # Create qemu servers images s1.qcow, s2.qcow,..., sn.qcow
    qemu_create_cow(NSERVERS)
    # Create XML server templates
    create_xml_template(XML_TEMPLATE, NSERVERS)
    # Create XML C1 client template
    create_xml_template(XML_TEMPLATE)

def start():
    pass

def stop():
    pass

def release():
    pass



if __name__ == '__main__':
    ARGS = parse_Arguments().__dict__
    ORDER = check_order_input_value(ARGS['order'])
    NSERVERS = check_servers_input_value(ARGS['serversNumber'])

    # Minor bug, it is possible to specify server number if the value is 2
    #optional_without_create()

    # Save data in config file
    config_file = open("cp1.cfg", 'w')
    config_file.write("num_serv=" + str(NSERVERS))
    config_file.close()


    config = open("cp1.cfg", "r")
    NSERVERS = int(config.readlines()[0][-1] )


    # loggin config
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.debug("DEBUG MODE")
    # Debug trace
    logger.debug(ORDER)
    logger.debug(NSERVERS)

    # Call the suitable function depending on user ORDER input {create/start/stop/release}
    command_function = ORDER
    getattr(sys.modules[__name__], "%s" % command_function)()

    print("End")