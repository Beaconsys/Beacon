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
This part helps users to deploy Beacon on other clusters.  

## i. Runtime environment
1. Linux OS
2. Python 2.7 or above
3. C
4. Elasticserach-1.5 or above
5. Redis-3.0 or above
6. Logstash-1.5 or above

## ii. Deployment
Prepare monitoring nodes (Beacon's client will collect data on these nodes), storage nodes (Beacon's server will store data on these nodes), and  a dedicated visualization node (Beacon's web server will run on this node)
1. Deploy monitoring daemons on monitoring nodes
2. Deploy Elasticsearch + Redis + Logstash on storage nodes
3. Deploy web server on the dedicated visualization node

## iii. Configuration
Before run Beacon's client (monitoring daemons) on monitoring nodes, we should configure Beacon's storage server first.
Below will show how to configure Beacon's sotrage server after we install Elasticsearch, redis, logstash successfully. 

* Use logstash to collect messages from monitoring daemons
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

* Use logstash to extract message from Redis and store it to the Elasticsearch  
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
* Use Redis to cache messages  
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
* Use Elasticsearch to store data
```
 cluster.name: elasticsearchzhengji
 # default configuration
```

We can nearly use the default configuration. 
However, remember to set the same cluster name and ensure these backend nodes are in the same network segment.

# Introduction of sys code

Our code will be opened source in /sys, including monitoring module, analysis module and web interface. For more detailed information, please read [README](https://github.com/Beaconsys/Beacon/blob/master/sys/README.md) in sys directory.


# Introduction of released data
The directory /data is used to store released data, and we plan to release data gradually.

Step to obtain the data:

* We put released data on cloud
* We share the link here 
* Anyone can obtian these data by access the [link here](https://pan.baidu.com/s/1TasclvmkpqPDHmTTkKMFiQ) with fetchCode `8pja`
  
The released dataset is a sample 14-day (start from 2018-01-01, the total data size is about 50GB compressed) multi-level I/O monitoring dataset from the [TaihuLight Supercomputer](http://performance.netlib.org/utk/people/JackDongarra/PAPERS/sunway-taihulight.pdf), currently the world's 3rd largest.

Original data format are shown below:
`index-name  ||  data-type  ||  id  ||  score  ||  message  ||  @version  ||  @timestamp  ||  host`

After data cleaning:
`message || timestamp || host`

In order to release data, we perform a mapping strategy:

1. Every file or directory will be instead by a hash value. 
2. Every User will be instead by "Userxxx"

Example:
```
    Original:
    [2018-09-10 14:16:52] T OPEN() /User_storage/job1/file1/file2/file3/file4/file5 => 0x1200bd3f0
    
    After mapping:
    [2018-09-10 14:16:52] T OPEN() /User146/6596814368836924247/-1160749754054947605/-8481035609384531935/2230746621555036977/756880090362066628/-1752974055252976644 =>  0x1200bd3f0
```
By the way, for `open opearation`: There may be two same open opearation in the trace. e.g:
```    
    [2018-09-10 14:16:52] T OPEN() /User_storage/job1/file1/file2/file3/file4/file5 => 0x1200bd3f0
    
    [2018-09-10 14:16:52] T OPEN() /User_storage/job1/file1/file2/file3/file4/file5
```    
We can find that only one open operation has the file descriptor. The reason for this phenomenon is that one operation is the request initiator without file descriptor, and the other operation has alreadly received the request comletation signal with file descriptor.


## Data format

* ES_COMP
    (Data collected by Beacon from compute nodes node by node)
* ES_FWD1
    (Data collected by Beacon from default forwarding nodes)
* ES_FWD2
    (Data collected by Beacon from rest forwarding nodes)
* ES_MDS
    (Data collected by Beacon from MDS)
* ES_Latency
    (Data collected by Beacon from forwarding nodes, on LWFS servers, including queue length and latency)
* ES_OST1
    (Data collected by Beacon from default storage nodes)
* ES_OST2
    (Data collected by Beacon from rest storage nodes)
* Job
    (Data collected by Beacon from applications running on the TaihuLight `# PS: we are still applying for open sourece this part.`)
    
Detailed data format: ![Figure](https://github.com/Beaconsys/Beacon/blob/master/icon/Dataformat.png)

More data will be released, if you are interested, please follow us.

# Thank You
Thanks for checking this project out! I hope you find it useful.
Of course, there's always room for improvement. Feel free to [open an issue](https://github.com/Beaconsys/Beacon/issues) so we can make Beacon better, stronger, faster.

Also, if you have any questions，contact us:

Email: tianyuzhang1214@163.com.
