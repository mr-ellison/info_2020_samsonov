import pygame as pg
from pygame import Surface as Surf

from pygame.draw import circle, arc, line, rect
import pygame.transform as tform

from random import randint, choice
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

######### Colors

BLACK = (0, 0, 0) 
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255) 
PINK = (100, 100, 100)

#######

veil = Surf((W, H))
veil.fill(WHITE)
veil.set_alpha(100)

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

def drop_veil():
	sc.blit(veil, (0, 0))

####### These functions describe routines for generating starting parameters for new ENEMIES

def default_routine():
	'''
	Default ball-shaped enemy creating rountine - random integer coordinates, radius and velocity
	'''
	r = randint(25, 50)
	return (randint(r, ACTIVE_SCREEN_SIZE[0] - r), randint(r, ACTIVE_SCREEN_SIZE[1] - r)), r, vec(randint(-2, 2), randint(-2, 2))

def boss_routine():
	return ACTIVE_SCREEN_SIZE*0.5, 20, vec(choice([-5, 5]), choice([-5, 5]))

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

	def __str__(self):
		return str(self.val)

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

	def __init__(self, screen=sc, referrent='Noref', position=(0, 0), size=(200, 100), 
			click_functionality=[lambda x: None], click_arg=[]):

		super().__init__(screen, referrent, position, size)
		self.on_click = click_functionality
		self.arg = click_arg


	def click(self, displacement):
		loc = pg.mouse.get_pos() - vec(displacement)
		if self.soul.get_rect(topleft=self.loc).collidepoint(loc):
			self.on_click(*self.arg)

class Listener:
	def __init__(self, key=pg.K_SPACE, action=lambda x: None, action_args=[]):
		self.key = key
		self.action = action
		self.action_args = action_args

	def check(self, event):
		if event.key == self.key:
			self.action(*self.action_args)

#########

SCORE = SharedValue(0)

########

@unique
class EnemyType(Enum):
	'''
	An enum to store different templates for ENEMIES
	([:color:, :base_hp:, :point_value:], generation_routine)
	generation_routine is a function that returns parameters to initialize the starting position and velocity
	'''
	BASIC = ([RED, 1, 10], default_routine)
	LIEUTENANT = ([BLUE, 2, 30], default_routine)
	GENERAL = ([GREEN, 10, 500], boss_routine)
	RING = ([YELLOW, 1, 50], ring_routine)
	FIGHTER = ([YELLOW, 3, 50], default_routine)
	COWARD = ([PINK, 1, 200], default_routine)

class Enemy:
	'''
	Enemy class 
	'''
	def __init__(self, screen=active_screen, variety='BASIC', score_tracker=SCORE):
		data = EnemyType[variety].value

		self.perish = False # A flag to be able to call del from outside the class
		self.scoreboard = score_tracker # An indicator pointing to a SharedValue of the game score

		##########
		self.base_speed = 5
		########

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
	
	def take_damage(self, dmg=1):
		self.hp -= dmg

	def shift_collide(self, dx, dy):
		if dx > 0:
			self.loc = vec(self.x - 2 * dx, self.y)
			self.v = vec(-self.v[0], self.v[1])
		if dy > 0:
			self.loc = vec(self.x, self.y - 2*dy)
			self.v = vec(self.v[0], -self.v[1])
		dx, dy = 2* self.x - dx - ACTIVE_SCREEN_SIZE[0], 2* self.y - dy - ACTIVE_SCREEN_SIZE[1]
		if dx < 0:
			self.loc = vec(self.x + 2 * abs(dx), self.y)
			self.v = vec(-self.v[0], self.v[1])
		if dy < 0:
			self.loc = vec(self.x, self.y+ 2 * abs(dy))
			self.v = vec(self.v[0], -self.v[1])

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

	def hit(self, dmg=0):
		'''	
		Determines wether the point :hole_loc: is inside the enemy's hitbox
		If so, decrements hp
		'''
		pass

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
		self.shift_collide(dx, dy)

	def sketch(self):
		circle(self.soul, self.color, (self.r, self.r), self.r)

	def draw(self):
		self.sc.blit(self.soul, self.loc - vec(self.r, self.r))

	def hit(self, dmg=1):
		hole_loc = mouse_state()[0]
		if (vec(hole_loc) - self.loc).magnitude_squared() <= self.r**2:
			self.take_damage(dmg)

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
		self.shift_collide(dx, dy)

	def sketch(self):
		self.soul = Surf(2*vec(self.r_out, self.r_out)) 
		self.soul.set_colorkey(BLACK)

		circle(self.soul, self.color, (self.r_out, self.r_out), self.r_out)
		circle(self.soul, BLACK, (self.r_out, self.r_out), self.r_in)

	def draw(self):
		self.sc.blit(self.soul, self.loc - vec(self.r_out, self.r_out))

	def hit(self, dmg=1):
		hole_loc = mouse_state()[0]
		if self.r_in**2 <= (vec(hole_loc) - self.loc).magnitude_squared() <= self.r_out**2:
			self.hp -= dmg

