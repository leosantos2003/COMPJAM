import math
import pygame
from settings import *
from utils import clamp

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y): # Alterado para receber uma posição inicial
        super().__init__()
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y) # Define a posição inicial
        self.dir = pygame.math.Vector2(1, 0)  # direção "olhando"
        self.vel = pygame.math.Vector2(0, 0)

    def update(self, dt, player): # Adicionado o parâmetro 'player'
        # O alvo agora é sempre o jogador
        target = pygame.math.Vector2(player.rect.center)
        pos = pygame.math.Vector2(self.rect.center)
        delta = target - pos
        dist = delta.length()

        # Move-se em direção ao jogador se não estiver muito perto
        if dist > TILE / 2: # Evita que o inimigo "trema" em cima do jogador
            self.vel = delta.normalize() * ENEMY_SPEED
            move = self.vel * dt
            self.rect.centerx += move.x
            self.rect.centery += move.y
        else:
            self.vel = pygame.math.Vector2(0, 0)

        # Atualiza a direção para onde está se movendo
        if self.vel.length_squared() > 0:
            self.dir = self.vel.normalize()

    # Checa se player está no cone de visão
    def sees(self, player):
        to_player = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        dist = to_player.length()
        if dist > FOV_RANGE or dist == 0:
            return False
        to_player_n = to_player.normalize()
        dot = self.dir.dot(to_player_n)
        angle = math.degrees(math.acos(clamp(dot, -1, 1)))
        return angle <= FOV_DEGREES / 2

    # Desenho do cone (debug/feedback)
    def draw_fov(self, surface):
        origin = pygame.math.Vector2(self.rect.center)
        base_angle = math.degrees(math.atan2(self.dir.y, self.dir.x))
        left_a  = math.radians(base_angle - FOV_DEGREES/2)
        right_a = math.radians(base_angle + FOV_DEGREES/2)
        left_vec  = (math.cos(left_a)*FOV_RANGE,  math.sin(left_a)*FOV_RANGE)
        right_vec = (math.cos(right_a)*FOV_RANGE, math.sin(right_a)*FOV_RANGE)
        pts = [origin, origin + left_vec, origin + right_vec]
        pygame.draw.polygon(surface, (255, 100, 100), pts, width=2)