#!/usr/bin/python
# Filename: ssh.py
# Function: ssh target execute cli
# coding:utf-8
# Author: Well
# Example command:ssh.py -d ip -u user -p password -m prompt -o timeout -l logdir -z logfile -v "show run" -v "show version"
import pexpect, sys, argparse, re, os, time
from console import generate_cli_sendmode_expect_timeout_wait_list, debug, sleep, spawn_timeout_retry, generate_cli_list, execute_command_via_cli_sendmode_expect_timeout_wait_list_ssh, general_login, str2list

def ssh_login(ip, user, passwd, prompt, port=22, login_timeout=2, login_retry_times=20, log_file_path=[], log_file_open=[], is_debug=True):
    # ##transfer all para to correct format
    port = int(port)
    login_timeout = int(login_timeout)
    login_retry_times = int(login_retry_times)
    # ##define private para
    is_user = False
    is_passwd = False
    is_no = False
    is_prompt = False
    is_error = False
    # ##start login process
    ssh_login_command = 'ssh %s@%s -p %s' % (user, ip, port)
    debug('''SSH login process start, the command is "%s"''' % ssh_login_command, is_debug)  
    # ##use timeout retry func to login
    ######define timeoute retry func's para
    cli_mode_tuple_list = [(ssh_login_command, 'sendline')]
    # ##v14 add support login without username passwd
    expect_list = [pexpect.TIMEOUT, 'Connection timed out', 'No route to host.*', 'Are you sure you want to continue connecting .*\?', '[Pp]assword:', prompt]
    timeout = login_timeout
    # ##v13
    retry_cli_mode_tuple_list = [[('', 'sendnone')]] * 5 + [[('', 'sendline')]] * (login_retry_times - 5)
    ssh_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, '', is_debug)
    ssh_login_result = ssh_login_info[0]
    ssh_login_index = ssh_login_info[1]
    if log_file_path == './stdout':
        ssh_login_result.logfile_read = sys.stdout
    else:
        ssh_login_result.logfile_read = log_file_open
    if ssh_login_index == 0:
        print 'SSH host timeout, please confirm you can reach the host'
        is_error = True
        debug('''From 'SSH command' mode jump to is_error''', is_debug)
    elif ssh_login_index == 1:
        print 'The mpc connect to the remote target timeout, please confirm the target is reachable.'
        is_error = True
        debug('''From 'SSH command' mode jump to is_error''', is_debug)
    elif ssh_login_index == 2:
        print 'The mpc has no route to the target, please confirm the route table and interface status'
        is_error = True
        debug('''From 'SSH command' mode jump to is_error''', is_debug)
    elif ssh_login_index == 3:
        debug('The target is not in known host list, need send yes to confirm login', is_debug)
        cli_mode_tuple_list = [('yes', 'sendline')]
        # ##v14 add support login without username password
        expect_list = [pexpect.TIMEOUT, '[Pp]assword:', prompt]
        timeout = login_timeout
        spwan_child = ssh_login_result
        # ##v13
        retry_cli_mode_tuple_list = [[('', 'sendnone')]] * 5 + [[('', 'sendline')]] * (login_retry_times - 5)
        ssh_auth_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, spwan_child, is_debug)
        ssh_auth_result = ssh_auth_info[0]
        ssh_auth_index = ssh_auth_info[1]
        if ssh_auth_index == 0:
            print 'SSH host send yes to confirm login timeout, please confirm the host is reachable'
            is_error = True
            debug('''From 'send yes to pass auth' mode jump to is_error''', is_debug)
        elif ssh_auth_index == 1:
            debug('Add host to known host list successfully, and meet password part', is_debug)
            is_passwd = True
            debug('''From 'send yes to pass auth' mode jump to is_passwd''', is_debug)
        # ##v14 add support login without username password
        elif ssh_auth_index == 2:
            debug('Add host to known host list successfully, and meet password part', is_debug)
            is_prompt = True
            debug('''From 'send yes to pass auth' mode jump to is_prompt''', is_debug)
        # ##v14
        ssh_login_result = ssh_auth_result
    elif ssh_login_index == 4:
        is_passwd = True
        debug('''From 'SSH command' mode jump to is_passwd''', is_debug)
    # ##v14 add support login without username password
    elif ssh_login_index == 5:
        is_prompt = True
        debug('''From 'SSH command' mode jump to is_prompt''', is_debug)
    else:
        print 'Not match any expect in step1 expect_list, please check'
        is_error = True
        debug('''From 'SSH command' mode jump to is_error''', is_debug)
    ssh_login_result = general_login(ssh_login_result, user, passwd, prompt, login_timeout, login_retry_times, is_user, is_passwd, is_no, is_prompt, is_error, is_debug)               
    return ssh_login_result

