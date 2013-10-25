import math

import transroute
import json
import socket



homeltd = 55.+45./60.+16.97/3600.
homelng = 37.+38./60.+48.52/3600.


#homelng = 37.+38./60.+52.6/3600.

begining = 55.752361111111114, 37.64678333333333
end = 55.755430555555556, 37.64849722222222
t = transroute.TransRoute(begining, end)

#dist = 0.002809206764613

#cells = [
#		{"CID": 11532, "RSSI": 17, "type": "GPRS"},
#		{"CID": 32770, "RSSI": 17, "type": "GPRS"},
#		{"CID": 32777, "RSSI": 24, "type": "GPRS"},
#		{"CID": 32778, "RSSI": 27, "type": "GPRS"},
#		{"CID": 32779, "RSSI": 21, "type": "GPRS"},
#		{"CID": 41522, "RSSI": 20, "type": "GPRS"},
#		{"CID": 41526, "RSSI": 22, "type": "GPRS"}
#	]
#GSM = {"cellcount": 7, "cells": cells}

#ltd, lng = t.dist_to_longlat(dist)

#GPS = {"lng": lng+2.0/3600, "ltd": ltd-3.0/2600, "acc": 15}

#data = {"GPS": GPS, "GSM": GSM}

f = open("raw_mobile_data.txt", "r")
d = f.readlines()
i = 0

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
	if i >= len(d):
		i = 0
	data = d[i]
	i += 1
	s.sendto(data, ("vkphoto.auditory.ru", 31415))
