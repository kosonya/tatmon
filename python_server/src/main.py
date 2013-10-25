#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 09.12.2010

@author: maxikov
'''

import socket
import json
import dbconn
import validator
import transroute
import math
import threading
import Queue

begining = 55.752361111111114, 37.64678333333333
end = 55.755430555555556, 37.64849722222222



class FrontEnd(threading.Thread):
	def __init__(self, q, port):
		self.q = q
		self.port = port
		threading.Thread.__init__(self)

	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('', self.port))
		s.listen(1)
		while True:
			conn, addr = s.accept()
			print "Connected from:", addr
			try:
				while True:
					data = self.q.get()
					conn.sendall(data)
					self.q.task_done()
					print "sent", data
			except Exception as e:
				print e

def main():
	PORT = 31415
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serversocket.bind(('', PORT))
	t = transroute.TransRoute(begining, end)
	conn = dbconn.DBConn(TransRoute=t)
	q = Queue.Queue()
	frontend = FrontEnd(q, 31416)
	frontend.start()
	

	while True:
		data = serversocket.recv(65535)
#		print "received:", data
		jsondata = json.loads(data)
		valid_data = validator.validator(jsondata)
		if valid_data:
			conn.save_netdata(valid_data)
			print "GPS Lat:", valid_data['GPS']['ltd'], "GPS Lon:", valid_data['GPS']['lng']
			closest = t.closest(valid_data)
			dist = t.point_to_dist(valid_data)
			print "Route Lat:", closest[0], "Route Lon:", closest[1]
			print "Distance:", dist, "degrees\t", dist/8.987202970605459e-06, "meters"
			pos = valid_data['GPS']['lng'], valid_data['GPS']['ltd']
			dlat = pos[0] - closest[0]
			dlon = pos[1] - closest[1]
			err = math.sqrt(dlat*dlat + dlon*dlon)
			print "error:", err, "degress", err/8.987202970605459e-06, "meters\n\n"
			to_send = {"GPS": {"ltd": valid_data['GPS']['ltd'], "lng":valid_data['GPS']['lng']}, "Route":{"ltd": closest[0], "lng": closest[1], "dst": dist, "dstm": dist/8.987202970605459e-06}, "GPSerr":err, "GPSerrm": err/8.987202970605459e-06}
			q.put(json.dumps(to_send) + "\n")
#			print json.dumps(valid_data, sort_keys=True, indent=4)


if __name__ == "__main__":
	main()
