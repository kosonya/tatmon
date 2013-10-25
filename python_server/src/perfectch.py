# -*- coding: utf8 -*-

import datamanager
import transroute
import socket
import validator
import json
import threading
import math
import Queue
import sys

meter = 8.9827e-6
begining = 55.752361111111114, 37.64678333333333
end = 55.755430555555556, 37.64849722222222


def main():
	dm = datamanager.DataManager()
	t = transroute.TransRoute(begining, end)

#	cell = int(sys.argv[1])

	dm.cells = [41526, 32778, 32777, 12056, 14296, 32779]

#	dm.cells = [32777]
	f = open("cell_interpol.m", "w")

	print "Building interpols"

	dm.build_interpols()

	print "Built"

	for cell in dm.cells:
		print "Processing", cell
		f.write("inetr%d = [\n" % cell)
		x = 0
		while x < 400:
			y = dm.cellfuncs[cell].value(x*meter)
			f.write("%f %f\n" % (x, y))
			x += 0.5
		f.write("];\n\n")
	f.close()
	print "Done"

	return


	cells_rssi = [ (41526, 21), (32778, 28), (32777, 20), (12056, 18), (14296, 20), (32779, 15) ]

	f = open("pseudop.m", "w")
	print "Calculationg pseudoprobabilities"


	for cid, rssi in cells_rssi:
		print "Processing", cid
		f.write("pseudop%d = [\n" % cid)
		x = 0
		while x < 400:
			p = dm.cellfuncs[cid].pseudop(x*meter, rssi)
			f.write("%f %f\n" %(x, p))
			print x, p
			x += 0.5
		f.write("];\n\n")
	f.close()
	print "Done"

	f = open("totalpseudop.m", "w")
	print "Calculation total P"

	f.write("totalp = [\n")
	x = 0
	x_max = 0
	p_max = 0
	while x < 400:
		p = dm.total_pseudop(cells_rssi, x*meter)
		f.write("%f %f\n" % (x, p))
		if p > p_max:
			x_max = x
			p_max = p
		x += 0.5
	f.write("];\n\n")
	f.close()
	print "Done"
	print "I'm at", x_max


if __name__ == "__main__":
	main()
