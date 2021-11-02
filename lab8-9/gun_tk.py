from random import randrange as rnd, choice
import tkinter as tk
import math
import time

# print (dir(math))

root = tk.Tk()
fr = tk.Frame(root)
root.geometry('800x600')
canv = tk.Canvas(root, bg='white')
canv.pack(fill=tk.BOTH, expand=1)

g = 2
decay = 0.5
stop_threshold = 0.1

class ball():
    def __init__(self, x=40, y=450, vx=0, vy=0):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.x = x
        self.y = y
        self.r = 10
        self.vx = vx
        self.vy = vy
        self.color = choice(['blue', 'green', 'red', 'brown'])
        self.id = canv.create_oval(
                self.x - self.r,
                self.y - self.r,
                self.x + self.r,
                self.y + self.r,
                fill=self.color
        )
        self.live = 30

    def set_coords(self):
        canv.coords(
                self.id,
                self.x - self.r,
                self.y - self.r,
                self.x + self.r,
                self.y + self.r
        )

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """

        #screen rect (20, 0), (800, 450)
        # FIXME
        global g, canv, stop_threshold
        self.x += self.vx
        self.y += self.vy
        self.vy += g

        if self.y > 600 :
            self.y = 600
            self.vy = -decay*self.vy
            self.vx *= decay

        if self.x > 800 :
            self.x = 800
            self.vx = -1* self.vx

        if abs(self.vx) < stop_threshold:
            self.vx = 0
        
        if self.vx == 0:
            self.vy = 0
        
        self.set_coords()


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

    def stopped(self):
        return self.vx**2 + self.vy**2 == 0

    def hide(self):
        global canv
        canv.coords(self.id, -10- self.r, -10-self.r, -10-self.r, -10-self.r)


class gun():
    def __init__(self, x=20, y=450):
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.id = canv.create_line(20,450,50,420,width=7) 
        self.x, self.y = x, y

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        print(f'Used {bullet} bullets')
        new_ball = ball()
        new_ball.r += 5
        self.an = math.atan((event.y-new_ball.y) / (event.x-new_ball.x))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = self.f2_power * math.sin(self.an)
        balls += [new_ball]
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event=0):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.an = math.atan((event.y-self.y) / (event.x-self.x))
        if self.f2_on:
            canv.itemconfig(self.id, fill='orange')
        else:
            canv.itemconfig(self.id, fill='black')
        canv.coords(self.id, self.x, self.y,
                    self.x + max(self.f2_power, 20) * math.cos(self.an),
                    self.y + max(self.f2_power, 20) * math.sin(self.an)
                    )

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            canv.itemconfig(self.id, fill='orange')
        else:
            canv.itemconfig(self.id, fill='black')

class Platform():
    def __init__(self, x=20, y=450, w=30, h=50):
        self.loc = x, y
        self.shape= w, h
        self.id = canv.create_rectangle(
                *self.loc, *self.shape,
                fill='green', width=2
            )
        self.gun = gun(x, y)


    def set_coords(self):
        canv.coords(
            self.id,
            self.loc[0] - self.shape[0]//2,
            self.loc[1] - self.shape[1]//2,
            self.loc[0] + self.shape[0]//2,
            self.loc[1] + self.shape[1]//2
        )

    def move(self, direct):
        print('Key pressed: ', direct)
        if direct in ('ws'):
            self.y += 5 * 1 if direct=='w' else -1
            if self.y < 0:
                self.y = 0
            if self.y > 600:
                self.y = 600
            self.set_coords()
        if direct in ('ad'):
            self.x += 5 * 1 if direct=='d' else -1
            if self.x < 0:
                self.x = 0
            if self.x > 500:
                self.x = 500
            self.set_coords()



class target():
    def __init__(self):
        self.points = 0
        self.id = canv.create_oval(0,0,0,0)
        self.id_points = canv.create_text(30,30,text = self.points,font = '28')
        self.new_target()

        self._live = 1

    @property
    def live(self):
        return self._live

    def new_target(self):
        """ Инициализация новой цели. """
        x = self.x = rnd(600, 780)
        y = self.y = rnd(300, 550)

        vx = self.vx = rnd(-5, 5)
        vy = self.vy = rnd(-5, 5)

        r = self.r = rnd(10, 50)
        color = self.color = 'red'
        canv.coords(self.id, x-r, y-r, x+r, y+r)
        canv.itemconfig(self.id, fill=color)

    def set_coords(self):
        canv.coords(
                self.id,
                self.x - self.r,
                self.y - self.r,
                self.x + self.r,
                self.y + self.r
        )

    def move(self):
        self.x += self.vx
        self.y += self.vy

        if self.y > 600 :
            self.y = 600
            self.vy = -self.vy

        if self.y < 0 :
            self.y = 0
            self.vy = -self.vy

        if self.x > 800 :
            self.x = 800
            self.vx = -self.vx

        if self.x < 500:
            self.x = 500
            self.vx = -self.vx
        self.set_coords()

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.vx = self.vy = 0
        canv.coords(self.id, -10, -10, -10, -10)
        canv.itemconfig(self.id, fill='white', width=0)
        self.points += points
        canv.itemconfig(self.id_points, text=self.points)

    def retire(self):
        self._live = False

    def __bool__(self):
        return bool(self._live)

targets = [target(), target()]
screen1 = canv.create_text(400, 300, text='', font='28')
g1 = Platform()
bullet = 0
balls = []

def hit_target(b: ball, t: target):
    if b.hittest(t) and t:
        t.retire()
        t.hit()
        b.hide()
    del t


def new_game(event=''):
    global gun, targets, screen1, balls, bullet
    for t in targets:
        t.new_target()
    bullet = 0
    balls = []
    canv.bind('<Button-1>', g1.gun.fire2_start)
    canv.bind('<ButtonRelease-1>', g1.gun.fire2_end)
    canv.bind('<Motion>', g1.gun.targetting)

    canv.bind('w', lambda e: print('w, lmao'))#g1.move('w'))
    canv.bind('a', lambda e: g1.move('a'))
    canv.bind('s', lambda e: g1.move('s'))
    canv.bind('d', lambda e: g1.move('d'))

    z = 0.03
    while any(targets) or balls:
        for i, b in enumerate(balls):
            b.move()
            if b.stopped():
                    b.hide()
                    deadman = balls[i]
                    canv.delete(deadman)
                    del deadman
            for t in targets:
                t.move()
                hit_target(b, t)
            if not any(targets):
                canv.bind('<Button-1>', '')
                canv.bind('<ButtonRelease-1>', '')
                canv.itemconfig(screen1, text='Вы уничтожили все цели за ' + str(bullet) + ' выстрелов')
        canv.update()
        time.sleep(0.03)
        g1.gun.targetting()
        g1.gun.power_up()
    canv.itemconfig(screen1, text='')
    canv.delete(gun)
    root.after(750, new_game)


new_game()

mainloop()
