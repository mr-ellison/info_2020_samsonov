import pygame
from pygame import Color as clr
from pygame.draw import ellipse, rect, polygon, circle
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
FISH_LOC = vec(500, 500)

###
def scale_sequence(seq, sf):
    return [sf*v for v in seq]

#//////////////// Colors

class Palette:
    '''
    A structure describing used colors
    '''
    def __init__(self):
        self.water = clr('#006680')
        sky = ['#ff9955', '#de87aa', '#cd87de', '#8d5fd3', '#212178']
        self.sky = list(map(clr, sky))
        self.yellow = clr('#ffdd55')
        self.black = clr('#000000')
        self.white = clr('#ffffff')
        self.fish_scales = clr('#478893')

class Bird:
    '''
    A class containing functions for drawing the bird. Used by Artist class
    '''
    def __init__(self, pos, palette):
        self.p = palette
        self.pos = pos
        
        #defining the shape of the bird
        self.BIRD_BODY_RECT = [vec(0, 0), vec(400, 150)]
        self.BIRD_LEG_RECT = [vec(0, 0) + vec(.4*BIRD_BODY_RECT[1][0], 0.8*BIRD_BODY_RECT[1][1]), vec(250, 250)]
        self.BIRD_LEG_DIST = 50
        self.BIRD_WING_RECT = [vec(0, 0) + vec(-100, -220), vec(375, 300)]
        self.BIRD_FACE_RECT = [vec(0, 0) + vec(BIRD_BODY_RECT[1][0] - 50, -15), vec(300, 100)]
        self.BIRD_TAIL_RECT = [vec(0, 0) - vec(50, -25), vec(75, 75)]


    def leg(self, lig_pos=vec(0, 0)):
        leg_surf = pygame.Surface(self.BIRD_LEG_RECT[1], pygame.SRCALPHA, 32)

        temp_canvas = pygame.Surface(vec(100, 35), pygame.SRCALPHA, 32)
        ellipse(temp_canvas, self.p.white, (0, 0, 100, 35))
        temp_canvas = rotate(temp_canvas, -50)
        leg_surf.blit(temp_canvas, (0, 0))

        temp_canvas = pygame.Surface(vec(150, 100), pygame.SRCALPHA, 32)
        ellipse(temp_canvas, self.p.white ,(-10, 20, 110, 25))
        temp_canvas = rotate(temp_canvas, -20)
        leg_surf.blit(temp_canvas, vec(40, 50))

        return leg_surf, self.BIRD_LEG_RECT[0] + self.pos + lig_pos
    
    
    def wings(self):
        bwr = self.BIRD_WING_RECT
        bwr[0] += self.pos

        wing_points = (vec(0, 50), vec(175, 20), vec(250, 300))
        wing_surf = pygame.Surface(bwr[1], pygame.SRCALPHA, 32)

        wing_points = [v + vec(75, -20) for v in wing_points]
        polygon(wing_surf, self.p.white, wing_points)
        gfxpolygon(wing_surf, wing_points, self.p.black)

        wing_points = [v + vec(-75, +20) for v in wing_points]
        polygon(wing_surf, self.p.white, wing_points)
        gfxpolygon(wing_surf, wing_points, self.p.black)

        return wing_surf, bwr[0]


    def body(self):
        bbr = self.BIRD_BODY_RECT
        bbr[0] += self.pos

        body_surf = pygame.Surface(bbr[1], pygame.SRCALPHA, 32)
        ellipse(body_surf, self.p.white, ((0, 0), bbr[1]))

        return body_surf, bbr[0]

    def face(self):
        bfr = self.BIRD_FACE_RECT
        bfr[0] += self.pos
        neck_rect = (vec(0, 50), vec(120, 45))
        head_rect_dim = vec(90, 45)

        face_surf = pygame.Surface(bfr[1], pygame.SRCALPHA, 32)

        ellipse(face_surf, self.p.white, neck_rect) # Neck

        beak_dims = vec(60, 12)
        beak_surf = pygame.Surface(beak_dims, pygame.SRCALPHA, 32)

        rect(beak_surf, self.p.yellow, ((0, 0), beak_dims))# \Beak
        rect(beak_surf, self.p.black, ((0, 0), beak_dims),1)
        beak_half1 = rotate(beak_surf, 5)
        face_surf.blit(beak_half1, vec(175, 45))
        beak_half2 = rotate(beak_surf, -5)
        face_surf.blit(beak_half2, vec(175, 50))# Beak

        ellipse(face_surf, self.p.white, (vec(90, 30), head_rect_dim)) # Head
        ellipse(face_surf, self.p.black, (vec(145, 40), 0.1*head_rect_dim)) # Eye

        return face_surf, bfr[0]

    
    def tail(self):
        btr = self.BIRD_TAIL_RECT
        btr[0] += self.pos

        tail_points = ((75, 25), (0, 0), (0, 75), (75, 50))

        tail_surf = pygame.Surface(btr[1], pygame.SRCALPHA, 32)
        polygon(tail_surf, self.p.white, tail_points)
        gfxpolygon(tail_surf, tail_points, self.p.black)

        return tail_surf, btr[0]

