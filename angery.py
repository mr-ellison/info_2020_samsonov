import pygame
from pygame.draw import circle, line, arc

pygame.init()

#////////////// Constants

c_yellow = pygame.Color('#ffff00')
c_red = pygame.Color('#ff0000')
c_black = pygame.Color('#000000')
c_background = pygame.Color('#d9d9d9')

FPS = 30
screen = pygame.display.set_mode((400, 400))

#\\\\\\\\\\\\\\

pygame.display.update()
clock = pygame.time.Clock()
banish = False

#\\\\\\\\\\ Code before cycle
screen.fill(c_background)

c = (200, 200)
r = 100
eye_level = -25
eye_width = 30 # Actualy half-width
eye_r = 20
mouth_level = 35
mouth_width = 25 # c.f. eye_width

circle(screen, c_yellow, c, r)
circle(screen, c_black, c, r, width=1)

circle(screen, c_red, (c[0] - eye_width, c[1] + eye_level), eye_r)
circle(screen, c_red, (c[0] + eye_width, c[1] + eye_level), eye_r)

circle(screen, c_black, (c[0] - eye_width, c[1] + eye_level), eye_r/3)
circle(screen, c_black, (c[0] + eye_width, c[1] + eye_level), eye_r/3)

line(screen, c_black, 
		(c[0] - eye_width - eye_r, c[1] + eye_level - 2*eye_r + 5), 
		(c[0] - eye_width + eye_r, c[1] + eye_level - eye_r + 5), 
		width=5)
line(screen, c_black, 
		(c[0] + eye_width - eye_r, c[1] + eye_level - eye_r + 5), 
		(c[0] + eye_width + eye_r, c[1] + eye_level - 2*eye_r + 5), 
		width=5)

line(screen, c_black, (c[0] - mouth_width, c[1] + mouth_level), (c[0] +	 mouth_width, c[1] + mouth_level), width=7)

#////////////

while not banish:
	clock.tick(FPS)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			banish = True

	pygame.display.update()

pygame.quit()