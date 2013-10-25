#!/usr/bin/env python
# -*- coding:utf8 -*-
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
# @version $Id: sputnik.py 351 2012-07-27 05:09:23Z maxim.kovalev $
# maxim.kovalev@2012.auditory.ru

import pygame
import sys
import math
import argparse
import random

mu = 200

class Sputnik:
	def __init__(self, start_point, g_point, v, planet_r):
		self.point = float(start_point[0]), float(start_point[1])
		self.vx, self.vy = float(v[0]), float(v[1])
		self.g_point = g_point
		self.enginex = self.enginey = 0.0
		self.speed = 0.0
		self.past = []
		self.future = []
		self.zoom = 1.0
		self.planet_r = planet_r
		self.center_shift = 0, 0
		self.willfail = False


	def render(self, surface, color=(0,0,255)):

                R = (self.point[0] - self.g_point[0]), (self.point[1] - self.g_point[1])
                SMA = sma(dist(self.point, self.g_point), self.speed)
                ECC = ecc(R, (self.vx, self.vy))
                SMI = (SMA*((1+0j-ECC*ECC)**0.5)).real
		F = math.sqrt(SMA**2 - SMI**2)
		AGP = agp(R, (self.vx, self.vy))
		shiftx = int(F*math.cos(math.pi*AGP/180)*self.zoom)
		shifty = int(F*math.sin(math.pi*AGP/180)*self.zoom)
		print shiftx, shifty

		elrect = pygame.Rect(0, 0, int(SMA*2*self.zoom), int(SMI*2*self.zoom))
		elsur = pygame.Surface(  (int(SMA*2*self.zoom), int(SMI*2*self.zoom))  )  
		elsur.fill((255,255,255))
		elsur.set_colorkey((255, 255, 255))
		pygame.draw.ellipse(elsur, (255, 255, 0), elrect, 2)


		transelsur = pygame.transform.rotate(elsur, AGP)
		transelsurrect = transelsur.get_rect()
		transelsurrect.center = self.g_point
		transelsurrect = transelsurrect.move(shiftx, shifty)

		surface.blit(transelsur, transelsurrect)

		to_render = int(self.point[0]*self.zoom + self.center_shift[0]), int(self.point[1]*self.zoom + self.center_shift[1])
		pygame.draw.circle(surface, (255,0,255), to_render, 5)
		pygame.draw.line(surface, (255,0,0), to_render, (to_render[0]-self.enginex*10, to_render[1]-self.enginey*10), 3)
		if len(self.future) >= 2: pygame.draw.lines(surface, (127, 127, 0), False, map( (lambda (x, y, xv, xy): (x*self.zoom + self.center_shift[0], y*self.zoom + self.center_shift[1])), self.future))
		if len(self.past) >= 2: pygame.draw.aalines(surface, color, False, map( (lambda (x, y): (x*self.zoom+self.center_shift[0], y*self.zoom+self.center_shift[1])) , self.past))
		


	def step(self, fps=25, prediction_distance=10000, history_depth=500, ep=0.01):
		timestep = 25.0/fps
		if self.g_point == self.point:
			ax = ay = 0
		else:
			vx, vy = self.vx, self.vy
			x, y = self.point
			if len(self.future) < 3 or (x, y, vx, vy) != self.future[0]:
				self.future = []
				distance = 0
				while distance < prediction_distance:
					ax, ay = gravity(self.g_point, (x, y))
					vx += ax * 5 
					vy += ay * 5
					new_x = x + vx*5
					new_y = y + vy*5 
					distance += dist((x,y), (new_x, new_y))
					x, y = new_x, new_y 
					self.future.append( (x, y, vx, vy) )
					if dist((x, y), self.g_point) <= self.planet_r:
						self.willfail = True
						break
					else:
						self.willfail = False
			else:
				x, y, vx, vy = self.future[-1]
				del self.future[0]
				ax, ay = gravity(self.g_point, (x, y))
				vx += 25*ax/fps
				vy += 25*ay/fps
				x += 25*vx/fps
				y += 25*vy/fps
				self.future.append( (x, y, vx, vy) )
			ax, ay = gravity(self.g_point, self.point)
		ax += self.enginex*ep
		ay += self.enginey*ep
		self.vx += ax * timestep
		self.vy += ay *timestep
		x, y = self.point
		x += self.vx * timestep
		y += self.vy * timestep
		self.point = x, y
		self.speed = math.sqrt(self.vx*self.vx+self.vy*self.vy)
		self.past.append(self.point)
		if len(self.past) >= history_depth:
			del self.past[0]

	def process_event(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				self.enginey = -1
			elif event.key == pygame.K_DOWN:
				self.enginey = 1
			elif event.key == pygame.K_LEFT:
				self.enginex = -1
			elif event.key == pygame.K_RIGHT:
				self.enginex = 1
		elif event.type == pygame.KEYUP:
			if event.key in [pygame.K_UP, pygame.K_DOWN]:
				self.enginey = 0
			elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
				self.enginex = 0

def gravity(g_point, sputnik):
        global mu
	gx, gy = g_point
	sx, sy = sputnik
	dx = float(gx - sx)
	dy = float(gy - sy)
	dst = math.sqrt(dx*dx + dy*dy)
	force = mu/(dst*dst)
	fx = dx*force/dst
	fy = dy*force/dst
	return fx, fy

def sma(r, v):
        global mu
        return 1/( (2.0/r) - ( (v*v) / mu))


def vecc(rv, vv):

        global mu
        rx, ry = map(float, rv)
        vx, vy = map(float, vv)
        vsq = vx*vx + vy*vy
        r = math.sqrt(rx*rx + ry*ry)
        h = rx*vy - ry*vx
        vxh = vy*h
        vyh = -vx*h
#        r_d_v = rx*vx + ry*vy
#        ex = (1.0/mu)*(vsq*rx - r_d_v*vx) - rx/r
#        ey = (1.0/mu)*(vsq*ry - r_d_v*vy) - ry/r
#        ex = -rx*vx/(r**3) - vx/r
#        ey = -ry*vy/(r**3) - vy/r
        ex = (1.0/mu)*(vxh - mu*rx/r)
        ey = (1.0/mu)*(vyh - mu*ry/r)
	return ex, ey

def ecc(rv, vv):
        global mu
        rx, ry = map(float, rv)
        vx, vy = map(float, vv)
        vsq = vx*vx + vy*vy
        r = math.sqrt(rx*rx + ry*ry)
        h = rx*vy - ry*vx
        vxh = vy*h
        vyh = -vx*h
#        r_d_v = rx*vx + ry*vy
#        ex = (1.0/mu)*(vsq*rx - r_d_v*vx) - rx/r
#        ey = (1.0/mu)*(vsq*ry - r_d_v*vy) - ry/r
#        ex = -rx*vx/(r**3) - vx/r
#        ey = -ry*vy/(r**3) - vy/r
        ex = (1.0/mu)*(vxh - mu*rx/r)
        ey = (1.0/mu)*(vyh - mu*ry/r)

        return math.sqrt(ex*ex + ey*ey)

def project(X, Y):
        x1, x2 = map(float, X)
        y1, y2 = map(float, Y)
        dy = math.sqrt(y1*y1 + y2*y2)
        ny = y1/dy, y2/dy
        r1 = x1*ny[0]
        r2 = x2*ny[1]
        dx = math.sqrt(x1**2 + x2**2)
        dot = x1*ny[0] + x2*ny[1]
        res =  dot
        return res

def agp(rv, vv):
        global mu
        rx, ry = map(float, rv)
        vx, vy = map(float, vv)
        vsq = vx*vx + vy*vy
        r = math.sqrt(rx*rx + ry*ry)
        h = rx*vy - ry*vx
        n = -h, 0
        dn = math.sqrt(n[0]**2 + n[1]**2)
        vxh = vy*h
        vyh = -vx*h
        ex = (1.0/mu)*(vxh - mu*rx/r)
        ey = (1.0/mu)*(vyh - mu*ry/r)
        de = math.sqrt(ex*ex + ey*ey)
        res = math.acos((n[0]*ex + n[1]*ey)/(dn*de))
        if ey > 0:
            res = 2*math.pi - res
        return 180*res/math.pi

def tra(rv, vv):
        global mu
        rx, ry = map(float, rv)
        vx, vy = map(float, vv)
        vsq = vx*vx + vy*vy
        r = math.sqrt(rx*rx + ry*ry)
        h = rx*vy - ry*vx
        vxh = vy*h
        vyh = -vx*h        
        ex = (1.0/mu)*(vxh - mu*rx/r)
        ey = (1.0/mu)*(vyh - mu*ry/r)
        er = ex*rx + ey*ry
        de = math.sqrt(ex*ex + ey*ey)
        res = math.acos(er/(de*r))
        rv = rx*vx + ry*vy
        if rv < 0:
                res = math.pi*2 - res
        return 180*res/math.pi

def eca(ECC, TRA):
        ECC = ECC*math.pi/180
        TRA = TRA*math.pi/180
#        tane = math.sqrt(1-ECC**2)*math.sin(TRA)/(ECC+math.cos(TRA))
#        res = math.atan(tane)
        t = math.tan(TRA/2)/(math.sqrt((1+ECC)/(1-ECC)))
        res = 2*math.atan(t)
        return 180*res/math.pi

def _mea(ECC, ECA):
        ECC = ECC*math.pi/180
        ECA = ECA*math.pi/180
        res = ECA - ECC*math.sin(ECA)
        if res < 0:
		    res = 2*math.pi + res
        return 180*res/math.pi

def mea(ECC, TRA):
        return _mea(ECC, eca(ECC, TRA))

class Label(object):
	def __init__(self, text, form, **kwargs):
		""" self, text, form, color=(0,0,0), font="Arial", fontsize=24, align="left" """
		self.text = text
		self.form = form
		self.color = kwargs.get("color", (32,255,32))
		self.align = kwargs.get("align", "left")
		self.font = pygame.font.Font(pygame.font.match_font(kwargs.get("font", "Arial")), kwargs.get("fontsize", 24))
		self.label = self.font.render(unicode(self.text), True, self.color)
		self.rect = self.label.get_rect()
	
	def set_value(self, value):
		self.val = self.font.render(unicode(self.form) % value, True, self.color)
		valrect = self.val.get_rect()
		labrect = self.label.get_rect()
		self.surface = pygame.Surface( (valrect.width + labrect.width, valrect.height + labrect.height) )
		self.rect = self.surface.get_rect()
		if self.align == "left":
			labrect.topleft = 0,0
			valrect.topleft = labrect.bottomleft
		else:
			labrect.topright = self.rect.topright
			valrect.topright = labrect.bottomright
		self.surface.fill((255,255,255))
		self.surface.set_colorkey((255,255,255))
		self.surface.blit(self.label, labrect)
		self.surface.blit(self.val, valrect)

	
	def render(self, surface):
		surface.blit(self.surface, self.rect)



def dist(a, b):
	xa, ya = a
	xb, yb = b
	return math.sqrt( (xa-xb)**2 + (ya-yb)**2 )

def scaleblit(dst, src, zoom, center_shift = (0, 0) ):
	w, h = src.get_rect().size
	w, h = int(w*zoom), int(h*zoom)
	rect = src.get_rect()
	rect.centerx += center_shift[0]
	rect.centery += center_shift[1]
	
	dst.blit(pygame.transform.scale(src, (w, h)), rect ) 

def main():
        global mu
	size = 700, 700
	g_point = size[0]/2, size[0]/2
	bgcolor = 255, 255, 255
	planet_r = 50
	star_count = 100
	air_alt = 10

	parser = argparse.ArgumentParser(description=u"Simple sputnik emulator. Keys: UP, DOWN, LEFT, RIGHT -- start engine to corresponding direction; \"-\" -- zoom out; \"+\" -- zoom in")
	parser.add_argument("-p", "--prediction-depth", action="store", default=1000, type=int, help="Number of steps calculated while predicting the orbit. 1000 by default.") 

	parser.add_argument("-t", "--trace-depth", action="store", default=1000, type=int, help="Number of steps stored in orbit history. 1000 by default")

	parser.add_argument("-e", "--engine-power", action="store", default=0.01, type=float, help="Force of sputnik's engine. 0.01 by default")

	parser.add_argument("--tangent-speed", action="store", default=1.581, type=float, help="Initial tangent speed of sputnik. 1.581 by defaut")

	parser.add_argument("--normal-speed", action="store", default=0, type=float, help="Initial normal speed of sputnik. 0 by default.")

	parser.add_argument("-a", "--altitude", action="store", default=30, type=int, help="Initial altitude of sputnik. 30 by default")

	args = parser.parse_args()

	prediction_depth = args.prediction_depth

	history_depth = args.trace_depth

	ep = args.engine_power

	vx = args.tangent_speed
	vy = args.normal_speed
	alt = args.altitude

	pygame.init()

	sma_label = Label("Semi-major axis:", "%.2f")
	ecc_label = Label("Eccentricity:", "%.2f")
	smi_label = Label("Semi-minor axis:", "%.2f")
	per_label = Label("Periapsis (radius):", "%.2f")
	apo_label = Label("Apoapsis (radius):", "%.2f")
	agp_label = Label("Agrument of periapsis:", "%.2f")
	rad_label = Label("Radius:", "%.2f", align="right")
	t_label = Label("Period:", "%.2f")
	vs_label = Label("Vertical speed:", "%.2f", align="right")
	hs_label = Label("Horizontal speed:", "%.2f", align="right")
	tra_label = Label("True anomaly:", "%.2f", align="right")
	mea_label = Label("Mean anomaly:", "%.2f", align="right")

	alt_label = Label("Altitude:", "%.2f", align="right")
	
	speed_label = Label("Speed:", "%.2f", align="right")
	fps_label = Label("FPS:", "%.2f")

	screen = pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.HWSURFACE)
	pygame.display.set_caption(u"Sputnik")
	clock = pygame.time.Clock()

