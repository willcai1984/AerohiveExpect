#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import pexpect, sys, argparse, re, time
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

parse = argparse.ArgumentParser(description='Login target host and execute CLI')
parse.add_argument('-d', '--destination', required=False, default='localhost', dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-e', '--serialname', required=True, default=None, dest='serialname',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='user',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='passwd',
                    help='Login Password')

parse.add_argument('-m', '--prompt', required=False, default='AH-\w+#.*', dest='prompt',
                    help='The login prompt you want to meet')

parse.add_argument('-o', '--timeout', required=False, default=5, type=int, dest='timeout',
                    help='Time out value for every execute cli step')

parse.add_argument('-l', '--logdir', required=False, default='.', dest='logdir',
                    help='The log file dir')

parse.add_argument('-z', '--logfile', required=False, default='stdout', dest='logfile',
                    help='The log file name')

parse.add_argument('-v', '--command', required=False, action='append', default=[], dest='cli_list',
                    help='The command you want to execute')

parse.add_argument('-sp', '--shellpasswd', required=False, default='', dest='shellpasswd',
                    help='Shell password for enter to shell mode')

parse.add_argument('-debug', '--debug', required=False, default=False, action='store_true', dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-b', '--shell', required=False, default=False, action='store_true', dest='is_shell',
                    help='enable shell mode')

parse.add_argument('-i', '--interface', required=False, default='', dest='serial',
                    help='Serial number')

parse.add_argument('-n', '--nowait', required=False, default=False, action='store_true', dest='is_wait',
                    help='enable wait mode')

parse.add_argument('-f', '--file', required=False, default='', dest='configfilepath',
                    help='The path of configurefile')
# ##v13 modify to 90 and timeout modify to 2
parse.add_argument('-k', '--retry', required=False, default=90, type=int, dest='retry_times',
                    help='How many times you want to retry when the login step is timeout')

parse.add_argument('-w', '--wait', required=False, default=0, type=float , dest='wait_time',
                    help='wait time between the current cli and next cli')

parse.add_argument('-bp', '--bootpassword', required=False, default='', dest='bootpasswd',
                    help='boot password')

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

def main():
    args = parse.parse_args() 
    is_debug = args.is_debug
    ip = args.desip
    user = args.user
    passwd = args.passwd
    prompt = args.prompt
    prompt = re.sub('\$', '\\$', prompt)
    prompt_para_list = prompt.split('|')
    debug('prompt_para_list is as below', is_debug)
    debug(prompt_para_list, is_debug)
    prompt_len = len(prompt_para_list)
    prompt = ''
    for prompt_num in range(prompt_len):
        if prompt_num == prompt_len - 1:
            prompt = prompt + '%s.*' % prompt_para_list[prompt_num]
        else:
            prompt = prompt + '%s.*|' % prompt_para_list[prompt_num]
    debug('Real prompt is as below', is_debug)
    debug(prompt, is_debug)    
    timeout = args.timeout
    logdir = args.logdir
    ###v17
    logfile = args.logfile.strip()
    cli_list = args.cli_list
    shellpasswd = args.shellpasswd
    is_shell = args.is_shell
    serialname = args.serialname
    config_file_path = args.configfilepath
    retry_times = args.retry_times
    wait_time = args.wait_time
    bootpasswd = args.bootpasswd
    loop = str2list(args.loop)
    input_para_list = sys.argv
    debug('''Type command is "python %s"''' % (' '.join(input_para_list)), is_debug)
    execute_cli_list = []
    reg = re.compile('%')
    for i in loop:
        for cli in cli_list:
            #Check how many % in the cli
            reg_result = reg.findall(cli)
            if len(reg_result) == 0:
                execute_cli_list.append(cli)
            else: 
                i_num = len(reg_result)
                i_tuple = tuple([i] * i_num) 
                execute_cli_list.append(cli % i_tuple)
    execute_cli_list = generate_cli_list(execute_cli_list, config_file_path, input_para_list, is_debug)
    try:
        console_result = console_execute_cli(ip, user, passwd, serialname, execute_cli_list, prompt, timeout, retry_times, logdir, logfile, is_debug, is_shell, shellpasswd, wait_time, bootpasswd)
    except Exception, e:
        print str(e)
    else:
        return console_result
            
if __name__ == '__main__':
    console_result = main()
    if console_result:
        console_result.close(force=True)
        print 'Console successfully, exit 0'
        sys.exit(0)
    else:
        print 'Console failed, exit 1'
        sys.exit(1)
