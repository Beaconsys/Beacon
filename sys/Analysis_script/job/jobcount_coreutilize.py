import MySQLdb
import datetime,time
import MySQLdb.cursors
import math
import sys
import types
import csv


job_count = []
job_corehour = []
timeStamp = 0
SQL_host = ""
SQL_user = ""
SQL_db = ""
SQL_passwd = ""
SQL_port = ""
#job_count=[0 for i in range(24)]
#job_corehour=[0 for i in range(24)]

def makeTimeStamp(target):
    global timeStamp
    if type(target) == types.StringType:
        timeArray = time.strptime(target, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
    elif type(target) == datetime.datetime:
        timeStamp = int(time.mktime(target.timetuple()))
    return timeStamp

def makeDateTime(timestamp):
    dateArray = datetime.datetime.utcfromtimestamp(timestamp)
    return dateArray

def query_by_date(start,end):
    global db
    db = MySQLdb.connect(host=SQL_host, user=SQL_user, db=SQL_db, passwd=SQL_passwd, port=SQL_port)
    print "connect succeed"

    global start_timestamp,end_timestamp
    start_timestamp = makeTimeStamp(start)
    end_timestamp = makeTimeStamp(end)
        
    num_hour = (end_timestamp - start_timestamp) / 3600
    global job_count,job_corehour
    job_count = [0 for i in range(num_hour)]
    job_corehour = [0 for i in range(num_hour)]
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")	
    try:
        global cursor
        cursor = db.cursor()
        sql1 = ("select JOBID,CORE,STARTTIME,ENDTIME from JOB_log_all where STARTTIME > '" + start + "' AND ENDTIME < '" + 
                end + "' AND QUEUE not like '%x86%' and STARTTIME<>'0000-00-00 00:00:00';")
        sql2 = ("select JOBID,CORE,STARTTIME,ENDTIME from JOB_log_all where STARTTIME <= '" + start + "' AND ENDTIME >= '" + 
                end + "' AND QUEUE not like '%x86%' and STARTTIME<>'0000-00-00 00:00:00';")
        sql3 = ("select JOBID,CORE,STARTTIME,ENDTIME from JOB_log_all where STARTTIME < '" + start + "' AND ENDTIME <= '" + 
                end + "' AND ENDTIME > '" + start + "'AND QUEUE not like '%x86%' and STARTTIME<>'0000-00-00 00:00:00';")
        sql4 = ("select JOBID,CORE,STARTTIME,ENDTIME from JOB_log_all where STARTTIME >= '" + start + "' AND STARTTIME < '" + 
                end + "' AND ENDTIME > '" + end + "'AND QUEUE not like '%x86%' and STARTTIME<>'0000-00-00 00:00:00';")
        deal_first(sql1)
        deal_second(sql2)
        deal_third(sql3)
        deal_fourth(sql4)
        cursor.close()
    except Exception as e:
        print e
        db.rollback()
        db.close()

def deal_first(sql):
    global db,cursor
    cursor.execute(sql)
    result = cursor.fetchall()
    db.commit()
    global start_timestamp,end_timestamp
    #print result
    for item in result:
        if type(item[3]) == types.NoneType:
            continue
        else:
            #print item
            core = item[1]
            head = (makeTimeStamp(item[2])) % 3600
            tail = (makeTimeStamp(item[3])) % 3600
            st = makeTimeStamp(item[2]) - head + 3600
            en = makeTimeStamp(item[3]) - tail
            if en < st:
                if head <> 0:
                    job_count[(st - start_timestamp) / 3600 - 1] += 1
                    job_corehour[(st - start_timestamp) / 3600 - 1] += (tail - head) / 3600.0 * core
                    continue
            elif en >= st:
                if head <> 0:
                    job_count[(st - start_timestamp) / 3600 - 1] += 1
                    job_corehour[(st - start_timestamp) / 3600 - 1] += (3600 - head) / 3600.0 * core
                if tail <> 0:
                    job_count[(en - start_timestamp) / 3600] += 1
                    job_corehour[(en - start_timestamp) / 3600] += tail / 3600.0 * core
                    for i in range(st, en, 3600):
                        job_count[(i - start_timestamp) / 3600] += 1
                        job_corehour[(i - start_timestamp) / 3600] += core

def deal_second(sql):
    global db,cursor
    cursor.execute(sql)
    result = cursor.fetchall()
    db.commit()
    global start_timestamp, end_timestamp
    for item in result:
        if type(item[3]) == types.NoneType:
            continue
        else:
            #print item
            core = item[1]
            for i in range(start_timestamp, end_timestamp, 3600):
                job_count[(i - start_timestamp) / 3600] += 1
                job_corehour[(i - start_timestamp) / 3600] += core

def deal_third(sql):
    global db,cursor
    cursor.execute(sql)
    result = cursor.fetchall()
    db.commit()
    global start_timestamp, end_timestamp
    for item in result:
            if type(item[3]) == types.NoneType:
                    continue
            else:
                    core = item[1]
                    tail = (makeTimeStamp(item[3])) % 3600
                    en = makeTimeStamp(item[3]) - tail
                    if tail <> 0:
                            job_count[(en - start_timestamp) / 3600] += 1
                            job_corehour[(en-start_timestamp) / 3600] += tail / 3600.0 * core
                    for i in range(start_timestamp, en, 3600):
                            job_count[(i - start_timestamp) / 3600] += 1
                            job_corehour[(i - start_timestamp) / 3600] += core        



def deal_fourth(sql):
    global db,cursor
    cursor.execute(sql)
    result = cursor.fetchall()
    db.commit()
    global start_timestamp,end_timestamp
    for item in result:
        if type(item[3]) == types.NoneType:
            continue
        else:
            core = item[1]
            head = (makeTimeStamp(item[2])) % 3600
            st = makeTimeStamp(item[2]) - head + 3600
            if head <> 0:
                    job_count[(st - start_timestamp) / 3600 - 1] += 1
                    job_corehour[(st - start_timestamp) / 3600 - 1] += (3600 - head) / 3600.0 * core
            else:
                for i in range(st, end_timestamp, 3600):
                    job_count[(i - start_timestamp) / 3600] += 1
                    job_corehour[(i - start_timestamp) / 3600] += core

if __name__ == "__main__":
    s = sys.argv[1] + " " + sys.argv[2]
    e = sys.argv[3] + " " + sys.argv[4]
    print s," ",e
    query_by_date(s, e)
    csvfile = file('./core_corehour_' + sys.argv[1] + '-' + sys.argv[3] + '.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(['jobcount','corehour'])
    for i in range(len(job_count)):
        writer.writerow([job_count[i], job_corehour[i]])
    csvfile.close()

