# procedural_map.py (Corrigido para gerar itens corretamente)
import random
from collections import deque

class ProceduralMapGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []

    def generate_map(self, wall_chance=0.43, generations=5):
        attempts = 0
        while attempts < 100:
            self._initialize_grid(wall_chance)
            for _ in range(generations):
                self._run_generation_step()
            
            self._place_borders()
            
            largest_cave = self._find_largest_cave()
            if largest_cave:
                self._retain_largest_cave(largest_cave)
                
                floor_count = sum(row.count('.') for row in self.grid)
                total_cells = self.width * self.height
                
                if (floor_count / total_cells) >= 0.55:
                    self._place_features()
                    print(f"Mapa gerado com sucesso em {attempts + 1} tentativas.")
                    return self.grid, self.player_spawn, self.cig_positions, self.bar_positions
            
            attempts += 1
            print(f"Tentativa {attempts}: Mapa gerado inválido, tentando novamente...")

        print("Aviso: Limite de tentativas atingido. Usando o último mapa gerado.")
        self._place_features()
        return self.grid, self.player_spawn, self.cig_positions, self.bar_positions

    def _initialize_grid(self, wall_chance):
        self.grid = [['1' if random.random() < wall_chance else '.' for _ in range(self.width)] for _ in range(self.height)]

    def _run_generation_step(self):
        new_grid = [row[:] for row in self.grid]
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                wall_neighbors = self._count_wall_neighbors(x, y)
                if self.grid[y][x] == '1':
                    if wall_neighbors < 4:
                        new_grid[y][x] = '.'
                else:
                    if wall_neighbors > 4:
                        new_grid[y][x] = '1'
        self.grid = new_grid

    def _count_wall_neighbors(self, x, y):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if self.grid[y + i][x + j] == '1':
                    count += 1
        return count

    def _place_borders(self):
        for y in range(self.height):
            self.grid[y][0] = '1'
            self.grid[y][self.width - 1] = '1'
        for x in range(self.width):
            self.grid[0][x] = '1'
            self.grid[self.height - 1][x] = '1'

    def _find_largest_cave(self):
        visited = set()
        caves = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == '.' and (x, y) not in visited:
                    cave = self._flood_fill((x, y))
                    caves.append(cave)
                    visited.update(cave)
        
        return max(caves, key=len) if caves else None

    def _flood_fill(self, start_pos):
        q = deque([start_pos])
        visited = {start_pos}
        region = []
        while q:
            x, y = q.popleft()
            region.append((x, y))
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and \
                   self.grid[ny][nx] == '.' and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))
        return region

    def _retain_largest_cave(self, largest_cave):
        largest_cave_set = set(largest_cave)
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == '.' and (x, y) not in largest_cave_set:
                    self.grid[y][x] = '1'

    def _place_features(self):
        """Coloca o jogador e os itens em posições válidas no mapa."""
        floor_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == '.':
                    floor_tiles.append((x, y))
        
        if not floor_tiles:
            self.player_spawn = (self.width // 2, self.height // 2)
            self.grid[self.height // 2][self.width // 2] = 'P'
            self.cig_positions = []
            self.bar_positions = []
            return

        random.shuffle(floor_tiles)
        
        self.player_spawn = floor_tiles.pop()
        self.grid[self.player_spawn[1]][self.player_spawn[0]] = 'P' # Marca o spawn na grade
        
        num_cigs = self.width * self.height // 100
        num_bars = self.width * self.height // 150
        
        self.cig_positions = []
        self.bar_positions = []

        for _ in range(num_cigs):
            if floor_tiles:
                pos = floor_tiles.pop()
                self.cig_positions.append(pos)
                self.grid[pos[1]][pos[0]] = 'C'

        for _ in range(num_bars):
            if floor_tiles:
                pos = floor_tiles.pop()
                self.bar_positions.append(pos)
                self.grid[pos[1]][pos[0]] = 'B'