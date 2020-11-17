#!/usr/bin/env python

import os
import sys
from subprocess import call
# import lxml
import argparse

#Constat definitions
ORDER_MODES = ["create", "start", "stop", "release"]
MIN_SERVERS = 1
MAX_SERVERS = 5

def parse_Arguments():
    parser = argparse.ArgumentParser()

    # Positional mandatory argument
    parser.add_argument("order", help="possible values create/start/stop/release", type=int)
    # Optional arguments
    parser.add_argument("-sn", "--serversNumber", help="Help placeholder", type=int, default=2)
    # Parse arguments
    return parser.parse_args()

def check_servers_input_value(servers_number):
    if(MIN_SERVERS <= servers_number <= MAX_SERVERS):
        return servers_number
    else:
        print("Unsupported servers number, must be in 1 - 5 range")
    


if __name__ == '__main__':
    ARGS = parse_Arguments().__dict__
    ORDER = ARGS['order']
    NSERVERS = check_servers_input_value(ARGS['serversNumber'])

    print(ORDER, NSERVERS)



