# -*- coding: utf8 -*- 

import dbconn
import interpol

class DataManager(object):
	def __init__(self):
		self.conn = dbconn.DBConn()
		self.cellfuncs = {}

	def fetch_cells(self):
		self.cells = self.conn.all_cells()

	def build_interpols(self, order=10):
		for cell in self.cells:
			samples = self.conn.samples_by_cell(cell)
			print len(samples)
			func = interpol.Interpol(10)
			func.create_vars(samples)
			func.solve_theta()
			self.cellfuncs[cell] = func




	def total_pseudop(self, cells_rssi, x):
		res = 1.0
		for cid, rssi in cells_rssi:
			res *= self.cellfuncs[cid].pseudop(x, rssi)
		return res

	def position(self, cells_rssi, minx, maxx, step):
		max_x = minx
		max_p = 0
		x = minx
		while x < maxx:
			p = self.total_pseudop(cells_rssi, x)
			if p > max_p:
				max_p = p
				max_x = x
			x += step
		return max_x

