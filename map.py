import pygame
from settings import *

class Map:
    def __init__(self):
        pass

    def draw(self, surface):
        # chão quadriculado leve
        for x in range(0, SCREEN_WIDTH, TILE):
            pygame.draw.line(surface, (30,30,45), (x,0), (x,SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE):
            pygame.draw.line(surface, (30,30,45), (0,y), (SCREEN_WIDTH,y))


