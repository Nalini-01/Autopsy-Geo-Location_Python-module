# Autopsy-Python-module

Requirements -
1. Autopsy Forensics software must be installed on the system.
2. Download the PyGeoIP package from here - https://pypi.python.org/pypi/pygeoip
3. Download the Geolitecity.dat database from here - http://dev.maxmind.com/geoip/geoip2/geolite2/ 


Note - I have already uploaded these dependencies in this repository, you can also download these from here. :)



 Further Steps - 
 
1. Put these files in C drive path like following -
  C:\Users\ADMIN_NAME\AppData\Roaming\autopsy\python_modules\
 
 Note :  You can also create a folder named as geolocation and then put these files into it.

2. In Geolocation.py file , in line no. 103 , edit the path location of  uncompressed database(i.e GeoLiteCity.dat) according to your system.
for example 'C:\Users\ADMIN_NAME\AppData\Roaming\autopsy\python_modules\geolocation\GeoLiteCity.dat'

Note : Edit your system's Admin name accordingly.
