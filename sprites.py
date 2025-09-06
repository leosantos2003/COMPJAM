import math
import pygame
from settings import *

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

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

class Cigarette(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE//2, TILE//2))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))

class PullUpBar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_color = CYAN
        self.image = pygame.Surface((TILE, TILE//3))
        self.image.fill(self.base_color)
        self.rect = self.image.get_rect(center=(x, y))

        self.hold = 0.0                # tempo acumulado de permanência
        self.hold_needed = BAR_HOLD_SECONDS
        self.cooldown_timer = 0.0      # cooldown após contar

    def progress_ratio(self):
        return clamp(self.hold / self.hold_needed, 0.0, 1.0)

    def on_count(self):
        # reseta hold e ativa cooldown
        self.hold = 0.0
        self.cooldown_timer = BAR_COOLDOWN

    def update(self, dt):
        # feedback visual simples no cooldown
        if self.cooldown_timer > 0:
            self.cooldown_timer = max(0.0, self.cooldown_timer - dt)
            # quanto mais cooldown, mais escuro
            k = 0.5 + 0.5 * (self.cooldown_timer / BAR_COOLDOWN)
            shade = (int(0*k), int(200*k), int(200*k))
            self.image.fill(shade)
        else:
            self.image.fill(self.base_color)

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

