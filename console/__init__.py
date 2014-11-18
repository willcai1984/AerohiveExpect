#!/usr/bin/python
# Filename: console.py
# Function: login target execute cli via console server
# coding:utf-8
# Author: Well
# Example command: console.py -i 782 -e tb1-ap350-3 -v "show run" -d localhost -u admin -p aerohive -m "AH.*#"
# Transmit command: console -M localhost tb1-ap350-3 -f -l root
import pexpect, sys, argparse, re, time

def sleep(mytime=1):
    time.sleep(mytime)


def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print '%s DEBUG' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
        print mesage

###v18 Check if the command is more than 80 characters(prompt may have more than 10 characters)
def send_command(command, spawn_child, send_mode='sendline', is_debug=True):
    ###define private parameters
    buffer_sleep_time = 5
    step_sleep_time = 0.1
    divid_cli_length = 60
    eatbuffer_cli_length = 70
    if len(command) < divid_cli_length:
        if send_mode == 'sendline':
            spawn_child.sendline(command)
        elif send_mode == 'sendcontrol':
            spawn_child.sendcontrol(command)
        elif send_mode == 'send':
            spawn_child.send(command)
        elif send_mode == 'sendnone':
            pass
        else:
            print 'Incorrect sendmode, please check'
            spawn_child.close(force=True)
            return None
    else:
        debug('Meet long command(more than %s) status, send cli one letter by one' % divid_cli_length, is_debug)
        for i in command:
            spawn_child.send(i)
        #v26 start
        sleep(step_sleep_time)
        #v26 end
        if send_mode == 'sendline':
            spawn_child.sendline('')
            debug('Send enter first time', is_debug)
        elif send_mode == 'send':
            pass
        else:
            print 'Incorrect sendmode, please check'
            spawn_child.close(force=True)
            return None
        if len(command) >= eatbuffer_cli_length:
            debug('Meet long command(more than %s) status' % eatbuffer_cli_length, is_debug)
            debug('Sleep %ss to eat all buffer' % buffer_sleep_time, is_debug)
            sleep(buffer_sleep_time)
            spawn_child.expect('.*')
            debug('First time enter is over, and the buffer has been cleared', is_debug)
            debug('spawn_child.after is as below', is_debug)
            debug(str(spawn_child.after), is_debug)
            spawn_child.sendline('')
            debug('Send enter second time', is_debug)

# ## cli mode: send/sendline/sendcontrol/sendnone, for example: [('','sendline'),('d','sendcontrol'),('','sendnone')]
###### if you want to send ctrl-e+co cli_mode_tuple_list=[[('e','sendcontrol'),('co','send')]]
# ## retry_cli_mode: send/sendline/sendcontrol/sendnone
def spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout=5 , retry_cli_mode_tuple_list=[], retry_times=5, spawn_child='', is_debug=True):
    debug('............Timeout_retry func Init sendline parameters............', is_debug)
    retry_num = 0
    retry_times = int(retry_times)
    debug('CLI is', is_debug)
    debug(cli_mode_tuple_list, is_debug)
    debug('Expect list is', is_debug)
    debug(expect_list, is_debug)
    debug('Timeout is', is_debug)
    debug(timeout, is_debug)
    # ##process retry_cli_list
    if len(retry_cli_mode_tuple_list) < retry_times:
        # ##if retry_cli num is less than retry times, extend with sendnone type
        extend_num = retry_times - len(retry_cli_mode_tuple_list)
        retry_execute_tuple_list = retry_cli_mode_tuple_list + [[('', 'sendnone')]] * extend_num
    elif len(retry_cli_mode_tuple_list) == retry_times:
        retry_execute_tuple_list = retry_cli_mode_tuple_list
    else:
        print '''retry_cli_list's length is more than retry_times, cannot process'''
        return None, None
#    debug('............Timeout_retry func Execute command send process............', is_debug)
    # ##Judge if spawn exist, yes--sendline directly, no--create spawn_child
    if spawn_child:
        debug('spawn child exist, sendline directly', is_debug)
        for cli, cli_mode in cli_mode_tuple_list:
            if cli_mode == 'send':
                spawn_child.send(cli)
            elif cli_mode == 'sendline':
                spawn_child.sendline(cli)
            elif cli_mode == 'sendcontrol':
                spawn_child.sendcontrol(cli)
            elif cli_mode == 'sendnone':
                pass
            else:
                print '''Error cli mode error, please check your cli's mode is send/sendline/sendcontrol/sendnone'''
                return None, None 
    else:
        debug('spawn child not exist, create spawn firstly', is_debug)
        for cli, cli_mode in cli_mode_tuple_list:
            spawn_child = pexpect.spawn(cli)
    retry_index = spawn_child.expect(list(expect_list), timeout=timeout)
    # ##check whether enter to retry mode
    if retry_index == 0:
        debug('Meet time out status, enable retry mode')
        debug('retry_execute_tuple_list is', is_debug)
        debug(retry_execute_tuple_list, is_debug)
        while retry_index == 0:
            # ## the first retry, the num is 1
            retry_num += 1
            # ## if more than retry total num, return None
            if retry_num > retry_times:
                print 'Retry %s times and still failed, close the expect child and return none' % retry_times
                print 'before is %s, after is %s' % (spawn_child.before, spawn_child.after)
                spawn_child.close(force=True)
                return None, retry_index  
            debug('Retry %s time begin' % retry_num, is_debug)
            # ##retry_execute_tuple_list increased via index     
            for cli, cli_mode in retry_execute_tuple_list[retry_num - 1]:
                if cli_mode == 'send':
                    spawn_child.send(cli)
                elif cli_mode == 'sendline':
                    spawn_child.sendline(cli)
                elif cli_mode == 'sendcontrol':
                    spawn_child.sendcontrol(cli)
                elif cli_mode == 'sendnone':
                    pass
                else:
                    print '''Error cli mode error, please check your cli's mode is send/sendline/sendcontrol/sendnone'''
                    return None, None 
            retry_index = spawn_child.expect(expect_list, timeout=timeout)
            debug('Retry %s time over' % retry_num, is_debug)
    debug('''Match expect index is %s, value is '%s' ''' % (retry_index, spawn_child.after), is_debug)
    return spawn_child, retry_index
        

