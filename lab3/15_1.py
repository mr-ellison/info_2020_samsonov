#15_1
import pygame
from pygame import Color as clr
from pygame.draw import ellipse, circle, rect
from pygame.gfxdraw import bezier, arc

pygame.init()
banish = False

#////////////////Constants

FPS = 30
clock = pygame.time.Clock()
H, W = 500, 750
sc = pygame.display.set_mode((W, H))

#//////////////// Colors

class Palette:
	def __init__(self):
		self.water = clr('#006680')
		sky = ['#ff9955', '#de87aa', '#cd87de', '#8d5fd3', '#212178']
		self.sky = list(map(clr, sky))
		self.yellow = clr('#ffdd55')
		self.black = clr('#000000')
		self.white = clr('#ffffff')

p = Palette()

################ 

class Artist: # Класс для рисования единичных объектов 
	def __init__(self, screen, palette):
		self.sc = screen
		self.p = palette

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

	def fish(self):
		pass

	def bird(self):
		pass

	def distant_bird(self, pos, rot): 
		pass


#############

goya = Artist(sc, p)

while not banish:
	clock.tick(FPS)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			banish = True

	goya.sky()
	goya.fish()
	goya.water()
	goya.bird()

	pygame.display.update() 

pygame.quit()