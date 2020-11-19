#!/usr/bin/env python

import os
import sys
from subprocess import call
import argparse
from lxml import etree
import logging

#Constat definitions
ORDER_MODES = ["create", "start", "stop", "release"]
MIN_SERVERS = 1
MAX_SERVERS = 5

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

    # Create qemu servers images s1.qcow, s2.qcow,..., sn.qcow
    qemu_create_cow(NSERVERS)

    print("End")