def general_login(spawn_chlid, user, passwd, prompt, login_timeout=2, login_retry_times=10, is_user=False, is_passwd=False, is_no=False, is_prompt=False, is_error=False, is_debug=False):
    general_login_result = spawn_chlid
    if is_user:
        debug('Meet login successfully, send user to confirm login', is_debug)
        debug('............Step1 send user to confirm login............', is_debug)            
        cli_mode_tuple_list = [(user, 'sendline')]
        expect_list = [pexpect.TIMEOUT, '[Pp]assword.*']
        timeout = login_timeout
        # ##only need expect func, sendnone
        retry_cli_mode_tuple_list = [[('', 'sendnone')]] * login_retry_times
        general_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, general_login_result, is_debug)
        general_login_result = general_login_info[0]
        general_login_index = general_login_info[1]
        if general_login_index == 0:
            print 'Send user to confirm login timeout, please confirm the host is alive'
            is_error = True
            debug('''From is_user jump to is_error''', is_debug)
        elif general_login_index == 1:                  
            is_passwd = True
            debug('''From is_user jump to is_passwd process ''', is_debug)
    if is_passwd:
        debug('Meet password successfully, send passwd to confirm login', is_debug)
        debug('............Step2 send password to confirm login............', is_debug)
        cli_mode_tuple_list = [(passwd, 'sendline')]
        expect_list = [pexpect.TIMEOUT, '\nlogin.*', '[Pp]assword.*', 'yes\|no>:.*', prompt]
        timeout = login_timeout
        # ##only need expect func, sendnone
        retry_cli_mode_tuple_list = [[('', 'sendnone')]] * login_retry_times
        general_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, general_login_result, is_debug)
        general_login_result = general_login_info[0]
        general_login_index = general_login_info[1]
        if general_login_index == 0:
            print 'Send password to confirm login timeout, please confirm the host is alive'
            is_error = True
            debug('''From is_passwd jump to is_error''', is_debug)
        elif general_login_index == 1:
            print 'Meet login again, user or password maybe incorrect, please check'
            is_error = True
            debug('''From is_passwd jump to is_error''', is_debug)
        elif general_login_index == 2:
            print 'Meet password again, password maybe incorrect, please check'
            is_error = True
            debug('''From is_passwd jump to is_error''', is_debug)                         
        elif general_login_index == 3:
            is_no = True
            debug('''From is_passwd jump to is_no process ''', is_debug)
        elif general_login_index == 4:
            is_prompt = True
            debug('''From is_passwd jump to is_prompt process ''', is_debug)
    if is_no:
        debug('Meet is_default yes or no successfully, send no to not use default config', is_debug)
        debug('............Step3 send no to not use default config............', is_debug)
        cli_mode_tuple_list = [('no', 'sendline')]
        expect_list = [pexpect.TIMEOUT, prompt]
        timeout = login_timeout
        # ##only need expect func, sendnone
        retry_cli_mode_tuple_list = [[('', 'sendnone')]] * login_retry_times
        general_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, general_login_result, is_debug)
        general_login_result = general_login_info[0]
        general_login_index = general_login_info[1]            
        if general_login_index == 0:
            print 'Send no to confirm login timeout, please confirm the host is alive'
            is_error = True
            debug('''From is_no jump to is_error''', is_debug)
        elif general_login_index == 1:
            is_prompt = True
            debug('''From is_no jump to is_prompt''', is_debug)
    if is_prompt:
        debug('Meet prompt successfully, can execute cli now', is_debug)
    if is_error:
        ###v22 del telnet_login_result
        print 'before is %s, after is %s' % (general_login_result.before, general_login_result.after)
        general_login_result.close(force=True)
        return None        
    return general_login_result

