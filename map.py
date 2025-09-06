import pygame
from settings import *
from pathlib import Path

class Tile(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, x, y, kind="wall"):
        super().__init__()
        self.kind = kind
        # imagem e retângulo para DRAW
        self.image = image
        self.rect = self.image.get_rect(topleft=(x * TILE, y * TILE))
        # hitbox: colisão
        if kind == "tree":
            # colisão só no "tronco": 1/3 inferior do tile
            self.hitbox = self.rect.copy()
            self.hitbox.height = TILE // 3
            self.hitbox.midbottom = self.rect.midbottom
        else:
            self.hitbox = self.rect.copy()

class Map:
    def __init__(self, map_file: str = "map.txt"):
        self.grid = []
        self.solids = pygame.sprite.Group()
        self.spawn_tile = (4, 5)  # fallback se não houver 'P' no arquivo

        # carrega sprites e faz scale pro TILE
        self.wall_img = pygame.image.load("assets/wall.png").convert_alpha()
        self.wall_img = pygame.transform.scale(self.wall_img, (TILE, TILE))

        self.tree_img = pygame.image.load("assets/tree.png").convert_alpha()
        self.tree_img = pygame.transform.scale(self.tree_img, (TILE, TILE))

        # lê o mapa
        path = Path(map_file)
        with path.open("r", encoding="utf-8") as f:
            for j, raw in enumerate(f.read().splitlines()):
                line = list(raw.rstrip("\n"))
                self.grid.append(line)
                for i, ch in enumerate(line):
                    if ch == "1":
                        self.solids.add(Tile(self.wall_img, i, j, kind="wall"))
                    elif ch == "T":
                        self.solids.add(Tile(self.tree_img, i, j, kind="tree"))
                    elif ch == "P":
                        self.spawn_tile = (i, j)

        # fundo xadrez suave (pré-draw simples)
        self.bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg.fill((20, 20, 30))
        for x in range(0, SCREEN_WIDTH, TILE):
            pygame.draw.line(self.bg, (30, 30, 45), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE):
            pygame.draw.line(self.bg, (30, 30, 45), (0, y), (SCREEN_WIDTH, y))

        # cria uma surface para tiles estáticos (draw mais barato)
        self.static_surface = self.bg.copy()
        for spr in sorted(self.solids, key=lambda s: (s.rect.y, s.rect.x)):
            self.static_surface.blit(spr.image, spr.rect.topleft)

    @property
    def spawn_px(self):
        sx, sy = self.spawn_tile
        # alinhar pela base do tile (coerente com player)
        return (sx * TILE + TILE // 2, (sy + 1) * TILE)

    def draw(self, surface: pygame.Surface):
        # só blita a camada pronta
        surface.blit(self.static_surface, (0, 0))
