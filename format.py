#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import pexpect, sys, re, time
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

def generate_cli_sendmode_expect_timeout_wait_list(cli_list, prompt, timeout, wait, passwd='', shellpasswd='', bootpasswd=''):
    ###define private parameters
    cli_sendmode_expect_timeout_wait_list = [] 
    reboot_timeout = 300
    save_img_timeout = 1200
    sendmode = 'sendline'
    log_regex = re.compile('^show log.*')
    reset_config_regex = re.compile('^reset config$')
    reset_boot_regex = re.compile('^reset config bootstrap$')
    reboot_regex = re.compile('^reboot$|^reboot backup$|^reboot current$|reboot offset')
    save_config_regex = re.compile('^save config tftp:.* (current|bootstrap)')
    save_image_regex = re.compile('^save image tftp:.*img')
    save_image_reboot_regex = re.compile('^save image tftp:.*now$')
    shell_regex = re.compile('^_shell$')
    exit_regex = re.compile('^exit$')
    enble_regex = re.compile('^enable$')
    country_regex = re.compile('^boot-param country-code.*')
    ctrl_regex = re.compile('ctrl-.*')
    reset_regex = re.compile('^reset$')
    quit_regex = re.compile('^quit$')
    scp_vpn_regex = re.compile('^save vpn.*scp.*')
    scp_img_regex = re.compile('^save image scp.*')
    scp_toconfig_regex = re.compile('^save config (current|bootstrap) scp.*')
    scp_fromconfig_regex = re.compile('^save config scp.* (current|bootstrap)')
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
                cli_sendmode_expect_timeout_wait_list.append(('', sendmode, 'Hit.*to stop.*autoboot.*2.*', timeout, wait))
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
            if shellpasswd:
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '[Pp]assword|%s' % prompt, timeout, wait))
                cli_sendmode_expect_timeout_wait_list.append((shellpasswd, sendmode, prompt, timeout, wait))
            else:
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, prompt, timeout, wait))
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
            cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '%s|login:.*' % prompt, timeout, wait))
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

def execute_command_via_cli_sendmode_expect_timeout_wait_list(spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times=2, is_debug=True):
    execute_cli_result = spawn_child
    cli_num = 1
    for cli, send_mode, cli_expect, cli_timeout, cli_wait in cli_sendmode_expect_timeout_wait_list:
        send_command(cli, execute_cli_result, send_mode, is_debug)
        if cli_expect == 'None':
            pass
        else:
            index = execute_cli_result.expect([pexpect.TIMEOUT, cli_expect, '--More--', 'More:', '-- More --'], timeout=cli_timeout)
            more_num = 0
            more_index = 1
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
                    cli_mode_tuple_list = [(' ', 'send')]
                    expect_list = [pexpect.TIMEOUT, '--More--', cli_expect]
                    retry_cli_mode_tuple_list = [[('', 'sendline')]] * cli_retry_times
                    more_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, cli_timeout, retry_cli_mode_tuple_list , cli_retry_times, execute_cli_result, is_debug)
                    more_result = more_info[0]
                    more_index = more_info[1]
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

def execute_command_via_cli_sendmode_expect_timeout_wait_list_ssh(spawn_child, cli_sendmode_expect_timeout_wait_list, cli_retry_times=2, is_debug=True):
    execute_cli_result = spawn_child
    cli_num = 1
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
            more_num = 0
            more_index = 1
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
                    cli_mode_tuple_list = [(' ', 'send')]
                    expect_list = [pexpect.TIMEOUT, '--More--', cli_expect]
                    retry_cli_mode_tuple_list = [[('', 'sendline')]] * cli_retry_times
                    more_info = spawn_timeout_retry(cli_mode_tuple_list, expect_list, cli_timeout, retry_cli_mode_tuple_list , cli_retry_times, execute_cli_result, is_debug)
                    more_result = more_info[0]
                    more_index = more_info[1]
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
