# -*- coding: utf8 -*-

import datamanager
import transroute
import socket
import validator
import json
import threading
import math
import Queue

meter = 8.9827e-6
begining = 55.752361111111114, 37.64678333333333
end = 55.755430555555556, 37.64849722222222
DATAPORT = 31415
FRONTPORT = 31416


class FrontEnd(threading.Thread):
	def run(self):
		frontsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		frontsocket.bind(('', FRONTPORT))
		frontsocket.listen(1)
		while True:
			conn, addr = frontsocket.accept()
			print "Connected from:", addr
			try:
				while True:
					data = self.queue.get()
					conn.sendall(data)
					self.queue.task_done()
			except Exception as e:
				print e




def main():
	dm = datamanager.DataManager()
	t = transroute.TransRoute(begining, end)
	dm.fetch_cells()
	print "All cells:", dm.cells
	dm.build_interpols()

	datasocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	datasocket.bind(('', DATAPORT))

	q = Queue.Queue()
	frontend = FrontEnd()
	frontend.queue = q
	frontend.start()

	f = open("rawdata.log", "w", 0)

	erf = open("errors.log", "w", 0)

	while True:
		data = datasocket.recv(65535)
		print "Received:", data
		jsondata = json.loads(data)
		valid_data = validator.validator(jsondata)
		if valid_data:
			print "True lat:", valid_data['GPS']['ltd'], "true lon:", valid_data['GPS']['lng'], "true acc:", valid_data['GPS']['acc']
			closest = t.closest(valid_data)
			closest = closest[1], closest[0]
			gpsdist = t.point_to_dist(valid_data)
			pos = valid_data['GPS']['ltd'], valid_data['GPS']['lng']
			dlat = pos[0] - closest[0]
			dlon = pos[1] - closest[1]
			err = math.sqrt(dlat*dlat + dlon*dlon)/meter
			print "closest lat:", closest[0], "closest lon:", closest[1], "it's", err, "meters away"
			print "Dist by GPS:", gpsdist/meter
			gpsroute = {"ltd": closest[0], "lng":closest[1], "dstd":gpsdist, "dstm": gpsdist/meter, "fromtruem": err}
			cells_rssi = []
			for cell in valid_data['GSM']['cells']:
				cells_rssi.append([cell['CID'], cell['RSSI']])
			gsmdist = dm.position(cells_rssi, 0, 400*meter, 0.5*meter)
			gsmpos = t.dist_to_longlat(gsmdist)
			print "Dist by GSM:", gsmdist/meter, "\n\n\n"
			response = {}
			response['TrueGPS'] = valid_data['GPS']
			response['RouteGPS'] = gpsroute
			response['RouteGSM'] = {"dstm": gsmdist/meter, "ltd": gsmpos[0], "lng": gsmpos[1]}
			q.put(json.dumps(response)+"\n")
			f.write(json.dumps(response, sort_keys=True, indent=4))
			erf.write("%f\n" % (abs(gsmdist-gpsdist)/meter))

if __name__ == "__main__":
	main()