class OrbUnreflecting(Orb): # An orb that shifts through walls instead of reflecting off them
	def move(self):
		self.loc = vec([(self.loc[i] + self.v[i]) % (ACTIVE_SCREEN_SIZE[i])  for i in range(2)])

class OrbFleeing(OrbUnreflecting): # An orb that moves away from the cursor if it gets close
	def move(self):
		cursor_loc = vec(pg.mouse.get_pos()) 
		dr = (ACTIVE_SCREEN_TOPLEFT +  self.loc - cursor_loc)
		if dr.magnitude() <= 2 * self.r:
			self.v = dr
			self.v /= self.v.magnitude()
			self.v *= self.base_speed
		super().move()

	

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

	def __init__(self, screen=active_screen, artist_func=target, button_logic='click', damage_per_hit=1):
		self.soul = Surf((30, 30), pg.SRCALPHA, 32)
		self.soul.set_colorkey(BLACK)

		self.loaded_margin = 20
		self.reload_state = 0
		self.artist = artist_func

		self.sc = screen

		self.dmg = damage_per_hit
	
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

@unique
class States(Enum):
	START_MENU = 0
	GAME = 1
	PAUSE = 2
	SAVE_MENU = 3

########

class StateMachine:
	def __init__(self, canvas=sc, state=States.START_MENU, screen=None, w=500, h=150):
		self.state = state
		self.environments = dict( zip(States, [dict() for i in States]) )

		self.screens = dict( zip(States, [None for i in States]) )
		self.screens[self.state] = Surf((w, h)) if screen is None else screen
		self.prev_layer = canvas

		self.x_d = dict( zip(States, [0 for i in States]) )
		self.y_d = dict( zip(States, [0 for i in States]) )

		self.x_d[self.state] = self.prev_layer.get_width()//2 - w//2
		self.y_d[self.state] = self.prev_layer.get_height()//2 - h//2
	
	@property
	def x(self):
		return self.x_d[self.state]

	@property
	def y(self):
		return self.y_d[self.state]
	
	@property
	def val(self):
		return str(self.state)
	
	@property
	def fields(self):
		return self.environments[self.state]

	@property
	def screen(self):
		return self.screens[self.state]

	def create_seq_field(self, name, value=[]):
		self.fields[name] = value

	def create_bool_field(self, name, value=False):
		self.fields[name] = value

	def create_str_field(self, name, value=''):
		self.fields[name] = value

	def draw_state_screen(self):
		self.prev_layer.blit(self.screen, (self.x, self.y))


def set_state(st_machine, state):
	print(f"State changed from {st_machine.state} to {state}")
	st_machine.state = state


########
STATE = StateMachine(canvas=sc, state=States.PAUSE, screen=None)
STATE.x_d[States.GAME] = 0
STATE.y_d	[States.GAME] = 0

STATE.create_seq_field('CONTROLS', [])
STATE.create_seq_field('INDICATORS', [])

def new_button(state=STATE, **kwargs):
	if 'CONTROLS' not in state.fields:
		state.fields['CONTROLS'] = []
	state.fields['CONTROLS'].append(Button(screen=STATE.screen, **kwargs))
	return state.fields['CONTROLS'][-1]

def new_listener(state=STATE, **kwargs):
	if 'LISTENERS' not in state.fields:
		state.fields['LISTENERS'] = []
	state.fields['LISTENERS'].append(Listener(**kwargs))

def new_indicator(state=STATE, **kwargs):
	if 'INDICATORS' not in state.fields:
		state.fields['INDICATORS'] = []
	state.fields['INDICATORS'].append(Indicator(screen=STATE.screen, **kwargs))
	return state.fields['INDICATORS'][-1]

