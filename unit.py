#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import pexpect, sys, re, time
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

'''
Sleep
'''
def sleep(mytime=1):
    time.sleep(mytime)

'''
Print log to stdout
'''
def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print '%s DEBUG' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
        print mesage

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
    str_list=[]
    for i in i_list:
        if ran_reg.search(i):
            ran_start=int(i.split('-')[0])
            ran_end=int(i.split('-')[-1])
            for j in range(ran_start,ran_end+1):
                str_list.append(j)
        else:
            str_list.append(i)
    return str_list
