import socket
import sys
import os
import string
import datetime, time

es_server = ""
trace_file = ""
host = socket.gethostname()

if "vbfs" in host:
    es_server = "20.0.8.93"
    trace_file = "/var/log/lwfs/etc-lwfs-lwfsd.vol.log"
if "gio" in host:
    es_server = "20.0.8.91"
    trace_file = "/var/log/lwfs/etc-lwfs-lwfsd.vol.log"
if "testhost" in host:
    es_server = "20.0.8.95"
    trace_file = "/var/log/lwfs/lwfs_testbed.log"

print host
print es_server
print trace_file

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((es_server, 9987))

#FLUSH_FREQUENCE = 10
FLUSH_FREQUENCE = 3600 * 24 * 10


def GetSendTrace():
    timer = 0
    f = open(trace_file, "r")
    line = f.readline()
    while True:
        line = f.readline()

        if not line:
            time.sleep(0.1)
            timer += 1
        elif "Trace" in line:
            #Remove the useless information, TODO use regex.
            line = line.replace("N [sw-threads.c:85:record_log]", "")
            line = line.replace("N [sw-threads.c:93:record_log]", "")
            line = line.replace("N [sw-threads.c:97:record_log]", "")
            s.send(line)
            #print line

        if timer == FLUSH_FREQUENCE:
            break

    f.close()


if __name__ == "__main__":

    while True:
        try:
            GetSendTrace()
        except Exception as e:
            print e
        os.popen("cat %s | grep -v Trace >> %s.bak" % (trace_file, trace_file))
        os.popen("echo \"\" > %s" % trace_file)
