#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will
import sys
from AerohiveExpect import ExpectConnect

def ssh_exec():
    ssh = ExpectConnect()
    ssh.ssh_login()
    ssh._basic_exec()
    ssh._basic_logout()

if __name__ == '__main__':
    try:
        ssh_exec()
    except Exception, e:
        print str(e)
        sys.exit(1)
    else:
        sys.exit(0)