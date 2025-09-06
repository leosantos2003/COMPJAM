import math
import pygame
from settings import *
from utils import clamp

def _rect_of(spr):
    return getattr(spr, "hitbox", spr.rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.dir = pygame.math.Vector2(1, 0)
        self.vel = pygame.math.Vector2(0, 0)

        self.move_speed = ENEMY_SPEED
        self.turn_speed = ENEMY_TURN_SPEED

        self.target_pos = pygame.math.Vector2(x, y)
        self.retarget_timer = 0.0

    def update(self, dt, player, solids=None):
        if solids is None: solids = []

        self.retarget_timer -= dt
        if self.retarget_timer <= 0:
            self.retarget_timer = ENEMY_RETARGET_SECONDS
            self.target_pos = pygame.math.Vector2(player.rect.center)

        pos = pygame.math.Vector2(self.rect.center)
        dist_to_target = (self.target_pos - pos).length()

        if dist_to_target > TILE / 2:
            target_dir = (self.target_pos - pos).normalize()
            self.dir = self.dir.slerp(target_dir, self.turn_speed * dt)
            self.vel = self.dir * self.move_speed
        else:
            self.vel = pygame.math.Vector2(0, 0)

        # tentativa de movimento com resolução simples de colisão por eixo
        # X
        old = pygame.math.Vector2(self.rect.center)
        self.rect.centerx += self.vel.x * dt
        for s in solids:
            if _rect_of(s).colliderect(self.rect):
                # empurra pra fora
                if self.vel.x > 0:
                    self.rect.right = _rect_of(s).left
                elif self.vel.x < 0:
                    self.rect.left = _rect_of(s).right
        # Y
        self.rect.centery += self.vel.y * dt
        for s in solids:
            if _rect_of(s).colliderect(self.rect):
                if self.vel.y > 0:
                    self.rect.bottom = _rect_of(s).top
                elif self.vel.y < 0:
                    self.rect.top = _rect_of(s).bottom

    def sees(self, player):
        to_player = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        dist = to_player.length()
        if dist > FOV_RANGE or dist == 0:
            return False
        to_player_n = to_player.normalize()
        dot = self.dir.dot(to_player_n)
        angle = math.degrees(math.acos(clamp(dot, -1, 1)))
        return angle <= FOV_DEGREES / 2

    def draw_fov(self, surface):
        origin = pygame.math.Vector2(self.rect.center)
        base_angle = math.degrees(math.atan2(self.dir.y, self.dir.x))
        left_a  = math.radians(base_angle - FOV_DEGREES/2)
        right_a = math.radians(base_angle + FOV_DEGREES/2)
        left_vec  = (math.cos(left_a)*FOV_RANGE,  math.sin(left_a)*FOV_RANGE)
        right_vec = (math.cos(right_a)*FOV_RANGE, math.sin(right_a)*FOV_RANGE)
        pts = [origin, origin + left_vec, origin + right_vec]
        pygame.draw.polygon(surface, (255, 100, 100), pts, width=2)
