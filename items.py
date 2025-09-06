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


