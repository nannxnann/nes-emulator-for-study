import pygame as pg
import numpy as np


pg.init()
screen = pg.display.set_mode((640, 480))
clock = pg.time.Clock()

colors = np.array([[120, 250, 90], [250, 90, 120], [255, 255, 255]])
gridarray = np.random.randint(3, size=(32, 32))
surface = pg.surfarray.make_surface(colors[gridarray])
surface = pg.transform.scale(surface, (400, 400))  # Scaled a bit.

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    gridarray = np.random.randint(3, size=(32, 32))
    surface = pg.surfarray.make_surface(colors[gridarray])
    surface = pg.transform.scale(surface, (400, 400)) 
    screen.fill((30, 30, 30))
    screen.blit(surface, (0, 0))
    pg.display.flip()
    clock.tick(60)