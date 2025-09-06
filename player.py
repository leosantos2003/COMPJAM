import pygame
from settings import *
from utils import clamp

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE
        self.rect.y = y * TILE
        self.vx = 0
        self.vy = 0

    def get_keys(self):
        self.vx = self.vy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = PLAYER_SPEED
        if self.vx and self.vy:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def update(self, dt):
        self.get_keys()
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt
        # Mantém na tela
        self.rect.x = clamp(self.rect.x, 0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = clamp(self.rect.y, 0, SCREEN_HEIGHT - self.rect.height)


