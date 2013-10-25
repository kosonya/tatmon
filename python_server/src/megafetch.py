# -*- coding: utf8 -*-
import MySQLdb
import transroute
import sys
import dbconn

def main():
	conn = MySQLdb.connect(host = "localhost", user = "root", db = "tatmon")
	cursor = conn.cursor()
	if len(sys.argv) == 1:
		query = "SELECT CellID, sum(Observations) FROM route_rssi_data GROUP BY CellID"
		cursor.execute(query)
		print cursor.fetchall()
	else:
		cid = int(sys.argv[1])
		f = open("rssi.dat", "w")
		if len(sys.argv) == 2:
			query = "SELECT Distance, ObservedRSSI, Observations FROM route_rssi_data WHERE CellID = %d AND Observations > 16" % cid
			cursor.execute(query)

			while True:
				cur = cursor.fetchone()
				if not cur:
					break
				for _ in xrange(cur[2]):
					f.write("%4.15f %d\n" % (cur[0], cur[1]))
		else:
			c = dbconn.DBConn()
			avg_arr = c.avg_rssi(cid)
			for dst in avg_arr.keys():
				f.write("%4.15f %f\n" %(dst, avg_arr[dst]))
		f.close()
	cursor.close()

if __name__ == "__main__":
	main()