def generate_cli_list(cli_list, config_file_path, input_para_list, is_debug=True):
    if config_file_path:
        debug('config file flag is set, special process the cli_list', is_debug)
        v_argv_list = []
        f_argv_list = []
        para_index = 0
        # get -v and -f indexes for redesign all cli's order
        for para in input_para_list:
            if para == '-v':
                v_argv_list.append(para_index)
            if para == '-f':
                f_argv_list.append(para_index)
            para_index += 1
        debug('input_para_list is as below', is_debug)
        debug(input_para_list, is_debug)
        debug('v_command_index_list is as below', is_debug)
        debug(v_argv_list, is_debug)
        debug('f_command_index_list is as below', is_debug)
        debug(f_argv_list, is_debug)
        try:
            with open(config_file_path, mode='r') as config_file_open:
                read_cli_list = config_file_open.readlines()
            # ##remove \r\n for windows file
            file_cli_list = []
            for cli in read_cli_list:
                file_cli_list.append(re.sub('[\r\n]', '', cli))   
        except IOError:
            print 'Your file path %s is wrong or the file is not exist' % config_file_path
        else:
            debug('Open configure file successfully', is_debug)
        execute_cli_list = []

        if v_argv_list:
            debug('Both -v -f flag exist', is_debug)
            is_v_less_than_f = True
            is_appended_f = False
            for v_index in v_argv_list:
                # if -v's index is less than -f's, add the para to cli_list directly
                if v_index < f_argv_list[0]:
                    execute_cli_list.append(input_para_list[v_index + 1])
                else:
                    # if -v's index is the first time more than -f's, should add the f's para firstly and then add v's(only support one file), set the flag to 0
                    if is_v_less_than_f:
                        execute_cli_list.extend(file_cli_list)
                        execute_cli_list.append(input_para_list[v_index + 1])
                        is_v_less_than_f = False
                        is_appended_f = True
                    else:
                        # if -v's index is not the first time more than -f's, add the para to cli_list directly
                        execute_cli_list.append(input_para_list[v_index + 1])
            #v28 if not append f, add the file in the end
            if not is_appended_f:
                execute_cli_list.extend(file_cli_list)
                
        else:
            debug('Only -f flag exist', is_debug)
            execute_cli_list.extend(file_cli_list)
    else:
        execute_cli_list = cli_list
    return execute_cli_list
    
###v21
def generate_cli_sendmode_expect_timeout_wait_list(cli_list, prompt, timeout, wait, passwd='', shellpasswd='', bootpasswd=''):
    ###define private parameters
    cli_sendmode_expect_timeout_wait_list = [] 
    reboot_timeout = 300
    save_img_timeout = 1200
    #v27 start
    #boot_timeout = 30
    #v27 end
    sendmode = 'sendline'
    #v26
    log_regex = re.compile('^show log.*')
    reset_config_regex = re.compile('^reset config$')
    reset_boot_regex = re.compile('^reset config bootstrap$')
    ###v23
    #v28
    #v29 add support reboot offset 
    reboot_regex = re.compile('^reboot$|^reboot backup$|^reboot current$|reboot offset')
    save_config_regex = re.compile('^save config tftp:.* (current|bootstrap)')
    # ##v9 add img for accurate match
    #v24 delete $ at the end to support img.S
    save_image_regex = re.compile('^save image tftp:.*img')
    # ##v9 add support save image reboot cases
    save_image_reboot_regex = re.compile('^save image tftp:.*now$')
    shell_regex = re.compile('^_shell$')
    exit_regex = re.compile('^exit$')
    enble_regex = re.compile('^enable$')
    country_regex = re.compile('^boot-param country-code.*')
    ctrl_regex = re.compile('ctrl-.*')
    # ##v12 add ^reset$ for logout bootload
    reset_regex = re.compile('^reset$')
    # ##v12 add quit for quit login status
    quit_regex = re.compile('^quit$')
    ###v20 add scp reg
     ###v25 add save vpn scp mode
    scp_vpn_regex = re.compile('^save vpn.*scp.*')
    ###v25 modify to save image format
    scp_img_regex = re.compile('^save image scp.*')
    ###v25 add save to remote config mode
    scp_toconfig_regex = re.compile('^save config (current|bootstrap) scp.*')
    ###v25 add save from  config mode
    scp_fromconfig_regex = re.compile('^save config scp.* (current|bootstrap)')
    ###v25 add scp transfer mode special handle
    scp_transfer_regex = re.compile(r'> *scp:')
    
    for cli in cli_list:        
        if log_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '\w+.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('', sendmode, prompt, timeout, wait))
        elif reset_boot_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'bootstrap configuration.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('y', sendmode, prompt, reboot_timeout, wait))
        elif reset_config_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'bootstrap configuration.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('y', sendmode, prompt, timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('', sendmode, 'login:', reboot_timeout, wait))
        elif reboot_regex.search(cli):
            if bootpasswd:
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'Do you really want to reboot.*', timeout, wait))
                cli_sendmode_expect_timeout_wait_list.append(('y', sendmode, prompt, timeout, wait))
                #v27 start modify boot_timeout = 30 to timeout
                cli_sendmode_expect_timeout_wait_list.append(('', sendmode, 'Hit.*to stop.*autoboot.*2.*', timeout, wait))
                #v27 end
                cli_sendmode_expect_timeout_wait_list.append(('', sendmode, '[Pp]assword:', timeout, wait))
                cli_sendmode_expect_timeout_wait_list.append((bootpasswd, sendmode, '.*>.*|[Pp]assword', timeout, wait))
            else:
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'Do you really want to reboot.*', timeout, wait))
                cli_sendmode_expect_timeout_wait_list.append(('y', sendmode, prompt, timeout, wait))
                cli_sendmode_expect_timeout_wait_list.append(('', sendmode, 'login:.*', reboot_timeout, wait))             
        elif save_config_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'configuration.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('y', sendmode, prompt, timeout, wait))
        elif save_image_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, r'update image.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('y', sendmode, prompt, save_img_timeout, wait))
        elif save_image_reboot_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'update image.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('y', sendmode, prompt, save_img_timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('', sendmode, 'login:.*', reboot_timeout, wait))
        elif shell_regex.search(cli):
            #v26 start
            ### add prompt to expect
            if shellpasswd:
                #v29 add prompt for no shell passwd situation
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '[Pp]assword|%s' % prompt, timeout, wait))
                cli_sendmode_expect_timeout_wait_list.append((shellpasswd, sendmode, prompt, timeout, wait))
            else:
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, prompt, timeout, wait))
            #v26 end
        elif exit_regex.search(cli):
            if shellpasswd:
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, prompt, timeout, wait))                
            else:
                cli_sendmode_expect_timeout_wait_list.append(('save config', sendmode, prompt, timeout, wait))
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'login:.*|%s' % prompt, timeout, wait))  
        elif enble_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '[Pp]assword.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append((passwd, sendmode, prompt, timeout, wait))             
        elif country_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'To apply radio setting.*it now\?.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('y', sendmode, prompt, timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('', sendmode, 'login:.*', reboot_timeout, wait))  
        elif ctrl_regex.search(cli):
            cli = re.sub('[Cc]trl-', '', cli)
            ###v21
            ######check if ctrl command has +
            if  re.search('\+', cli):
                cli_list = cli.split('+')
                real_index = 0
                for real_cli in cli_list:
                    if real_index == 0:
                        cli_sendmode_expect_timeout_wait_list.append((real_cli, 'sendcontrol', 'None', timeout, wait))
                    elif real_index == len(cli_list) - 1:
                        cli_sendmode_expect_timeout_wait_list.append((real_cli, 'send', prompt, timeout, wait))
                    else:
                        cli_sendmode_expect_timeout_wait_list.append((real_cli, 'send', 'None', timeout, wait))
                    real_index += 1
            else:
                cli_sendmode_expect_timeout_wait_list.append((cli, 'sendcontrol', prompt, timeout, wait))
        elif reset_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'login:.*', reboot_timeout, wait))
        elif quit_regex.search(cli):
            ###v21 add prompt for quit
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '%s|login:.*' % prompt, timeout, wait))
        ###v25 add scp vpn and img
        elif scp_vpn_regex.search(cli) or scp_img_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '[Pp]assword:.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append((passwd, sendmode, prompt, timeout, wait))
        elif scp_toconfig_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '[Pp]assword:.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append((passwd, sendmode, prompt, timeout, wait))      
        elif scp_fromconfig_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, 'config to .* configuration.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append(('y', sendmode, '[Pp]assword:.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append((passwd, sendmode, prompt, timeout, wait))         
        elif scp_transfer_regex.search(cli):
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '[Pp]assword:.*', timeout, wait))
            cli_sendmode_expect_timeout_wait_list.append((passwd, sendmode, prompt, timeout, wait))
        else:
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, prompt, timeout, wait))
    return cli_sendmode_expect_timeout_wait_list


