#!/usr/bin/python
# Filename: telnet.py
# Function: telnet target execute cli
# coding:utf-8
# Author: Well
# Example command:telnet.py -d ip -u user -p password -m prompt -o timeout -l logdir -z logfile -v "show run" -v "show version"
import pexpect, sys, argparse, re, os, time
from console import generate_cli_sendmode_expect_timeout_wait_list, debug, sleep, spawn_timeout_retry, generate_cli_list, execute_command_via_cli_sendmode_expect_timeout_wait_list, general_login

def telnet_login_via_ip(ip, user, passwd, prompt, login_timeout=2, login_retry_times=20, log_file_path=[], log_file_open=[], is_debug=True):
    ###transfer all para to correct format
    login_retry_times = int(login_retry_times)
    login_timeout = int(login_timeout)
    ###define private para
    is_user = False
    is_passwd = False
    is_no = False
    is_prompt = False
    is_error = False
    ###use timeout retry func to login
    ######define timeoute retry func's para
    telnet_login_command = 'telnet %s' % ip
    debug('''Telnet IP prcoess start, command is "%s"''' % telnet_login_command, is_debug)  
    cli_mode_tuple_list = [(telnet_login_command, 'sendline')]
    expect_list = [pexpect.TIMEOUT, 'Connection timed out', 'No route to host.*', 'Connected.*Escape character.*User Name:.*', 'Connected.*[Pp]assword:.*', 'Welcome to Aerohive Product.*login:.*']
    timeout = login_timeout
    ###The last one send enter to confirm
    retry_cli_mode_tuple_list = [[('', 'sendnone')]] * (login_retry_times - 1) + [['', 'sendline']]
    telnet_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, '', is_debug)
    telnet_login_result = telnet_login_info[0]
    telnet_login_index = telnet_login_info[1]
    if log_file_path == './stdout':
        telnet_login_result.logfile_read = sys.stdout
    else:
        telnet_login_result.logfile_read = log_file_open
    if telnet_login_index == 0:
        print 'Telnet host timeout, please confirm you can reach the host'
        is_error = True
        debug('''From 'telnet command' mode jump to is_error''', is_debug)
    elif telnet_login_index == 1:
        print 'The mpc connect to the remote target timeout, please confirm'
        is_error = True
        debug('''From 'telnet command' mode jump to is_error''', is_debug)
    elif telnet_login_index == 2:
        print 'The mpc has no route to the target, please confirm'
        is_error = True
        debug('''From 'telnet command' mode jump to is_error''', is_debug)
    elif telnet_login_index == 3 or telnet_login_index == 5:
        is_user = True
        debug('''From 'telnet command' mode jump to is_user''', is_debug)
    elif telnet_login_index == 4:
        is_passwd = True 
        debug('''From 'telnet command' mode jump to is_passwd''', is_debug)
    else:
        print 'Not match any expect in step1 expect_list, please check'
        is_error = True
        debug('''From 'telnet command' mode jump to is_error''', is_debug)
    telnet_login_result = general_login(telnet_login_result, user, passwd, prompt, login_timeout, login_retry_times, is_user, is_passwd, is_no, is_prompt, is_error, is_debug)               
    return telnet_login_result        