def ssh_logout(spawn_child, logout_timeout=2, logout_retry_times=20, is_debug=True):
    ssh_logout_result = spawn_child
    debug('....................Quit login status....................', is_debug)
    ssh_logout_result.sendcontrol('d')
    index = ssh_logout_result.expect([pexpect.TIMEOUT, 'Connection to .* closed'], timeout=logout_timeout)
    if index == 0:
        logout_retry_index = 0
        # ##v13 modify logout retry times from 2 to 5 
        logout_retry_times = 5
        logout_retry_num = 0
        while logout_retry_index == 0:
            logout_retry_num += 1
            debug('%s time retry begin' % logout_retry_num, is_debug)
            #v18 add sendline for show log buffer
            ssh_logout_result.sendline('')
            #v18 end
            ssh_logout_result.sendcontrol('d')
            logout_retry_index = ssh_logout_result.expect([pexpect.TIMEOUT, 'Connection to .* closed'], timeout=logout_timeout)
            debug('%s time retry over' % logout_retry_num, is_debug)
            # ##add retry_num check here, when retry_num = retry_times, return none
            if logout_retry_num == logout_retry_times:
                print 'Retry %s times and logout still failed, return none' % logout_retry_times
                print 'before is %s' % ssh_logout_result.before
                print 'after is %s' % ssh_logout_result.after
                ssh_logout_result.close(force=True)
                return None
    elif index == 1:
        pass
    debug('Free ssh successfully', is_debug)
    return ssh_logout_result

class ssh_host:
    # ##v10 add wait time
    def __init__(self, ip, user, passwd, port=22, absolute_logfile='', prompt='[$#>]', wait_time=0, is_debug=False):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.port = port
        self.is_debug = is_debug
        self.absolute_logfile = absolute_logfile
        self.prompt = prompt
        # ##v10 add wait time
        #v16 set to float mode
        self.wait_time = float(wait_time)
        if absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open = open(absolute_logfile, mode='w')
        print 'SSH %s process start, init parameters............' % ip
    
    def __del__(self):
        if self.absolute_logfile == './stdout':
            pass
        else:
            # ##close the mode a file firstly
            self.absolute_logfile_open.close()
            absolute_logfile = self.absolute_logfile
            with open(absolute_logfile, mode='r') as absolute_logfile_open:
                originate_logfile = absolute_logfile_open.read()
            #v19
            # ##sub '--More--'
            correct_logfile = re.sub(' --More-- \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08          \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08', '', originate_logfile)
            #correct_logfile = re.sub('\s{33}', '', correct_logfile)
            # ##sub 28 blanks and \r
            correct_logfile = re.sub(' {28}|\r', '', correct_logfile)
            with open(absolute_logfile, mode='w') as absolute_logfile_open:
                absolute_logfile_open.write(correct_logfile)            
        print 'SSH %s process over.' % self.ip
    # v5 timeout 10s
    def login(self, login_timeout=2, login_retry_times=20):
        ip = self.ip
        user = self.user
        passwd = self.passwd
        port = self.port
        prompt = self.prompt
        is_debug = self.is_debug
        log_file_path = self.absolute_logfile
        if log_file_path == './stdout':
            log_file_open = []
        else:
            log_file_open = self.absolute_logfile_open
        ssh_login_result = ssh_login(ip, user, passwd, prompt, port, login_timeout, login_retry_times, log_file_path, log_file_open, is_debug)
        return ssh_login_result
    
    def execute_command_via_cli_sendmode_expect_timeout_wait_list_ssh(self, spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times=2, is_debug=True):
        is_debug = self.is_debug
        wait_time = self.wait_time
        ssh_cli_result = execute_command_via_cli_sendmode_expect_timeout_wait_list_ssh(spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times, is_debug=True)        
        return ssh_cli_result
    
    def logout(self, spawn_child, logout_timeout=2, logout_retry_times=20):
        is_debug = self.is_debug
        ssh_logout_result = ssh_logout(spawn_child, logout_timeout, logout_retry_times, is_debug)
        return ssh_logout_result


def ssh_execute_cli(ip, user, passwd, port, cli_list, prompt, timeout, retry_times, logdir, logfile, is_debug, is_shell, shellpasswd, wait_time, bootpasswd=[]):
    # ##define format
    timeout = int(timeout)
    wait_time = float(wait_time)
    absolute_logfile = logdir + '/' + logfile
    debug('logfile path is %s' % absolute_logfile, is_debug)
    port = int(port)
    # ##set private var
    login_timeout = 2
    login_retry_times = retry_times
    cli_timeout = timeout
    cli_retry_times = 2
    logout_timeout = 2
    logout_retry_times = 10
    # ##start ssh process
    ssh = ssh_host(ip, user, passwd, port, absolute_logfile, prompt, wait_time, is_debug)
    ssh_host_login = ssh.login(login_timeout, login_retry_times)
    if ssh_host_login:
        cli_sendmode_expect_timeout_wait_list = generate_cli_sendmode_expect_timeout_wait_list(cli_list, prompt, cli_timeout, wait_time, passwd, shellpasswd, bootpasswd)
        debug('Cli_sendmode_expect_timeout_wait_list is as below: %s' % str(cli_sendmode_expect_timeout_wait_list), is_debug)
        ssh_host_execute = ssh.execute_command_via_cli_sendmode_expect_timeout_wait_list_ssh(ssh_host_login, cli_sendmode_expect_timeout_wait_list, cli_retry_times)                                       
    else:
        print 'ssh login failed'
        return None
    # ##logout
    if ssh_host_execute:
        ssh_host_logout = ssh.logout(ssh_host_execute, logout_timeout, logout_retry_times)
    else:
        print 'ssh execute cli failed'
        return None        
    return ssh_host_logout


