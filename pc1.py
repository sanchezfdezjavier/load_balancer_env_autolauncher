#!/usr/bin/env python

import os
import sys
import subprocess
from subprocess import call
import argparse
from lxml import etree
import sys
import shutil

from os import listdir
from os.path import isfile, join
from time import sleep

# WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!111
# This code does not work if you don't have installed the following dependecies:
#  lxml                 --> sudo apt-get install python3-lxml
#  qemu images support  --> sudo apt-get install qemu

# Constat definitions
FILES_TO_PRESERVE = ["pc1.py","script1.py", "cp1.cfg",".gitignore", "tests.py", "dudas.txt", "README.md", "test2.py"]
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ORDER_MODES = ["create", "start", "stop", "release"]
MIN_SERVERS = 1
MAX_SERVERS = 5
XML_TEMPLATE = "plantilla-vm-p3.xml"
BASE_IMAGE_NAME = "cdps-vm-base-p3.qcow2"
BRIDGE = "virbr0"
IMAGE_SOURCE_PATH = CURRENT_PATH + "/" + BASE_IMAGE_NAME
CLIENT_NAME = "c1"
LOAD_BALANCER_NAME = "lb"

SERVER_IPs = ["10.0.2.11", "10.0.2.12", "10.0.2.13", "10.0.2.14", "10.0.2.15"]
CLIENT_IP = "10.0.1.2"

LAN1_NAME = "LAN1"
BASE_ADRESS_LAN1 = "10.0.1.2"
LAN1 = {
    "network":  "10.0.1.0",
    "netmask":  "255.255.255.0",
    "gateway":  "10.0.1.1",
    "broadcast": "10.0.1.255"
}

LAN2_NAME = "LAN2"
BASE_ADRESS_LAN2 = "10.0.2.11"
LAN2 = {
  "network": "10.0.2.0",
  "netmask": "255.255.255.0",
  "gateway": "10.0.2.1",
  "broadcast": "10.0.2.255"
}

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
        call(["chmod", "+w", sx_image_name])
        # Saves the created servers names in server_names in main thread
        server_names.append("s%i" % i)



     call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", LOAD_BALANCER_NAME + ".qcow2"])
     call(["chmod", "+w", LOAD_BALANCER_NAME + ".qcow2"])
     call(["qemu-img", "create", "-f", "qcow2", "-b", "cdps-vm-base-p3.qcow2", CLIENT_NAME + ".qcow2"])
     call(["chmod", "+w", CLIENT_NAME + ".qcow2"])

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

def setup_xml(vm_name, lan,load_balancer=False):
    BRIDGE = ""
    if (lan == 1):
        BRIDGE = "LAN1"
    elif(lan == 2):
        BRIDGE = "LAN2"

    # Load xml file
    file = etree.parse(vm_name + ".xml")
    # Finds the root tag
    root = file.getroot()

    # Change VM name tag: takes the xml_file name without the extension
    name_tag = root.find("name")
    name_tag.text = vm_name

    # Change brige type of source tag to 'virbr0'
    bridge_source_tag = root.find("./devices/interface/source")
    bridge_source_tag.set("bridge", BRIDGE)

    if(load_balancer):
        devices = root.find("devices")
        inter = etree.Element("interface")
        inter.set("type", 'bridge')
        var = etree.Element("source")
        var.set("bridge", 'LAN2')
        model = etree.Element("model")
        model.set("type", 'virtio')
        inter.append(var)
        inter.append(model)
        devices.append(inter)

    # Change qcow2 image source file with IMAGE_SOURCE_PATH
    image_source_tag = root.find('./devices/disk/source')
    image_source_tag.set("file", CURRENT_PATH + "/" + vm_name + ".qcow2")
    
    # Save the changes
    file_saved = open(vm_name + ".xml", 'w')
    file_saved.write(etree.tostring(root, pretty_print=True))
    file_saved.close()

def virsh_define(xml_file):
    call(["sudo", "virsh", "define", xml_file])

def virsh_start(vm_name):
    call(["sudo", "virsh", "start", vm_name])
    print(vm_name + " started!")

def virsh_undefine_all():
    ps = subprocess.Popen(["sudo", "virsh", "list", "--inactive", "--name"], stdout=subprocess.PIPE)
    output = subprocess.check_output(["xargs", "-r", "-n", "1", "virsh","undefine"], stdin=ps.stdout)
    ps.wait()

def virsh_shutdown(vm_name):
    call(["sudo", "virsh", "shutdown", vm_name])

def virsh_list(inactive=False):
    if inactive:
        call(["sudo", "virsh", "list", "--inactive"])
    else:
        call(["sudo", "virsh", "list"])

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
    shutil.rmtree(TMP_DIR_PATH)

