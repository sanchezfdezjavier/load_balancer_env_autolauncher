#!/usr/bin/env python
from subprocess import call

def virsh_console(vm):
    command = "xterm -rv -sb -rightbar -fa monospace -fs 10 -title 's1' -e 'sudo virsh console s1'"
    command_list = command.split(" ")
    print(command_list)
    command_list[-1] = vm + "'"
    print(command_list)
    call(command_list)

virsh_console('c1')