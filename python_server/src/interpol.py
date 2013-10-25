#-*- coding: utf8 -*-
import numpy
import numpy.linalg

import sys
class Interpol(object):
	def __init__(self, order=10):
		self.order = order
		self.theta = [0]*(self.order+1)

	def create_vars(self, data):
		l = len(data)
		print l
		self.X = numpy.empty([l, self.order+1])
		self.Y = numpy.empty([l, 1])
		try:
			for j in xrange(l):
				for i in xrange(0,self.order+1):
					self.X[j][i] =\
						data[j][0]**i
				self.Y[j][0] = data[j][1]
		except Exception as e:
			print e
			print "i:", i, "j:", j
			print "order:", self.order
			print "data[j]:", data[j]
			print "self.X[j][i]", self.X[j][i]
			print "self.Y[j][0]:", self.Y[j][0]
			sys.exit(0)

	def solve_theta(self):
		self.theta = numpy.transpose(self.X)
		self.theta = numpy.dot(self.theta, self.X)
		self.theta = numpy.linalg.pinv(self.theta)
		self.theta = numpy.dot(self.theta,\
					numpy.transpose(self.X))
		self.theta = numpy.dot(self.theta, self.Y)

	def value(self, x):
		res = 0
		for i in xrange(0, self.order+1):
			res += self.theta[i] * x**i
		return res


	def pseudop(self, x, y):
		return 1.0/(1.0+(self.value(x)-float(y))**2)