def telnet_login_via_serial(ip, serial, user, passwd, prompt, login_timeout=2, login_retry_times=20, log_file_path=[], log_file_open=[], is_debug=True):
    ###transfer all para to correct format
    login_retry_times = int(login_retry_times)
    login_timeout = int(login_timeout)
    ###define private para
    is_user = False
    is_passwd = False
    is_no = False
    is_prompt = False
    is_error = False
    ###use timeout retry func to login
    ######define timeoute retry func's para
    telnet_login_command = 'telnet %s %s' % (ip, serial)
    debug('''Telnet serial process start, command is "%s"''' % telnet_login_command, is_debug)
    cli_mode_tuple_list = [(telnet_login_command, 'sendline')]
    expect_list = [pexpect.TIMEOUT, 'No route to host.*', 'Unable .* Connection refused.*', 'Escape character is.*']
    timeout = login_timeout
    ###The last one send enter to confirm
    retry_cli_mode_tuple_list = [[('', 'sendnone')]] * (login_retry_times - 1) + [['', 'sendline']]
    telnet_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, '', is_debug)
    telnet_login_result = telnet_login_info[0]
    telnet_login_index = telnet_login_info[1]
    if log_file_path == './stdout':
        telnet_login_result.logfile_read = sys.stdout
    else:
        telnet_login_result.logfile_read = log_file_open
    if telnet_login_index == 0:
        print 'Telnet host timeout, please confirm you can reach the host'
        is_error = True
        debug('''From 'telnet command' mode jump to is_error''', is_debug)
    elif telnet_login_index == 1:
        print 'The mpc has no route to the target, please confirm'
        is_error = True
        debug('''From 'telnet command' mode jump to is_error''', is_debug)
        return None
    elif telnet_login_index == 2:
        debug('''The target serial is in using or not alive, please confirm''', is_debug)
        is_error = True
        debug('''From 'telnet command' mode jump to is_error''', is_debug)
        return None
    elif telnet_login_index == 3:
        debug('''Meet 'Escape' status, send enter to confirm login''', is_debug)
        cli_mode_tuple_list = [('', 'sendline')]
        ###0 If the cisco serial server's port connect nothing, would stay'Escape character is '^]'.' when you send 'enter', cannot diff it from the normal way ,use timeout to mark it
        ###1 May meet aerohive pruduct powerdown on vmwarw ---EOF, telnet command is EOF already
        ###2 Aerohive product already login---#
        ###3 Aerohive product already login, but is the first time to login after reset---'Use the Aerohive.*<yes|no>:'
        ###4 Aerohive product login normally
        ###5 login switch via serial(meet password) 
        expect_list = [pexpect.TIMEOUT, pexpect.EOF, 'login.*', '[Pp]assword.*', 'yes\|no>:.*', prompt]
        timeout = login_timeout
        ###The last one send enter to confirm
        retry_cli_mode_tuple_list = [[('', 'sendnone')]] * (login_retry_times - 1) + [['', 'sendline']]
        telnet_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, telnet_login_result, is_debug)
        telnet_login_result = telnet_login_info[0]
        telnet_login_index = telnet_login_info[1]   
        if telnet_login_index == 0:
            print '''Send enter to confirm telnet serial timeout, please confirm the serial is alive'''
            is_error = True
            debug('''From 'send enter' mode jump to is_error''', is_debug)
        elif telnet_login_index == 1:
            print '''Telnet vmware simulate OS timeout, please confirm the simulate OS is alive'''
            is_error = True
            debug('''From 'send enter' mode jump to is_error''', is_debug)
        elif telnet_login_index == 2:
            is_user = True
            debug('''From 'send enter confirm login' jump to is_user''', is_debug)
        elif telnet_login_index == 3:
            is_passwd = True
            debug('''From 'send enter confirm login' jump to is_passwd''', is_debug)
        elif telnet_login_index == 4:
            is_no = True
            debug('''From 'send enter confirm login' jump to is_no''', is_debug)
        elif telnet_login_index == 5:
            is_prompt = True
            debug('''From 'send enter confirm login' jump to is_prompt''', is_debug)
        else:
            print '''Not match any expect values, please check'''
            is_error = True
            debug('''From 'send enter' mode jump to is_error''', is_debug)
    else:
        print '''Not match any expect in expect_list, please check'''
        is_error = True
        debug('''From 'telnet command' mode jump to is_error''', is_debug)    
    telnet_login_result = general_login(telnet_login_result, user, passwd, prompt, login_timeout, login_retry_times, is_user, is_passwd, is_no, is_prompt, is_error, is_debug)               
    return telnet_login_result


def telnet_logout(spawn_child, logout_timeout=2, logout_retry_times=20, is_debug=True):
    telnet_logout_result = spawn_child
    debug('....................Quit login status....................', is_debug)
    cli_mode_tuple_list = [(']', 'sendcontrol')]
    expect_list = [pexpect.TIMEOUT, 'telnet>.*']
    retry_cli_mode_tuple_list = [[('', 'sendnone')]] + [[('', 'sendline')]] + [[(']', 'sendcontrol')]] + [[('', 'sendnone')]] * (logout_retry_times - 3)
    telnet_logout_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, logout_timeout, retry_cli_mode_tuple_list , logout_retry_times, telnet_logout_result, is_debug)
    telnet_logout_result = telnet_logout_info[0]
    telnet_logout_index = telnet_logout_info[1]
    if telnet_logout_index == 0:
        print '''TimeOut when send ctrl+] to to logout telnet prompt status'''
        print 'before is %s, after is %s' % (telnet_logout_result.before, telnet_logout_result.after)
        return None
    elif telnet_logout_index == 1:
        debug('''Meet telnet> status, should send q now''', is_debug)
        cli_mode_tuple_list = [('q', 'sendline')]
        expect_list = [pexpect.TIMEOUT, 'Connection closed.*']
        retry_cli_mode_tuple_list = [[('', 'sendnone')]] * logout_retry_times
        telnet_logout_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, logout_timeout, retry_cli_mode_tuple_list , logout_retry_times, telnet_logout_result, is_debug)
        telnet_logout_result = telnet_logout_info[0]
        telnet_logout_index = telnet_logout_info[1]
        if telnet_logout_index == 0:
            print '''TimeOut when send ctrl+] to to logout telnet prompt status'''
            print 'before is %s, after is %s' % (telnet_logout_result.before, telnet_logout_result.after)
            return None
        elif telnet_logout_index == 1:
            debug('Quit telnet successfully', is_debug)
        else:
            print '''Not match any expect in 'logout' expect_list, please check'''
            print 'before is %s, after is %s' % (telnet_logout_result.before, telnet_logout_result.after)
            telnet_logout_result.close(force=True)
            return None                           
    else:
        print '''Not match any expect in 'logout' expect_list, please check'''
        print 'before is %s, after is %s' % (telnet_logout_result.before, telnet_logout_result.after)
        telnet_logout_result.close(force=True)
        return None                
    return telnet_logout_result


