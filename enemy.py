import math
import pygame
from settings import *
from utils import clamp

class Enemy(pygame.sprite.Sprite):
    def __init__(self, patrol_points):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.patrol = patrol_points[:]  # lista de (x, y) em pixels
        self.i = 0
        self.rect.center = self.patrol[self.i]
        self.dir = pygame.math.Vector2(1, 0)  # direção "olhando"
        self.vel = pygame.math.Vector2(0, 0)

    def update(self, dt):
        # anda até o próximo ponto
        target = pygame.math.Vector2(self.patrol[self.i])
        pos = pygame.math.Vector2(self.rect.center)
        delta = target - pos
        dist = delta.length()
        if dist > 2:
            self.vel = delta.normalize() * ENEMY_SPEED
            move = self.vel * dt
            self.rect.centerx += move.x
            self.rect.centery += move.y
            if self.vel.length_squared() > 0:
                self.dir = self.vel.normalize()
        else:
            # vai para o próximo e já define a direção para lá
            self.i = (self.i + 1) % len(self.patrol)
            nxt = pygame.math.Vector2(self.patrol[self.i]) - pygame.math.Vector2(self.rect.center)
            if nxt.length_squared() > 0:
                self.dir = nxt.normalize()

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


