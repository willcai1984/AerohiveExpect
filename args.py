  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import argparse
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")


class ExpectArgs(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Login target and execute cmds')
        
        self.parser.add_argument('-i', '--ip', required=True, default=None, dest='ip',
                            help='Target IP')

        self.parser.add_argument('-u', '--user', required=False, default='root', dest='user',
                            help='Login Name')
        
        self.parser.add_argument('-p', '--passwd', required=False, default='aerohive', dest='passwd',
                            help='Login Password')

        self.parser.add_argument('--prompt', required=False, default='AH.*#|~ #', dest='prompt',
                            help='The login prompt you want to meet')
        
        self.parser.add_argument('-t', '--timeout', required=False, default=10, type=int, dest='timeout',
                            help='Time out value for every execute cli step')
        
        self.parser.add_argument('-l', '--logfile', required=False, default='stdout', dest='log_file',
                            help='The log file path')
        
        self.parser.add_argument('-c', '--command', required=False, action='append', default=[], dest='cli_list',
                            help='The command you want to execute')

        self.parser.add_argument('-f', '--file', required=False, default=False, dest='config_file',
                            help='The path of configurefile')

        self.parser.add_argument('-w', '--wait', required=False, default=0, type=int, dest='wait',
                            help='wait time between the current cli and next cli')

        self.parser.add_argument('-r', '--retry', required=False, default=5, type=int, dest='retry',
                            help='How many times you want to retry when the login step is failed')


        self.parser.add_argument('--debug', required=False, default='error', choices=['debug', 'info', 'warn', 'error'], dest='debug_level',
                            help='Debug mode, info>warn>error')

        self._parse_args()
        
    def _parse_args(self):
        self.args = self.parser.parse_args()
        self.ip = self.args.ip
        self.user = self.args.user
        self.passwd = self.args.passwd
        self.prompt = self.args.prompt
        self.timeout = self.args.timeout
        self.log_file = self.args.log_file
        self.cli_list = self.args.cli_list
        self.config_file = self.args.config_file
        self.wait = self.args.wait
        self.retry = self.args.retry
        self.debug_level = self.args.debug_level