class telnet_host:
    def __init__(self, ip, user, passwd, serial='', absolute_logfile='', prompt='[$#>]', wait_time=0, is_debug=False):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.is_debug = is_debug
        self.serial = serial
        self.prompt = prompt
        self.absolute_logfile = absolute_logfile
        ###v13 add wait time
        self.wait_time = wait_time
        if absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open = open(absolute_logfile, mode='w')
        print 'Telnet %s process start, init parameters............' % ip
    
    def __del__(self):
        if self.absolute_logfile == './stdout':
            pass
        else:
            ###v12
            self.absolute_logfile_open.close()
            absolute_logfile = self.absolute_logfile
            with open(absolute_logfile, mode='r') as absolute_logfile_open:
                originate_logfile = absolute_logfile_open.read()
            #v19
            # ##sub '--More--'
            correct_logfile = re.sub(' --More-- \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08          \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08', '', originate_logfile)
            # ##sub 28 blanks and \r
            correct_logfile = re.sub(' {28}|\r', '', correct_logfile)
            with open(absolute_logfile, mode='w') as absolute_logfile_open:
                absolute_logfile_open.write(correct_logfile)   
        print 'Telnet %s process over.' % self.ip

    def login_via_ip(self, login_timeout=2, login_retry_times=20):
        ip = self.ip
        user = self.user
        passwd = self.passwd
        prompt = self.prompt
        is_debug = self.is_debug
        log_file_path = self.absolute_logfile
        if log_file_path == './stdout':
            log_file_open = []
        else:
            log_file_open = self.absolute_logfile_open
        telnet_login_result = telnet_login_via_ip(ip, user, passwd, prompt, login_timeout, login_retry_times, log_file_path, log_file_open, is_debug)
        return telnet_login_result
            
    def login_via_serial(self, login_timeout=2, login_retry_times=20):
        ip = self.ip
        user = self.user
        passwd = self.passwd
        is_debug = self.is_debug
        serial = self.serial
        prompt = self.prompt
        log_file_path = self.absolute_logfile
        if log_file_path == './stdout':
            log_file_open = []
        else:
            log_file_open = self.absolute_logfile_open
        telnet_login_result = telnet_login_via_serial(ip, serial, user, passwd, prompt, login_timeout, login_retry_times, log_file_path, log_file_open, is_debug)
        return telnet_login_result

    def execute_command_via_cli_sendmode_expect_timeout_wait_list(self, spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times=2, is_debug=True):
        is_debug = self.is_debug
        wait_time = self.wait_time
        telnet_cli_result = execute_command_via_cli_sendmode_expect_timeout_wait_list(spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times, is_debug=True)        
        return telnet_cli_result

    def logout(self, spawn_child, logout_timeout=2, logout_retry_times=20):
        is_debug = self.is_debug
        telnet_logout_result = telnet_logout(spawn_child, logout_timeout, logout_retry_times, is_debug)
        return telnet_logout_result

