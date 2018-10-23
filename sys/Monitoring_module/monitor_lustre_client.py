# -*- coding: utf-8 -*-
# Author: swstorage

import socket
import sys
import os
import string
import datetime, time
from optparse import OptionParser

parser = OptionParser()
parser.add_option(
    "-g",
    "--gio",
    default=True,
    action="store_true",
    help="collect I/O behabiors from online1",
    dest="gio")
parser.add_option(
    "-b",
    "--bio",
    default=False,
    action="store_true",
    help="collect I/O behaviors from online2",
    dest="bio")
#parser.add_option("-s", "--no_socket", default = False, action = "store_true", help = "samping and obtain results by stdout", dest = "no_socket")
parser.add_option(
    "-n",
    "--need_help",
    default=False,
    action="store_true",
    help="show detail information",
    dest="need_help")
(options, args) = parser.parse_args()


def collect_lustre_server_gio(cluster_ip, port):
    dir_osc = '/proc/fs/lustre/osc/'
    dir_cache = '/proc/fs/lustre/llite/'
    count = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((cluster_ip, port))
    mes = dict()
    pre_cache = ''
    first_time_flag = 1

    command = "ls /proc/fs/lustre/osc/ | wc -l"
    f1 = os.popen(command)
    ost_sum = int(f1.readline())
    if ost_sum > 500:
        exit()

    while (1):
        for filename in os.listdir(dir_osc):
            try:
                names = filename.split('-')
                if (len(names) == 4 and names[0] == "gswgfs"):
                    rpc_stats = dir_osc + filename + '/rpc_stats'
                    count = 0
                    ost_number = string.replace(names[1], "OST", "")
                    ####  refesh rpc stats  #####
                    file = open(rpc_stats, 'r')
                    lines = file.readlines()
                    for items in lines:
                        count += 1
                    s1 = []
                    if (count > 16):
                        line_number = 8
                        items = lines[line_number]
                        while ("read" not in items) and ("write" not in items):
                            item = items.split()
                            if ((line_number > 7) and (len(item) > 0)):
                                if ":" in item[0]:
                                    size = int(
                                        string.replace(item[0], ":", ""))
                                    s1.append(
                                        [size,
                                         int(item[1]),
                                         int(item[5])])
                            line_number += 1
                            items = lines[line_number]
                #####   send message to server #######
                    if (first_time_flag == 1):
                        mes[ost_number] = s1
                        message = ost_number + " " + str(s1)
                        s.send(message)
                        s.send("\n")
#                        print message
                    else:
                        if mes[ost_number] != s1:
                            mes[ost_number] = s1
                            message = ost_number + " " + str(s1)
                            s.send(message)
                            s.send("\n")
#                            print message
            except Exception as e:
                continue

        first_time_flag = 0
        for gs in os.listdir(dir_cache):
            try:
                if 'gswgfs' in str(gs):
                    c_file = dir_cache + gs + '/read_ahead_stats'
                    cachefile = open(c_file, 'r')
                    clines = cachefile.readlines()
                    if len(clines) < 5:
                        continue
                    discard_mes = 'discard 0'
                    for sam in clines:
                        if 'discarded' in sam:
                            discard_mes = "discard " + str(sam.split(' ')[-3])
                            break
                    cache_mes = "cache_hit " + str(
                        str(clines[1]).split(' ')[-3]) + " cache_miss " + str(
                            str(clines[2]).split(' ')[-3]) + " " + discard_mes
                    if cache_mes != pre_cache:
                        pre_cache = cache_mes
                        s.send(cache_mes)
                        s.send("\n")


#                        print cache_mes
            except Exception as e:
                continue
        time.sleep(2)
    s.close()


def collect_lustre_server_bio(cluster_ip, port):
    dir_osc = '/proc/fs/lustre/osc/'
    dir_cache = '/proc/fs/lustre/llite/'
    count = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((cluster_ip, port))
    mes = dict()
    pre_cache = ''
    first_time_flag = 1

    command = "ls /proc/fs/lustre/osc/ | wc -l"
    f1 = os.popen(command)
    ost_sum = int(f1.readline())
    if ost_sum > 500:
        exit()

    while (1):
        for filename in os.listdir(dir_osc):
            try:
                names = filename.split('-')
                if (len(names) == 4 and names[0] == "bswgfs"):
                    rpc_stats = dir_osc + filename + '/rpc_stats'
                    count = 0
                    ost_number = string.replace(names[1], "OST", "")
                    ####  refesh rpc stats  #####
                    file = open(rpc_stats, 'r')
                    lines = file.readlines()
                    for items in lines:
                        count += 1
                    s1 = []
                    if (count > 16):
                        line_number = 8
                        items = lines[line_number]
                        while ("read" not in items) and ("write" not in items):
                            item = items.split()
                            if ((line_number > 7) and (len(item) > 0)):
                                if ":" in item[0]:
                                    size = int(
                                        string.replace(item[0], ":", ""))
                                    s1.append(
                                        [size,
                                         int(item[1]),
                                         int(item[5])])
                            line_number += 1
                            items = lines[line_number]
                #####   send message to server #######
                    if (first_time_flag == 1):
                        mes[ost_number] = s1
                        message = ost_number + " " + str(s1)
                        s.send(message)
                        s.send("\n")
#                        print message
                    else:
                        if mes[ost_number] != s1:
                            mes[ost_number] = s1
                            message = ost_number + " " + str(s1)
                            s.send(message)
                            s.send("\n")
#                            print message
            except Exception as e:
                continue

        first_time_flag = 0
        for gs in os.listdir(dir_cache):
            try:
                if 'bswgfs' in str(gs):
                    c_file = dir_cache + gs + '/read_ahead_stats'
                    cachefile = open(c_file, 'r')
                    clines = cachefile.readlines()
                    if len(clines) < 5:
                        continue
                    discard_mes = 'discard 0'
                    for sam in clines:
                        if 'discarded' in sam:
                            discard_mes = "discard " + str(sam.split(' ')[-3])
                            break
                    cache_mes = "cache_hit " + str(
                        str(clines[1]).split(' ')[-3]) + " cache_miss " + str(
                            str(clines[2]).split(' ')[-3]) + " " + discard_mes
                    if cache_mes != pre_cache:
                        pre_cache = cache_mes
                        s.send(cache_mes)
                        s.send("\n")


#                        print cache_mes
            except Exception as e:
                continue
        time.sleep(2)
    s.close()

if __name__ == "__main__":
    if options.need_help == True:
        print "-g collect I/O behabiors from online1"
        print "-b collect I/O behabiors from online2"
        print "-n help information"
    elif options.bio == True:
        cluster_ip = '20.0.8.89'
        port = 9987
        collect_lustre_server_bio(cluster_ip, port)
    else:
        print "gio"
        cluster_ip = '20.0.8.87'
        port = 9987
        collect_lustre_server_gio(cluster_ip, port)
