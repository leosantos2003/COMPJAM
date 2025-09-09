# camera.py
import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        """Aplica o deslocamento da câmera a uma entidade (sprite)."""
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        """Aplica o deslocamento da câmera a um retângulo."""
        return rect.move(self.camera.topleft)

    def update(self, target):
        """Atualiza a posição da câmera para centralizar no alvo (jogador)."""
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # Limita o scroll da câmera para não mostrar áreas fora do mapa
        x = min(0, x)  # Borda esquerda
        y = min(0, y)  # Borda superior
        x = max(-(self.width - SCREEN_WIDTH), x)   # Borda direita
        y = max(-(self.height - SCREEN_HEIGHT), y)  # Borda inferior

        self.camera = pygame.Rect(x, y, self.width, self.height)