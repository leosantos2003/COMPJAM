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
        original_image = pygame.image.load("assets/pullupbar.png").convert_alpha()
        self.image = pygame.transform.scale(original_image, (TILE, TILE)) # Ajustado para o tamanho do tile
        self.rect = self.image.get_rect(center=(x, y))

class Herb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Carrega a imagem do herb e a redimensiona
        original_image = pygame.image.load("assets/herb.png").convert_alpha()
        # --- CORREÇÃO APLICADA AQUI ---
        # Trocado para 'smoothscale' para uma melhor qualidade ao reduzir a imagem
        self.image = pygame.transform.smoothscale(original_image, (TILE, TILE))
        self.rect = self.image.get_rect(center=(x, y))