################ 

class Artist:
    '''
    A class for drawing objects. screen is the Surface object to draw in, palette is a Palette object with needed colors
    '''
    def __init__(self, screen, palette):
        self.sc = screen
        self.p = palette

    def sky(self):
        '''
        A function for drawing the background
        '''
        self.sc.fill(self.p.sky[0])

        for i in range(1, 5):
            layer = pygame.Rect(0, 0, self.sc.get_width(), self.sc.get_height()/(i+1))
            rect(self.sc, self.p.sky[i], layer)

        layer = pygame.Rect(0, 2*self.sc.get_height()/3, self.sc.get_width(), self.sc.get_height()/3) #Задник для воды без прозрачности, чтобы не было смешения с цветом фона
        rect(self.sc, self.p.water, layer)

    def water(self): # Прозрачный слой воды - фильтр для наложения поверх рыбы
        '''
        A function for drawing a layer of water
        '''
        surf = pygame.Surface((self.sc.get_width(), self.sc.get_height()/3 + 1))
        surf.fill(self.p.water)
        surf.set_alpha(150)
        self.sc.blit(surf, (0, 2*self.sc.get_height()/3))

    def fish(self, pos, sf=1, rot=0):
        '''
        A function for drawing a fish, pos is vec(x, y), where x and y are coordinates of
        the top left corner of rect, containing the object, sf is the scaling factor and
        rot is the rotational angle measured in degrees
        '''
        fish_surf = pygame.Surface(vec(200, 100), pygame.SRCALPHA, 32)

        polygon(fish_surf, self.p.fish_scales, (vec(0, 80), vec(75, 30), vec(0, 0)))
        polygon(fish_surf, self.p.black, (vec(0, 80), vec(75, 30), vec(0, 0)), 1)
        ellipse(fish_surf, self.p.fish_scales, ((50, 0), vec(150, 60)))
        ellipse(fish_surf, self.p.black, ((50, 0), vec(150, 60)), 1)
        circle(fish_surf, self.p.white, (175, 35), 10)
        circle(fish_surf, self.p.black, (175, 35), 7)

        fish_surf = smoothscale(fish_surf, tuple(map(int, sf*vec(200, 100))))
        fish_surf = rotate(fish_surf, rot)

        self.sc.blit(fish_surf, pos)

    ########### Птица



    def bird(self, pos, sf=1, rot=0):
        '''
        A function for drawing a bird. Relies heavily on the Bird class.
        pos is vec(x, y), where x and y are coordinates of
        the top left corner of rect, containing the object, sf is the scaling factor and
        rot is the rotational angle measured in degrees
        '''
        birdObj = Bird(pos, self.p)

        bird_surf = pygame.Surface((W, H), pygame.SRCALPHA, 32)

        bird_surf.blit(*birdObj.wings())
        bird_surf.blit(*birdObj.tail())
        bird_surf.blit(*birdObj.body())
        bird_surf.blit(*birdObj.leg(lig_pos=vec(birdObj.BIRD_LEG_DIST/2, 0)))
        bird_surf.blit(*birdObj.leg(lig_pos=vec(-birdObj.BIRD_LEG_DIST, 0)))
        bird_surf.blit(*birdObj.face())

        bird_surf = smoothscale(bird_surf, tuple(map(int, sf*vec(W, H))))
        bird_surf = rotate(bird_surf, rot)
        self.sc.blit(bird_surf, (0, 0))


    def distant_bird(self, pos, rot=0, sf=1):
        '''
        A function for drawing distant birds, pos is vec(x, y), where x and y are coordinates of
        the top left corner of rect, containing the object, sf is the scaling factor and
        rot is the rotational angle measured in degrees
        '''
        DISTANT_BIRD_WIDTH = 200
        DISTANT_BIRD_HEIGHT = 20
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

while not banish:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            banish = True
    if flag:
        goya.sky()
        goya.fish(FISH_LOC)
        goya.water()  
        goya.bird(BIRD_LOC, rot=5, sf=0.8)

        goya.distant_bird((700, 250), rot=20, sf=1)
        goya.distant_bird((520, 150), rot=-40, sf=0.4)
        goya.distant_bird((50, 100), rot=0, sf=0.7)

        flag = False

    pygame.display.update() 

pygame.quit()