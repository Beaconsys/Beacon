# Beacon 
![Beacon icon](https://github.com/Beaconsys/Beacon/blob/master/icon/Beacon_icon.jpg)

![sdu icon](https://github.com/Beaconsys/Beacon/blob/master/icon/sdu.jpg) ![thu icon](https://github.com/Beaconsys/Beacon/blob/master/icon/thu.jpg)  ![qcri icon](https://github.com/Beaconsys/Beacon/blob/master/icon/qcri.jpg) ![emory icon](https://github.com/Beaconsys/Beacon/blob/master/icon/emory.jpg) ![nscc icon](https://github.com/Beaconsys/Beacon/blob/master/icon/nscc.jpg)

Beacon is an end-to-end I/O resource monitoring and diagnosis system, for the 40960-node Sunway TaihuLight supercomputer, current ranked world No.3. Beacon simultaneously collects and correlates I/O tracing/profiling data from all the compute nodes, forwarding nodes, storage nodes and metadata servers. With mechanisms such as aggressive online+offline trace compression and distributed caching/storage, it delivers scalable, low-overhead, and sustainable I/O diagnosis under production use. 

With its deployment on TaihuLight for around 18 months, it has successfully helped center administrators identify obscure design or configuration flaws, system anomaly occurrences, I/O performance interference, and resource under- or over-provisioning problems. Several of the exposed problems have already been fixed, with others being currently addressed. In addition, Beacon can be adopted by other platforms. Beacon's building blocks, such as operation log collection and compression, scheduler-assisted per-application data correlation and analysis, history-based anomaly identification, automatic I/O mode detection, and built-in interference analysis, can all be performed on other supercomputers.

This is joint work among 5 institutes, Shandong University, Tsinghua University, Qatar Computing Research institute, Emory University, and National Supercomputing Center in Wuxi.

# Documents and publications

1. NSDI19, End-to-end I/O Monitoring on a Leading Supercomputer, Bin Yang, Xu Ji, Xiaosong Ma, Xiyang Wang, Tianyu Zhang, Xiupeng Zhu, Nosayba El-Sayed, Haidong Lan, Yibo Yang, Jidong Zhai, Weiguo Liu, and Wei Xue, [PDF](https://www.usenix.org/system/files/nsdi19-yang.pdf)  
2. FAST19, Automatic, Application-Aware I/O Forwarding Resource Allocation, Xu Ji, Bin Yang, Tianyu Zhang, Xiaosong Ma, Xiupeng Zhu, Xiyang Wang, Nosayba El-Sayed, Jidong Zhai, Weiguo Liu, and Wei Xue, [PDF](https://www.usenix.org/system/files/fast19-ji.pdf)

We are now cleaning up our codes and gradually open source Beacon code/Data collected on Sunway TaihuLight, including monitoring and analysis methods.

# User guide
Beacon can be easily deployed on other clusters.  

## i. Runtime environment
1. Linux OS
2. Python 2.7 or above
3. C
4. Elasticserach-1.5 or above
5. Redis-3.0 or above
6. Logstash-1.5 or above

## ii. Deployment
Prepare monitoring nodes (Beacon's client will collect data on these nodes), storage nodes (Beacon's server will store all of data on these nodes), and  a dedicated visualization node (Optional, Beacon's web server will run on this node)
1. Deploy monitoring daemons on monitoring nodes
2. Deplot Elasticsearch + Redis + Logstash on storage nodes
3. Deploy web server on the dedicated visualization node

## iii. Configuration
Collect messages from monitoring programs  
```
  input {
           file {
                   type => "lala test"
                   path => "/root/testfile"
           }
           file {
                   type => "sys messages"
                   path => "/var/log/messages"
           }
           tcp {
                port => "9999"
                codec => "plain"
           }
           stdin {
           }
   }
  output {
            stdout {
                    codec=>rubydebug
            }
   }
  output {
          redis {
                  host => 'localhost'
                  data_type => 'list'
                  port => '6379'
                  key => 'logstash:redis'
          }
   }
```

Extract message from Redis and store it to the Elasticsearch  
```
  input {
        redis {
                host => 'localhost'
                data_type => 'list'
                port => "6379"
                key => 'logstash:redis'
                type => 'redis-input'
        }
   }
  output {
        stdout {
                 codec=>rubydebug
         }
   }
  output {
        elasticsearch {
                host=>localhost
                cluster=> "elasticsearch_cluster"
        }
   }
```

Use Redis to cache messages  
``` 
  pidfile /var/run/redis.pid
  port 6379
  timeout 0
  loglevel verbose 
  logfile /var/log/redis.log
  dbfilename dump.rdb
  dir /root/ELK/redis/db/
  ## vm-swap-file /tmp/redis.swap
```

You can nearly use the default configuration. 
However, remember to set the same cluster name and ensure these backend nodes are in the same network segment.

# Introduction of sys code

Our code will be opened source in /sys, including monitoring module, analysis module and web interface. For more detailed information, please read [README](https://github.com/Beaconsys/Beacon/blob/master/sys/README.md) in sys directory.


# Introduction of data
This directory is used to store open source data. Because data collected by Beacon is mass and we had to put it here, we plan to open source data gradually.

Step to obtain the data:

* We put open source data on cloud
* We share the link here 
* Anyone can obtian these data by access the [link here](https://pan.baidu.com/s/1TasclvmkpqPDHmTTkKMFiQ) with fetchCode `8pja`
  
The released dataset is a sample-14 day (start from 2018-01-01, the total data size is about 50GB compressed) multi-level I/O monitoring dataset from the [TaihuLight Supercomputer](http://performance.netlib.org/utk/people/JackDongarra/PAPERS/sunway-taihulight.pdf), currently the world's 3rd largest.
For more detailed information, please read [README](https://github.com/Beaconsys/Beacon/blob/master/data/README.md) in data directory.

# Thank You
Thanks for checking this library out! I hope you find it useful.
Of course, there's always room for improvement. Feel free to [open an issue](https://github.com/Beaconsys/Beacon/issues) so we can make Beacon better, stronger, faster.

Also, if you have any questions，contact us:

Email: tianyuzhang1214@163.com.
