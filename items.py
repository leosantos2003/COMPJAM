import pygame
from settings import *
from utils import clamp

class Cigarette(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Carrega a imagem do cigarro e a redimensiona
        original_image = pygame.image.load("assets/cigarette.png").convert_alpha()
        self.image = pygame.transform.scale(original_image, (TILE, TILE)) # Ajustado para o tamanho do tile
        self.rect = self.image.get_rect(center=(x, y))

class PullUpBar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Carrega a imagem da barra e a redimensiona
        original_image = pygame.image.load("assets/pullbar.png").convert_alpha()
        self.image = pygame.transform.scale(original_image, (TILE, TILE)) # Ajustado para o tamanho do tile
        self.rect = self.image.get_rect(center=(x, y))