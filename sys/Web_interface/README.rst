☤ Beacon
------------

Beacon is a monitoring tool for HPC centers, and has been deployed on the current No.2 Sunway TaihuLight Supercomputer for a year. With the help of Beacon, various performance problems and system anomaly have been detected and relieved.

☤ About web interface directory
------------

In this directory, we plan to open source our web code here, including the efficient cache strategy.

- app.py
    This is the main program entry, to launch our Beacon monitoring application server, please run the following command:
.. code:: python

        python app.py
- auth
    This module is used for User Authentication. In our environment, we implement our user authentication based on LDAP. You can custom your own user authentication via modifying the auth.py file.
- static
    This directory contains the static files for Beacon web applications, including css files, js files, images, etc.
- util
    This module contains utility tools and methods, including database access, data caching, auxiliary tools, etc.
- templates
    This directory contains the flask template HTML files.
    
☤ To be continued...
------------
   
Contact us:   

Email: tianyuzhang1214@163.com.
