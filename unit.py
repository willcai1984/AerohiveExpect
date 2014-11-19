#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import re, time, argparse, pexpect
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

'''
Sleep
'''
def sleep(mytime=1):
    time.sleep(mytime)

'''
Print log based on debug level
'''
def debug(msg, is_debug):
    if msg and is_debug:
            print '%s DEBUG' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg
            
def info(msg, is_info):
    if msg and is_info:
            print '%s INFO ' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg
            
def warn(msg, is_warn):
    if msg and is_warn:
            print '%s WARN ' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg
            
def error(msg, is_error):
    if msg and is_error:
            print '%s ERROR' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg

'''
Transfer str to list
for example: input is '1,3,5-8,10', output is [1,3,5,6,7,8,10]
'''
def str2list(string):
    p_list = string.split(',')
    int_reg = re.compile('^\d+')
    ran_reg = re.compile('^\d+-\d+$')
    #remove not int para and blank
    i_list = [i.replace(' ', '') for i in p_list if int_reg.search(i)]
    str_list = []
    for i in i_list:
        if ran_reg.search(i):
            ran_start = int(i.split('-')[0])
            ran_end = int(i.split('-')[-1])
            for j in range(ran_start, ran_end + 1):
                str_list.append(str(j))
        else:
            str_list.append(str(i))
    return str_list





class ExpectArgs(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Login target and execute cmds')

        self.parse.add_argument('-m', '--mode', required=False, default='ssh' , choices=['ssh', 'telnet'], dest='mode',
                            help='Login mode')
        
        self.parse.add_argument('-i', '--ip', required=True, default=None, dest='ip',
                            help='Target IP')

        self.parse.add_argument('--port', required=False, default=22, type=int, dest='port',
                            help='Taget port')

        self.parse.add_argument('-u', '--user', required=False, default='admin', dest='user',
                            help='Login Name')
        
        self.parse.add_argument('-p', '--passwd', required=False, default='aerohive', dest='passwd',
                            help='Login Password')

        self.parse.add_argument('--prompt', required=False, default='AH.*#', dest='prompt',
                            help='The login prompt you want to meet')
        
        self.parse.add_argument('-t', '--timeout', required=False, default=10, type=int, dest='timeout',
                            help='Time out value for every execute cli step')
        
        self.parse.add_argument('-l', '--logfile', required=False, default='.', dest='log_file',
                            help='The log file path')
        
        self.parse.add_argument('-c', '--command', required=False, action='append', default=[], dest='cli_list',
                            help='The command you want to execute')

        self.parse.add_argument('-f', '--file', required=False, default=False, dest='config_file',
                            help='The path of configurefile')

        self.parse.add_argument('-w', '--wait', required=False, default=0, type=int, dest='wait',
                            help='wait time between the current cli and next cli')

        self.parse.add_argument('-r', '--retry', required=False, default=5, type=int, dest='retry',
                            help='How many times you want to retry when the login step is failed')

        self.parse.add_argument('-sp', '--shellpasswd', required=False, default='', dest='sp',
                            help='Shell password for enter to shell mode')

        self.parse.add_argument('--debug', required=False, default='error', choices=['debug', 'info', 'warn', 'error'], dest='debug_level',
                            help='Debug mode, info>warn>error')

        self._parse_args()
        
    def _parse_args(self):
        self.args = self.parser.parse_args()
        self.mode = self.args.mode
        self.ip = self.args.ip
        self.port = self.args.port
        self.user = self.args.user
        self.passwd = self.args.passwd
        self.prompt = self.args.prompt
        self.timeout = self.args.timeout
        self.log_file = self.args.log_file
        self.cli_list = self.args.cli_list
        self.config_file = self.args.config_file
        self.wait = self.args.wait
        self.retry = self.args.retry
        self.sp = self.args.sp
        self.debug_level = self.args.debug_level