def click_buttons(state=STATE):
	CONTROLS = state.fields['CONTROLS']
	displacement = (state.x, state.y)
	for btn in CONTROLS:
		btn.click(displacement)

def update_menu_items(state=STATE):
	elements = state.fields['CONTROLS'] + state.fields['INDICATORS']
	for el in elements:
		el.update()

def update_enemies(state=STATE):
	if state.state != States.GAME:
		return 
	ENEMIES = STATE.fields['ENEMIES']
	for nme in ENEMIES:
		nme.evolute()
		if nme.perish:
			del ENEMIES[ENEMIES.index(nme)]
		nme.update()

def shoot(manip, state=STATE):
	if 'ENEMIES' not in state.fields:
		return
	ENEMIES = state.fields['ENEMIES']
	if manip.reload_state < manip.loaded_margin:
			return
	else:
		manip.unload()
		for nme in ENEMIES:
			nme.hit(manip.dmg)

new_button(referrent=SharedValue('continue'), position=(25, 25), click_functionality=set_state, click_arg=[STATE, States.GAME])
new_button(referrent=SharedValue('exit'), position=(275, 25), click_functionality=pg.event.post, click_arg=[pg.event.Event(pg.QUIT)])
new_listener(key=pg.K_SPACE, action=set_state, action_args=[STATE, States.GAME])

STATE.state = States.GAME

STATE.screens[STATE.state] = sc
STATE.create_seq_field('ENEMIES', [])
STATE.create_seq_field('CONTROLS', [])
STATE.create_seq_field('INDICATORS', [])

new_listener(key=pg.K_SPACE, action=set_state, action_args=[STATE, States.PAUSE])

manip = Cursor(active_screen)
scoreboard = new_indicator(referrent=SCORE, position=(22.5, 75))

def exit_func():
	pg.event.post(pg.QUIT)

def next_wave_func():
	global STATE
	STATE.fields['ENEMIES'] += [Orb() for i in range(3)]
	STATE.fields['ENEMIES'] += [OrbFleeing(variety='COWARD')]
	STATE.fields['ENEMIES'] += [Ring()]

def clear_screen_func():
	global STATE
	STATE.fields['ENEMIES'] = []

def spawn_horde_func():
	global STATE
	STATE.fields['ENEMIES'] += [Orb() for i in range(8)]
	STATE.fields['ENEMIES'] += [Orb(variety='LIEUTENANT') for i in range(3)]
	STATE.fields['ENEMIES'] += [Ring() for i in range(5)]
	STATE.fields['ENEMIES'] += [Orb(variety='GENERAL') for i in range(3)]
	#ENEMIES += [OrbFleeing(variety='COWARD') for i in range(5)]

def call_boss_func():
	global STATE
	STATE.fields['ENEMIES'] += [Orb(variety='GENERAL')]

new_button(referrent=SharedValue('next wave'), position=(22.5, 200), click_functionality=next_wave_func)
new_button(referrent=SharedValue('exit'), position=(22.5, 575), click_functionality=pg.event.post, click_arg=[pg.event.Event(pg.QUIT)])#call_boss_func)
new_button(referrent=SharedValue('clear screen'), position=(22.5, 450), click_functionality=clear_screen_func)
new_button(referrent=SharedValue('Spawn many'), position=(22.5, 325), click_functionality=spawn_horde_func)

while not retire:
	clock.tick(FPS)

	for event in pg.event.get():
		if event.type == pg.QUIT:
			retire = True
		elif event.type == pg.MOUSEBUTTONDOWN:
			click_buttons()
			shoot(manip)
		elif event.type == pg.KEYDOWN:
			if 'LISTENERS' not in STATE.fields:
				STATE.fields['LISTENERS'] = []
			for lsnr in STATE.fields['LISTENERS']:
				lsnr.check(event)


	update_menu_items()

	if STATE.state == States.GAME:
		active_screen.fill(BLACK)
		update_enemies()
		display_edges()
		manip.draw()
		sc.blit(active_screen, ACTIVE_SCREEN_TOPLEFT)
		frame = sc.copy()
	elif STATE.state == States.PAUSE:
		sc.blit(frame, (0, 0))
		drop_veil()
		STATE.draw_state_screen()
	pg.display.update()
	sc.fill(BLACK)

pg.quit()