def console_login(ip, user, passwd, serialname, prompt, login_timeout=2, login_retry_times=20, log_file_path=[], log_file_open=[], is_debug=True):
    ###transfer all para to correct format
    login_retry_times = int(login_retry_times)
    login_timeout = int(login_timeout)
    if login_retry_times < 12:
        print 'Error, Retry times should be more than 12'
        return None
    ###define private para
    is_user = False
    is_passwd = False
    is_no = False
    is_prompt = False
    is_error = False
    # ##Execute login process
    console_login_command = 'console -M %s %s -f -l root' % (ip, serialname)
    debug('''Console login process start, command is "%s"''' % console_login_command, is_debug)
    cli_mode_tuple_list = [(console_login_command, 'sendline')]
    # ##0 timeout
    # ##1 no this console name in the localhost
    # ##2 normal login, cannot add.* after enter ... help due to bumped and warning check in the next step 
    expect_list = [pexpect.TIMEOUT, 'localhost: console .* not found.*', 'Enter .* for help']
    timeout = login_timeout
    # ## if not meet the expect list, should not send enter(may cause enter to login or prompt mode), only use expect func
    ######retry_cli_mode_tuple_list should have more [] with cli_mode_tuple_list
    retry_cli_mode_tuple_list = [[('', 'sendnone')]] * 10 + [[('', 'sendline')]] + [[('', 'sendnone')]] * (login_retry_times - 11)
