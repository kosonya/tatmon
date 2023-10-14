#!/usr/bin/env python
# -*- coding: utf8 -*-

import pygame
import sys
import threading
#import math
import socket
import Queue
#import transroute
import json

shared_json = ""




# !!!!! Latitude - y, Longitude - x


class Net(threading.Thread):
	def __init__(self, q, q2, host="vkphoto.auditory.ru"):
		self.queue = q
		self.exit = q2
		self.host = host
		threading.Thread.__init__(self)
	def run(self):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.host, 31416))
			while True:
				local_json = ""
				cur = ""
				while cur != "\n":
					cur = s.recv(1)
					local_json += cur

				print "local_json:", local_json
				lj = json.loads(local_json)
				self.queue.put(json.loads(local_json))
				print "sent"
				try:
					msg = self.exit.get(block=False)
					print msg
					break
				except Exception:
					pass
			s.close()
		except Exception as e:
			print e

class gpstosdl(object):
	def __init__(self, screensize, top = (55. + 45./60. + 24.48/3600.), left = (37. + 38./60. + 31.38/3600.), bottom = (55. + 45./60. + 2.46/3600.), right = (37. + 39./60. + 13.4/3600.)):
		self.pytop = 0.0
		self.pyleft = 0.0
		self.pydown = float(screensize[0])
		self.pyright = float(screensize[1])
		self.top = top
		self.down = bottom
		self.right = right
		self.left = left
		self.pydx = float(screensize[0])
		self.pydy = float(screensize[1])
		self.dy = float(self.top - self.down)
		self.dx = float(self.right - self.left)

	def gts(self, mappoint):
		laty, lonx = mappoint
		x = self.pyleft - (self.left - lonx) * self.pydx / self.dx
		y = self.pytop + (self.top - laty) * self.pydy / self.dy
		return 10+int(x), int(y)

	def stg(self, pypoint):
		x, y = pypoint
		x = float(x) - 10
		y = float(y)
		lonx = self.left - (self.pyleft - x) * self.dx / self.pydx
		laty = self.top + (self.pytop - y) * self.dy / self.pydy
		return laty, lonx



begining = 55.752361111111114, 37.64678333333333
end = 55.755430555555556, 37.64849722222222


#shared_json = cool_json

def main():
	size = 500, 500
	pygame.init()
	chizu = pygame.image.load("map.png")
	size = chizu.get_rect().size
	screen = pygame.display.set_mode(size)
	font = pygame.font.Font(None, 36)
	linecolor = 255, 255, 0
	truecolor = 0, 255, 0
	gpsroutecolor = 255, 0, 0
	gsmcolor = 128, 128, 255

	q = Queue.Queue()
	stoper = Queue.Queue()
	if len(sys.argv) == 2:
		net = Net(q, stoper, sys.argv[1])
	else:
		net = Net(q, stoper)

	net.start()
	gts = gpstosdl(screensize = size)

	shared_json = ""

	font = pygame.font.Font(None, 36)

	try:
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					stoper.put("quit!")
					sys.exit(0)
			screen.blit(chizu, chizu.get_rect())
	
	
			pygame.draw.line(screen, linecolor, gts.gts(begining), gts.gts(end), 3)
			pygame.draw.circle(screen, linecolor, gts.gts(begining), 10)
	
			try:
				shared_json = q.get(block=False)
				print "received!"
			except Exception:
				pass
	
			if shared_json:
				print "received:", shared_json
				if shared_json.has_key("RouteGSM"):
					pygame.draw.circle(screen, truecolor, gts.gts((shared_json['TrueGPS']['lng'], shared_json['TrueGPS']['ltd'])), 5)
					pygame.draw.circle(screen, gpsroutecolor, gts.gts((shared_json['RouteGPS']['lng'], shared_json['RouteGPS']['ltd'])), 5)
					pygame.draw.circle(screen, gsmcolor, gts.gts((shared_json['RouteGSM']['ltd'], shared_json['RouteGSM']['lng'])), 7)
	
					gpsdl = font.render(unicode("GPS dist: %d" % shared_json['RouteGPS']['dstm']), True, gpsroutecolor)
					gpsdl_rect = gpsdl.get_rect()
					gpsdl_rect.topleft = screen.get_rect().topleft
					screen.blit(gpsdl, gpsdl_rect)
	
					gsmdl = font.render(unicode("GSM dist: %d" % shared_json['RouteGSM']['dstm']), True, gsmcolor)
					gsmdl_rect = gsmdl.get_rect()
					gsmdl_rect.topleft = gpsdl_rect.bottomleft
					screen.blit(gsmdl, gsmdl_rect)
				elif shared_json.has_key("GPS"):
					pygame.draw.circle(screen, truecolor, gts.gts((shared_json['GPS']['lng'], shared_json['GPS']['ltd'])), 5)
					pygame.draw.circle(screen, gpsroutecolor, gts.gts((shared_json['Route']['lng'], shared_json['Route']['ltd'])), 5)
					pygame.draw.circle(screen, gsmcolor, gts.gts((shared_json['Route']['ltd'], shared_json['Route']['lng'])), 7)
	


					gpsdl = font.render(unicode("Dist: %d" % shared_json['Route']['dstm']), True, gpsroutecolor)
					gpsdl_rect = gpsdl.get_rect()
					gpsdl_rect.topleft = screen.get_rect().topleft
					screen.blit(gpsdl, gpsdl_rect)
	
					gsmdl = font.render(unicode("Err: %d" % shared_json['GPSerrm']), True, gsmcolor)
					gsmdl_rect = gsmdl.get_rect()
					gsmdl_rect.topleft = gpsdl_rect.bottomleft
					screen.blit(gsmdl, gsmdl_rect)

	
			pygame.display.flip()
	except Exception as e:
		print "Sorry, I've failed", e
		stoper.put("quit!")
		sys.exit(0)





if __name__ == "__main__":
	main()
