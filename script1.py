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

# WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!111
# This code does not work if you don't have installed the following dependecies:
#  lxml                 --> sudo apt-get install python3-lxml
#  qemu images support  --> sudo apt-get install qemu

#Constat definitions
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ORDER_MODES = ["create", "start", "stop", "release"]
MIN_SERVERS = 1
MAX_SERVERS = 5
XML_TEMPLATE = "plantilla-vm-p3.xml"
IMAGE_NAME = "cdps-vm-base-p3.qcow2"
BRIDGE = "virbr0"
IMAGE_SOURCE_PATH = "/home/javier/Desktop/load_balancer_env_autolauncher/" + IMAGE_NAME
CLIENT_NAME = "c1"
LOAD_BALANCER_NAME = "lb"
LAN1_NAME = "LAN1"
LAN2_NAME = "LAN2"

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
        # Saves the created servers names in server_names in main thread
        server_names.append("s%i" % i)

     call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", "lb.qcow2"])
     call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", "c1.qcow2"])

     print("cow images successfully created")

def create_xml_templates(xml_template, nservers=1):
    # Creates servers xml templates from s1 to sn
    for i in range(1, nservers+1):
        sx_xml_template_name = "s%i.xml" % i
        call(["cp", xml_template, sx_xml_template_name])
    # Create XML C1 client template
    call(["cp", XML_TEMPLATE, CLIENT_NAME + ".xml"])
    # Create XML lb load balancer template
    call(["cp", XML_TEMPLATE, LOAD_BALANCER_NAME + ".xml"])

def setup_xml(xml_file):
    # Load xml file
    file = etree.parse(xml_file)
    # Finds the root tag
    root = file.getroot()

    # Change VM name tag: takes the xml_file name without the extension
    name_tag = root.find("name")
    name_tag.text = xml_file.split('.')[0]

    # Change brige type of source tag to 'virbr0'
    bridge_source_tag = root.find("./devices/interface/source")
    bridge_source_tag.set("bridge", BRIDGE)

    # Change qcow2 image source file with IMAGE_SOURCE_PATH
    image_source_tag = root.find('./devices/disk/source')
    image_source_tag.set("file", IMAGE_SOURCE_PATH)
    
    # Save the changes
    file_saved = open(xml_file, 'w')
    file_saved.write(etree.tostring(root, pretty_print=True))
    file_saved.close()

def virsh_define(xml_file):
    call(["sudo", "virsh", "define", xml_file])

def virsh_start(vm_name):
    call(["sudo", "virsh", "start", vm_name])

def virsh_undefine(vm_name):
    call(["sudo", "virsh", "undefine", vm_name])

# Opens the 
def virsh_console(vm):
    command = "xterm -rv -sb -rightbar -fa monospace -fs 10 -title 's1' -e 'sudo virsh console s1'"
    command_list = command.split(" ")
    command_list[-1] = vm + "'"
    call(command_list)

def brctl_addbr(lan_name):
    # sudo brctl addbr <lan name>
    call(["sudo", "brctl", "addbr", lan_name])
    
def lan_up(lan_name):
    # sudo ifconfig <lan name> up
    call(["sudo", "ifconfig", lan_name, "up"])

def bridges_config():
    # sudo brctl addbr LAN1_NAME
    brctl_addbr(LAN1_NAME)
    # sudo ifconfig LAN1_NAME up
    lan_up(LAN1_NAME)

    # sudo brctl addbr LAN2_NAME
    brctl_addbr(LAN2_NAME)
    # sudo ifconfig addbr LAN2_NAME
    lan_up(LAN2_NAME)

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

def create():
    # Create qemu servers images s1.qcow, s2.qcow,..., sn.qcow and c1.qcow2 and lb.qcow2
    qemu_create_cow(NSERVERS)
    # Create XML server, c1 client and load balancer templates
    create_xml_templates(XML_TEMPLATE, NSERVERS)

    # XML setup for each server
    for s in server_names:
        setup_xml("%s.xml" % s)
    # XML setup for the client
    setup_xml(CLIENT_NAME + ".xml")
    # XML setup for load balancer
    setup_xml(LOAD_BALANCER_NAME + ".xml")

    # virsh define for all servers
    for server in server_names:
        virsh_define(server + ".xml")

    # virsh define for client
    virsh_define(CLIENT_NAME + ".xml")
    # virsh define for load balancer
    virsh_define(LOAD_BALANCER_NAME + ".xml")

    # Bridges creation and config for both viratual networks
    bridges_config()

    print("Create successfully")

def start():
    pass

def stop():
    pass

def release():
    # Stops the environment before deleting the files
    stop()
    
    # Deletes the environment files creted by the option create
    files_to_delete = get_files_to_delete(CURRENT_PATH)
    for file_name in files_to_delete:
        call(["rm", file_name])
    
    print("Files successfully deleted")



if __name__ == '__main__':
    ARGS = parse_Arguments().__dict__
    ORDER = check_order_input_value(ARGS['order'])
    NSERVERS = check_servers_input_value(ARGS['serversNumber'])
    server_names = []

    # Minor bug, it is possible to specify server number if the value is 2
    #optional_without_create()

    # Save data in config file
    config_file = open("cp1.cfg", 'w')
    config_file.write("num_serv=" + str(NSERVERS))
    config_file.close()

    # Reading the config file
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

    print(server_names)

    print("End")