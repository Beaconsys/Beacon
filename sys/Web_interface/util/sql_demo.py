# -*- coding: utf-8 -*-
import MySQLdb, sys, csv, exceptions, time, multiprocessing, gc

# Structure of Table JOB_IO_INFO 
'''
+-----------------------+--------------+------+-----+---------+-------+
| Field                 | Type         | Null | Key | Default | Extra |
+-----------------------+--------------+------+-----+---------+-------+
| 0 JOBID                 | varchar(20)  | NO   | PRI | NULL    |       |
| 1 PROGRAM_NAME          | varchar(500) | NO   |     | NULL    |       |
| 2 CNC                   | int(11)      | NO   |     | NULL    |       |
| 3 IOBW_READ_SUM         | double       | YES  |     | NULL    |       |
| 4 IOBW_READ_COUNT       | int(11)      | YES  |     | NULL    |       |
| 5 IOBW_READ_AVERAGE     | double       | YES  |     | NULL    |       |
| 6 IOBW_WRITE_SUM        | double       | YES  |     | NULL    |       |
| 7 IOBW_WRITE_COUNT      | int(11)      | YES  |     | NULL    |       |
| 8 IOBW_WRITE_AVERAGE    | double       | YES  |     | NULL    |       |
| 9 IOBW_ALL_COUNT        | int(11)      | YES  |     | NULL    |       |
| 0 IOPS_READ_SUM         | double       | YES  |     | NULL    |       |
| 1 IOPS_READ_COUNT       | int(11)      | YES  |     | NULL    |       |
| 2 IOPS_READ_AVERAGE     | double       | YES  |     | NULL    |       |
| 3 IOPS_WRITE_SUM        | double       | YES  |     | NULL    |       |
| 4 IOPS_WRITE_COUNT      | int(11)      | YES  |     | NULL    |       |
| 5 IOPS_WRITE_AVERAGE    | double       | YES  |     | NULL    |       |
| 6 IOPS_ALL_COUNT        | int(11)      | YES  |     | NULL    |       |
| 7 IOTIME_COUNT          | int(11)      | YES  |     | NULL    |       |
| 8 MDS_OPEN_SUM          | int(11)      | YES  |     | NULL    |       |
| 9 MDS_OPEN_COUNT        | int(11)      | YES  |     | NULL    |       |
| 0 MDS_OPEN_AVERAGE      | double       | YES  |     | NULL    |       |
| 1 MDS_CLOSE_SUM         | int(11)      | YES  |     | NULL    |       |
| 2 MDS_CLOSE_COUNT       | int(11)      | YES  |     | NULL    |       |
| 3 MDS_CLOSE_AVERAGE     | double       | YES  |     | NULL    |       |
| 4 MDS_ALL_COUNT         | int(11)      | YES  |     | NULL    |       |
| 5 PROCESS_READ_MAX      | int(11)      | YES  |     | NULL    |       |
| 6 PROCESS_WRITE_MAX     | int(11)      | YES  |     | NULL    |       |
| 7 FILENAME_UNIQUE_COUNT | int(11)      | YES  |     | NULL    |       |
| 8 JOB_NAME              | varchar(500) | YES  |     | NULL    |       |
+-----------------------+--------------+------+-----+---------+-------+
'''

def get_jobid():
    jobid = []
    conn = MySQLdb.connect(host='20.0.2.201', user='root', db='JOB_IO', passwd='', port=3306) 
    cursor = conn.cursor()
    sql = "select * from JOB_IO_INFO where IOBW_READ_SUM > 80000 and CNC >= 128 and CNC <= 30000 and JOBID > 40000000 order by JOBID asc;"
    #sql = "select * from JOB_IO_INFO where JOBID = 43118913"

    cursor.execute(sql)
    result = cursor.fetchall()
    for res in result:
        print res[0] + ' ' + str(res[28]) + ' ' + str(res[2 ]) + ' read:' + str(round(res[3] / 1024.0, 1)) 
    conn.commit()
    cursor.close()
    conn.close()

    return jobid
    
if __name__ == "__main__":
    
    jobid = get_jobid()

