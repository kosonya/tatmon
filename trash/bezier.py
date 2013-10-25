#!/usr/bin/env python
# -*- coding:utf8 -*-

import pygame
import sys
import numpy

class Activity(object):
	def __init__(self, screen_size, manager, clock):
		self.screen_size = screen_size
		self.manager = manager

	def render(self, surface):
		pass

	def process_event(self, event):
		pass

	def step(self):
		pass

	def exit(self):
		self.manager.exit(self)

class StateManager(object):
	def __init__(self, first_activity, screen_size, clock):
		self.screen_size = screen_size
		self.stack = []
		self.clock = clock
		self.call(first_activity)

	def call(self, activity):
		self.stack.append(activity(self.screen_size, self, self.clock))
	
	def exit(self, activity):
		if len(self.stack) > 1:
			for i in xrange(len(self.stack)):
				if self.stack[i] == activity:
					del self.stack[i]
	
	def render(self, surface):
		self.stack[-1].render(surface)

	def step(self):
		self.stack[-1].step()

	def process_event(self, event):
		if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]:
			self.call(ExitActivity)
		else:
			self.stack[-1].process_event(event)

class ExitActivity(Activity):
	def __init__(self, screen_size, manager, clock):
		Activity.__init__(self, screen_size, manager, clock)
		self.mask = pygame.Surface(screen_size)
		self.mask.fill((0,0,150))
		self.mask.set_alpha(20)
		font = pygame.font.Font(pygame.font.match_font("Times New Roman"), 72)
		font.set_italic(True)
		font.set_bold(True)
		self.gb = font.render(u"Goodbye!", True, (150, 150, 255))
		self.gb.set_alpha(75)

	def render(self, surface):
		surface.blit(self.mask, (0,0))
		rect = self.gb.get_rect()
		rect.center = surface.get_rect().center
		surface.blit(self.gb, rect)
		pygame.display.flip()
		sys.exit(0)

class BezierActivity(Activity):
	def __init__(self, screen_size, manager, clock):
		Activity.__init__(self, screen_size, manager, clock)
	#	self.curve = BezierCurve([(100, 100), (150, 50), (200, 200),  (250, 100)], 0.01)
		self.clock = clock
		self.spline = BezierSpline([(100, 300), (100, 100), (400, 100)])
		self.fps_label = Label(u"FPS:", u"%.2f")

	def render(self, surface):
	#	self.curve.render(surface, (0,0,255))
		self.spline.render(surface)
		self.fps_label.set_value(self.clock.get_fps())
		self.fps_label.rect.topleft = 10, 10
		self.fps_label.render(surface)

class BezierCurve(object):
	def __init__(self, points, step=0.1):
		self.points = map(numpy.array, points)
		self.step = step
		self.calculate()

	def calculate(self):
		self.curve = []
		p = self.points
		prev_t = t = 0
		while prev_t < 1:
			self.curve.append( ((1-t)**3)*p[0] + 3*t*((1-t)**2)*p[1] + 3*(t**2)*(1-t)*p[2] + (t**3)*p[3] )
			prev_t = t
			t += self.step

	def render(self, surface, color):
		pygame.draw.aalines(surface, color, False, self.curve)

