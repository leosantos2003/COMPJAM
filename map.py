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
        self.cig_positions = []
        self.bar_positions = []

        # Carrega sprites e faz scale pro TILE
        self.wall_img = pygame.image.load("assets/wall.png").convert_alpha()
        self.wall_img = pygame.transform.scale(self.wall_img, (TILE, TILE))

        self.tree_img = pygame.image.load("assets/tree.png").convert_alpha()
        self.tree_img = pygame.transform.scale(self.tree_img, (TILE, TILE))

        self.ground_img = pygame.image.load("assets/grass.png").convert_alpha()
        self.ground_img = pygame.transform.scale(self.ground_img, (TILE, TILE))

        # 1. Carrega e prepara a imagem da logo (já existente)
        self.logo_img = pygame.image.load("assets/logo.png").convert()
        logo_pixel_width = 3 * TILE
        logo_pixel_height = 2 * TILE
        self.logo_img = pygame.transform.scale(self.logo_img, (logo_pixel_width, logo_pixel_height))

        # Lê o mapa
        path = Path(map_file)
        with path.open("r", encoding="utf-8") as f:
            for j, raw in enumerate(f.read().splitlines()):
                line = list(raw.rstrip("\n"))
                self.grid.append(line)
                for i, ch in enumerate(line):
                    # Posição em pixels
                    px_center = i * TILE + TILE // 2
                    py_center = j * TILE + TILE // 2
                    if ch == "1":
                        self.solids.add(Tile(self.wall_img, i, j, kind="wall"))
                    elif ch == "T":
                        self.solids.add(Tile(self.tree_img, i, j, kind="tree"))
                    elif ch == "P":
                        self.spawn_tile = (i, j)
                    elif ch == "C":
                        self.cig_positions.append((px_center, py_center))
                    elif ch == "B":
                        self.bar_positions.append((px_center, py_center))

        # Cria a superfície do mapa com o chão
        self.static_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.static_surface.fill((20, 20, 30))
        # Preenche com ground.png em todos os tiles
        for y in range(0, SCREEN_HEIGHT, TILE):
            for x in range(0, SCREEN_WIDTH, TILE):
                self.static_surface.blit(self.ground_img, (x, y))

        # Desenha tiles sólidos ANTES da logo
        for spr in sorted(self.solids, key=lambda s: (s.rect.y, s.rect.x)):
            self.static_surface.blit(spr.image, spr.rect.topleft)

        # --- ALTERAÇÃO FEITA AQUI ---
        # 2. Calcula a posição para centralizar a logo na tela
        logo_x = (SCREEN_WIDTH - logo_pixel_width) / 2
        logo_y = (SCREEN_HEIGHT - logo_pixel_height) / 2
        
        # 3. Desenha a logo sobre TODOS os outros elementos estáticos
        self.static_surface.blit(self.logo_img, (logo_x, logo_y))
        # -----------------------------

    @property
    def spawn_px(self):
        sx, sy = self.spawn_tile
        # Alinhar pela base do tile (coerente com player)
        return (sx * TILE + TILE // 2, (sy + 1) * TILE)

    def draw(self, surface: pygame.Surface):
        # Só blita a camada pronta
        surface.blit(self.static_surface, (0, 0))