#    spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout=5 , retry_cli_mode_tuple_list=[], login_retry_times=5, spawn_child='', is_debug=True)
    console_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, '', is_debug)
    console_login_result = console_login_info[0]
    console_login_index = console_login_info[1]
    if log_file_path == './stdout':
        console_login_result.logfile_read = sys.stdout
    else:
        console_login_result.logfile_read = log_file_open
    if console_login_index == 0:
        print 'console host timeout, please confirm you can reach the host'
        is_error = True
        debug('''From 'console command' mode jump to is_error''', is_debug)  
    elif console_login_index == 1:
        print 'The hostname %s is not aliveable in the localhost, please confirm' % serialname
        is_error = True
        debug('''From 'console command' mode jump to is_error''', is_debug)
    elif console_login_index == 2:
        # ##check if is the reboot status(reboot status no need to type 'enter' will show something on the screen)(before boot load, for the reset status not wait 30s)
        is_reboot_before_bootload = console_login_result.expect([pexpect.TIMEOUT, '[\w]+'], timeout=1)                   
        if is_reboot_before_bootload:
            debug('Reboot before bootload status or login device generate logs', is_debug)
            debug('Before is ...', is_debug)
            debug(console_login_result.before, is_debug)
            debug('After is ...', is_debug)
            debug(console_login_result.after, is_debug)
            if console_login_result.after == 'bumped' or console_login_result.after == 'WARNING':
                debug('Login device generate logs status', is_debug)
                if console_login_result.after == 'bumped':
                    debug('Meet Bumped mode, send enter to confirm')
                elif console_login_result.after == 'WARNING':
                    debug('Meet WARNING mode, send enter to confirm')
                cli_mode_tuple_list = [('', 'sendline')]
                expect_list = [pexpect.TIMEOUT, 'login.*', '[Pp]assword.*', 'yes\|no>:.*', prompt]
                timeout = login_timeout
                retry_cli_mode_tuple_list = [[('', 'sendline')]] + [[('', 'sendnone')]] * 10 + [[('', 'sendline')]] + [[('', 'sendnone')]] * (login_retry_times - 12)
                console_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, console_login_result, is_debug)
                console_login_result = console_login_info[0]
                console_login_index = console_login_info[1]
                if console_login_index == 0:
                    print 'Send enter to confirm login bumped/waning mode timeout'
                    is_error = True
                    debug('''From 'login device generate logs status' mode jump to is_error''', is_debug)  
                elif console_login_index == 1:
                    is_user = True
                    debug('''From 'login device generate logs status' mode jump to is_user''', is_debug)  
                elif console_login_index == 2:
                    is_passwd = True
                    debug('''From 'login device generate logs status' mode jump to is_passwd''', is_debug)  
                elif console_login_index == 3:
                    is_no = True
                    debug('''From 'login device generate logs status' mode jump to is_no''', is_debug)  
                elif console_login_index == 4:
                    is_prompt = True
                    debug('''From 'login device generate logs status' mode jump to is_prompt''', is_debug)  
            else:
                debug('Meet Reboot before bootload mode, wait for power on successfully')
                # ##before bootload mode cannot send anything , use sendnone 
                cli_mode_tuple_list = [('', 'sendnone')]
                expect_list = [pexpect.TIMEOUT, 'login.*', '[Pp]assword.*', 'yes\|no>:.*', prompt]
                timeout = login_timeout
                ###v18 sendline at the last for special status(generate \w+ not warning and bumped)
                ###v24 add 2 times sendline at the end for devices may generate logs automatically
                retry_cli_mode_tuple_list = [[('', 'sendnone')]] * (login_retry_times - 3) + [[('', 'sendline')]] * 3
                console_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, console_login_result, is_debug)
                console_login_result = console_login_info[0]
                console_login_index = console_login_info[1]
                if console_login_index == 0:
                    print 'Send enter to confirm login bumped/waning mode timeout'
                    is_error = True
                    debug('''From 'Reboot/Reset' mode jump to is_error''', is_debug) 
                elif console_login_index == 1:
                    is_user = True
                    debug('''From 'Reboot/Reset' mode jump to is_user''', is_debug)
                elif console_login_index == 2:
                    is_passwd = True
                    debug('''From 'Reboot/Reset' mode jump to is_passwd''', is_debug)
                elif console_login_index == 3:
                    is_no = True
                    debug('''From 'Reboot/Reset' mode jump to is_no''', is_debug)
                elif console_login_index == 4:
                    is_prompt = True
                    debug('''From 'Reboot/Reset' mode jump to is_prompt''', is_debug)  
        else:
            debug('Reboot after bootload status or normal(no reboot) status', is_debug)
            cli_mode_tuple_list = [('', 'sendline')]
            # ##0 May meet aerohive pruduct powerdown on vmwarw ---EOF, console command is EOF already
            # ##1 If the cisco console server's port console nothing, would stay'Escape character is '^]'.' when you send 'enter', cannot diff it from the normal way ,use timeout to mark it
            # ##2 Aerohive product already login---#
            # ##3 Aerohive product already login, but is the first time to login after reset---'Use the Aerohive.*<yes|no>:'
            # ##4 Aerohive product login normally
            # ##5 login switch via console(meet password) 
            expect_list = [pexpect.TIMEOUT, pexpect.EOF, 'login.*', '[Pp]assword.*', 'yes\|no>:.*', prompt]
            timeout = login_timeout
            # ##the first time send ctrl-e+co, the others send enter
            # ##v13 first and second times send enter only, if timeout: send ctrl-e+co
            # ## should add to none for wait enter take effect, because send ctrl-e+co may before the enter take effort(generate prompt), may cause confunse.
            ###v23 add sendline to the end for confirm login
            retry_cli_mode_tuple_list = [[('', 'sendnone')]] * 10 + [[('e', 'sendcontrol'), ('co', 'send')], [('', 'sendline')]] + [[('', 'sendnone')]] * (login_retry_times - 13) + [[('', 'sendline')]]
            console_login_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, console_login_result, is_debug)
            console_login_result = console_login_info[0]
            console_login_index = console_login_info[1] 
            if console_login_index == 0:
                print 'Send enter to confirm login timeout, please confirm the host is alive'
                is_error = True
                debug('''From 'Normal_login' mode jump to is_error''', is_debug)                
            elif console_login_index == 1:
                print 'The hostname %s not exist or in using, please check' % serialname
                is_error = True
                debug('''From 'Normal_login' mode jump to is_error''', is_debug)   
            elif console_login_index == 2:
                is_user = True
                debug('''From 'Normal_login' mode jump to is_user''', is_debug)
            elif console_login_index == 3:
                is_passwd = True
                debug('''From 'Normal_login' mode jump to is_passwd''', is_debug)
            elif console_login_index == 4:
                is_no = True
                debug('''From 'Normal_login' mode jump to is_no''', is_debug)
            elif console_login_index == 5:
                is_prompt = True
                debug('''From 'Normal_login' mode jump to is_prompt''', is_debug)
        # ##Process the login via flag
        # ## the four flags' logic are if/if/if/if not if/elif/elif/elif due to is_user may use is_passwd's func
        console_login_result = general_login(console_login_result, user, passwd, prompt, login_timeout, login_retry_times, is_user, is_passwd, is_no, is_prompt, is_error, is_debug)       
    return console_login_result


