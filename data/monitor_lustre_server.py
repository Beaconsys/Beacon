# -*- coding: utf-8 -*-
# Author: swstorage


import socket
import sys
import os
import string
import datetime,time 

cluster_ip='20.0.9.89'
port=9987
 

def collect_lustre_server():
    global cluster_ip,port
    dir_osc='/proc/fs/lustre/osc/'
    dir_cache='/proc/fs/lustre/llite/'
    count=0
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((cluster_ip,port))
    mes=dict()
    pre_cache=''
    first_time_flag=1

    
    command="ls /proc/fs/lustre/osc/ | wc -l"
    f1=os.popen(command)
    ost_sum=int(f1.readline())
    if ost_sum >500:
      exit()

    while(1):
      for filename in os.listdir(dir):
        try:
          names=filename.split('-')
          if( len(names) == 4 and names[0]=="bswgfs"):
           rpc_stats=dir+filename+'/rpc_stats'
           count=0 
           ost_number=string.replace(names[1],"OST","")
         ####  refesh rpc stats  #####
           file = open(rpc_stats,'r')
           lines = file.readlines()
           for items in lines:
            count+=1
           s1=[]
           if (count > 16):
            line_number=8
            items=lines[line_number]
            while ("read" not in items) and ("write" not in items):
              item=items.split()
              if((line_number > 7) and (len(item)> 0)):
                if ":" in item[0]:
                 size=int(string.replace(item[0],":",""))
                 s1.append([size,int(item[1]),int(item[5])])
              line_number+=1
              items=lines[line_number]
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
        except Exception as e:
          continue
       first_time_flag=0
       for gs in os.listdir(dir_c):
         try:
           if 'bswgfs' in str(gs):
             c_file=dir_c+gs+'/read_ahead_stats'
             cachefile = open(c_file,'r')
             clines=cachefile.readlines()
             if len(clines)<5:
              continue
             discard_mes='discard 0'
             for sam in clines:
              if 'discarded' in sam:
               discard_mes="discard "+str(sam.split(' ')[-3])
               break
             cache_mes="cache_hit "+str(str(clines[1]).split(' ')[-3])+" cache_miss "+str(str(clines[2]).split(' ')[-3])+" "+discard_mes
             if cache_mes!=pre_cache:
              pre_cache=cache_mes
              s.send(cache_mes)
              s.send("\n")
         except Exception as e:
           continue
       time.sleep(1)
      s.close()

if __name__="__main__":
    collect_lustre_server()
