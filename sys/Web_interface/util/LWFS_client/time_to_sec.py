#!/usr/bin/python
# Filename: time_to_sec.py
import datetime
import time


year_sec = 365*24*60*60
day_sec   = 24*60*60
hour_sec = 60*60
sec = 60

mon1_sec   = (31)*day_sec
mon2_sec   = (31+28)*day_sec
mon3_sec   = (31+28+31)*day_sec
mon4_sec   = (31+28+31+30)*day_sec
mon5_sec   = (31+28+31+30+31)*day_sec
mon6_sec   = (31+28+31+30+31+30)*day_sec
mon7_sec   = (31+28+31+30+31+30+31)*day_sec
mon8_sec   = (31+28+31+30+31+30+31+31)*day_sec
mon9_sec   = (31+28+31+30+31+30+31+31+30)*day_sec
mon10_sec = (31+28+31+30+31+30+31+31+30+31)*day_sec
mon11_sec = (31+28+31+30+31+30+31+31+30+31+30)*day_sec
mon_sec = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]

def time_to_sec_fast(day_time):
    x = time.strptime(day_time,'%Y-%m-%d %H:%M:%S')

    year_day_hour_min =  (x.tm_year) * year_sec + (x.tm_mday-1)*day_sec + x.tm_hour*hour_sec + x.tm_min*sec + x.tm_sec
    now_sec = mon_sec[x.tm_mon - 1] * day_sec + year_day_hour_min
    #print x.tm_mon[10]
    return now_sec

def time_to_sec(day_time):
    x = time.strptime(day_time,'%Y-%m-%d %H:%M:%S')

    year_day_hour_min =  (x.tm_year) * year_sec + (x.tm_mday-1)*day_sec + x.tm_hour*hour_sec + x.tm_min*sec + x.tm_sec

    if x.tm_mon == 1:
        now_sec = year_day_hour_min
    elif x.tm_mon == 2:
        now_sec = mon1_sec + year_day_hour_min
    elif x.tm_mon == 3:
        now_sec = mon2_sec + year_day_hour_min
    elif x.tm_mon == 4:
        now_sec = mon3_sec + year_day_hour_min
    elif x.tm_mon == 5:
        now_sec = mon4_sec + year_day_hour_min
    elif x.tm_mon == 6:
        now_sec = mon5_sec + year_day_hour_min
    elif x.tm_mon == 7:
        now_sec = mon6_sec + year_day_hour_min
    elif x.tm_mon == 8:
        now_sec = mon7_sec + year_day_hour_min
    elif x.tm_mon == 9:
        now_sec = mon8_sec + year_day_hour_min
    elif x.tm_mon == 10:
        now_sec = mon9_sec + year_day_hour_min
    elif x.tm_mon == 11:
        now_sec = mon10_sec + year_day_hour_min
    else:
        now_sec = mon11_sec + year_day_hour_min
    return now_sec

def sec_to_time(secs):
    year=secs/year_sec
    res=secs-year*year_sec
    if res>=mon11_sec:
        month=12
        res=res-mon11_sec
    elif res>=mon10_sec:
        month=11
        res=res-mon10_sec
    elif res>=mon9_sec:
        month=10
        res=res-mon9_sec
    elif res>=mon8_sec:
        month=9
        res=res-mon8_sec
    elif res>=mon7_sec:
        month=8
        res=res-mon7_sec
    elif res>=mon6_sec:
        month=7
        res=res-mon6_sec
    elif res>=mon5_sec:
        month=6
        res=res-mon5_sec
    elif res>=mon4_sec:
        month=5
        res=res-mon4_sec
    elif res>=mon3_sec:
        month=4
        res=res-mon3_sec
    elif res>=mon2_sec:
        month=3
        res=res-mon2_sec
    elif res>=mon1_sec:
        month=2
        res=res-mon1_sec
    else:
        month=1
        res=res-0
    day=res/day_sec
    res=res-day*day_sec
    day=day+1
    hour=res/hour_sec
    res=res-hour*hour_sec
    mininute=res/sec
    second=res-mininute*sec
    str_year=str(year)
    if month<10:
        str_month='0'+str(month)
    else:
        str_month=str(month)
    if day<10:
        str_day='0'+str(day)
    else:
        str_day=str(day)
    if hour<10:
        str_hour='0'+str(hour)
    else:
        str_hour=str(hour)
    if mininute<10:
        str_min='0'+str(mininute)
    else:
        str_min=str(mininute)
    if second<10:
        str_sec='0'+str(second)
    else:
        str_sec=str(second)
    time=str_year+"-"+str_month+"-"+str_day+" "+str_hour+":"+str_min+":"+str_sec
    return time


if __name__=="__main__":
    time1="2017-12-31 23:59:59"
    t_s=time_to_sec(time1)
    s_t=sec_to_time(t_s)
    print t_s
    print s_t








# End of time_to_sec.py