def execute_command_via_cli_sendmode_expect_timeout_wait_list(spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times=2, is_debug=True):
    ###define private parameters
    execute_cli_result = spawn_child
    cli_num = 1
    ###v21
    for cli, send_mode, cli_expect, cli_timeout, cli_wait in cli_sendmode_expect_timeout_wait_list:
        send_command(cli, execute_cli_result, send_mode, is_debug)
        if cli_expect == 'None':
            pass
        else:
            index = execute_cli_result.expect([pexpect.TIMEOUT, cli_expect, '--More--', 'More:', '-- More --'], timeout=cli_timeout)
            # ##v13 set private var for meet more status
            more_num = 0
            more_index = 1
            # ##
            if index == 0:
                print '''TimeOut when execute the %s CLI, fail in Execute CLI parter''' % cli_num
                print 'CLI is %s, Expect is %s, Timeout is %s' % (cli, cli_expect, cli_timeout)
                print 'before is %s' % (execute_cli_result.before)
                print 'after is %s' % (execute_cli_result.after)
                execute_cli_result.close(force=True)
                return None
            elif index == 1:
                debug('%s successfully executed' % cli, is_debug)
            elif index == 2:
                debug('''Meet 'more', should send 'blank' to continue, Aerohive products''', is_debug)
                while more_index == 1:
                    more_num += 1
                    # ##v13 add retry for status 'more'
                    cli_mode_tuple_list = [(' ', 'send')]
                    expect_list = [pexpect.TIMEOUT, '--More--', cli_expect]
                    retry_cli_mode_tuple_list = [[('', 'sendline')]] * cli_retry_times
                    more_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, cli_timeout, retry_cli_mode_tuple_list , cli_retry_times, execute_cli_result, is_debug)
                    more_result = more_info[0]
                    more_index = more_info[1]
                    #v29 if more_index == 0, raise timeout err, if == 1,continue while loop, if ==2, jump out of the loop 
                    if more_index == 0:
                        print 'Send blank to confirm show the left log timeout, please confirm the host is alive'
                        return None         
                debug('Meet more %s times' % more_num, is_debug)
                debug('The more index is %s, value is %s' % (more_index, expect_list[more_index]), is_debug)
                debug('Send enter to eat all blanks', is_debug)
                more_result.sendline("")
                index = more_result.expect([pexpect.TIMEOUT, cli_expect], cli_timeout)
                execute_cli_result = more_result 
            elif index == 3:
                debug('''Meet 'more', should send 'blank' to continue, Dell products''', is_debug)
                while more_index == 1:
                    execute_cli_result.send(' ')
                    more_index = execute_cli_result.expect([pexpect.TIMEOUT, 'More:', cli_expect], timeout=cli_timeout)
                    if more_index == 0:
                        print 'Send blank to confirm show the left log timeout, please confirm the host is alive'
                        execute_cli_result.close(force=True)
                        return None                
            elif index == 4:
                debug('''Meet 'more', should send 'blank' to continue, H3C products''', is_debug)
                while more_index == 1:
                    execute_cli_result.send(' ')
                    more_index = execute_cli_result.expect([pexpect.TIMEOUT, '-- More --', cli_expect], timeout=cli_timeout)
                    if more_index == 0:
                        print 'Send blank to confirm show the left log timeout, please confirm the host is alive'
                        execute_cli_result.close(force=True)
                        return None
            else:
                print '''Not match any expect in 'step cli execute' expect_list, please check'''
                print 'before is %s, after is %s' % (execute_cli_result.before, execute_cli_result.after)
                execute_cli_result.close(force=True)
                return None     
            debug('Sleep wait time %s to execute next cli' % cli_wait, is_debug)
            sleep(cli_wait)
            cli_num += 1   
    return execute_cli_result

