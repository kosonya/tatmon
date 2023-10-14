#!/usr/bin/env python
# -*- coding: utf8 -*-
# Copyright (C) 2011 Maxim Kovalev
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id$
# maxim.kovalev@2012.auditory.ru

import pygame
import sys
import math

def dist(p1, p2):
	(x1, y1), (x2, y2) = p1, p2
	return math.sqrt( (x1 - x2) ** 2 + (y1 - y2) ** 2 )

def gravity(direction_point, direction_mass, point_in_scope, G):
	dst = dist(direction_point, point_in_scope)
	if dst == 0:
		return 0
	acceleration_value = float(G * direction_mass) / (dst ** 2)
	dx = float(direction_point[0] - point_in_scope[0])
	dy = float(direction_point[1] - point_in_scope[1])
	ax = dx * acceleration_value / dst
	ay = dy * acceleration_value / dst
	return ax, ay

def main():
	caption = u'N body problem'
	size = 480, 480
	default_framerate = fps = 5000

	screen = pygame.display.set_mode(size)
	pygame.display.set_caption(caption)
	clock = pygame.time.Clock()

	bodies = [(100, 100), (300, 300), (100, 300)]
	
	velocities = [(1, 1), (-1, -1), (-1, 1)]

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit(0)

		accelerations = None
		fps = clock.get_fps()
		pygame.display.flip()
		clock.tick(default_framerate)

if __name__ == "__main__":
	main()
