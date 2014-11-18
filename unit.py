#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import re, time
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

'''
Sleep
'''
def sleep(mytime=1):
    time.sleep(mytime)

'''
Print log based on debug level
'''
def debug(msg, is_debug):
    if msg and is_debug:
            print '%s DEBUG' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg
            
def info(msg, is_info):
    if msg and is_info:
            print '%s INFO ' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg
            
def warn(msg, is_warn):
    if msg and is_warn:
            print '%s WARN ' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg
            
def error(msg, is_error):
    if msg and is_error:
            print '%s ERROR' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg

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
                str_list.append(str(j))
        else:
            str_list.append(str(i))
    return str_list
