# -*- coding: utf8 -*-
import MySQLdb
import transroute

class DBConn(object):
	def __init__(self, host = "localhost", user = "root", password = "", db = "tatmon", TransRoute=transroute.TransRoute()):
		self.host = host
		self.user = user
		self.password = password
		self.db = db
		self.conn = MySQLdb.connect(host = self.host, user = self.user, db = self.db)
		self.t = TransRoute

	def save_netdata(self, raw_data):
		cursor = self.conn.cursor()
		lon = float(raw_data['GPS']['lng'])
		lat = float(raw_data['GPS']['ltd'])
		dist = self.t.point_to_dist(raw_data)
		cursor.execute("START TRANSACTION")
		for cell in raw_data['GSM']['cells']:
			cid = int(cell['CID'])
			rssi = int(cell['RSSI'])
			query = "SELECT Longitude, Latitude, CellID, ObservedRSSI FROM raw_rssi_data WHERE Longitude = %4.15f AND Latitude = %4.15f AND CellID = %d AND ObservedRSSI = %d" % (lon, lat, cid, rssi)
			cursor.execute(query)
			if cursor.fetchall():
				query = "UPDATE raw_rssi_data SET Observations = Observations + 1 WHERE Longitude = %4.15f AND Latitude = %4.15f AND CellID = %d AND ObservedRSSI = %d" % (lon, lat, cid, rssi)
			else:
				query = "INSERT INTO raw_rssi_data(Longitude, Latitude, CellID, ObservedRSSI, Observations) VALUES (%4.15f, %4.15f, %d, %d, %d)" % (lon, lat, cid, rssi, 1)
			cursor.execute(query)


			query = "SELECT Route, Distance, CellID, ObservedRSSI FROM route_rssi_data WHERE Route = %d AND Distance = %4.15f AND CellID = %d AND ObservedRSSI = %d" % (1, dist, cid, rssi)
			cursor.execute(query)
			if cursor.fetchall():
				query = "UPDATE route_rssi_data SET Observations = Observations + 1 WHERE Route = %d AND Distance = %4.15f AND CellID = %d AND ObservedRSSI = %d" % (1, dist, cid, rssi)
			else:
				query = "INSERT INTO route_rssi_data(Route, Distance, CellID, ObservedRSSI, Observations) VALUES (%d, %4.15f, %d, %d, %d)" % (1, dist, cid, rssi, 1)
			cursor.execute(query)
		cursor.execute("COMMIT")
		cursor.close()

	def avg_rssi(self, cid):
		cursor = self.conn.cursor()
		query = "SELECT Distance, ObservedRSSI, Observations FROM route_rssi_data WHERE CellID = %d" % cid
		cursor.execute(query)
		resp = cursor.fetchall()
		result = {} #{dst: (rssi_sum, total)}
		for (dst, rssi, num) in resp:
			if result.has_key(dst):
				(rssi_sum, total) = result[dst]
				rssi_sum += rssi*num
				total += num
				result[dst] = (rssi_sum, total)
			else:
				result[dst] = (rssi, num)
		for dst in result.keys():
			rssi_sum, total = result[dst]
			result[dst] = float(rssi_sum)/total
		return result


	def all_cells(self):
		cursor = self.conn.cursor()
		query = "SELECT DISTINCT CellID FROM route_rssi_data"
		cursor.execute(query)
		res = []
		for row in cursor.fetchall():
			res.append(row[0])
		cursor.close()
		return res

	def samples_by_cell(self, cid):
		cursor = self.conn.cursor()
		query = "SELECT DISTANCE, ObservedRSSI, Observations FROM route_rssi_data WHERE CellID = %d" % cid
		cursor.execute(query)
		res = []
		for row in cursor.fetchall():
#			print row
			for _ in xrange(row[2]):
				res.append((row[0], row[1]))
		cursor.close()
		return res
