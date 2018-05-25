# -*- coding: utf-8 -*-
# Author: swstorage

import socket
import sys
import os
import string
import datetime,time 


cluster_ip='20.0.8.90'
port=9987


def collect_lustre_client():
    global cluster_ip,port
    dir='/proc/fs/lustre/obdfilter/'
    first_time_flag=1
    mes=dict()
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((cluster_ip,port))

    while(1):
     for filename in os.listdir(dir):
      names=filename.split('-')
      if( len(names) == 2 and names[0]=="bswgfs"):
       rpc_stats=dir+filename+'/brw_stats'
       count=0 
       ost_number=string.replace(names[1],"OST","")
       ####  refesh ost stats  #####
       file = open(rpc_stats,'r')
       lines = file.readlines()
       for items in lines:
        count+=1
       s1=[]
       if (count > 20):
        line_number=0
        for items in lines:
          item=items.split()
          if(line_number > 3 and line_number < 13 and len(item)> 0):
            if ":" in item[0]:
             size=int(string.replace(item[0],":",""))
             s1.append([size,int(item[1]),int(item[5])])
            
          line_number+=1
       
        #####   send message to server #######
       if(first_time_flag==1):
         mes[ost_number]=s1
         message=ost_number+" "+str(s1)
         s.send(message)
         s.send("\n")
       else:
        if mes[ost_number]!=s1:
         mes[ost_number]=s1
         message=ost_number+" "+str(s1)
         s.send(message)
         s.send("\n")
     first=0
     time.sleep(2)
    s.close()


if __name__=='__main__':
    collect_lustre_client()