#v25 add ssh execute cli mode to forbid long command special handle 
def execute_command_via_cli_sendmode_expect_timeout_wait_list_ssh(spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times=2, is_debug=True):
    ###define private parameters
    execute_cli_result = spawn_child
    cli_num = 1
    ###v21
    for cli, send_mode, cli_expect, cli_timeout, cli_wait in cli_sendmode_expect_timeout_wait_list:
        if send_mode == 'sendline':
            spawn_child.sendline(cli)
        elif send_mode == 'sendcontrol':
            spawn_child.sendcontrol(cli)
        elif send_mode == 'send':
            spawn_child.send(cli)
        elif send_mode == 'sendnone':
            pass
        else:
            print 'Incorrect sendmode %s, please check' % send_mode
            spawn_child.close(force=True)
            return None
        if cli_expect == 'None':
            pass
        else:
            index = execute_cli_result.expect([pexpect.TIMEOUT, cli_expect, '--More--', 'More:', '-- More --'], timeout=cli_timeout)
            # ##v13 set private var for meet more status
            more_num = 0
            more_index = 1
            # ##
            if index == 0:
                print '''TimeOut when execute the %s CLI, fail in Execute CLI parter''' % cli_num
                print 'CLI is %s, Expect is %s, Timeout is %s' % (cli, cli_expect, cli_timeout)
                print 'before is %s' % (execute_cli_result.before)
                print 'after is %s' % (execute_cli_result.after)
                execute_cli_result.close(force=True)
                return None
            elif index == 1:
                debug('%s successfully executed' % cli, is_debug)
            elif index == 2:
                debug('''Meet 'more', should send 'blank' to continue, Aerohive products''', is_debug)
                while more_index == 1:
                    more_num += 1
                    # ##v13 add retry for status 'more'
                    cli_mode_tuple_list = [(' ', 'send')]
                    expect_list = [pexpect.TIMEOUT, '--More--', cli_expect]
                    retry_cli_mode_tuple_list = [[('', 'sendline')]] * cli_retry_times
                    more_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, cli_timeout, retry_cli_mode_tuple_list , cli_retry_times, execute_cli_result, is_debug)
                    more_result = more_info[0]
                    more_index = more_info[1]
                    #v29 if more_index == 0, raise timeout err, if == 1,continue while loop, if ==2, jump out of the loop 
                    if more_index == 0:
                        print 'Send blank to confirm show the left log timeout, please confirm the host is alive'
                        return None         
                debug('Meet more %s times' % more_num, is_debug)
                debug('The more index is %s, value is %s' % (more_index, expect_list[more_index]), is_debug)
                debug('Send enter to eat all blanks', is_debug)
                more_result.sendline("")
                index = more_result.expect([pexpect.TIMEOUT, cli_expect], cli_timeout)
                execute_cli_result = more_result 
            elif index == 3:
                debug('''Meet 'more', should send 'blank' to continue, Dell products''', is_debug)
                while more_index == 1:
                    execute_cli_result.send(' ')
                    more_index = execute_cli_result.expect([pexpect.TIMEOUT, 'More:', cli_expect], timeout=cli_timeout)
                    if more_index == 0:
                        print 'Send blank to confirm show the left log timeout, please confirm the host is alive'
                        execute_cli_result.close(force=True)
                        return None                
            elif index == 4:
                debug('''Meet 'more', should send 'blank' to continue, H3C products''', is_debug)
                while more_index == 1:
                    execute_cli_result.send(' ')
                    more_index = execute_cli_result.expect([pexpect.TIMEOUT, '-- More --', cli_expect], timeout=cli_timeout)
                    if more_index == 0:
                        print 'Send blank to confirm show the left log timeout, please confirm the host is alive'
                        execute_cli_result.close(force=True)
                        return None
            else:
                print '''Not match any expect in 'step cli execute' expect_list, please check'''
                print 'before is %s, after is %s' % (execute_cli_result.before, execute_cli_result.after)
                execute_cli_result.close(force=True)
                return None     
            debug('Sleep wait time %s to execute next cli' % cli_wait, is_debug)
            sleep(cli_wait)
            cli_num += 1   
    return execute_cli_result






def console_logout(spawn_child, logout_timeout=2, logout_retry_times=20, is_debug=True):
    console_logout_result = spawn_child
    debug('....................Free console port....................', is_debug)
    cli_mode_tuple_list = [('e', 'sendcontrol'), ('c.', 'send')]
    expect_list = [pexpect.TIMEOUT, 'disconnect']
    retry_cli_mode_tuple_list = [[('', 'sendline')]] + [[('e', 'sendcontrol'), ('c.', 'send')]] + [[('', 'sendline')]] * (logout_retry_times - 2)
    console_logout_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, logout_timeout, retry_cli_mode_tuple_list , logout_retry_times, console_logout_result, is_debug)
    console_logout_result = console_logout_info[0]
    console_logout_index = console_logout_info[1]
    if console_logout_index == 0:
        print '''TimeOut when send ctrl+ec. to to logout console prompt status'''
        print 'before is %s, after is %s' % (console_logout_result.before, console_logout_result.after)
        return None
    elif console_logout_index == 1:
        debug('Free console successfully', is_debug)
    else:
        print '''Not match any expect in 'logout' expect_list, please check'''
        print 'before is %s, after is %s' % (console_logout_result.before, console_logout_result.after)
        console_logout_result.close(force=True)
        return None                
    return console_logout_result



