#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will
import sys
from AerohiveExpect import ExpectConnect

def telnet_exec():
    telnet = ExpectConnect()
    telnet.telnet_login()
    telnet._basic_exec()
    telnet._basic_logout()

if __name__ == '__main__':
    try:
        telnet_exec()
    except Exception, e:
        print str(e)
        sys.exit(1)
    else:
        sys.exit(0)