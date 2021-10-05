#15_1
import pygame
from pygame import Color as clr
from pygame.draw import ellipse, rect, polygon
from pygame.gfxdraw import bezier#, aaellipse
from pygame.gfxdraw import polygon as gfxpolygon
from pygame.math import Vector2 as vec
from pygame.transform import rotate, smoothscale

from random import random

pygame.init()
banish = False

#////////////////Constants

FPS = 30
clock = pygame.time.Clock()
H, W = 750, 1000
sc = pygame.display.set_mode((W, H))

#Task 1 - specific constants

BIRD_LOC = vec(250, 350)
FISH_LOC = vec(0, 0)
#

DISTANT_BIRD_WIDTH = 200
DISTANT_BIRD_HEIGHT = 20
BIRD_BODY_RECT = (BIRD_LOC, vec(400, 150))
BIRD_LEG_RECT = (BIRD_LOC + vec(0.45*BIRD_BODY_RECT[1][0], 0.7*BIRD_BODY_RECT[1][1]), vec(250, 250))
BIRD_WING_RECT = (BIRD_LOC + vec(-100, -220), vec(375, 300))
BIRD_FACE_RECT = (BIRD_LOC + vec(BIRD_BODY_RECT[1][0] - 50, -15), vec(300, 100))
BIRD_TAIL_RECT = (BIRD_LOC - vec(50, -25), vec(75, 75))

###
def scale_sequence(seq, sf):
	return [sf*v for v in seq]

#//////////////// Colors

class Palette:
	def __init__(self):
		self.water = clr('#006680')
		sky = ['#ff9955', '#de87aa', '#cd87de', '#8d5fd3', '#212178']
		self.sky = list(map(clr, sky))
		self.yellow = clr('#ffdd55')
		self.black = clr('#000000')
		self.white = clr('#ffffff')

class Bird:
	def __init__(self, palette):
		self.p = palette

	def leg(self, lig_pos=0, sf=1):
		blr = scale_sequence(BIRD_LEG_RECT, sf)

		leg_surf = pygame.Surface(blr[1], pygame.SRCALPHA, 32)

		temp_canvas = pygame.Surface(sf* vec(100, 35), pygame.SRCALPHA, 32)
		ellipse(temp_canvas, self.p.white, (0, 0, sf* 100, sf* 35))
		temp_canvas = rotate(temp_canvas, -50)
		leg_surf.blit(temp_canvas, (0, 0))

		temp_canvas = pygame.Surface(sf* vec(150, 100), pygame.SRCALPHA, 32)
		ellipse(temp_canvas, self.p.white ,(-10, 20, sf* 110, sf* 25))
		temp_canvas = rotate(temp_canvas, -20)
		leg_surf.blit(temp_canvas, sf* vec(40, 50))

		return leg_surf, blr[0]

	def wings(self, sf=1):
		bwr = scale_sequence(BIRD_WING_RECT, sf)
		wing_points = (vec(0, 50), vec(175, 20), vec(250, 300))
		wing_surf = pygame.Surface(bwr[1], pygame.SRCALPHA, 32)

		wing_points = [v + vec(75, -20) for v in wing_points]
		polygon(wing_surf, self.p.white, [v*sf for v in wing_points])
		gfxpolygon(wing_surf, [v*sf for v in wing_points], self.p.black)

		wing_points = [v + vec(-75, +20) for v in wing_points]
		polygon(wing_surf, self.p.white, [v*sf for v in wing_points])
		gfxpolygon(wing_surf, [v*sf for v in wing_points], self.p.black)

		return wing_surf, bwr[0]


	def body(self, sf=1):
		bbr = scale_sequence(BIRD_BODY_RECT, sf)

		body_surf = pygame.Surface(bbr[1], pygame.SRCALPHA, 32)
		ellipse(body_surf, self.p.white, ((0, 0), bbr[1]))

		return body_surf, bbr[0]

	def face(self, sf=1):
		bfr = scale_sequence(BIRD_FACE_RECT, sf)
		neck_rect = (vec(0, 50), vec(120, 45))
		#head_surf = pygame.Surface((sf* vec(200), sf* vec(60)), pygame.SRCALPHA, 32)
		head_rect_dim = vec(90, 45)

		face_surf = pygame.Surface(bfr[1], pygame.SRCALPHA, 32)

		ellipse(face_surf, self.p.white, [sf*v for v in neck_rect]) # Neck

		beak_dims = sf*vec(60, 12)
		beak_surf = pygame.Surface(beak_dims, pygame.SRCALPHA, 32)

		rect(beak_surf, self.p.yellow, ((0, 0), beak_dims))# \Beak
		rect(beak_surf, self.p.black, ((0, 0), beak_dims), width=1)
		beak_half1 = rotate(beak_surf, 5)
		face_surf.blit(beak_half1, sf*vec(175, 45))
		beak_half2 = rotate(beak_surf, -5)
		face_surf.blit(beak_half2, sf*vec(175, 50))# Beak

		ellipse(face_surf, self.p.white, (sf*vec(90, 30), sf*head_rect_dim)) # Head
		ellipse(face_surf, self.p.black, (sf*vec(145, 40), 0.1*sf*head_rect_dim)) # Eye


		
		#rect()
		return face_surf, bfr[0]

	def tail(self, sf=1):
		btr = scale_sequence(BIRD_TAIL_RECT, sf)
		tail_points = ((75, 25), (0, 0), (0, 75), (75, 50))

		tail_surf = pygame.Surface(btr[1], pygame.SRCALPHA, 32)
		polygon(tail_surf, self.p.white, [sf*vec(p) for p in tail_points])
		gfxpolygon(tail_surf, [sf*vec(p) for p in tail_points], self.p.black)

		return tail_surf, btr[0]

