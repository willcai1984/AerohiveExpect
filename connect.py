﻿  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will
import sys
from AerohiveExpect import ExpectConnect

def connect_exec():
    connect = ExpectConnect()
    if connect.mode == 'ssh':
        connect.ssh_login()
    elif connect.mode == 'telnet':
        connect.telnet_login()
    connect.basic_exec()
    connect.basic_logout()

if __name__ == '__main__':
    connect_exec()
#    try:
#        connect_exec()
#    except Exception, e:
#        print str(e)
#        sys.exit(1)
#    else:
#        sys.exit(0)
