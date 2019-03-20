# Itroduction of released data

## Introduction of released dataset

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



## Data categories

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
    (Data collected by Beacon from applications running on the TaihuLight) 
    (PS: we are still applying for open sourece this part.)
    
Detailed data format: ![Figure](https://github.com/Beaconsys/Beacon/blob/master/icon/Dataformat.png)

We will continue to open source our data, including many fields.  

Data are gradually put on the clound.
