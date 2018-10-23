# -*- coding: utf-8 -*-
import MySQLdb
import datetime
import time
import MySQLdb.cursors
import math
import numpy as np
import sys
from readCABID import output_cabid_gio
from readCABID import output_gio_cabid
import csv

result_file_name = "cabid_job/cabid_"
data_file_name = "cabid_job/data_tmp.csv"
#search_cabid = [Cabid to FwdID]
SQL_host = ""
SQL_user = ""
SQL_db = ""
SQL_passwd = ""
SQL_port = ""


def save_results(result_file_name, data):
    result_file = file(result_file_name, 'wb')
    writer = csv.writer(result_file)
    writer.writerow(['Program_name', 'JobID', 'Runtime', 'Cabid', 'FwdID'])
    writer.writerows(data)


def get_re(time1, time2):
    conn = MySQLdb.connect(
        host=SQL_host,
        user=SQL_user,
        db=SQL_db,
        passwd=SQL_passwd,
        port=SQL_port)
    print 'connect succeed'
    try:
        cursor = conn.cursor()
        item1 = "STARTTIME < '" + time2 + "' and ENDTIME >= '" + time2 + "'"
        item2 = "ENDTIME > '" + time1 + "' and ENDTIME < '" + time2 + "'"
        item3 = "ENDTIME = '0000-00-00 00:00:00' and STARTTIME < '" + time2 + "'"
        ite = "NODELIST <> '-' and RUNTIME <> 0 and CORE<> 0"
        ite1 = "QUEUE not like '%x86%'"
        sql1 = (
            'select PROGRAM_NAME,NODELIST,RUNTIME,JOBID,STARTTIME,ENDTIME from JOB_log_all where '
            + ite + ' and ' + ite1 + ' and ' + '( ' + item1 + ' or ' + item2 +
            ' or ' + item3 + ' ) order by PROGRAM_NAME')
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        re = []
        program_name = []
        nodelist = []
        runtime = []
        jobid = []
        start_time = []
        end_time = []

        for data in result1:
            program_name.append(data[0])
            nodelist.append(data[1])
            runtime.append(data[2])
            jobid.append(data[3])
            try:
                start_time.append((data[4]).strftime('%Y-%m-%d %H:%M:%S'))
            except Exception as e:
                print e
                start_time.append('0000-00-00 00:00:00')

            try:
                end_time.append((data[5]).strftime('%Y-%m-%d %H:%M:%S'))
            except Exception as e:
                print e
                end_time.append('0000-00-00 00:00:00')
            re.append(data)

        data_tmp = []
        for i in range(len(program_name)):
            data_tmp.append([jobid[i], program_name[i], nodelist[i], runtime[i], \
            start_time[i], end_time[i]])
        save_results(data_file_name, data_tmp)

        re.sort()
        if len(re) < 1:
            print 'NONE'
        else:
            val = re[0]
            node = val[1]
            node = node.split(',')
            cabid = set()
            name_cabid = dict()
            name_time = dict()
            name_jobid = dict()
            for x in node:
                r = x.split('-')
                if len(r) == 2:
                    for i in range(int(r[0]) // 1024, int(r[1]) // 1024 + 1):
                        cabid.add(i)

                elif len(r) == 1:
                    cabid.add(int(r[0]) // 1024)
                else:
                    print 'nodelist err1: ', x

            name_cabid[val[3]] = cabid
            name_time[val[3]] = val[2]
            name_jobid[val[3]] = val[0]
            #            name_cabid[val[0]] = cabid
            #            name_time[val[0]] = val[2]
            #            name_jobid[val[0]] = val[3]
            print len(re)
            for i in range(1, len(re)):
                val = re[i]
                node = val[1]
                node = node.split(',')
                cabid = set()
                for x in node:
                    r = x.split('-')
                    if len(r) == 2:
                        for i in range(
                                int(r[0]) // 1024,
                                int(r[1]) // 1024 + 1):
                            cabid.add(i)

                    elif len(r) == 1:
                        cabid.add(int(r[0]) // 1024)
                    else:
                        print 'nodelist err2: ', x

                flag = False
                for key in name_cabid.keys():
                    if val[3] == key:
                        #                    if val[0] == key:
                        flag = True
                        break


#                if flag == True:
#                    name_cabid[val[0]] = name_cabid[val[0]] | cabid
#                    name_time[val[0]] += val[2]
#                    name_jobid[val[0]] = name_jobid[val[0]] + ',' + val[3]
#                else:
#                    name_cabid[val[0]] = cabid
#                    name_time[val[0]] = val[2]
#                    name_jobid[val[0]] = val[3]

                if flag == True:
                    name_cabid[val[3]] = name_cabid[val[3]] | cabid
                    name_time[val[3]] += val[2]
                    name_jobid[val[3]] = name_jobid[val[3]] + ',' + val[0]
                else:
                    name_cabid[val[3]] = cabid
                    name_time[val[3]] = val[2]
                    name_jobid[val[3]] = val[0]
            result = []
            for key in name_cabid.keys():
                gio = []
                for va in name_cabid[key]:
                    if va > 49:
                        gio = ['vbfs']
                        break
                    else:
                        for xa in output_cabid_gio(va):
                            gio.append(int(xa))

                gio.sort()
                result.append([
                    key, name_jobid[key], name_time[key], name_cabid[key], gio
                ])

            result.sort()
        conn.commit()
        cursor.close()
    except Exception as e:
        print e
        conn.rollback()

    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'please input time1 to time2 e.g:2017-09-02 12:30:00 2017-09-02 14:30:00'
        sys.exit()
    time1 = sys.argv[1] + ' ' + sys.argv[2]
    time2 = sys.argv[3] + ' ' + sys.argv[4]
    result = get_re(time1, time2)
    result_file_name += time1 + "-" + time2 + "all.csv"
    save_results(result_file_name, result)