# ##define class, for logfile can be opened and closed automatic
class console_host:
    # ##v10 add wait time
    def __init__(self, ip, serialname, user, passwd, absolute_logfile='', prompt='[$#>]', wait_time=0, is_debug=False):
        self.ip = ip
        self.serialname = serialname
        self.user = user
        self.passwd = passwd
        self.is_debug = is_debug
        self.prompt = prompt
        self.absolute_logfile = absolute_logfile
        # ##v10 add wait time
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
            # ##close the mode a file firstly
            self.absolute_logfile_open.close()
            absolute_logfile = self.absolute_logfile
            
            with open(absolute_logfile, mode='r') as absolute_logfile_open:
                originate_logfile = absolute_logfile_open.read()
            # ##sub '--More--'
            correct_logfile = re.sub(' --More-- \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08          \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08', '', originate_logfile)
            # ##sub 28 blanks and \r
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

    # ##v11 modify timeout from 5 to 10 for low performance devices
    def logout(self, spawn_child, logout_timeout=10, logout_retry_times=5):
        is_debug = self.is_debug
        console_logout_result = console_logout(spawn_child, logout_timeout, logout_retry_times, is_debug)
        return console_logout_result


# ##def login-execute-logout func
def console_execute_cli(ip, user, passwd, serialname, cli_list, prompt, timeout, retry_times, logdir, logfile, is_debug, is_shell, shellpasswd, wait_time, bootpasswd):
    timeout = int(timeout)
    retry_times = int(retry_times)
    wait_time = float(wait_time)
    retry_times = int(retry_times)
    # ##set private var
    login_timeout = 2
    login_retry_times = retry_times
    cli_timeout = timeout
    cli_retry_times = 2
    logout_timeout = 2
    logout_retry_times = 10   
    # ##start login process
    absolute_logfile = logdir + '/' + logfile
    debug('logfile path is %s' % absolute_logfile, is_debug)
    console = console_host(ip, serialname, user, passwd, absolute_logfile, prompt, wait_time, is_debug)
    console_host_login = console.login(login_timeout, login_retry_times)
    ###v16 add waite time between login and execute cli
    debug('login successfully, wait %s to execute CLI' % wait_time, is_debug)
    sleep(wait_time)
    if console_host_login:
        ###v21
        cli_sendmode_expect_timeout_wait_list = generate_cli_sendmode_expect_timeout_wait_list(cli_list, prompt, cli_timeout, wait_time, passwd, shellpasswd, bootpasswd)
        debug('Cli_sendmode_expect_timeout_wait_list is as below: %s' % str(cli_sendmode_expect_timeout_wait_list), is_debug)                                   
        console_host_execute = console.execute_command_via_cli_sendmode_expect_timeout_wait_list(console_host_login, cli_sendmode_expect_timeout_wait_list, cli_retry_times)
    else:
        print 'Console login failed'
        return None
    if console_host_execute:
        console_host_logout = console.logout(console_host_execute, logout_timeout, logout_retry_times)
    else:
        print 'Console execute cli failed'
        return None        
    return console_host_logout


def str2list(string, is_debug=True):
    input_list = string.split(',')
    str_list = []
    for input_member in input_list:
        index1 = re.search(r'[\D+]', input_member)
        index2 = re.search(r'^\d+-\d+$', input_member)
        ###when index1 is None, match format'x'
        if index1 == None:
            str_list.append(int(input_member))
        ###If index1 is Not None(True), need check index2, index2 should be True, match 'x-x' 
        elif index1 and index2:
            input_member_range_list = re.findall(r'\d+', input_member)
            ###need switch to int() before calculate
            input_member_range = int(input_member_range_list[1]) - int(input_member_range_list[0])
            ###Judge if input_range is more than 0
            ######if equal to 0 add the member to the list 
            if input_member_range == 0:
                str_list.append(int(input_member_range_list[0]))
            ######if the range is >0 add the member in order
            elif input_member_range > 0:
                ###range() cannot cover the last one, so you need add 1 for the last
                for str_member in range(int(input_member_range_list[0]), int(input_member_range_list[1]) + 1):
                    ###primary mode is int, do not need switch 
                    str_list.append(int(str_member))
            else:
                print '''This parameter %s is not match format, the first member should less than the second ''' % input_member
                return None
        else:
            print '''This parameter %s is not match format, please enter correct format such as 'x,x,x' or 'x-x,x-x,x' ''' % input_member
            return None
    return str_list

parse = argparse.ArgumentParser(description='Console host to execute CLI')
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
#v26 start
parse.add_argument('-sp', '--shellpasswd', required=False, default='', dest='shellpasswd',
                    help='Shell password for enter to shell mode')
#v26 end
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
#v26 start
parse.add_argument('-loop', '--loop', required=False, default='1', dest='loop',
                    help='The loop times')
#v26 end

def main():
    args = parse.parse_args() 
    is_debug = args.is_debug
    ip = args.desip
    user = args.user
    passwd = args.passwd
    # ##process prompt: add \\ for $ and .* for the end, special process for '|'
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
    #v26 start
    loop = str2list(args.loop)
    #v26 end
    input_para_list = sys.argv
    debug('''Type command is "python %s"''' % (' '.join(input_para_list)), is_debug)
    #v26 start
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
    #v26 end
    execute_cli_list = generate_cli_list(execute_cli_list, config_file_path, input_para_list, is_debug)
    ###v18
#    debug('execute_cli_list is as below', is_debug)
#    debug(execute_cli_list, is_debug)
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
