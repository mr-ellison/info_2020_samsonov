import pygame as pg
from pygame import Surface as Surf

from pygame.draw import circle, arc, line, rect
import pygame.transform as tform

from random import randint
from pygame.math import Vector2 as vec
from math import pi

from enum import Enum, unique

# Есть проблема - последний на экране не моргает фиолетовым


pg.init()
retire = False

####### 

FPS = 30
clock = pg.time.Clock()
H, W = 750, 1400
sc = pg.display.set_mode((W, H))

ACTIVE_SCREEN_SIZE = vec(W-300, H-100)
ACTIVE_SCREEN_TOPLEFT = vec(250, 75)
active_screen = Surf(ACTIVE_SCREEN_SIZE)

######## 

def display_edges():
	'''
	A rectangle around the edges of the game zone. Gameplay elements inside, menus and indicators - outside
	'''
	rect(sc, WHITE, (ACTIVE_SCREEN_TOPLEFT - vec(5, 5), ACTIVE_SCREEN_SIZE + vec(10, 10)), width = 10)

def mouse_state():
	'''
	Returns the position of the mouse relative to ACTIVE_SCREEN_TOPLEFT and button state sequence
	'''
	return pg.mouse.get_pos() - vec(ACTIVE_SCREEN_TOPLEFT), pg.mouse.get_pressed()

####### These functions describe routines for generating starting parameters for new enemies

def default_routine():
	'''
	Default enemy creating rountine - random integer coordinates, radius and velocity
	'''
	r = randint(25, 50)
	return (randint(r, ACTIVE_SCREEN_SIZE[0] - r), randint(r, ACTIVE_SCREEN_SIZE[1] - r)), r, vec(randint(-2, 2), randint(-2, 2))

def boss_routine():
	return ACTIVE_SCREEN_SIZE*0.5, 20, vec(-5, 5)

def ring_routine():
	r_in, r_out = 15, 25
	min_x, max_x = r_out, ACTIVE_SCREEN_SIZE[0] - r_out
	min_y, max_y = r_out, ACTIVE_SCREEN_SIZE[1] - r_out
	return (randint(min_x, max_x), randint(min_y, max_y)), vec(r_in, r_out), vec(randint(-2, 2), randint(-2, 2)), vec(randint(0, 3))

######## Functional classes

class SharedValue:
	'''
	Basically a variable I can pass into a function/instance of a class and still treat as a global variable
	An implementation of some pointer functionality
	'''

	def __init__(self, value):
		self.value = [value]

	@property
	def val(self):
		return self.value[0]

	def add(self, delta):
		self.value[0] += delta

	def switch(self):
		if type(self.value[0]) != type(False):
			return
		self.value[0] = not self.value[0]
	def set(self, value):
		self.value = [value]

class Indicator:
	'''
	A simple field on the screen with a SharedValue, the val of which it will display at all times
	'''

	font = pg.font.Font('fonts\\Ruslan Display\\RuslanDisplay.ttf', 50)

	def __init__(self, screen=sc, referrent=SharedValue('Noref'), position=(0, 0), size=(200, 100)):
		self.ref = referrent

		self.sc = screen
		self.loc = position

		self.soul = Surf(size)

	def sketch(self):
		self.soul.fill(BLACK)
		rect(self.soul, WHITE, self.soul.get_rect(), width=3)
		text_surf = self.font.render(str(self.ref.val), False, WHITE)
		x = 0.5*(self.soul.get_rect()[2] - text_surf.get_rect()[2])
		y = 0.5*(self.soul.get_rect()[3] - text_surf.get_rect()[3])

		self.soul.blit(text_surf, (x, y))

	def draw(self):
		self.sc.blit(self.soul, self.loc)

	def update(self):
		self.sketch()
		self.draw()

class Button(Indicator):
	'''
	Basically a button
	Actualy an indicator with a func that is called each time the Button instance is clicked on
	'''
	font = pg.font.Font('fonts\\Ruslan Display\\RuslanDisplay.ttf', 24)

	def __init__(self, screen=sc, referrent=SharedValue('Noref'), position=(0, 0), size=(200, 100), 
			click_functionality=[lambda x: None], click_arg=[]):

		super().__init__(screen, referrent, position, size)
		self.on_click = click_functionality
		self.arg = click_arg


	def click(self):
		loc = pg.mouse.get_pos()
		if self.soul.get_rect(topleft=self.loc).collidepoint(loc):
			self.on_click(*self.arg)


######### Colors

BLACK = (0, 0, 0) 
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255) 

#########

SCORE = SharedValue(0)

########

@unique
class EnemyType(Enum):
	'''
	An enum to store different templates for enemies
	([:color:, :base_hp:, :point_value:], generation_routine)
	generation_routine is a function that returns parameters to initialize the starting position and velocity
	'''
	BASIC = ([RED, 1, 10], default_routine)
	LIEUTENANT = ([BLUE, 3, 100], default_routine)
	GENERAL = ([GREEN, 10, 500], boss_routine)
	RING = ([YELLOW, 1, 50], ring_routine)
	FIGHTER = ([YELLOW, 3, 50], default_routine)

