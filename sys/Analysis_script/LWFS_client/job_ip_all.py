import MySQLdb
import datetime, time
import MySQLdb.cursors
import math
import numpy as np
import sys
import re


def findjob(time1, time2):  #RUNTIME cover time1 and time2
    conn = MySQLdb.connect(
        host='20.0.2.12', user='swqh', db='JOB', passwd='', port=3306)
    print 'connect succeed'
    try:
        cursor = conn.cursor()
        item1 = "STARTTIME <= '" + time1 + "' and ENDTIME >= '" + time2 + "'"
        item2 = "ENDTIME = '0000-00-00 00:00:00'" + " and STARTTIME <= '" + time1 + "'"
        ite = "NODELIST <> '-' and RUNTIME <> 0"
        ite1 = "QUEUE not like '%x86%'"
        sql1 = "select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,CORE,NODELIST from JOB_log_all where " + ite + " and " + ite1 + " and ( " + item1 + " or " + item2 + " ) order by PROGRAM_NAME"
        #sql1="select JOBID,USER,STATE,QUEUE,CNC,STARTTIME,ENDTIME,RUNTIME,PROGRAM_NAME,NODELIST from JOB_log where "+ite+" and "+item3+" order by PROGRAM_NAME"
        #print sql1
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        re = []
        for date in result1:
            re.append(date)
        re.sort()
        resu = []
        if len(re) < 1:
            print "NONE"
        else:
            for val in re:
                id = val[0]
                jname = val[1]
                pname = val[2]
                stime = str(val[3])
                etime = str(val[4])
                atime = val[5]
                cnc = val[6]
                core = val[7]
                node = val[8]
                node = node.split(",")
                resu.append(
                    [id, jname, pname, stime, etime, atime, cnc, core, node])
    except Exception as e:
        print e
        conn.rollback()
    return resu


def searchjob(time1, time2):  #ENDTIME between time1 and time2
    conn = MySQLdb.connect(
        host='20.0.2.12', user='swqh', db='JOB', passwd='', port=3306)
    print 'connect succeed'
    try:
        cursor = conn.cursor()
        item1 = "STARTTIME <= '" + time2 + "' and ENDTIME > '" + time2 + "'"
        item2 = "ENDTIME > '" + time1 + "' and ENDTIME <= '" + time2 + "'"
        item3 = "ENDTIME = '0000-00-00 00:00:00'" + " and STARTTIME < '" + time2 + "'"
        ite = "NODELIST <> '-' and RUNTIME <> 0"
        ite1 = "QUEUE not like '%x86%'"
        sql1 = "select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,CORE,NODELIST from JOB_log_all where " + ite + " and " + ite1 + " and " + item2 + " order by PROGRAM_NAME"
        #sql1="select JOBID,USER,STATE,QUEUE,CNC,STARTTIME,ENDTIME,RUNTIME,PROGRAM_NAME,NODELIST from JOB_log where "+ite+" and "+item3+" order by PROGRAM_NAME"
        #print sql1
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        re = []
        for date in result1:
            re.append(date)
        re.sort()
        resu = []
        if len(re) < 1:
            print "NONE"
        else:
            for val in re:
                id = val[0]
                jname = val[1]
                pname = val[2]
                stime = str(val[3])
                etime = str(val[4])
                atime = val[5]
                cnc = val[6]
                core = val[7]
                node = val[8]
                node = node.split(",")
                resu.append(
                    [id, jname, pname, stime, etime, atime, cnc, core, node])
    except Exception as e:
        print e
        conn.rollback()
    return resu


