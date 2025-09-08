# utils.py
import pygame
import heapq
from collections import deque

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _rect_of(spr):
    return getattr(spr, "hitbox", spr.rect)

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

# --- Funções de Pathfinding ---

def _pos_to_tile(pos):
    from settings import TILE
    return (int(pos[0] // TILE), int(pos[1] // TILE))

def _tile_center(tx, ty):
    from settings import TILE
    return pygame.math.Vector2(tx * TILE + TILE // 2, ty * TILE + TILE // 2)

def _has_clear_los(a, b, solids):
    for s in solids:
        if _rect_of(s).clipline(a, b):
            return False
    return True

def _blocked(tx, ty, game_map):
    if ty < 0 or ty >= len(game_map.grid): return True
    if tx < 0 or tx >= len(game_map.grid[ty]): return True
    return game_map.grid[ty][tx] in ('1', 'T')

def _nearest_walkable(tx, ty, game_map, max_r=6):
    if not _blocked(tx, ty, game_map):
        return (tx, ty)
    q = deque([(tx, ty)])
    seen = {(tx, ty)}
    while q:
        x, y = q.popleft()
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if (nx, ny) in seen or abs(nx-tx)+abs(ny-ty) > max_r:
                continue
            seen.add((nx, ny))
            if not _blocked(nx, ny, game_map):
                return (nx, ny)
            q.append((nx, ny))
    return (tx, ty)

def astar(start, goal, game_map):
    if _blocked(goal[0], goal[1], game_map):
        goal = _nearest_walkable(*goal, game_map=game_map)

    def h(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    openh = [(h(start, goal), 0, start, None)]
    came = {}
    gbest = {start: 0}

    while openh:
        f, g, node, parent = heapq.heappop(openh)
        if node in came: 
            continue
        came[node] = parent
        if node == goal:
            break
        x, y = node
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if _blocked(nx, ny, game_map):
                continue
            ng = g + 1
            if ng < gbest.get((nx,ny), float('inf')):
                gbest[(nx,ny)] = ng
                heapq.heappush(openh, (ng + h((nx,ny), goal), ng, (nx,ny), node))

    if goal not in came:
        return []
    
    path = []
    curr = goal
    while curr is not None:
        path.append(curr)
        curr = came[curr]
    return path[::-1][1:]

def smooth_path(start_px, path_tiles, solids):
    if not path_tiles:
        return []
    pts = []
    cur_px = pygame.math.Vector2(start_px)
    i = 0
    while i < len(path_tiles):
        j = len(path_tiles) - 1
        chosen = i
        while j >= i:
            candidate_px = _tile_center(*path_tiles[j])
            if _has_clear_los(cur_px, candidate_px, solids):
                chosen = j
                break
            j -= 1
        pts.append(path_tiles[chosen])
        cur_px = _tile_center(*path_tiles[chosen])
        i = chosen + 1
    return pts