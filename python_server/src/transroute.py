# -*- coding: utf8 -*-
import math

#В одном метре 8.987202970605459e-06 градусов

class TransRoute(object):
	def __init__(self, begining=(55.752361111111114, 37.64678333333333), end = (55.755430555555556, 37.64849722222222)):
		self.begining = begining
		self.end = end
		self.norm_u = 1.0


	def closest(self, raw_data):
		if not raw_data:
			return None
		if not raw_data.has_key('GPS'):
			return None
		if not all (k in raw_data['GPS'] for k in ['lng', 'ltd', 'acc']):
			return
		if raw_data['GPS']['acc'] == 0.0:
			return None
		lon = float(raw_data['GPS']['lng'])
		lat = float(raw_data['GPS']['ltd'])
#		print "TransRoute.closest lat: %4.15f, lon:%4.15f" % (lat, lon)

#		blat = self.begining[0]
#		blon = self.begining[1]
#		elat = self.end[0]
#		elon = self.end[1]
#
#		lonmblon = lon - blon
#		print "lonmblon: %4.15f - %4.15f = %4.15f" % (lon, blon, lonmblon)
#		elonmblon = elon - blon
#		print "elonmblon: %4.15f - %4.15f = %4.15f" % (elon, blon, elonmblon)
#		latmblat = lat - blat
#		print "latmblat: %4.15f - %4.15f = %4.15f" % (lat, blat, latmblat)
#		elatmblat = elat - blat
#		print "elatmblat: %4.15f - %4.15f = %4.15f" % (elat, blat, elatmblat)
#		mag = (elat - blat)**2 + (elon - blon)**2
#		norm_u = ((lonmblon * elonmblon) + (latmblat * elatmblat))/mag
#		print "TransRoute.closest norm_u %9.14f" % norm_u
#		self.norm_u = norm_u
#		y = self.begining[0] + norm_u * (self.end[0] - self.begining[0])
#		x = self.begining[1] + norm_u * (self.end[1] - self.begining[1])
#		print "x:", x, "y:", y, "\n\n\n"

		x1 = self.begining[1]
		y1 = self.begining[0]
		x2 = self.end[1]
		y2 = self.end[0]
		x3 = lat
		y3 = lon

#		u = ( (x3-x1)*(x2-x1) + (y3-y1)*(y2-y1) ) / ( (x2-x1)**2 + (y2-y1)**2)
#		x = x1 + u*(x2-x1)
#		y = y1 + u*(y2-y1)

#		print "x1:", x1, "y1:", y1
#		print "x2:", x2, "y2:", y2
#		print "x3:", x3, "y3:", y3

		route_dir = x2 - x1, y2 - y1
#		print "x2-x2, y2-y1  dir:", route_dir
		rel = x3 - x1, y3 - y1
#		print "x3-x1, y3-y1  rel:", rel
		n = normalize(route_dir)
		l = n[0]*rel[0] + n[1]*rel[1]
		x = x1 + n[0]*l
		y = y1 + n[1]*l

#		print "x:", x, "y:", y, "\n\n\n\n"

		return y, x

	def point_to_dist(self, raw_data):
		closest = self.closest(raw_data)
		if not closest:
			return None
		if self.norm_u > 0:
			sign = 1
		else:
			sign = -1
		return sign * math.sqrt((closest[0]-self.begining[0])**2 + (closest[1]-self.begining[1])**2)

	def dist_to_longlat(self, dist):
		dy = self.end[0] - self.begining[0]
		dx = self.end[1] - self.begining[1]
		l = magn((dx, dy))
		y = self.begining[0] + dist*dy/l
		x = self.begining[1] + dist*dx/l
		return y, x


def normalize(vector):
	if not vector:
		return None
	if len(vector) != 2:
		return vector
	x, y = vector
	magnitude = magn(vector)
	if magnitude == 0:
		return vector
	return (vector[0]/magnitude, vector[1]/magnitude)

def dotproduct(foo, bar):
	if not foo or not bar:
		return 0
	if len(foo) != 2 or len(bar) != 2:
		return 0
	return foo[0]*bar[0] + foo[1]*bar[1]

def magn(vector):
	if not vector:
		return 0
	if len(vector) != 2:
		return 0
	x, y = vector
	return float(math.sqrt(x*x + y*y))
