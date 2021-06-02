import ntplib
import datetime
from time import ctime
from dateutil import parser

c = ntplib.NTPClient()
response = c.request('uk.pool.ntp.org', version=3)
response.offset
# print (ctime(response.tx_time))
# print (ntplib.ref_id_to_text(response.ref_id))

# date_time_obj = datetime.datetime.strptime(ctime(response.tx_time), '%b %d %Y %I:%M%p')

# print(date_time_obj)
ntpDate = datetime.datetime.strptime(ctime(response.tx_time), "%a %b %d %H:%M:%S %Y")
nowDate = datetime.datetime.now()
print ("NTP Date: ", ntpDate)
print ("Now Date: ", nowDate)

if ntpDate > nowDate:
    c = ntpDate - nowDate 
else:
    c = nowDate - ntpDate 

print('Difference: ', c)
print('Difference in secounds: ', c.seconds)
print('Difference in Micro: ', (c.seconds*1000000) + c.microseconds)

print("New genesis:? ", parser.parse(ctime(response.tx_time)))