def open_VM_console(vm_name):
    ps = subprocess.Popen(["virt-viewer", vm_name])

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
    
    for file_name in FILES_TO_PRESERVE:
        if(file_name in to_return):
            to_return.remove(file_name)

    # Get all .qcow images file names except the source, IMAGE_NAME
    for file_name in to_return:
        if (file_name.endswith(".qcow2") and (file_name == BASE_IMAGE_NAME)):
            to_return.remove(file_name)

    # Get all .xml config files, except the template, XML_TEMPLATE
    for file_name in to_return:
        if(file_name.endswith(".xml") and (file_name == XML_TEMPLATE)):
            to_return.remove(file_name)

    return to_return

def config_VM_hostname_interfaces(vm_name, vm_type):
    vm_types = ['server', 'client', 'load_balancer']
    current_path = os.getcwd()
    TMP_DIR_NAME = "tmp_config_files"
    TMP_DIR_PATH= current_path + '/' + TMP_DIR_NAME
    LINES_TO_WRITE = []

    if (not (vm_type in vm_types)):
        print("The elegible VM types are: server/client/load_balancer")
        return

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
        if(vm_type == 'server'):
            LINES_TO_WRITE = ["auto lo\n"
                            , "iface lo inet loopback\n"
                            , "auto eth0\n"
                            , "iface eth0 inet static\n"
                            , "    address " + SERVER_IPs.pop(0) + "\n"
                            , "    network " + LAN2['network']  +  "\n"
                            , "    netmask " + LAN2['netmask']  +  "\n"
                            , "    gateway " + LAN2['gateway']  +  "\n"]

        elif(vm_type == 'client'):
            LINES_TO_WRITE = ["auto lo\n"
                            , "iface lo inet loopback\n"
                            , "auto eth0\n"
                            , "iface eth0 inet static\n"
                            , "    address "  + CLIENT_IP + "\n"
                            , "    network "  + LAN1['network']  +  "\n"
                            , "    netmask "  + LAN1['netmask']  +  "\n"
                            , "    gateway "  + LAN1['gateway']  +  "\n"]
        elif(vm_type == 'load_balancer'):
            LINES_TO_WRITE = ["auto lo\n"
                            , "iface lo inet loopback\n"
                            , "auto eth0\n"
                            , "iface eth0 inet static\n"
                            , "    address "  + LAN1['gateway']  + "\n"
                            , "    network "  + LAN1['network']  + "\n"
                            , "    netmask "  + LAN1['netmask']  + "\n"
                            , "    broadcast "+ LAN1['broadcast']+ "\n\n"
                            , "auto eth1\n"
                            , "iface eth1 inet static\n"
                            , "    address "  + LAN2['gateway']  + "\n"
                            , "    netmask "  + LAN2['netmask']  + "\n"]

        interfaces_file.writelines(LINES_TO_WRITE)
        interfaces_file.close()
        # copy interfaces file into the VM /etc/network/inteface path
        call(["sudo", "virt-copy-in", "-a", vm_name + ".qcow2", TMP_DIR_PATH + "/interfaces", "/etc/network"])

        # Print the config files inside the VMs
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

def edit_HTML_server_name(vm_name):
    TMP_DIR_NAME = "tmp_config_html"
    current_path = os.getcwd()
    TMP_DIR_PATH= current_path + '/' + TMP_DIR_NAME
    os.mkdir(TMP_DIR_PATH)

    # /var/www/html/index.html file creation
    indexHTML_file = open(TMP_DIR_PATH + '/index.html', 'w')
    indexHTML_file.write(vm_name)
    indexHTML_file.close()
    # /var/www/html/index.html"
    # TMP_DIR_PATH + "/hostname", "/etc" 
    call(["sudo", "virt-copy-in", "-a", vm_name + ".qcow2", TMP_DIR_PATH + "/index.html", "/var/www/html/"])

    # delete all temporary files
    shutil.rmtree(TMP_DIR_PATH)
    print(vm_name + " index.html successfully configured!")

def get_server_names_from_config_file():
    f = open('cp1.cfg', 'r')
    NUM_SERV = int(f.readline()[-1])
    server_names = [("s" + str(i)) for i in range(1,NUM_SERV +1)]
    return server_names

def config_hosts(vm_name):
    #sudo virt-copy-out -a s1.qcow2 /etc/network/interfaces .
    current_path = os.getcwd()
    TMP_DIR_NAME = "tmp_host"
    TMP_DIR_PATH= current_path + '/' + TMP_DIR_NAME
    os.mkdir(TMP_DIR_PATH)

    # /etc/hostname config file creation
    # hosts file edit
    # hosts file edit
    hosts = open(TMP_DIR_NAME + "/hosts", "w")
    hosts.write("127.0.1.1 {}\n".format(vm_name))
    hosts.write("127.0.0.1 localhost\n")
    hosts.write("::1 ip6-localhost ip6-loopback\n")
    hosts.write("fe00::0 ip6-localnet\n")
    hosts.write("ff00::0 ip6-mcastprefix\n")
    hosts.write("ff02::1 ip6-allnodes\n")
    hosts.write("ff02::2 ip6-allrouters\n")
    hosts.write("ff02::3 ip6-allhosts\n")
    hosts.close()

    # copy hostname file into the VM /etc/hostname path
    call(["sudo", "virt-copy-in", "-a", "{}.qcow2".format(vm_name), "{}/hosts".format(TMP_DIR_PATH), "/etc"])
    shutil.rmtree(TMP_DIR_PATH)