parse = argparse.ArgumentParser(description='SSH host to execute CLI')
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='user',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='passwd',
                    help='Login Password')
# ##v8 modify the prompt to AH-\w+#.*
parse.add_argument('-m', '--prompt', required=False, default='AH.*#', dest='prompt',
                    help='The login prompt you want to meet')

parse.add_argument('-o', '--timeout', required=False, default=10, type=int, dest='timeout',
                    help='Time out value for every execute cli step')

parse.add_argument('-l', '--logdir', required=False, default='.', dest='logdir',
                    help='The log file dir')

parse.add_argument('-z', '--logfile', required=False, default='stdout', dest='logfile',
                    help='The log file name')

parse.add_argument('-v', '--command', required=False, action='append', default=[], dest='cli_list',
                    help='The command you want to execute')
#v17 start
parse.add_argument('-sp', '--shellpasswd', required=False, default='', dest='shellpasswd',
                    help='Shell password for enter to shell mode')
#v17 end
parse.add_argument('-debug', '--debug', required=False, default=False, action='store_true', dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-b', '--shell', required=False, default=False, action='store_true', dest='is_shell',
                    help='enable shell mode')

parse.add_argument('-i', '--interface', required=False, default=22, type=int, dest='port',
                    help='ssh port')

parse.add_argument('-n', '--nowaite', required=False, default=False, action='store_true', dest='is_waite',
                    help='enable waite mode')

parse.add_argument('-f', '--file', required=False, default=False, dest='configfilepath',
                    help='The path of configurefile')
## ##v10
#parse.add_argument('-w', '--wait', required=False, default=0, type=float , dest='wait_time',
#                    help='wait time between the current cli and next cli')
#v16
parse.add_argument('-w', '--wait', required=False, action='append', default=[0], dest='wait_time_list',
                    help='wait time between the current cli and next cli')

parse.add_argument('-bp', '--bootpassword', required=False, default='', dest='bootpasswd',
                    help='boot password')

parse.add_argument('-k', '--retry', required=False, default=90, type=int, dest='retry_times',
                    help='How many times you want to retry when the login step is failed')
#v17 start
parse.add_argument('-loop', '--loop', required=False, default='1', dest='loop',
                    help='The loop times')
#v17 end

def main():
    args = parse.parse_args() 
    ip = args.desip
    user = args.user
    passwd = args.passwd
    # ##v4 transfer \$ to \\$
    prompt = args.prompt
    prompt = re.sub('\$', '\\$', prompt)
    # ##v13 add support win client
    prompt = '%s|(root|logger)@.*~.*\$' % prompt
    timeout = args.timeout
    logdir = args.logdir
    logfile = args.logfile.strip()
    cli_list = args.cli_list
    is_debug = args.is_debug
    shellpasswd = args.shellpasswd
    is_shell = args.is_shell
    port = args.port
    retry_times = args.retry_times
    config_file_path = args.configfilepath
    #v16
    wait_time_list = args.wait_time_list
    #v16 select the last one as current wait time, set to float mode
    wait_time = float(wait_time_list[-1])
    bootpasswd = args.bootpasswd
    #v17 start
    loop = str2list(args.loop)
    #v17 end
    input_para_list = sys.argv
    debug('''Type command is "python %s"''' % (' '.join(input_para_list)), is_debug)
    #v17 start
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
    #v17 end
    execute_cli_list = generate_cli_list(execute_cli_list, config_file_path, input_para_list, is_debug)
    debug('execute_cli_list is as below', is_debug)
    debug(execute_cli_list, is_debug)
    try:
        ssh_result = ssh_execute_cli(ip, user, passwd, port, execute_cli_list, prompt, timeout, retry_times, logdir, logfile, is_debug, is_shell, shellpasswd, wait_time, bootpasswd)
    except Exception, e:
        print str(e)
    else:
        return ssh_result
            
if __name__ == '__main__':
    ssh_result = main()
    if ssh_result:
        ssh_result.close()
        print 'SSH successfully, exit 0'
        sys.exit(0)
    else:
        print 'SSH failed, exit 1'
        sys.exit(1)
