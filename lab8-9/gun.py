import math
from random import choice, randint as rnd

import pygame

from pygame.draw import line
from pygame.math import Vector2 as vec


FPS = 30

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
SPACESHIP = 0x8C86A0
GAME_COLORS = [GREY, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600

##### gravitation modelling constants
g = 2
decay = 0.5
stop_threshold = 0.1


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.loc = vec(x, y)
        self.r = 10
        self.v = vec(0, 0)
        self.color = choice(GAME_COLORS)
        self._fallen = False

    @property
    def x(self):
        return self.loc[0]

    @property
    def y(self):
        return self.loc[1]

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        # FIXME
        self.loc += self.v
        self.v += vec(0, g)

        if self.y > 600:
            self.loc[1] = 600
            self.v = self.v.elementwise() * vec(decay, -decay)

        if self.x > 800:
            self.loc[0] = 800
            self.v = self.v.elementwise() * vec(-1, 1)

        if abs(self.v[0]) < stop_threshold:
            self.v[0] = 0
        
        if self.v[0] == 0:
            self.v[1] = 0
            self._fallen = True
    @property
    def deadman(self):
        return self._fallen

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            self.loc,
            self.r
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        dx = self.x - obj.x
        dy = self.y - obj.y
        if (self.r + obj.r)**2 >= dx**2 + dy**2:
            return True
        return False

class Platform:
    def __init__(self, canvas, x=20, y=450, w=30, h=75, color=SPACESHIP):
        self.loc = vec(x, y)
        self.shape = vec(w, h)
        self.color = color
        self.sc = canvas

        self.surf = pygame.Surface(self.shape)

        self.v = vec(0, 0) # velocity - ima add Sunless Sea-like controls
    @property
    def x(self):
        return self.loc[0]
    @property
    def y(self):
        return self.loc[1]

    def get_rect(self):
        return pygame.Rect(self.loc, self.shape)
    
    def draw(self):
        self.surf.fill(self.color)
        self.sc.blit(self.surf, self.loc)
        #pygame.draw.rect(self.sc, self.color, (self.loc, self.shape))

    def move(self):
        self.loc += self.v
        if self.y < 0:
            self.loc[1] = 0
        if self.y > HEIGHT - self.shape[1]:
            self.loc[1] = HEIGHT - self.shape[1]
        if self.x < 0:
            self.loc[0] = 0
        if self.x > WIDTH//4 - self.shape[0]:
            self.loc[0] = WIDTH//4 - self.shape[0]

class Tank(Platform):
    v0 = 1.5
    max_steam = (1, 2)

    def __init__(self, canvas, *args, **kwargs):
        super().__init__(canvas, *args, **kwargs)
        self.cannon = Gun(self.sc, *(self.loc - self.shape//2))
        self.steam = vec(0, 0)

    def control(self, direct):
        if direct == 's':
            self.steam[1] = min(self.steam[1] + 1, self.max_steam[1])
        elif direct == 'w':
            self.steam[1] = max(self.steam[1] - 1, -self.max_steam[1])
        elif direct == 'a':
            self.steam[0] = max(self.steam[0] - 1, -self.max_steam[0])
        elif direct == 'd':
            self.steam[0] = min(self.steam[0] + 1, self.max_steam[0])            

    def move(self):
        self.v = self.steam * self.v0
        super().move()
        self.cannon.set_loc(self.loc + self.shape//2)

    def draw(self):
        self.surf.fill(self.color)
        if self.steam[1] >= 1:
            pygame.draw.rect(self.surf, YELLOW, 
                ((self.shape[0]//2 - 10, 4*self.shape[1]//6), 
                                (20, 10)))
        if self.steam[1] == 2:
            pygame.draw.rect(self.surf, RED, 
                ((self.shape[0]//2 - 10, 5*self.shape[1]//6), 
                                (20, 10)))
        if self.steam[1] <= -1:
            pygame.draw.rect(self.surf, YELLOW, 
                ((self.shape[0]//2 - 10, self.shape[1]//6), 
                                (20, 10)))
        if self.steam[1] == -2:
            pygame.draw.rect(self.surf, RED, 
                ((self.shape[0]//2 - 10, 0), 
                                (20, 10)))
        self.sc.blit(self.surf, self.loc)
        self.cannon.draw()

class Gun:
    def __init__(self, screen, x=20, y=450):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = WHITE
        self.loc = vec(x, y)

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen, *self.loc)
        new_ball.r += 5
        self.an = math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x))
        new_ball.v[0] = self.f2_power * math.cos(self.an)
        new_ball.v[1] = self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прице
        ливание. Зависит от положения мыши."""
        if event:
            self.an = math.atan((event.pos[1]-self.loc[1]) / (event.pos[0]-self.loc[0]))
        if self.f2_on:
            self.color = RED
        else:
            self.color = WHITE

    def set_loc(self, location):
        self.loc = location

    def draw(self):
        line(self.screen, self.color, self.loc, 
            self.loc + max(self.f2_power, 20) * 
            vec(math.cos(self.an), math.sin(self.an)),
            width = 7)

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = WHITE

class Target:
    def __init__(self, canvas):
        self.sc = canvas
        self.points = 0
        self.live = 1
        self._fallen = False
        #(((FIXME: don't work!!! How to call this functions when object is created?
        self.new_target()

    def new_target(self):
        """ Инициализация новой цели. """
        r = self.r = rnd(2, 50)

        x = rnd(WIDTH*3//4 + r, WIDTH - r)
        y = rnd(r, HEIGHT - r)
        self.loc = vec(x, y)

        self.v = vec(rnd(-5, 5), rnd(-5, 5))
        color = self.color = RED

    @property
    def x(self):
        return self.loc[0]
    @property
    def y(self):
        return self.loc[1]

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.live -= 1
        if self.live <= 0:
            self.retire()

    def retire(self):
        self._fallen = True
    @property
    def deadman(self):
        return self._fallen

    def move(self):
        self.loc += self.v

        if abs(self.y - HEIGHT//2) > HEIGHT//2 - self.r:
            self.v = self.v.elementwise() * vec(1, -1)
        if abs(self.x - 7*WIDTH//8) > WIDTH//8 - self.r:
            self.v = self.v.elementwise() * vec(-1, 1)

    def draw(self):
        pygame.draw.circle(
            self.sc,
            self.color,
            self.loc,
            self.r
        )

class Enemies:
    def __init__(self, canvas, n=2):
        self.targets = [Target(canvas) for i in range(n)]

    def new_target(self):
        self.targets += [Target(canvas)]

    def draw(self):
        for t in self.targets:
            t.draw()
    def move(self):
        for t in self.targets:
            t.move()

def handle_hits(b: Ball, ts: Enemies):
    for i, t in enumerate(ts.targets):
        if b.hittest(t):
            t.hit()
            if t.deadman:
                del ts.targets[i]



pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

clock = pygame.time.Clock()
tank = Tank(screen)
gun = tank.cannon
targets = Enemies(screen)
finished = False

def reset_screen(sc):
    sc.fill(BLACK)
    line(sc, WHITE, (WIDTH//4, 0), (WIDTH//4, HEIGHT), width=2)
    line(sc, WHITE, (3*WIDTH//4, 0), (3*WIDTH//4, HEIGHT), width=2)


while not finished:
    reset_screen(screen)
    tank.move()
    tank.draw()
    for b in balls:
        b.draw()
    targets.move()
    targets.draw()
    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)
        elif event.type == pygame.KEYDOWN and event.unicode in 'wasd':
            tank.control(event.unicode)

    for i, b in enumerate(balls):
        b.move()
        handle_hits(b, targets)

        if b.deadman:
            del balls[i]
    gun.power_up()

pygame.quit()
