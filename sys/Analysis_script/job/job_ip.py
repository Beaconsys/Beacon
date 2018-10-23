import MySQLdb
import datetime,time
import MySQLdb.cursors
import matplotlib.pyplot as plt
import math
import numpy as np
import sys

SQL_host = ""
SQL_user = ""
SQL_db = ""
SQL_passwd = ""
SQL_port = ""

def findjob(time1, time2):  #RUNTIME cover time1 and time2
    conn = MySQLdb.connect(host=SQL_host, user=SQL_user, db=SQL_db, passwd=SQL_passwd, port=SQL_port)
    print "connect succeed"
    try:
        cursor = conn.cursor()
        item1 = "STARTTIME <= '" + time1 + "' and ENDTIME >= '" + time2 + "'"
        item2 = "ENDTIME = '0000-00-00 00:00:00'" + " and STARTTIME <= '" + time1 + "'"
        ite = "NODELIST <> '-' and RUNTIME <> 0"
        ite1 = "QUEUE not like '%x86%'"
        sql1 = ("select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,CORE,NODELIST from JOB_log_all where " 
                + ite + " and " + ite1 + " and ( " + item1 + " or " + item2 + " ) order by PROGRAM_NAME")
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
                resu.append([id, jname, pname, stime, etime, atime, cnc, core, node])
    except Exception as e:
        print e
        conn.rollback()
    return resu

def searchjob(time1, time2):  #ENDTIME between time1 and time2
    conn = MySQLdb.connect(host=SQL_host, user=SQL_user, db=SQL_db, passwd=SQL_passwd, port=SQL_port)
    print 'connect succeed'
    try:
        cursor = conn.cursor()
        item1 = "STARTTIME <= '" + time2 + "' and ENDTIME > '" + time2 + "'"
        item2 = "ENDTIME > '" + time1 + "' and ENDTIME <= '" + time2 + "'"
        item3 = "ENDTIME = '0000-00-00 00:00:00'" + " and STARTTIME < '" + time2 + "'"
        ite = "NODELIST <> '-' and RUNTIME <> 0"
        ite1 = "QUEUE not like '%x86%'"
        sql1 = ("select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,CORE,NODELIST from JOB_log_all where "
               + ite + " and " + ite1 + " and " + item2 + " order by PROGRAM_NAME")
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        re = []
        for date in result1:
            re.append(date)
        re.sort()
        resu = []
        if len(re)<1:
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
                resu.append([id, jname, pname, stime, etime, atime, cnc, core, node])
    except Exception as e:
        print e
        conn.rollback()
    return resu

def get_re(time1, time2):#Run time between time1 and time2
    conn = MySQLdb.connect(host=SQL_host, user=SQL_user, db=SQL_db, passwd=SQL_passwd, port=SQL_port)
    print "connect succeed"
    try:
        cursor = conn.cursor()
        item1 = "STARTTIME <= '" + time2 + "' and ENDTIME > '" + time2 + "'"
        item2 = "ENDTIME > '" + time1 + "' and ENDTIME <= '" + time2 + "'"
        item3 = "ENDTIME = '0000-00-00 00:00:00'" + " and STARTTIME < '" + time2 + "'"
        ite = "NODELIST <> '-' and RUNTIME <> 0 and CORE<>0"
        ite1 = "QUEUE not like '%x86%'"
        sql1 = ("select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,CORE,NODELIST from JOB_log_all where "
                + ite + " and " + ite1 + " and " + "( " + item1 + " or " + item2 + " or " + item3 + " ) order by PROGRAM_NAME")
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        re = []
        for date in result1:
            re.append(date)
        resu = []
        if len(re)<1:
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
                resu.append([id, jname, pname, stime, etime, atime, cnc, core, node])
    except Exception as e:
        print e
    conn.rollback()
    return resu

def get_re_jobid(jobid):
    conn = MySQLdb.connect(host=SQL_host, user=SQL_user, db=SQL_db, passwd=SQL_db, port=SQL_port)
    print "connect succeed"
    resu = []
    try:
        cursor = conn.cursor()
        database = "JOB_log_all"
        sql1 = ("select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,CORE,NODELIST from " + database + 
                " where jobid=" + str(jobid) + " and RUNTIME<>0 order by PROGRAM_NAME")
        cursor.execute(sql1)
        result1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        re = []
        for date in result1:
            re.append(date)
        re.sort()
        if len(re)<1:
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
                resu.append([id, jname, pname, stime, etime, atime, cnc, core, node])
    except Exception as e:
        print e
        conn.rollback()
    return resu

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "please input time1 to time2 e.g:2016-07-19 12:30:00 2016-07-19 14:30:00"
        sys.exit()
    time1 = sys.argv[1] + " " + sys.argv[2]
    time2 = sys.argv[3] + " " + sys.argv[4]
    #jobid = sys.argv[5]
    results = get_re(time1,time2)
    #results = get_re_jobid(jobid)