################ 

class Artist: # Класс для рисования единичных объектов 
	def __init__(self, screen, palette):
		self.sc = screen
		self.p = palette

		self.seagull = Bird(self.p)

	def sky(self): # Отрисовка фона
		self.sc.fill(self.p.sky[0])

		for i in range(1, 5):
			layer = pygame.Rect(0, 0, W, H/(i+1))
			rect(self.sc, self.p.sky[i], layer)

		layer = pygame.Rect(0, 2*H/3, W, H/3) #Задник для воды без прозрачности, чтобы не было смешения с цветом фона
		rect(self.sc, self.p.water, layer)

	def water(self): # Прозрачный слой воды - фильтр для наложения поверх рыбы
		surf = pygame.Surface((W, H/3 + 1))
		surf.fill(self.p.water)
		surf.set_alpha(225)
		self.sc.blit(surf, (0, 2*H/3))

	def fish(self, pos, sf=1, rot=0):
		pass

	########### Птица

	

	def bird(self, pos, sf=1, rot=0):
		#self.sc.blit(self.seagull.wings(sf=1.2*sf)[0], scale_sequence(BIRD_WING_RECT[0], 1.2*sf))

		bird_surf = pygame.Surface((W, H), pygame.SRCALPHA, 32)

		bird_surf.blit(*self.seagull.wings())
		bird_surf.blit(*self.seagull.tail())

		bird_surf.blit(*self.seagull.body())

		bird_surf.blit(self.seagull.leg()[0], (BIRD_LEG_RECT[0] - vec(50, 0)))
		bird_surf.blit(self.seagull.leg()[0], (BIRD_LEG_RECT[0] + vec(50, 0)))

		bird_surf.blit(*self.seagull.face())

		self.sc.blit(smoothscale(bird_surf, tuple(map(int, sf*vec(W, H)))), (0, 0))


	def distant_bird(self, pos, rot=0, sf=1):
		w = DISTANT_BIRD_WIDTH*sf
		h = DISTANT_BIRD_HEIGHT*sf

		ld = vec(0, h) 
		lu = vec(w/4, 0)
		ru = vec(3*w/4, 0)
		rd = vec(w, h)

		bird = pygame.Surface((w, h), pygame.SRCALPHA, 32)
		bird = bird.convert_alpha()

		bezier(bird, (ld, lu, (w/2, h)), 20, self.p.white)
		bezier(bird, ((w/2, h), ru, rd), 20, self.p.white)
		bird = rotate(bird, rot)
		self.sc.blit(bird, pos)


#############

goya = Artist(sc, Palette())
flag = True

# Task1 - constant
#Fish_loc = (300, 550)




while not banish:
	clock.tick(FPS)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			banish = True
	if flag:
		goya.sky()
		#goya.fish(Fish_loc)
		goya.water()  
		goya.bird(BIRD_LOC)

		goya.distant_bird((700, 250), rot=20, sf=1)
		goya.distant_bird((520, 150), rot=-40, sf=0.4)
		goya.distant_bird((50, 100), rot=0, sf=0.7)

		flag = False

	pygame.display.update() 

pygame.quit()