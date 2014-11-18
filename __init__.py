#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import pexpect, sys, argparse, re, time
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

class console_host:
    def __init__(self, ip, serialname, user, passwd, absolute_logfile='', prompt='[$#>]', wait_time=0, is_debug=False):
        self.ip = ip
        self.serialname = serialname
        self.user = user
        self.passwd = passwd
        self.is_debug = is_debug
        self.prompt = prompt
        self.absolute_logfile = absolute_logfile
        self.wait_time = wait_time
        if absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open = open(absolute_logfile, mode='w')
        print 'console %s process start, init parameters............' % serialname
    def __del__(self):
        if self.absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open.close()
            absolute_logfile = self.absolute_logfile
            
            with open(absolute_logfile, mode='r') as absolute_logfile_open:
                originate_logfile = absolute_logfile_open.read()
            correct_logfile = re.sub(' --More-- \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08          \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08', '', originate_logfile)
            correct_logfile = re.sub(' {28}|\r', '', correct_logfile)
            with open(absolute_logfile, mode='w') as absolute_logfile_open:
                absolute_logfile_open.write(correct_logfile)            
        print 'console %s process over.' % self.ip
        
    def login(self, login_timeout=2, login_retry_times=5):
        ip = self.ip
        serialname = self.serialname
        user = self.user
        passwd = self.passwd
        is_debug = self.is_debug
        prompt = self.prompt
        log_file_path = self.absolute_logfile
        if log_file_path == './stdout':
            log_file_open = []
        else:
            log_file_open = self.absolute_logfile_open
        console_login_result = console_login(ip, user, passwd, serialname, prompt, login_timeout, login_retry_times, log_file_path, log_file_open, is_debug)            
        return console_login_result

    def execute_command_via_cli_sendmode_expect_timeout_wait_list(self, spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times=2):
        is_debug = self.is_debug
        wait_time = self.wait_time
        console_cli_result = execute_command_via_cli_sendmode_expect_timeout_wait_list(spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times, is_debug)
        return console_cli_result

    def logout(self, spawn_child, logout_timeout=10, logout_retry_times=5):
        is_debug = self.is_debug
        console_logout_result = console_logout(spawn_child, logout_timeout, logout_retry_times, is_debug)
        return console_logout_result
