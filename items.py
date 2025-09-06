import pygame
from settings import *
from utils import clamp

class Cigarette(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE//2, TILE//2))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))

class PullUpBar(pygame.sprite.Sprite):
    # CLASSE MUITO SIMPLIFICADA
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE//3))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect(center=(x, y))