def create():
    # Create qemu servers images s1.qcow, s2.qcow,..., sn.qcow and c1.qcow2 and lb.qcow2
    qemu_create_cow(NSERVERS)
    # Create XML server, c1 client and load balancer templates
    create_xml_templates(XML_TEMPLATE, NSERVERS)

    # XML setup for each server
    for server in server_names:
        setup_xml(server,2)
    # XML setup for the client
    setup_xml(CLIENT_NAME,1)
    # XML setup for load balancer
    setup_xml(LOAD_BALANCER_NAME, 1,load_balancer=True)

    # HTML server setup
    for server in server_names:
        edit_HTML_server_name(server)

    # virsh define for all servers
    for server in server_names:
        virsh_define(server + ".xml")

    # virsh define for client
    virsh_define(CLIENT_NAME + ".xml")
    # virsh define for load balancer
    virsh_define(LOAD_BALANCER_NAME + ".xml")

    # Bridges creation and config for both virtual networks
    bridges_config()

    # Hostname and interfaces config for each VM
    # Servers config
    for server in server_names:
        config_VM_hostname_interfaces(server, 'server')
    # Client config
    config_VM_hostname_interfaces(CLIENT_NAME, 'client')
    # Load balancer config
    config_VM_hostname_interfaces(LOAD_BALANCER_NAME, 'load_balancer')

    # Hosts file config for each VM
    # Servers
    for server in server_names:
        config_hosts(server)
    
    config_hosts(CLIENT_NAME)
    config_hosts(LOAD_BALANCER_NAME)

    # Enable ip forwarding for load balancer
    virsh_lb_forwarding_setup()

    print("Create successfully")
    virsh_list(inactive=True)

    #sudo ifconfig LAN1 10.0.1.3/24
    #sudo ip route add 10.0.0.0/16 via 10.0.1.1
    os.system("sudo ifconfig LAN1 10.0.1.3/24")
    os.system("sudo ip route add 10.0.0.0/16 via 10.0.1.1")

def start():
    SERVER_NAMES = get_server_names_from_config_file()
    print(SERVER_NAMES)

    # Server start
    for server in SERVER_NAMES:
        virsh_start(server)

    # Client start
    virsh_start(CLIENT_NAME)
    # Load balancer start
    virsh_start(LOAD_BALANCER_NAME)

    # open server consoles
    for server in SERVER_NAMES:
        open_VM_console(server)
    # open load balancer console
    open_VM_console(LOAD_BALANCER_NAME)
    # open client console
    open_VM_console(CLIENT_NAME)    

    virsh_list()

def stop():
    SERVER_NAMES = get_server_names_from_config_file()

    # Stop servers
    for server in SERVER_NAMES:
        virsh_shutdown(server)
        sleep(1)
    
    # Stop client
    virsh_shutdown(CLIENT_NAME)
    sleep(1)


    # Stop load balancer
    virsh_shutdown(LOAD_BALANCER_NAME)
    sleep(1)
    print("Stop finished")

    virsh_list(inactive=True)

def release():
    # Stops the environment before deleting the files
    stop()

    #undefine the domains
    virsh_undefine_all()
    
    # Deletes the environment files creted by the option create
    files_to_delete = get_files_to_delete(CURRENT_PATH)
    for file_name in files_to_delete:
        call(["sudo", "rm", file_name])
    print("Files successfully deleted")

    virsh_list()
    virsh_list(True)

if __name__ == '__main__':
    ARGS = parse_Arguments().__dict__
    ORDER = check_order_input_value(ARGS['order'])
    NSERVERS = check_servers_input_value(ARGS['serversNumber'])
    server_names = []

    if NSERVERS < 1 or NSERVERS > 5:
        raise Exception("Please specify a number of servers between 1-5")

    # Minor bug, it is possible to specify server number if the value is 2
    #optional_without_create()

    # Save data in config file
    if ORDER == 'create':
        config_file = open("cp1.cfg", 'w')
        config_file.write("num_serv=" + str(NSERVERS))
        config_file.close()

    # Reading the config file
    config = open("cp1.cfg", "r")
    NSERVERS = int(config.readlines()[0][-1] )

    # Call the suitable function depending on user ORDER input {create/start/stop/release}
    command_function = ORDER
    getattr(sys.modules[__name__], "%s" % command_function)()

    print("End")