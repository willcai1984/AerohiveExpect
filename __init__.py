#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import pexpect, sys, argparse, re, time
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

from unit import sleep, debug, info, warn, error, str2list

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


class ExpectConnect(object):
    def __init__(self):
        self.args = ExpectArgs()
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
        self.spawn=None
        self.is_user=False
        self.is_passwd=False
        self.is_prompt=False
        self.is_no=False
        self.is_error=False
        
        
        self._debug()

    def __str__(self):
        s = []
        s.append('Mode         = %s' % self.mode)
        s.append('IP           = %s' % self.browser_type)
        s.append('Port         = %s' % self.log_level)
        s.append('User         = %s' % self.log_file)
        s.append('Passwd       = %s' % self.log_pic_dir)
        s.append('Prompt       = %s' % str(self.para_dict))
        s.append('Timeout      = %s' % self.preserve_session)
        s.append('Log_file     = %s' % self.session_id)
        for i in self.cli_list:
            s.append('CLI          = %s' % i)
        s.append('Config_file  = %s' % self.config_file)
        s.append('Wait         = %s' % self.wait)
        s.append('Retry        = %s' % self.retry)
        s.append('Shell_passwd = %s' % self.sp)
        s.append('Debug_level  = %s' % self.debug_level)
        return '\n'.join(s)

    def gen_login(self):
        if self.is_user:
            info('Meet login successfully, send user to confirm login', self.is_info)
            info('............Step1 send user to confirm login............', self.is_info)            
            cli_mode_tuple_list = [(user, 'sendline')]
            expect_list = [pexpect.TIMEOUT, '[Pp]assword.*']
            timeout = login_timeout
            # ##only need expect func, sendnone
            retry_cli_mode_tuple_list = [[('', 'sendnone')]] * login_retry_times
            general_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, general_login_result, self.is_info)
            general_login_result = general_login_info[0]
            general_login_index = general_login_info[1]
            if general_login_index == 0:
                print 'Send user to confirm login timeout, please confirm the host is alive'
                is_error = True
                info('''From is_user jump to is_error''', self.is_info)
            elif general_login_index == 1:                  
                is_passwd = True
                info('''From is_user jump to is_passwd process ''', self.is_info)
        if is_passwd:
            info('Meet password successfully, send passwd to confirm login', self.is_info)
            info('............Step2 send password to confirm login............', self.is_info)
            cli_mode_tuple_list = [(passwd, 'sendline')]
            expect_list = [pexpect.TIMEOUT, '\nlogin.*', '[Pp]assword.*', 'yes\|no>:.*', prompt]
            timeout = login_timeout
            # ##only need expect func, sendnone
            retry_cli_mode_tuple_list = [[('', 'sendnone')]] * login_retry_times
            general_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, general_login_result, self.is_info)
            general_login_result = general_login_info[0]
            general_login_index = general_login_info[1]
            if general_login_index == 0:
                print 'Send password to confirm login timeout, please confirm the host is alive'
                is_error = True
                info('''From is_passwd jump to is_error''', self.is_info)
            elif general_login_index == 1:
                print 'Meet login again, user or password maybe incorrect, please check'
                is_error = True
                info('''From is_passwd jump to is_error''', self.is_info)
            elif general_login_index == 2:
                print 'Meet password again, password maybe incorrect, please check'
                is_error = True
                info('''From is_passwd jump to is_error''', self.is_info)                         
            elif general_login_index == 3:
                is_no = True
                info('''From is_passwd jump to is_no process ''', self.is_info)
            elif general_login_index == 4:
                is_prompt = True
                info('''From is_passwd jump to is_prompt process ''', self.is_info)
        if is_no:
            info('Meet is_default yes or no successfully, send no to not use default config', self.is_info)
            info('............Step3 send no to not use default config............', self.is_info)
            cli_mode_tuple_list = [('no', 'sendline')]
            expect_list = [pexpect.TIMEOUT, prompt]
            timeout = login_timeout
            # ##only need expect func, sendnone
            retry_cli_mode_tuple_list = [[('', 'sendnone')]] * login_retry_times
            general_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, general_login_result, self.is_info)
            general_login_result = general_login_info[0]
            general_login_index = general_login_info[1]            
            if general_login_index == 0:
                print 'Send no to confirm login timeout, please confirm the host is alive'
                is_error = True
                info('''From is_no jump to is_error''', self.is_info)
            elif general_login_index == 1:
                is_prompt = True
                info('''From is_no jump to is_prompt''', self.is_info)
        if is_prompt:
            info('Meet prompt successfully, can execute cli now', self.is_info)
        if is_error:
            ###v22 del telnet_login_result
            print 'before is %s, after is %s' % (general_login_result.before, general_login_result.after)
            general_login_result.close(force=True)
            return None        
        return general_login_result

    def _debug(self):
        self.is_debug=False
        self.is_info=False
        self.is_warn=False
        self.is_error=False
        if self.debug_level=='debug':
            self.is_debug=True
            self.is_info=True
            self.is_warn=True
            self.is_error=True          
        elif self.debug_level=='info':
            self.is_info=True
            self.is_warn=True
            self.is_error=True   
        elif self.debug_level=='warn':
            self.is_warn=True
            self.is_error=True   
        elif self.debug_level=='error':
            self.is_error=True