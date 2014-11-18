﻿#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import pexpect, sys, re, time
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

def sleep(mytime=1):
    time.sleep(mytime)

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
    
    
#    for input_member in input_list:
#        index1 = re.search(r'[\D+]', input_member)
#        index2 = re.search(r'^\d+-\d+$', input_member)
#        if index1 == None:
#            str_list.append(int(input_member))
#        elif index1 and index2:
#            input_member_range_list = re.findall(r'\d+', input_member)
#            input_member_range = int(input_member_range_list[1]) - int(input_member_range_list[0])
#            if input_member_range == 0:
#                str_list.append(int(input_member_range_list[0]))
#            elif input_member_range > 0:
#                for str_member in range(int(input_member_range_list[0]), int(input_member_range_list[1]) + 1):
#                    str_list.append(int(str_member))
#            else:
#                print '''This parameter %s is not match format, the first member should less than the second ''' % input_member
#                return None
#        else:
#            print '''This parameter %s is not match format, please enter correct format such as 'x,x,x' or 'x-x,x-x,x' ''' % input_member
#            return None
#    return str_list