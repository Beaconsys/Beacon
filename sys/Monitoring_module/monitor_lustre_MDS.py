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
parser.add_option(
    "-n",
    "--need_help",
    default=False,
    action="store_true",
    help="show detail information",
    dest="need_help")
(options, args) = parser.parse_args()

time_sleep=1

def collect_lustre_mds_gio(cluster_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((cluster_ip, port))
    dir = '/proc/fs/lustre/mdt/gswgfs-MDT0000/exports/'
    mes = [0 for i in range(500)]
    while (1):
        count = 0
        for filename in os.listdir(dir):
            if 'o2ib' in filename:
                dest = filename.split('@')[0]
                mdstats = dir + filename + '/stats'
                file = open(mdstats, 'r')
                message = dest
                lines = file.readlines()
                for i in range(1, len(lines)):
                    sre = lines[i]
                    str = sre.split()
                    message = message + " " + str[0] + " " + str[1]
                if message <> mes[count]:
                    mes[count] = message
                    s.send(message)
                    s.send("\n")
                count = count + 1
                file.close()
        time.sleep(time_sleep)
    s.close()


def collect_lustre_mds_bio(cluster_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((cluster_ip, port))
    dir = '/proc/fs/lustre/mdt/bswgfs-MDT0000/exports/'
    mes = [0 for i in range(500)]
    while (1):
        count = 0
        for filename in os.listdir(dir):
            if 'o2ib' in filename:
                dest = filename.split('@')[0]
                mdstats = dir + filename + '/stats'
                file = open(mdstats, 'r')
                message = dest
                lines = file.readlines()
                for i in range(1, len(lines)):
                    sre = lines[i]
                    str = sre.split()
                    message = message + " " + str[0] + " " + str[1]
                if message <> mes[count]:
                    mes[count] = message
                    s.send(message)
                    s.send("\n")
                count = count + 1
                file.close()
        time.sleep(time_sleep)
    s.close()


if __name__ == "__main__":
    filesys1_host = ""
    filesys2_host = ""
    filesys1_port = null
    filesys2_port = null
    if options.need_help == True:
        print "-g collect I/O behabiors from online1"
        print "-b collect I/O behabiors from online2"
        print "-n help information"
    elif options.bio == True:
        cluster_ip = filesys2_host
        port = filesys2_port
        collect_lustre_MDS_bio(cluster_ip, port)
    else:
        cluster_ip = filesys1_host
        port = filesys1_port
        collect_lustre_MDS_gio(cluster_ip, port)
