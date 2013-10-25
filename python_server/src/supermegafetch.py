# -*- coding: utf8 -*-
import MySQLdb
import transroute
import sys
import dbconn

meter = 8.987202970605459e-06

def main():
	conn = MySQLdb.connect(host = "localhost", user = "root", db = "tatmon")
	cursor = conn.cursor()
	query = "SELECT DISTINCT CellID FROM route_rssi_data"
	cursor.execute(query)
	res = cursor.fetchall()
	print res
	cells = map(lambda x: x[0], res)
	f = open("rssi.dat", "w") 
	for cid in cells:
		f.write("cell%d = [\n" % cid)
		query = "SELECT Distance, ObservedRSSI FROM route_rssi_data WHERE CellID = %d ORDER BY Distance" % cid
		cursor.execute(query)
		for (dst, rssi) in cursor.fetchall():
			f.write("%f %d\n" % (dst/meter, rssi))
		f.write("];\n\n")
	f.close()
	cursor.close()

if __name__ == "__main__":
	main()
