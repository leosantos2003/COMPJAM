# map.py (Atualizado para aceitar mapas procedurais)
import pygame
from settings import *
from pathlib import Path

class Tile(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, x, y, kind="wall"):
        super().__init__()
        self.kind = kind
        self.image = image
        self.rect = self.image.get_rect(topleft=(x * TILE, y * TILE))
        if kind == "tree":
            self.hitbox = self.rect.copy()
            self.hitbox.height = TILE // 3
            self.hitbox.midbottom = self.rect.midbottom
        else:
            self.hitbox = self.rect.copy()

class Map:
    def __init__(self, map_file: str = None, grid_data=None):
        self.grid = []
        self.solids = pygame.sprite.Group()
        self.spawn_tile = (4, 5)
        self.cig_positions = []
        self.bar_positions = []

        self.wall_img = pygame.image.load("assets/wall.png").convert_alpha()
        self.wall_img = pygame.transform.scale(self.wall_img, (TILE, TILE))
        self.tree_img = pygame.image.load("assets/tree.png").convert_alpha()
        self.tree_img = pygame.transform.scale(self.tree_img, (TILE, TILE))
        self.ground_img = pygame.image.load("assets/grass.png").convert_alpha()
        self.ground_img = pygame.transform.scale(self.ground_img, (TILE, TILE))

        self.logo_img = pygame.image.load("assets/logo.png").convert()
        logo_pixel_width = 3 * TILE
        logo_pixel_height = 2 * TILE
        self.logo_img = pygame.transform.scale(self.logo_img, (logo_pixel_width, logo_pixel_height))

        # --- LÓGICA ATUALIZADA PARA CARREGAR O MAPA ---
        if grid_data:
            self.grid, self.spawn_tile, cig_coords, bar_coords = grid_data
            # Converter coordenadas de tile para pixels
            self.cig_positions = [(x * TILE + TILE // 2, y * TILE + TILE // 2) for x, y in cig_coords]
            self.bar_positions = [(x * TILE + TILE // 2, y * TILE + TILE // 2) for x, y in bar_coords]
            self._create_solids_from_grid()
        elif map_file:
            self._load_from_file(map_file)
        # ----------------------------------------------

        self.static_surface = pygame.Surface((self.width_px, self.height_px))
        self.static_surface.fill((20, 20, 30))
        for y in range(0, self.height_px, TILE):
            for x in range(0, self.width_px, TILE):
                self.static_surface.blit(self.ground_img, (x, y))

        for spr in sorted(self.solids, key=lambda s: (s.rect.y, s.rect.x)):
            self.static_surface.blit(spr.image, spr.rect.topleft)

        logo_x = (self.width_px - logo_pixel_width) / 2
        logo_y = (self.height_px - logo_pixel_height) / 2
        self.static_surface.blit(self.logo_img, (logo_x, logo_y))

    def _load_from_file(self, map_file):
        """Carrega a estrutura do mapa a partir de um arquivo .txt."""
        path = Path(map_file)
        with path.open("r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                self.grid.append(list(line.rstrip("\n")))
        self._create_solids_from_grid()

    def _create_solids_from_grid(self):
        """Cria os sprites sólidos e define posições com base na grade."""
        self.height_px = len(self.grid) * TILE
        self.width_px = len(self.grid[0]) * TILE if self.grid else 0
        
        # Limpa posições antigas caso esteja recarregando
        self.solids.empty()
        self.cig_positions.clear()
        self.bar_positions.clear()

        for j, row in enumerate(self.grid):
            for i, ch in enumerate(row):
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

    @property
    def spawn_px(self):
        sx, sy = self.spawn_tile
        return (sx * TILE + TILE // 2, (sy + 1) * TILE)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.static_surface, (0, 0))