class BezierSpline(object):
	def __init__(self, points):
		self.points = points
		self.curves = []
		self.create_curves(0.05)

	def create_curves(self, step=0.1):
		l = len(self.points)
		self.curves = []
		for i in xrange(l):
			prestart, start, end, postend = self.points[(i-1)%l], self.points[i%l], self.points[(i+1)%l], self.points[(i+2)%l]
			m1, m2 = self.interpoints(prestart, start, end, postend)
			self.curves.append(BezierCurve([start, m1, m2, end], step))

	def render(self, surface, color=(0,0,255)):
		for curve in self.curves:
			curve.render(surface, color)

		for curve in self.curves:
			map(lambda (x, y): pygame.draw.circle(surface, (255, 255, 0), (int(x), int(y)), 5), [curve.points[1], curve.points[2]])
			map(lambda (x, y): pygame.draw.circle(surface, (0, 255, 0), (int(x), int(y)), 10), [curve.points[0], curve.points[3]])


	def interpoints(self, prestart, start, end, postend, magic=0.2):
		#Удостоверимся, что работаем с numpy.array
		[prestart, start, end, postend] = map(numpy.array, [prestart, start, end, postend])

		#Находим направляющие векторы касательных к создаваемому сплайну в начальной и конечной точке
		start_tangent = self.get_tangent(prestart, start, end)
		end_tangent = self.get_tangent(start, end, postend)

		l = self.magnitude(start-end)

		start_inter = start + start_tangent*magic*l
		end_inter = end - end_tangent*magic*l

		return start_inter, end_inter

	def get_tangent(self, prv, cur, nxt):
		u"""Нахождение координат направляющего вектора касательной в точке cur.
		Находит оптимальную касательную как перпендикуляр к сумме векторов prv -> cur и nxt -> cur, отложенных от cur.
		Возвращает numpy.array из координат направляющего вектора найденной касательной."""
		#Удостоверимся, что работаем с numpy.array
		[prv, cur, nxt] = map(numpy.array, [prv, cur, nxt])

		#Находим векторы
		prv_cur = prv - cur
		nxt_cur = nxt - cur
	
		#Находим нормаль к искомой касательной как сумму полученных векторов, отложенных от точки cur
		norm = prv_cur + nxt_cur

		if self.magnitude(norm) == 0:
			return self.valuate(nxt_cur)

		#Находим касательную как перпендикуляр к полученному вектору
		counterclockwise = numpy.dot(numpy.array(	[[0, -1],
								[1, 0]]), norm)
		clockwise = numpy.dot(numpy.array(	[[0, 1],
							[-1, 0]] ), norm)

		tangent = min([counterclockwise, clockwise], key=lambda vec: self.angle(vec, nxt_cur))
		
		#Нормируем направляющий вектор на 1
		tangent = self.valuate(tangent)

		return tangent

	def angle(self, vec1, vec2):
		return numpy.arccos(numpy.dot(vec1, vec2)/(self.magnitude(vec1) * self.magnitude(vec2)))

	def valuate(self, arr):
		u"""Нормировка значений переданного массива на 1. Возвращает numpy.array"""
		factor = float(abs(max(arr, key=abs)))
		return arr/factor if factor != 0 else numpy.array([0, 0])

	def magnitude(self, arr):
		return numpy.sqrt(numpy.square(arr).sum())		

class Label(object):
	def __init__(self, text, form, **kwargs):
		""" self, text, form, color=(0,0,0), font="Arial", fontsize=24, align="left" """
		self.text = text
		self.form = form
		self.color = kwargs.get("color", (0,0,0))
		self.align = kwargs.get("align", "left")
		self.font = pygame.font.Font(pygame.font.match_font(kwargs.get("font", "Arial")), kwargs.get("fontsize", 24))
		self.label = self.font.render(unicode(self.text), True, self.color)
		self.rect = self.label.get_rect()
	
	def set_value(self, value):
		self.val = self.font.render(unicode(self.form) % value, True, self.color)
		valrect = self.val.get_rect()
		labrect = self.label.get_rect()
		if self.align == "left":
			valrect.topleft = labrect.bottomleft
		else:
			valrect.topright = labrect.bottomright
		self.surface = pygame.Surface( (valrect.width + labrect.width, valrect.height + labrect.height) )
		self.surface.fill((255,255,255))
		self.surface.set_colorkey((255,255,255))
		self.surface.blit(self.label, labrect)
		self.surface.blit(self.val, valrect)
		self.rect = self.surface.get_rect()
	
	def render(self, surface):
		surface.blit(self.surface, self.rect)


def main():
	size = 500, 500
	bgcolor = 255, 255, 255

	pygame.init()
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption(u"Brand new Bezier spline")

	clock = pygame.time.Clock()

	manager = StateManager(BezierActivity, size, clock)

	while True:

		clock.tick(400)

		for event in pygame.event.get():
			manager.process_event(event)

		manager.step()

		screen.fill(bgcolor)
		manager.render(screen)

		pygame.display.flip()

if __name__ == "__main__":
	main()
