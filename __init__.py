#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import pexpect, sys, argparse, re, time
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

from unit import sleep, debug, info, warn, error, str2list, ExpectArgs

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
        self.child = None
        self._debug()
        self._tag()

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

    def _basic_login(self):
        if self.is_user:
            info('[USER]Meet Prompt user,send user to confirm login', self.is_info)
            self._retry_not_expect(self.user, 'sendline', [pexpect.TIMEOUT, '[Pp]assword.*'])
            if self.exec_index == 0:
                is_error = True
                info('''[USER]Send username cannot get passwd, Timeout''', self.is_info)
                info('''[USER]From is_user jump to is_error''', self.is_info)
            elif self.exec_index == 1:                  
                is_passwd = True
                info('''[USER]From is_user jump to is_passwd''', self.is_info)
        
        if self.is_passwd:
            info('[PASSWD]Meet Prompt passwd,send passwd to confirm login', self.is_info)
            self._retry_not_expect(self.passwd, 'sendline', [pexpect.TIMEOUT, '\nlogin.*', '[Pp]assword.*', 'yes\|no>:.*', self.prompt])
            if self.exec_index == 0:
                is_error = True
                info('''[PASSWD]Send passwd cannot get expect, Timeout''', self.is_info)
                info('''[PASSWD]From is_passwd jump to is_error''', self.is_info)
            elif self.exec_index == 1:
                is_error = True
                info('''[PASSWD]Send passwd, meet user again, may wrong user or passwd''', self.is_info)
                info('''[PASSWD]From is_passwd jump to is_error''', self.is_info)
            elif self.exec_index == 2:
                is_error = True
                info('''[PASSWD]Send passwd, meet passwd again, may wrong user or passwd''', self.is_info)
                info('''[PASSWD]From is_passwd jump to is_error''', self.is_info)                         
            elif self.exec_index == 3:
                is_no = True
                info('''[PASSWD]From is_passwd jump to is_no process ''', self.is_info)
            elif self.exec_index == 4:
                is_prompt = True
                info('''[PASSWD]From is_passwd jump to is_prompt process ''', self.is_info)
        
        if self.is_no:
            info('[NO]Meet yes or no successfully,send no to not use default config', self.is_info)
            self._retry_not_expect('no', 'sendline', [pexpect.TIMEOUT, self.prompt])         
            if self.exec_index == 0:
                is_error = True
                info('''[NO]Send no cannot get prompt, Timeout''', self.is_info)
                info('''[NO]From is_no jump to is_error''', self.is_info)
            elif self.exec_index == 1:
                is_prompt = True
                info('''[NO]From is_no jump to is_prompt''', self.is_info)
        
        if self.is_prompt:
            info('''[PROMPT]Meet prompt successfully, can execute cli now''', self.is_info)
        
        if self.is_error:
            info('''[ERROR]BEFORE is: %s''' % self.child.before, self.is_info)
            info('''[ERROR]AFTER is : %s''' % self.child.after, self.is_info)
            raise ValueError, '''Login Error'''

    def _retry_not_expect(self, cli, mode, exp_list, noexp_index=0, retrymode='enter', retry=5, interval=5):
        if self.child:
            info('spawn child exist, send cli directly', self.is_info)
            exec_cli = '''self.child.%s(cli)''' % mode
        else:
            info('spawn child not exist, create spawn firstly', self.is_info)
            exec_cli = '''self.child=pexpect.spawn(cli)'''
        exec(exec_cli)
        self.exec_index = self.child.expect(list(exp_list), interval)
        if self.exec_index == noexp_index:
            info('............Trigger Retry Process............', self.is_info)
            info('CLI         = %s' % cli, self.is_info)
            info('MODE        = %s' % mode, self.is_info)
            info('EXPECT_LIST = %s' % str(exp_list), self.is_info)
            info('RETRY_MODE  = %s' % retrymode, self.is_info)
            info('RETRY       = %s' % retry, self.is_info)
            info('INTERVAL    = %s' % interval, self.is_info)
            for i in range(int(retry)):
                info('Retry %s time start' % (i + 1), self.is_info)
                if retrymode == 'enter':
                    self.child.sendline('')
                elif retrymode == 'repeat':
                    exec(exec_cli)
                self.exec_index = self.child.expect(list(exp_list), interval)
                if self.exec_index != noexp_index:
                    info('............End Retry Process............', self.is_info)
                    return
                info('Retry %s time end' % (i + 1), self.is_info)
        else:
            info('Match expect, no retry', self.is_info)
            return
        raise ValueError, '''Retry %s times and still cannot match expect''' % retry


    def _retry_not_expect_list(self, cli, mode, exp_list, noexp_index_list=[0], retrymode='enter', retry=5, interval=5):
        if self.child:
            info('spawn child exist, send cli directly', self.is_info)
            exec_cli = '''self.child.%s(cli)''' % mode
        else:
            info('spawn child not exist, create spawn firstly', self.is_info)
            exec_cli = '''self.child=pexpect.spawn(cli)'''
        exec(exec_cli)
        self.exec_index = self.child.expect(list(exp_list), interval)
        noexp_index_list=[int(i) for i in noexp_index_list]
        if self.exec_index in noexp_index_list:
            info('............Trigger Retry Process............', self.is_info)
            info('CLI         = %s' % cli, self.is_info)
            info('MODE        = %s' % mode, self.is_info)
            info('EXPECT_LIST = %s' % str(exp_list), self.is_info)
            info('RETRY_MODE  = %s' % retrymode, self.is_info)
            info('RETRY       = %s' % retry, self.is_info)
            info('INTERVAL    = %s' % interval, self.is_info)
            for i in range(int(retry)):
                info('Retry %s time start' % (i + 1), self.is_info)
                if retrymode == 'enter':
                    self.child.sendline('')
                elif retrymode == 'repeat':
                    exec(exec_cli)
                self.exec_index = self.child.expect(list(exp_list), interval)
                if self.exec_index not in noexp_index_list:
                    info('............End Retry Process............', self.is_info)
                    return
                info('Retry %s time end' % (i + 1), self.is_info)
        else:
            info('Match expect, no retry', self.is_info)
            return
        raise ValueError, '''Retry %s times and still cannot match expect''' % retry

     
    def _debug(self):
        self.is_debug = False
        self.is_info = False
        self.is_warn = False
        self.is_error = False
        if self.debug_level == 'debug':
            self.is_debug = True
            self.is_info = True
            self.is_warn = True
            self.is_error = True          
        elif self.debug_level == 'info':
            self.is_info = True
            self.is_warn = True
            self.is_error = True   
        elif self.debug_level == 'warn':
            self.is_warn = True
            self.is_error = True   
        elif self.debug_level == 'error':
            self.is_error = True
            
    def _tag(self):
        self.is_user = False
        self.is_passwd = False
        self.is_prompt = False
        self.is_no = False
        self.is_error = False
