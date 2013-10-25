#!/usr/bin/env python
# -*- coding: utf8 -*-

import pygame
import transroute
import sys

def main():
	size = 500, 500
	pygame.init()
	bgcolor = 0,0,0
	linecolor = 255, 0, 0
	mousecolor = 0, 255, 0
	keycolor = 127, 127, 255
	screen = pygame.display.set_mode(size)
	t = transroute.TransRoute( begining=(200, 400), end = (10,10)  )
	font = pygame.font.Font(None, 36)
	keydist = 0
	vkey = 0
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit(0)
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_DOWN:
					vkey = -1
				if event.key == pygame.K_UP:
					vkey = 1
			if event.type == pygame.KEYUP:
				vkey = 0
		keydist += vkey
		screen.fill(bgcolor)
		pygame.draw.line(screen, linecolor, (200, 400), (10, 10))
		pygame.draw.circle(screen, linecolor, (200,400), 10)
		pos = pygame.mouse.get_pos()
		print "mouse pos:", pos
		raw_data = {"GPS":{"acc":100, "lng": pos[0], "ltd":pos[1]}}
		print "raw_data:", raw_data
		closest = t.closest(raw_data)
		mousedist = t.point_to_dist(raw_data)
		mouselabel = font.render(unicode(mousedist), True, mousecolor)
		mouserect = mouselabel.get_rect()
		keylabel = font.render(unicode(keydist), True, keycolor)
		keyrect = keylabel.get_rect()
		keypos = t.dist_to_longlat(keydist)
		keypos = int(keypos[0]), int(keypos[1])
		pygame.draw.circle(screen, mousecolor, (int(closest[0]), int(closest[1])), 5)
		pygame.draw.circle(screen, keycolor, keypos, 5)
		mouserect.bottomleft = screen.get_rect().bottomleft
		screen.blit(mouselabel, mouserect)
		keyrect.bottomright = screen.get_rect().bottomright
		screen.blit(keylabel, keyrect)
		pygame.display.flip()






if __name__ == "__main__":
	main()
