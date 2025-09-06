import pygame
from settings import *
from utils import clamp, _rect_of

def load_spritesheet_grid(path, fw, fh):
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

        self.frames_grid = load_spritesheet_grid("assets/maleBase/full/advnt_full.png", 32, 64)
        self.idle_frames = [self.frames_grid[0][0]]
        self.walk_frames = self.frames_grid[0][1:7]
        self.SCALE = 1.2

        self.state = "idle"
        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.12
        self.direction = 'right'

        frame0 = self.idle_frames[0]
        self.image = self._apply_scale(frame0)
        self.rect = self.image.get_rect()

        # posição (se o Map tiver spawn_px, usa ele)
        if hasattr(self.game, "game_map") and hasattr(self.game.game_map, "spawn_px"):
            px, py = self.game.game_map.spawn_px
        else:
            px, py = x * TILE + TILE // 2, (y + 1) * TILE

        self.pos = pygame.math.Vector2(px, py)
        self.rect.midbottom = self.pos

        # hitbox do player (um pouco menor que o sprite)
        self.hitbox = pygame.Rect(0, 0, int(TILE * 0.6), int(TILE * 0.55))
        self.hitbox.midbottom = self.rect.midbottom


        self.vx = 0.0
        self.vy = 0.0

    def _apply_scale(self, surf: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(surf, (surf.get_width() * self.SCALE, surf.get_height() * self.SCALE))

    def get_keys(self):
        self.vx = self.vy = 0.0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED; self.direction = 'left'
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED; self.direction = 'right'
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = PLAYER_SPEED
        if self.vx and self.vy:
            self.vx *= 0.7071; self.vy *= 0.7071

    def _set_state(self):
        moving = abs(self.vx) > 1 or abs(self.vy) > 1
        if ("walk" if moving else "idle") != self.state:
            self.state = "walk" if moving else "idle"
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
        scaled = self._apply_scale(frame)
        self.image = pygame.transform.flip(scaled, True, False) if self.direction == 'left' else scaled
        self.rect = self.image.get_rect(midbottom=old_midbottom)

    def _clamp_pos(self):
        half_w = self.rect.width * 0.5
        self.pos.x = clamp(self.pos.x, half_w, SCREEN_WIDTH - half_w)
        self.pos.y = clamp(self.pos.y, self.rect.height, SCREEN_HEIGHT)

    def _collide_axis(self, solids, axis):
        for s in solids:
            r = _rect_of(s)
            if self.hitbox.colliderect(r):
                if axis == "x":
                    if self.vx > 0:
                        self.hitbox.right = r.left
                    elif self.vx < 0:
                        self.hitbox.left = r.right
                    self.pos.x = self.hitbox.centerx
                else:
                    if self.vy > 0:
                        self.hitbox.bottom = r.top
                    elif self.vy < 0:
                        self.hitbox.top = r.bottom
                    self.pos.y = self.hitbox.bottom
                # mantém sprite alinhado ao hitbox
                self.rect.midbottom = (int(self.pos.x), int(self.pos.y))

    def update(self, dt, solids=None):
        if solids is None: solids = []
        self.get_keys()
        self._set_state()

        # X
        self.pos.x += self.vx * dt
        self._clamp_pos()
        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))
        self.hitbox.midbottom = self.rect.midbottom
        self._collide_axis(solids, "x")

        # Y
        self.pos.y += self.vy * dt
        self._clamp_pos()
        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))
        self.hitbox.midbottom = self.rect.midbottom
        self._collide_axis(solids, "y")

        self._advance_anim(dt)
        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))
        self.hitbox.midbottom = self.rect.midbottom