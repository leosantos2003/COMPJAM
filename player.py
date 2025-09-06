import pygame
from settings import *
from utils import clamp

def load_spritesheet_grid(path, fw, fh):
    """Corta um spritesheet em grade fw×fh e retorna frames em [linhas][colunas]."""
    sheet = pygame.image.load(path).convert_alpha()
    sw, sh = sheet.get_size()
    cols, rows = sw // fw, sh // fh
    frames = []
    for r in range(rows):
        row = []
        for c in range(cols):
            rect = pygame.Rect(c*fw, r*fh, fw, fh)
            row.append(sheet.subsurface(rect).copy())
        frames.append(row)
    return frames

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game

        # Altura correta do corte (ajustada por você)
        self.frames_grid = load_spritesheet_grid("assets/maleBase/full/advnt_full.png", 32, 64)

        # Animações
        self.idle_frames = [self.frames_grid[0][0]]
        self.walk_frames = self.frames_grid[0][1:7]

        # escala
        self.SCALE = 2

        # estado/anim
        self.state = "idle"
        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.12  # s por frame
        
        # === NOVO: Variável para guardar a direção ===
        self.direction = 'right'

        # frame inicial + rect
        frame0 = self.idle_frames[0]
        self.image = self._apply_scale(frame0)
        self.rect = self.image.get_rect()

        # Posição em float, alinhada pela base
        self.pos = pygame.math.Vector2(x * TILE + TILE / 2, (y + 1) * TILE)
        self.rect.midbottom = self.pos

        # velocidade (px/s)
        self.vx = 0.0
        self.vy = 0.0

    def _apply_scale(self, surf: pygame.Surface) -> pygame.Surface:
        # nearest-neighbor pra manter pixel art nítido
        return pygame.transform.scale(surf, (surf.get_width() * self.SCALE, surf.get_height() * self.SCALE))

    def get_keys(self):
        self.vx = self.vy = 0.0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
            # === NOVO: Atualiza a direção para a esquerda ===
            self.direction = 'left'
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
            # === NOVO: Atualiza a direção para a direita ===
            self.direction = 'right'
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = PLAYER_SPEED
        if self.vx and self.vy:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def _set_state(self):
        moving = abs(self.vx) > 1 or abs(self.vy) > 1
        new_state = "walk" if moving else "idle"
        if new_state != self.state:
            self.state = new_state
            self.anim_index = 0
            self.anim_timer = 0.0

    def _advance_anim(self, dt):
        old_midbottom = self.rect.midbottom
        frames = self.walk_frames if self.state == "walk" else self.idle_frames

        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0.0
            self.anim_index = (self.anim_index + 1) % len(frames)

        frame = frames[self.anim_index]
        
        # A imagem é escalada primeiro
        scaled_image = self._apply_scale(frame)
        
        # === NOVO: Inverte a imagem se a direção for 'left' ===
        if self.direction == 'left':
            self.image = pygame.transform.flip(scaled_image, True, False)
        else:
            self.image = scaled_image
            
        self.rect = self.image.get_rect(midbottom=old_midbottom)

    def _clamp_pos(self):
        half_w = self.rect.width * 0.5
        self.pos.x = clamp(self.pos.x, half_w, SCREEN_WIDTH - half_w)
        self.pos.y = clamp(self.pos.y, self.rect.height, SCREEN_HEIGHT)


    def update(self, dt):
        self.get_keys()
        self._set_state()

        self.pos.x += self.vx * dt
        self.pos.y += self.vy * dt

        self._clamp_pos()
        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))

        self._advance_anim(dt)
        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))