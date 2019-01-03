☤ Beacon
------------

Beacon is a monitoring tool for HPC centers, and has been deployed on the current No.2 Sunway TaihuLight Supercomputer for over a year.
With the help of Beacon, various performance problems and system anomaly have been detected and relieved.


☤ data
------------

This directory is used to store open source data. Because data collected by Beacon is mass and we had to put it here, we plan to open source data gradually.

Step to obtain the data:

- We put open source data on cloud
- We share the link here 
- Anyone can obtian these data by access the `link here <https://pan.baidu.com/s/1TasclvmkpqPDHmTTkKMFiQ>`_ with fetchCode ``8pja``

We are now peaparing data and will open source gradually.

Data categories are:(Data format are shown below)

In order to open source the data, we perform a mapping strategy. e.g:

    Original:
    [2018-09-10 14:16:52] T OPEN() /User_storage/job1/file1/file2/file3/file4/file5 => 0x1200bd3f0
    
    After mapping:
    [2018-09-10 14:16:52] T OPEN() /User146/6596814368836924247/-1160749754054947605/-8481035609384531935/2230746621555036977/756880090362066628/-1752974055252976644 =>  0x1200bd3f0

Every file or directory will be instead by a hash value. Every User will be instead by "Userxxx"

particularly ：message, timestamp, host

- ES_COMP
    (Data collected by Beacon from compute nodes node by node)
- ES_FWD1
    (Data collected by Beacon from default forwarding nodes)
- ES_FWD2
    (Data collected by Beacon from rest forwarding nodes)
- ES_MDS
    (Data collected by Beacon from MDS)
- ES_Latency
    (Data collected by Beacon from forwarding nodes, on LWFS servers, including queue length and latency)
- ES_OST1
    (Data collected by Beacon from default storage nodes)
- ES_OST2
    (Data collected by Beacon from rest storage nodes)
    
We will continue to open source our data, including many fields.  

Still doing...

Data are gradually put on the clound.


contact us:

Email: tianyuzhang1214@163.com.