class Enemy:
	'''
	Enemy class 
	'''
	def __init__(self, screen=active_screen, variety='BASIC', score_tracker=SCORE):
		data = EnemyType[variety].value

		self.perish = False # A flag to be able to call del from outside the class
		self.scoreboard = score_tracker # An indicator pointing to a SharedValue of the game score
		

		self.sc = screen # Main screen to be blitted onto
		self.color, self.hp, self.points = data[0] # Basic attributes, shape-unrelated

		self.loc = (100, 100) # Default location on screen
		self.r = 50 # Default size

		self.soul = Surf(2*vec(self.r, self.r)) # A surface on which the whole shape will be drawn to be blitted onto main screen

	############# These methods will work as soon as other atrributes and methods are redefined in a child class

	def __del__(self):
		self.color = MAGENTA
		self.sketch()
		self.draw()
	
	@property
	def x(self):
		return self.loc[0]

	@property
	def y(self):
		return self.loc[1]

	def evolute(self):
		'''
		Change the enemy's state from one to the next iteration of the main cycle
		'''
		if self.hp <= 0:
			self.perish = True
			self.scoreboard.add(self.points)
			#self.color = MAGENTA
			return
		self.move()

	def update(self):
		'''
		update the enemy's representation on the active screen
		'''
		self.sketch()
		self.draw()

	############## These methods demonstrate default behaviour, need to be redefined in child classes

	def sketch(self):
		'''
		Update the inner surface that will be blitted onto the active screen
		'''
		self.soul.fill(WHITE)

	def move(self):
		'''
		Move the enemy according to its velocity, reflect off a wall if necessary
		'''
		self.loc += [(self.loc[i] + self.v[i]) % ACTIVE_SCREEN_SIZE[i] for i in range(2)]

	def draw(self):
		'''
		Blit :self.soul: onto the active screen at appropriate location
		'''
		self.sc.blit(self.soul, (100, 100))

	def hit(self):
		'''	
		Determines wether the point :hole_loc: is inside the enemy's hitbox
		If so, decrements hp
		'''
		return False

class Orb(Enemy):
	def __init__(self, screen=active_screen, variety='BASIC', score_tracker=SCORE):
		super().__init__(screen, variety, score_tracker)
		variety = EnemyType[variety].value
		self.loc, self.r, self.v = variety[1]()
		self.loc = vec(self.loc)

		self.soul = Surf(2*vec(self.r, self.r)) # Surface with the shape of the orb
		self.soul.set_colorkey(BLACK)

	def move(self):
		self.loc += self.v
		dx = self.x - (ACTIVE_SCREEN_SIZE[0] - self.r)
		dy = self.y - (ACTIVE_SCREEN_SIZE[1] - self.r)
		if dx > 0:
			self.loc = vec(self.x - 2 * dx, self.y)
			self.v = vec(-self.v[0], self.v[1])
		if dy > 0:
			self.loc = vec(self.x, self.y - 2*dy)
			self.v = vec(self.v[0], -self.v[1])
		dx, dy = self.x - self.r, self.y - self.r
		if dx < 0:
			self.loc = vec(self.x + 2 * abs(dx), self.y)
			self.v = vec(-self.v[0], self.v[1])
		if dy < 0:
			self.loc = vec(self.x, self.y+ 2 * abs(dy))
			self.v = vec(self.v[0], -self.v[1])

	def sketch(self):
		circle(self.soul, self.color, (self.r, self.r), self.r)

	def draw(self):
		self.sc.blit(self.soul, self.loc - vec(self.r, self.r))

	def hit(self):
		hole_loc = mouse_state()[0]
		if (vec(hole_loc) - self.loc).magnitude_squared() <= self.r**2:
			self.hp -= 1

class Ring(Enemy):
	def __init__(self, screen=active_screen, variety='RING', score_tracker=SCORE):
		super().__init__(screen, variety, score_tracker)
		variety = EnemyType[variety].value
		self.loc, self.r, self.v, self.dr = variety[1]()
		
		self.loc = vec(self.loc)

		self.soul = Surf(2*vec(self.r[1], self.r[1])) # Surface with the shape of the orb
		self.soul.set_colorkey(BLACK)

	@property
	def r_in(self):
		return self.r[0]

	@property
	def r_out(self):
		return self.r[1]

	def move(self):
		self.loc += self.v

		if self.r_out >= 50 or self.r_out <= 10:
			self.dr *= -1

		self.r += self.dr

		dx = self.x - (ACTIVE_SCREEN_SIZE[0] - self.r_out)
		dy = self.y - (ACTIVE_SCREEN_SIZE[1] - self.r_out)
		if dx > 0:
			self.loc = vec(self.x - 2 * dx, self.y)
			self.v = vec(-self.v[0], self.v[1])
		if dy > 0:
			self.loc = vec(self.x, self.y - 2*dy)
			self.v = vec(self.v[0], -self.v[1])
		dx, dy = self.x - self.r_out, self.y - self.r_out
		if dx < 0:
			self.loc = vec(self.x + 2 * abs(dx), self.y)
			self.v = vec(-self.v[0], self.v[1])
		if dy < 0:
			self.loc = vec(self.x, self.y+ 2 * abs(dy))
			self.v = vec(self.v[0], -self.v[1])

	def sketch(self):
		self.soul = Surf(2*vec(self.r_out, self.r_out)) 
		self.soul.set_colorkey(BLACK)

		circle(self.soul, self.color, (self.r_out, self.r_out), self.r_out)
		circle(self.soul, BLACK, (self.r_out, self.r_out), self.r_in)

	def draw(self):
		self.sc.blit(self.soul, self.loc - vec(self.r_out, self.r_out))

	def hit(self):
		hole_loc = mouse_state()[0]
		if self.r_in**2 <= (vec(hole_loc) - self.loc).magnitude_squared() <= self.r_out**2:
			self.hp -= 1