def telnet_execute_cli(ip, user, passwd, serial, cli_list, prompt, timeout, retry_times, logdir, logfile, is_debug, is_shell, shellpasswd, wait_time, bootpasswd=[]):
    timeout = int(timeout)
    wait_time = float(wait_time)
    absolute_logfile = logdir + '/' + logfile
    debug('logfile path is %s' % absolute_logfile, is_debug)
    telnet = telnet_host(ip, user, passwd, serial, absolute_logfile, prompt, wait_time, is_debug)
    serial = int(serial)
    ###set private var
    login_timeout = 2
    login_retry_times = retry_times
    cli_timeout = timeout
    cli_retry_times = 2
    logout_timeout = 2
    logout_retry_times = 10
    
    if serial != 23 and serial:
        debug('serial mode login', is_debug)
        telnet_host_login = telnet.login_via_serial(login_timeout, login_retry_times)
    else:
        debug('ip mode login', is_debug)
        telnet_host_login = telnet.login_via_ip(login_timeout, login_retry_times)
    if telnet_host_login:
        cli_sendmode_expect_timeout_wait_list = generate_cli_sendmode_expect_timeout_wait_list(cli_list, prompt, cli_timeout, wait_time, passwd, shellpasswd, bootpasswd)
        debug('Cli_sendmode_expect_timeout_wait_list is as below: %s' % str(cli_sendmode_expect_timeout_wait_list), is_debug)
        telnet_host_execute = telnet.execute_command_via_cli_sendmode_expect_timeout_wait_list(telnet_host_login, cli_sendmode_expect_timeout_wait_list, cli_retry_times)                                       
    else:
        print 'Telnet login failed'
        return None
    ###logout
    if telnet_host_execute:
        telnet_host_logout = telnet.logout(telnet_host_execute, logout_timeout, logout_retry_times)
    else:
        print 'Telnet execute cli failed'
        return None        
    return telnet_host_logout

parse = argparse.ArgumentParser(description='Telnet host to execute CLI')
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='user',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='passwd',
                    help='Login Password')
###v12 modify the prompt to AH-\w+#.*
parse.add_argument('-m', '--prompt', required=False, default='AH-\w+#.*', dest='prompt',
                    help='The login prompt you want to meet')

parse.add_argument('-o', '--timeout', required=False, default=10, type=int, dest='timeout',
                    help='Time out value for every execute cli step')

parse.add_argument('-l', '--logdir', required=False, default='.', dest='logdir',
                    help='The log file dir')

parse.add_argument('-z', '--logfile', required=False, default='stdout', dest='logfile',
                    help='The log file name')

parse.add_argument('-v', '--command', required=False, action='append', default=[], dest='cli_list',
                    help='The command you want to execute')
#v19
parse.add_argument('-sp', '--shellpasswd', required=False, default='', dest='shellpasswd',
                    help='Shell password for enter to shell mode')

parse.add_argument('-debug', '--debug', required=False, default=False, action='store_true', dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-b', '--shell', required=False, default=False, action='store_true', dest='is_shell',
                    help='enable shell mode')

parse.add_argument('-i', '--interface', required=False, default=23, type=int, dest='serial',
                    help='Serial number')

parse.add_argument('-n', '--nowaite', required=False, default=False, action='store_true', dest='is_waite',
                    help='enable waite mode')

parse.add_argument('-f', '--file', required=False, default=False, dest='configfilepath',
                    help='The path of configurefile')
###v13
parse.add_argument('-w', '--wait', required=False, default=0, type=float , dest='wait_time',
                    help='wait time between the current cli and next cli')

parse.add_argument('-k', '--retry', required=False, default=90, type=int, dest='retry_times',
                    help='How many times you want to retry when the login step is failed')

parse.add_argument('-bp', '--bootpassword', required=False, default='', dest='bootpasswd',
                    help='boot password')

def main():
    args = parse.parse_args() 
    ip = args.desip
    user = args.user
    passwd = args.passwd
    ###v4 transfer \$ to \\$
    prompt = args.prompt
    prompt = re.sub('\$', '\\$', prompt)
    timeout = args.timeout
    logdir = args.logdir
    ###v17
    logfile = args.logfile.strip()
    cli_list = args.cli_list
    is_debug = args.is_debug
    shellpasswd = args.shellpasswd
    is_shell = args.is_shell
    serial = args.serial
    config_file_path = args.configfilepath
    ###v10
    wait_time = args.wait_time
    retry_times = args.retry_times
    bootpasswd = args.bootpasswd
    input_para_list = sys.argv
    debug('''Type command is "python %s"''' % (' '.join(input_para_list)), is_debug)
    execute_cli_list = generate_cli_list(cli_list, config_file_path, input_para_list, is_debug)
    debug('execute_cli_list is as below', is_debug)
    debug(execute_cli_list, is_debug)
    try:
        telnet_result = telnet_execute_cli(ip, user, passwd, serial, execute_cli_list, prompt, timeout, retry_times, logdir, logfile, is_debug, is_shell, shellpasswd, wait_time, bootpasswd)
    except Exception, e:
        print str(e)
    else:
        return telnet_result
            
if __name__ == '__main__':
    telnet_result = main()
    if telnet_result:
        telnet_result.close()
        print 'Telnet successfully, exit 0'
        sys.exit(0)
    else:
        print 'Telnet failed, exit 1'
        sys.exit(1)
