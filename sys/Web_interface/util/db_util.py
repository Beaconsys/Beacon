import sys, math, datetime, time, types, MySQLdb, MySQLdb.cursors

db_host="20.0.2.15"
db_user="swqh"
db_name="JOB"
db_passwd="123456"
db_port=3306

def select_table(jobid):
    if (int(jobid) <= 9000000) and (int(jobid) >= 6000000):
        table = "JOB_log_all"
    elif (int(jobid) >= 40000001) and (int(jobid) <= 40500000):
        table = "JOB_log_4050"
    elif (int(jobid) >= 40500001) and (int(jobid) <= 41000000):
        table = "JOB_log_4100"
    elif (int(jobid) >= 41000001) and (int(jobid) <= 41500000):
        table = "JOB_log_4150"
    elif (int(jobid) >= 41500001) and (int(jobid) <= 42000000):
        table = "JOB_log_4200"
    elif (int(jobid) >= 42000001) and (int(jobid) <= 42500000):
        table = "JOB_log_4250"
    elif (int(jobid) >= 42500001) and (int(jobid) <= 43000000):
        table = "JOB_log_4300"
    else:
        table = "JOB_log"
    return table


def get_user_job_count(username,stime,etime):
    db = MySQLdb.connect(host = db_host, user = db_user, db = db_name, passwd = db_passwd, port = db_port) 
    try:
        sql = "select count(*) from JOB_log_all where USER = '" + username + "'"
        if stime != "" and etime != "" :
            sql += " and STARTTIME > '" + stime + "' and ENDTIME <'" + etime + "'"        
        cursor = db.cursor()
        cursor.execute(sql)
        count = cursor.fetchall()[0][0]
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print e
        db.rollback()
        db.close()
    
    return count

def get_users():
    db=MySQLdb.connect(host=db_host,user=db_user,db=db_name,passwd=db_passwd,port=db_port) 
    try:
        sql ="select distinct USER from JOB_log order by USER asc;"       
        cursor = db.cursor()
        cursor.execute(sql)
        users = cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print e
        db.rollback()
        db.close()
    
    return users
    
def get_jobs(username, stime, etime, job_name, begin):
    db = MySQLdb.connect(host = db_host, user = db_user, db = db_name, passwd = db_passwd, port = db_port)
    result = [] 
    try:
        sql = "select JOBID, JOB_NAME, STARTTIME, ENDTIME, RUNTIME, STATE from JOB_log  where USER = '" + username + "'"
        if job_name != "":
            sql += " and JOB_NAME like '%" + job_name + "%'"
        if stime != "" and etime != "":
            sql += " and STARTTIME between '" + stime + "' and '" + etime + "'" 
        sql += " union select JOBID, JOB_NAME, STARTTIME, ENDTIME, RUNTIME, STATE from JOB_log_all where USER = '" + username + "'"
        if job_name != "":
            sql += " and JOB_NAME like '%" + job_name + "%'"
        if stime != "" and etime != "":
            sql += " and STARTTIME between '" + stime + "' and '" + etime + "'" 
        sql +=  " order by STARTTIME desc limit " + str(begin) + ",30;" 
        #print sql
        cursor = db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        db.commit()    
        cursor.close()
        db.close()
    except Exception as e:
        print e
        db.rollback()
        db.close()
    return result
    
 
def get_job_by_idd(jobid):
    db = MySQLdb.connect(host = db_host, user = db_user, db = db_name, passwd = db_passwd, port = db_port) 
    db_table = select_table(jobid)
    #print db_table
    try:
        sql ="select * from " + db_table + " where JOBID = " + jobid + ";"        
        cursor = db.cursor()
        cursor.execute(sql)
        result=cursor.fetchall()
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print e
        db.rollback()
        db.close()
    
    return result       


def get_history_job(username,jobname):
    db=MySQLdb.connect(host=db_host,user=db_user,db=db_name,passwd=db_passwd,port=db_port)
    result = {} 
    try:
        sql1 = "select count(*) from JOB_log where USER='" + username + "' and JOB_NAME like '%" + jobname +"%' order by STARTTIME desc;"
        sql2 = "select JOBID,RUNTIME from JOB_log where USER='" + username + "' and JOB_NAME like '%" + jobname +"%' and STATE='Done' order by RUNTIME desc limit 0,1;"
        sql3 = "select JOBID,RUNTIME from JOB_log where USER='" + username + "' and JOB_NAME like '%" + jobname +"%' and STATE='Done' order by RUNTIME asc limit 0,1;"
        sql4 = "select avg(RUNTIME) from JOB_log where USER='" + username + "' and JOB_NAME like '%" + jobname +"%' and STATE='Done';"
        sql5 = "select count(*) from JOB_log where USER='" + username + "' and JOB_NAME like '%" + jobname +"%' and STATE='Done';"   
        cursor = db.cursor()
        cursor.execute(sql1)
        r1 = cursor.fetchall()
        if r1[0][0] == 0:
            cursor.close()
            db.close()
            return "empty"
        
        cursor.execute(sql2)
        r2 = cursor.fetchall()
        
        cursor.execute(sql3)
        r3 = cursor.fetchall()
        
        cursor.execute(sql4)
        r4 = cursor.fetchall()
        
        cursor.execute(sql5)
        r5 = cursor.fetchall()

        result['count'] = r1[0][0]
        result['max'] = r2[0][1]
        result['max_id'] = r2[0][0]
        result['min'] = r3[0][1]
        result['min_id'] = r3[0][0]
        result['avg'] = int(r4[0][0])
        result['done'] = int(float(r5[0][0])/result['count']*100)
        result['exit'] =100-result['done']
        #print result 
        
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        print e
        db.rollback()
        db.close()

    return result   

def get_job_by_id(jobid):
    conn = MySQLdb.connect(host = db_host, user = db_user, passwd = db_passwd, db = db_name, port = db_port)
    db_table = select_table(jobid)
    
    job_info = []
    try:
        cursor = conn.cursor()
        sql = 'select JOBID,JOB_NAME,PROGRAM_NAME,STARTTIME,ENDTIME,RUNTIME,CNC,CORE,NODELIST from ' + db_table + ' where jobid=' + str(jobid)
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.commit()
        cursor.close()
        if len(results) == 0:
            print "Sorry, there is no such job : " + jobid
        else:
            job = results[0]
            job_info.append(job[0]) # job_id
            job_info.append(job[1]) # job_name
            job_info.append(job[2]) # program_name
            job_info.append(str(job[3])) # start_time
            job_info.append(str(job[4])) # end_time
            job_info.append(job[5]) # runtime
            job_info.append(job[6]) # cnc
            job_info.append(job[7]) # core
            job_info.append(job[8]) # node_list
    except Exception as e:
        print e
        conn.rollback()
    return job_info




if __name__ == '__main__':
    #test = select_table(7878787)
    #print test
    print get_job_by_id("8431283")