class OrbUnreflecting(Orb): # An orb that shifts through walls instead of reflecting off them
	def move(self):
		self.loc = [(self.loc[i] + self.v[i]) % (ACTIVE_SCREEN_SIZE[i] + 2* self.r) - self.r/ACTIVE_SCREEN_SIZE[i]  for i in range(2)]
	

####### Cursor artists

'''
This set of functions takes only a screen (the cursor's :soul:)
and a float between 0 and 1 representing the reloading state.
They are used to draw custom cursors, which are animated based on
what proportion of the reload time has passed
'''

def target(soul, reload_gauge_value):
	arc(soul, WHITE, ((5, 5), (20, 20)), start_angle=0, 
			stop_angle=2*pi*reload_gauge_value, width=1)
	line(soul, WHITE, (0, 15), (30, 15), width=2)
	line(soul, WHITE, (15, 0), (15, 30), width=2)

#######

class Cursor:
	'''
	Class for drawing custom dynamic cursors
	'''

	def __init__(self, screen=active_screen, artist_func=target):
		self.soul = Surf((30, 30), pg.SRCALPHA, 32)
		self.soul.set_colorkey(BLACK)

		self.loaded_margin = 20
		self.reload_state = 0
		self.artist = artist_func

		self.sc = screen

	
	def evolute(self):
		if self.reload_state >= self.loaded_margin:
			self.sketch()
			return
		self.reload_state += 1
		self.sketch()

	def unload(self):
		self.reload_state = 0

	def sketch(self):
		self.soul.fill(BLACK)
		self.artist(self.soul, self.reload_state/self.loaded_margin)

	def draw(self):
		self.evolute()
		self.sc.blit(self.soul, mouse_state()[0] - vec(15, 15))


##############

manip = Cursor(active_screen)
enemies = [Orb() for i in range(3)]
enemies.append(OrbUnreflecting())
enemies.append(Ring())

scoreboard = Indicator(referrent=SCORE, position=(22.5, 75))
update_flag = SharedValue(False)

boss_flag = SharedValue(False)
clear_flag = SharedValue(False)
many_flag = SharedValue(False)

def next_wave_func(flag):
	flag.switch()

next_wave_button = Button(referrent=SharedValue('next wave'), position=(22.5, 200), click_functionality=next_wave_func, click_arg=[update_flag])
boss_button = Button(referrent=SharedValue('boss ball'), position=(22.5, 325), click_functionality=next_wave_func, click_arg=[boss_flag])
clear_button = Button(referrent=SharedValue('clear screen'), position=(22.5, 450), click_functionality=next_wave_func, click_arg=[clear_flag])
many_button = Button(referrent=SharedValue('Spawn many'), position=(22.5, 575), click_functionality=next_wave_func, click_arg=[many_flag])

while not retire:
	clock.tick(FPS)

	for event in pg.event.get():
		if event.type == pg.QUIT:
			retire = True
		elif event.type == pg.MOUSEBUTTONDOWN:
			next_wave_button.click()
			boss_button.click()
			clear_button.click()
			many_button.click()

			if manip.reload_state < manip.loaded_margin:
				continue
			else:
				manip.unload()
				for nme in enemies:
					nme.hit()
			
	display_edges()

	if update_flag.val:
		enemies += [Orb() for i in range(3)]
		enemies += [Ring()]
		update_flag.switch()

	if boss_flag.val:
		enemies += [OrbUnreflecting(variety='GENERAL')]
		boss_flag.switch()

	if clear_flag.val:
		enemies = []
		clear_flag.switch()

	if many_flag.val:
		enemies = [Orb() for i in range(8)]
		enemies += [Orb(variety='LIEUTENANT') for i in range(3)]
		enemies += [Ring() for i in range(5)]
		enemies += [OrbUnreflecting(variety='GENERAL') for i in range(3)]
		enemies += [OrbUnreflecting(variety='LIEUTENANT') for i in range(5)]
		many_flag.switch()
	
	active_screen.fill(BLACK)

	for nme in enemies:
		nme.evolute()
		if nme.perish:
			del enemies[enemies.index(nme)]
		nme.update()

	scoreboard.update()
	next_wave_button.update()
	boss_button.update()
	many_button.update()
	clear_button.update()
	manip.draw()
	sc.blit(active_screen, ACTIVE_SCREEN_TOPLEFT)

	pg.display.update()

pg.quit()