def get_re(time1, time2):  #Run time between time1 and time2
    conn = MySQLdb.connect(
        host='20.0.2.15', user='swqh', db='JOB', passwd='123456', port=3306)
    print 'connect succeed'
    try:
        cursor = conn.cursor()
        item1 = "STARTTIME <= '" + time2 + "' and ENDTIME > '" + time2 + "'"
        item2 = "ENDTIME > '" + time1 + "' and ENDTIME <= '" + time2 + "'"
        item3 = "ENDTIME = '0000-00-00 00:00:00'" + " and STARTTIME < '" + time2 + "'"
        ite = "NODELIST <> '-' and RUNTIME <> 0 and CORE<>0"
        ite1 = "QUEUE not like '%x86%'"
        sql1 = "select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,CORE,NODELIST from JOB_log_all where " + ite + " and " + ite1 + " and " + "( " + item1 + " or " + item2 + " or " + item3 + " ) order by PROGRAM_NAME"
        #sql1="select JOBID,USER,STATE,QUEUE,CNC,STARTTIME,ENDTIME,RUNTIME,PROGRAM_NAME,NODELIST from JOB_log where "+ite+" and "+item3+" order by PROGRAM_NAME"
        #print sql1
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        re = []
        for date in result1:
            re.append(date)
        resu = []
        if len(re) < 1:
            print "NONE"
        else:
            for val in re:
                id = val[0]
                jname = val[1]
                pname = val[2]
                stime = str(val[3])
                etime = str(val[4])
                atime = val[5]
                cnc = val[6]
                core = val[7]
                node = val[8]
                node = node.split(",")
                resu.append(
                    [id, jname, pname, stime, etime, atime, cnc, core, node])
    except Exception as e:
        print e
    conn.rollback()
    return resu


def get_re_jobid(jobid):
    conn = MySQLdb.connect(
        host='20.0.2.15', user='swqh', db='JOB', passwd='123456', port=3306)
    print 'connect succeed'
    resu = []
    #    print "shshshhhhhhhhhhhhhhhhhhhhhhhhhhh"
    try:
        cursor = conn.cursor()
        if int(jobid) <= 10000000:
            database = "JOB_log_all"
        elif int(jobid) <= 40500000:
            database = "JOB_log_4050"
        elif int(jobid) <= 41000000:
            database = "JOB_log_4100"
        elif int(jobid) <= 41500000:
            database = "JOB_log_4150"
        elif int(jobid) <= 42000000:
            database = "JOB_log_4200"
        else:
            database = "JOB_log"


#Modified by tyzhang. To maintain all the trace in mysql.
        sql1 = "select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,CORE,NODELIST from " + database + " where jobid=" + str(
            jobid) + " and RUNTIME<>0 order by PROGRAM_NAME"
        #sql1="select JOBID,USER,STATE,QUEUE,CNC,STARTTIME,ENDTIME,RUNTIME,PROGRAM_NAME,NODELIST from JOB_log where "+ite+" and "+item3+" order by PROGRAM_NAME"
        #print sql1
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        #print result1
        re = []
        for date in result1:
            re.append(date)
        re.sort()
        #print re
        if len(re) < 1:
            print "NONE"
        else:
            for val in re:
                id = val[0]
                jname = val[1]
                pname = val[2]
                stime = str(val[3])
                etime = str(val[4])
                atime = val[5]
                cnc = val[6]
                core = val[7]
                node = val[8]
                node = node.split(",")
                resu.append(
                    [id, jname, pname, stime, etime, atime, cnc, core, node])
    except Exception as e:
        print e
        conn.rollback()
    return resu


def get_cnc_only(jobid):
    conn = MySQLdb.connect(
        host='20.0.2.15', user='swqh', db='JOB', passwd='123456', port=3306)
    print 'connect succeed'
    resu = []
    #    print "shshshhhhhhhhhhhhhhhhhhhhhhhhhhh"
    try:
        cursor = conn.cursor()
        if int(jobid) <= 10000000:
            database = "JOB_log_all"
        elif int(jobid) <= 40500000:
            database = "JOB_log_4050"
        elif int(jobid) <= 41000000:
            database = "JOB_log_4100"
        else:
            database = "JOB_log"


#Modified by tyzhang. To maintain all the trace in mysql.
        sql1 = "select CNC from " + database + " where jobid=" + str(
            jobid) + " and RUNTIME<>0 order by PROGRAM_NAME"
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        print result1[0][2:-3]
        conn.commit()
        cursor.close()
        print result1
    except Exception as e:
        print e
        conn.rollback()
    return resu


