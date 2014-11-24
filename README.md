AerohiveExpect
==============
This lib is based on pexpect, so it can be used on linux server only. Be careful!
For example:
SSH target(10.68.101.103) execute cmds(show run)
root@Linux227:/home/will/git/AerohiveExpect# python connect.py -i '10.68.101.103' -c 'show run' --debug info
2014-11-24 07:59:37 INFO  Expect Args
Mode         = ssh
IP           = 10.68.101.103
Port         = 22
User         = admin
Passwd       = aerohive
Prompt       = AH.*#|~ #
Timeout      = 10
Log_file     = stdout
CLI          = show run
Config_file  = False
Wait         = 0
Retry        = 5
Shell_passwd = 
Debug_level  = info
2014-11-24 07:59:37 INFO  [LOGIN-SSH]Send cli to login target
2014-11-24 07:59:37 INFO  [CLI]spawn child not exist, create spawn firstly
2014-11-24 07:59:40 INFO  [CLI]Match expect, no retry
2014-11-24 07:59:40 INFO  [LOGIN-SSH]From 'SSH CMD' jump to is_passwd
2014-11-24 07:59:40 INFO  [LOGIN-PASSWD]Meet passwd,send passwd to confirm login
2014-11-24 07:59:40 INFO  [CLI]spawn child exist, send cli directly

Last login: Mon Nov 24 15:59:02 2014 from 10.68.100.227
Aerohive Networks Inc.
Copyright (C) 2006-2014
AH-8c97c0#2014-11-24 07:59:41 INFO  [CLI]Match expect, no retry
2014-11-24 07:59:41 INFO  [LOGIN-PASSWD]From is_passwd jump to is_prompt process 
2014-11-24 07:59:41 INFO  [LOGIN-PROMPT]Meet prompt, can execute cli now
show run
security mac-filter Aerohive default permit
hive Aerohive
hive Aerohive security mac-filter Aerohive
hive Aerohive password ***
interface eth0 manage telnet
interface eth0 manage snmp
interface wifi1 mode access
interface mgt0 hive Aerohive
lldp 
dns server-ip 208.67.222.222 
dns server-ip 208.67.220.220 second
ntp server ntp1.aerohive.com 
clock time-zone 8 
no reset-button reset-config-enable
config version 2 
config rollback enable
capwap client server name 10.155.39.201 
capwap client dtls hm-defined-passphrase *** key-id 1
capwap client vhm-name home
no capwap client dtls negotiation enable
alg http enable
bonjour-gateway vlan 1 4094
 --More-- 2014-11-24 07:59:41 INFO  [CLI]Meet 'more', should send 'blank' to continue, Aerohive products
2014-11-24 07:59:41 INFO  [CLI]spawn child exist, send cli directly
application reporting auto
AH-8c97c0#2014-11-24 07:59:41 INFO  [CLI]Match expect, no retry

AH-8c97c0#2014-11-24 07:59:41 INFO  [LOGOUT]SSH Logout Process
2014-11-24 07:59:41 INFO  [CLI]spawn child exist, send cli directly

Connection to 10.68.101.103 closed.
2014-11-24 07:59:41 INFO  [CLI]Match expect, no retry
2014-11-24 07:59:41 INFO  [LOGOUT]SSH Logout successfully
root@Linux227:/home/will/git/AerohiveExpect# 


Telnet target(10.68.101.103) execute cmds(show run)

root@Linux227:/home/will/git/AerohiveExpect# python connect.py -m telnet -i 10.68.101.103 -c "show run" --debug info
2014-11-24 08:16:09 INFO  Expect Args
Mode         = telnet
IP           = 10.68.101.103
Port         = 23
User         = admin
Passwd       = aerohive
Prompt       = AH.*#|~ #
Timeout      = 10
Log_file     = stdout
CLI          = show run
Config_file  = False
Wait         = 0
Retry        = 5
Shell_passwd = 
Debug_level  = info
2014-11-24 08:16:09 INFO  [LOGIN-TELNET]Send cli to login target
2014-11-24 08:16:09 INFO  [CLI]spawn child not exist, create spawn firstly
2014-11-24 08:16:09 INFO  [CLI]Match expect, no retry
2014-11-24 08:16:09 INFO  [LOGIN-TELNET]Send 'TELNET CMD' successfully, meet Escape
2014-11-24 08:16:09 INFO  [CLI]spawn child exist, send cli directly



Welcome to Aerohive Product

login: 2014-11-24 08:16:09 INFO  [CLI]Match expect, no retry
2014-11-24 08:16:09 INFO  [LOGIN-TELNET]From 'Enter' jump to is_user
2014-11-24 08:16:09 INFO  [LOGIN-USER]Meet user,send user to confirm login
2014-11-24 08:16:09 INFO  [CLI]spawn child exist, send cli directly

login: admin
Password: 2014-11-24 08:16:09 INFO  [CLI]Match expect, no retry
2014-11-24 08:16:09 INFO  [LOGIN-USER]From is_user jump to is_passwd
2014-11-24 08:16:09 INFO  [LOGIN-PASSWD]Meet passwd,send passwd to confirm login
2014-11-24 08:16:09 INFO  [CLI]spawn child exist, send cli directly

Aerohive Networks Inc.
Copyright (C) 2006-2014
AH-8c97c0#2014-11-24 08:16:09 INFO  [CLI]Match expect, no retry
2014-11-24 08:16:09 INFO  [LOGIN-PASSWD]From is_passwd jump to is_prompt process 
2014-11-24 08:16:09 INFO  [LOGIN-PROMPT]Meet prompt, can execute cli now
show run
security mac-filter Aerohive default permit
hive Aerohive
hive Aerohive security mac-filter Aerohive
hive Aerohive password ***
interface eth0 manage telnet
interface eth0 manage snmp
interface wifi1 mode access
interface mgt0 hive Aerohive
lldp 
dns server-ip 208.67.222.222 
dns server-ip 208.67.220.220 second
ntp server ntp1.aerohive.com 
clock time-zone 8 
no reset-button reset-config-enable
config version 2 
config rollback enable
capwap client server name 10.155.39.201 
capwap client dtls hm-defined-passphrase *** key-id 1
capwap client vhm-name home
no capwap client dtls negotiation enable
alg http enable
bonjour-gateway vlan 1 4094
 --More-- 2014-11-24 08:16:09 INFO  [CLI]Meet 'more', should send 'blank' to continue, Aerohive products
2014-11-24 08:16:09 INFO  [CLI]spawn child exist, send cli directly
application reporting auto
AH-8c97c0#2014-11-24 08:16:09 INFO  [CLI]Match expect, no retry

AH-8c97c0#2014-11-24 08:16:09 INFO  [LOGOUT]TELNET Logout Process
2014-11-24 08:16:09 INFO  [CLI]spawn child exist, send cli directly

telnet> 2014-11-24 08:16:10 INFO  [CLI]Match expect, no retry
2014-11-24 08:16:10 INFO  [CLI]spawn child exist, send cli directly
q
Connection closed.
2014-11-24 08:16:10 INFO  [CLI]Match expect, no retry
2014-11-24 08:16:10 INFO  [LOGOUT]TELNET Logout successfully
root@Linux227:/home/will/git/AerohiveExpect# 