#	sputnik1 = Sputnik((g_point[0],g_point[1]-planet_r-alt), g_point, (vx, vy), planet_r)
	sputnik1 = Sputnik((g_point[0],g_point[1]+planet_r+alt), g_point, (-vx, -vy), planet_r)
#	sputnik1 = Sputnik((g_point[0]-planet_r-alt,g_point[1]), g_point, (vy, -vx), planet_r)
#	sputnik1 = Sputnik((g_point[0]+planet_r+alt,g_point[1]), g_point, (-vy, vx), planet_r)


	sputnik2 = Sputnik((g_point[0], g_point[1]-planet_r-120), g_point, (1.1, 0), planet_r)

	trace = pygame.Surface(size)
	trace.fill((255,255,255))
	trace.set_colorkey((255,255,255))


	failfont = pygame.font.Font(pygame.font.match_font("Arial"), 24)
	faillabel = failfont.render(unicode("You will fail!"), True, (255, 0, 0))
	failrect = faillabel.get_rect()
	failrect.midbottom = screen.get_rect().midbottom

	pygame.draw.circle(trace, (0,0,255), g_point, planet_r)
	for _ in xrange(70):
		r = random.randrange(2, planet_r/4)
		dr = random.randrange(1, planet_r - r)
		vect = random.random()*2*math.pi
		x = int(g_point[0] + dr*math.cos(vect))
		y = int(g_point[1] + dr*math.sin(vect))
		pygame.draw.circle(trace, (0,255,0), (x, y), r)

	pygame.draw.line(trace, (0,0,0), (g_point[0]-planet_r, g_point[1]), (g_point[1]+planet_r, g_point[1]), 2)
	rct = pygame.Rect(g_point[0]-planet_r, g_point[1]-planet_r, 2*planet_r, 2*planet_r)
	rct.width -= planet_r/4
	rct.centerx = g_point[0]
	pygame.draw.ellipse(trace, (0,0,0), rct, 2)
	rct.width -= planet_r/2
	rct.centerx = g_point[0]
	pygame.draw.ellipse(trace, (0,0,0), rct, 2)
	rct.width -= planet_r/2
	rct.centerx = g_point[0]
	pygame.draw.ellipse(trace, (0,0,0), rct, 2)
	rct.width -= planet_r/2
	rct.centerx = g_point[0]
	pygame.draw.ellipse(trace, (0,0,0), rct, 2)

	for i in xrange(air_alt):
		c = int(255/float(i+1))
		pygame.draw.circle(trace, (0,c,c), g_point, planet_r + i, 1)


	stars = pygame.Surface(size)
	stars.fill((0,0,0))
	for _ in xrange(star_count):
		center = random.randrange(1, size[0]), random.randrange(1, size[1])
		pygame.draw.circle(stars, (255,255,255), center, 1)


	sputniks = pygame.Surface(size)
	sputniks.set_colorkey((0,0,0))

	running = True
	zoom = 1.0
	d_zoom = 0.0

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit(0)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_MINUS:
					d_zoom = -0.02
				elif event.key in [pygame.K_PLUS, pygame.K_EQUALS]:
					d_zoom = 0.02
			elif event.type == pygame.KEYUP:
				if event.key in [pygame.K_PLUS, pygame.K_EQUALS, pygame.K_MINUS]:
					d_zoom = 0.0
			sputnik1.process_event(event)
			
		fps = clock.get_fps()
		if not fps: fps = 100
		if running:
			sputnik1.step(50, prediction_depth, history_depth, ep)
			sputnik2.step(50, prediction_depth, history_depth, ep)
			if dist(sputnik1.point, g_point) <= planet_r:
				running = False
		if zoom > 0:
			zoom += d_zoom
		else:
			zoom = 0.02

		center = screen.get_rect().center
		fake_center = center[0]*float(zoom), center[1]*float(zoom)
		center_shift = center[0] - fake_center[0], center[1] - fake_center[1]

		sputnik1.center_shift = center_shift
		sputnik2.center_shift = center_shift
		sputnik1.zoom = zoom
		sputnik2.zoom = zoom

		screen.blit(stars, (0, 0))

		sputniks.fill((0,0,0))
		sputnik2.render(sputniks, (0,255,0))
		sputnik1.render(sputniks)
		scaleblit(screen, trace, zoom, center_shift)
		scaleblit(screen, sputniks, 1)

		if sputnik1.willfail:
			screen.blit(faillabel, failrect)

                R = (sputnik1.point[0] - g_point[0]), (sputnik1.point[1] - g_point[1])
                SMA = sma(dist(sputnik1.point, g_point), sputnik1.speed)
                RAD = dist(sputnik1.point, g_point)
                ALT = RAD -planet_r
                ECC = ecc(R, (sputnik1.vx, sputnik1.vy))
                SMI = SMA*((1+0j-ECC*ECC)**0.5)
                VS = project((sputnik1.vx, sputnik1.vy), R)
                HS = project((sputnik1.vx, sputnik1.vy), (-R[1], R[0]))
                APO = (1+ECC)*SMA
                PER = SMA - ECC*SMA
                T = (2*math.pi*(0j+SMA**3/mu)**(0.5)).real
                AGP = agp(R, (sputnik1.vx, sputnik1.vy))
                TRA = tra(R, (sputnik1.vx, sputnik1.vy))
                MEA = mea(ECC, TRA)

		rad_label.set_value(RAD)
		rad_label.rect.topright = size[0] - 10, 10
		rad_label.render(screen)

		alt_label.set_value(ALT)
		alt_label.rect.topright = rad_label.rect.bottomright
		alt_label.render(screen)

		speed_label.set_value(sputnik1.speed)
		speed_label.rect.topright = alt_label.rect.bottomright
		speed_label.render(screen)

		vs_label.set_value(VS)
		vs_label.rect.topright = speed_label.rect.bottomright
		vs_label.render(screen)

		hs_label.set_value(HS)
		hs_label.rect.topright = vs_label.rect.bottomright
		hs_label.render(screen)

                tra_label.set_value(TRA)
		tra_label.rect.topright = hs_label.rect.bottomright
		tra_label.render(screen)

                mea_label.set_value(MEA)
		mea_label.rect.topright = tra_label.rect.bottomright
		mea_label.render(screen)
		

                sma_label.set_value(SMA)
                sma_label.rect.topleft = 10,10
                sma_label.render(screen)

                smi_label.set_value(SMI.real)
                smi_label.rect.topleft = sma_label.rect.bottomleft
                smi_label.render(screen)

                ecc_label.set_value(ECC)
                ecc_label.rect.topleft = smi_label.rect.bottomleft
                ecc_label.render(screen)

                per_label.set_value(PER)
                per_label.rect.topleft = ecc_label.rect.bottomleft
                per_label.render(screen)

                apo_label.set_value(APO)
                apo_label.rect.topleft = per_label.rect.bottomleft
                apo_label.render(screen)

                agp_label.set_value(AGP)
                agp_label.rect.topleft = apo_label.rect.bottomleft
                agp_label.render(screen)

		t_label.set_value(T)
		t_label.rect.topleft = agp_label.rect.bottomleft
                t_label.render(screen)


#		VECC = map(lambda x: x*10000, vecc(R, (sputnik1.vx, sputnik1.vy)))
#		print VECC
		
#		pygame.draw.line(screen, (255, 0, 0), sputnik1.point, (sputnik1.point[0] + VECC[0], sputnik1.point[1]+VECC[1]), 2)



		fps_label.set_value(fps)
		fps_label.rect.bottomleft = 10, size[1] - 10
		fps_label.render(screen)

		pygame.display.flip()
	#	clock.tick(1)

if __name__ == "__main__":
	main()
		