def get_re_jobid_corehour(jobid):
    conn = MySQLdb.connect(
        host='20.0.2.15', user='swqh', db='JOB', passwd='123456', port=3306)
    print 'connect succeed'
    resu = []
    #    print "shshshhhhhhhhhhhhhhhhhhhhhhhhhhh"
    try:
        cursor = conn.cursor()
        if int(jobid) <= 10000000:
            database = "JOB_log_all"
        elif int(jobid) <= 40500000:
            database = "JOB_log_4050"
        else:
            database = "JOB_log"
        print database
        #Modified by tyzhang. To maintain all the trace in mysql.
        sql1 = "select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,COREHOUR,NODELIST from " + database + " where jobid=" + str(
            jobid) + " and RUNTIME<>0 order by PROGRAM_NAME"
        #sql1="select JOBID,USER,STATE,QUEUE,CNC,STARTTIME,ENDTIME,RUNTIME,PROGRAM_NAME,NODELIST from JOB_log where "+ite+" and "+item3+" order by PROGRAM_NAME"
        #print sql1
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        #print result1
        re = []
        for date in result1:
            re.append(date)
        re.sort()
        if len(re) < 1:
            print "NONE"
        else:
            for val in re:
                id = val[0]
                jname = val[1]
                pname = val[2]
                stime = str(val[3])
                etime = str(val[4])
                atime = val[5]
                cnc = val[6]
                corehour = val[7]
                node = val[8]
                node = node.split(",")
                resu.append([
                    id, jname, pname, stime, etime, atime, cnc, corehour, node
                ])
    except Exception as e:
        print e
        conn.rollback()
    print resu
    return resu


def get_re_jobid_CNC_runtime_corehour(jobid):
    conn = MySQLdb.connect(
        host='20.0.2.15', user='swqh', db='JOB', passwd='123456', port=3306)
    print 'connect succeed'
    resu = []
    #    print "shshshhhhhhhhhhhhhhhhhhhhhhhhhhh"
    try:
        cursor = conn.cursor()
        if int(jobid) <= 10000000:
            database = "JOB_log_all"
        elif int(jobid) <= 40500000:
            database = "JOB_log_4050"
        elif int(jobid) <= 41000000:
            database = "JOB_log_4100"
        elif int(jobid) <= 41500000:
            database = "JOB_log_4150"
        elif int(jobid) <= 42000000:
            database = "JOB_log_4200"
        else:
            database = "JOB_log"


#Modified by tyzhang. To maintain all the trace in mysql.
        sql1 = "select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,CNC,RUNTIME,COREHOUR,NODELIST from " + database + " where jobid=" + str(
            jobid) + " and RUNTIME<>0 order by PROGRAM_NAME"
        #sql1="select JOBID,USER,STATE,QUEUE,CNC,STARTTIME,ENDTIME,RUNTIME,PROGRAM_NAME,NODELIST from JOB_log where "+ite+" and "+item3+" order by PROGRAM_NAME"
        #print sql1
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        #print result1
        re = []
        for date in result1:
            re.append(date)
        re.sort()
        #print re
        if len(re) < 1:
            print "NONE"
        else:
            for val in re:
                id = val[0]
                jname = val[1]
                pname = val[2]
                stime = str(val[3])
                etime = str(val[4])
                cnc = val[5]
                runtime = val[6]
                corehour = val[7]
                node = val[8]
                node = node.split(",")
                resu.append([
                    id, jname, pname, stime, etime, cnc, runtime, corehour,
                    node
                ])
    except Exception as e:
        print e
        conn.rollback()
    return resu

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "please input time1 to time2 e.g:2016-07-19 12:30:00 2016-07-19 14:30:00"
        sys.exit()
    time1 = sys.argv[1] + " " + sys.argv[2]
    time2 = sys.argv[3] + " " + sys.argv[4]
    #jobid=sys.argv[5]
    results = get_re(time1, time2)
    #results=get_re_jobid(jobid)
    for i in results:
        print i
