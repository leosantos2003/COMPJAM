import math
import random
import heapq
import pygame
from settings import *
from utils import clamp, _rect_of

# --- helpers on tiles/pixels ---
def _pos_to_tile(pos):
    return (int(pos[0] // TILE), int(pos[1] // TILE))

def _tile_center(tx, ty):
    return pygame.math.Vector2(tx * TILE + TILE // 2, ty * TILE + TILE // 2)

def _has_clear_los(a, b, solids):
    """Line of sight entre dois pontos em pixels (sem clipline em sólidos)."""
    for s in solids:
        if _rect_of(s).clipline(a, b):
            return False
    return True

class Enemy(pygame.sprite.Sprite):
    """
    Estados:
      - 'patrol'       : circula por pontos de patrulha
      - 'investigate'  : ouviu algo e vai checar
      - 'search'       : perdeu o jogador; vasculha ao redor do último visto
      - 'chase'        : vendo o jogador (LOS + FOV); persegue com predição
    """
    def __init__(self, x, y, difficulty=None):
        super().__init__()
        # Carrega a imagem do inspetor e a redimensiona
        # Supondo que a imagem se chame 'geralzao.png' e esteja na pasta 'assets'
        original_image = pygame.image.load("assets/geralzao.png").convert_alpha()
        # Exemplo: 50% maior (1.5 vezes o tamanho do tile)
        largura = int(TILE * 1.5)
        altura = int(TILE * 1.5)
        self.image = pygame.transform.scale(original_image, (largura, altura))
        self.rect = self.image.get_rect(center=(x, y))

        # --- ADICIONE ESTA LINHA ---
        self.name = "Geralzão"
        # ---------------------------

        # movimento
        self.dir = pygame.math.Vector2(1, 0)
        self.vel = pygame.math.Vector2(0, 0)

        # Carrega as configurações de dificuldade ou usa os padrões
        if difficulty is None:
            difficulty = DIFFICULTY_LEVELS["Normal"] # Fallback

        self.move_speed = difficulty["ENEMY_SPEED"]
        self.turn_speed = difficulty["ENEMY_TURN_SPEED"]
        self.FOV_DEGREES = difficulty["FOV_DEGREES"]
        self.FOV_RANGE = difficulty["FOV_RANGE"]
        self.HEARING_BASE = difficulty["ENEMY_HEARING_BASE"]
        self.HEARING_RUN = difficulty["ENEMY_HEARING_RUN"]
        self.LEAD_TIME = difficulty["ENEMY_LEAD_TIME"]
        self.SEARCH_TIME = difficulty["ENEMY_SEARCH_TIME"]
        self.SEARCH_RADIUS_TILES = difficulty["ENEMY_SEARCH_RADIUS_TILES"]
        self.PATH_RECALC_EVERY = difficulty["ENEMY_PATH_RECALC"]
        self.FEELER = difficulty["ENEMY_FEELER_LEN"]

        # alvo atual em pixels
        self.target_pos = pygame.math.Vector2(self.rect.center)

        # estado/fsm
        self.state = 'patrol'
        self.state_timer = 0.0
        self.pause_timer = 0.0

        # memória do jogador
        self.last_seen_pos = None
        self.last_seen_timer = 0.0
        self.last_heard_pos = None
        self.last_heard_timer = 0.0

        # pathfinding
        self.path = []                       # lista de (tx, ty)
        self.path_recalc_cooldown = 0.0

        # anti-stuck
        self.last_center = pygame.math.Vector2(self.rect.center)
        self.stuck_timer = 0.0

        # patrulha (lazy init com base no mapa)
        self._patrol_points = []
        self._current_patrol_idx = 0

        # tunables
        self.PATROL_PAUSE_MINMAX = globals().get('ENEMY_PATROL_PAUSE_MINMAX', (0.5, 1.2))
        self.WAYPOINT_EPS = TILE * 0.25

    # ---------------- PATHFINDING ----------------
    def _blocked(self, tx, ty, game_map):
        if ty < 0 or ty >= len(game_map.grid): return True
        if tx < 0 or tx >= len(game_map.grid[ty]): return True
        ch = game_map.grid[ty][tx]
        return ch in ('1', 'T')

    def _nearest_walkable(self, tx, ty, game_map, max_r=6):
        """Se o alvo cair num tile bloqueado, busca o mais perto disponível."""
        if not self._blocked(tx, ty, game_map):
            return (tx, ty)
        from collections import deque
        q = deque()
        q.append((tx, ty))
        seen = {(tx, ty)}
        while q:
            x, y = q.popleft()
            for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if (nx, ny) in seen: continue
                if abs(nx-tx)+abs(ny-ty) > max_r: continue
                seen.add((nx, ny))
                if not self._blocked(nx, ny, game_map):
                    return (nx, ny)
                q.append((nx, ny))
        return (tx, ty)  # desiste

    def _astar(self, start, goal, game_map):
        if self._blocked(goal[0], goal[1], game_map):
            goal = self._nearest_walkable(*goal, game_map=game_map)

        def h(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

        openh = []
        heapq.heappush(openh, (h(start, goal), 0, start, None))
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
                if self._blocked(nx, ny, game_map):
                    continue
                ng = g + 1
                if ng < gbest.get((nx,ny), 1e9):
                    gbest[(nx,ny)] = ng
                    heapq.heappush(openh, (ng + h((nx,ny), goal), ng, (nx,ny), node))

        if goal not in came:
            return []
        # reconstrói
        cur = goal
        rev = []
        while cur is not None:
            rev.append(cur)
            cur = came[cur]
        rev.reverse()
        return rev[1:]

    def _smooth_path(self, start_px, path_tiles, solids):
        """Remove waypoints desnecessários se houver LOS direta para um ponto à frente."""
        if not path_tiles:
            return []
        pts = []
        cur_px = pygame.math.Vector2(start_px)
        i = 0
        while i < len(path_tiles):
            # tenta pular o máximo possível
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

    def _need_recalc(self, player_tile, game_map):
        if not self.path:
            return True
        last_goal = self.path[-1]
        return last_goal != player_tile or self.path_recalc_cooldown <= 0.0

    def _follow_path_target(self):
        if not self.path:
            return None
        tx, ty = self.path[0]
        return _tile_center(tx, ty)

    # ---------------- PERCEPÇÃO ----------------
    def has_line_of_sight(self, player, solids):
        return _has_clear_los(self.rect.center, player.rect.center, solids)

    def sees(self, player, solids):
        if not self.has_line_of_sight(player, solids):
            return False
        to_player = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        dist = to_player.length()
        if dist > self.FOV_RANGE or dist == 0:
            return False
        to_player_n = to_player.normalize()
        dot = self.dir.dot(to_player_n)
        angle = math.degrees(math.acos(clamp(dot, -1, 1)))
        return angle <= self.FOV_DEGREES / 2

    def hears(self, player):
        # barulho proporcional à velocidade
        speed = math.hypot(getattr(player, "vx", 0.0), getattr(player, "vy", 0.0))
        if speed <= 10: 
            return False, None
        # raio maior se correndo rápido
        hear_r = self.HEARING_BASE + (self.HEARING_RUN - self.HEARING_BASE) * clamp((speed / (PLAYER_SPEED+1e-6)), 0.0, 1.0)
        d = pygame.math.Vector2(player.rect.center).distance_to(self.rect.center)
        return d <= hear_r, pygame.math.Vector2(player.rect.center)

    # ---------------- PATRULHA ----------------
    def _build_patrol(self, game_map):
        if self._patrol_points:
            return
        # pegue alguns pontos "distribuídos": 6 setores da tela
        gw = len(game_map.grid[0]); gh = len(game_map.grid)
        sectors = [
            (int(gw*0.2), int(gh*0.3)),
            (int(gw*0.5), int(gh*0.25)),
            (int(gw*0.8), int(gh*0.3)),
            (int(gw*0.8), int(gh*0.7)),
            (int(gw*0.5), int(gh*0.75)),
            (int(gw*0.2), int(gh*0.7)),
        ]
        pts = []
        for tx, ty in sectors:
            tx, ty = self._nearest_walkable(tx, ty, game_map, max_r=8)
            pts.append(_tile_center(tx, ty))
        # embaralha para evitar rotas iguais sempre
        random.shuffle(pts)
        self._patrol_points = pts

    def _next_patrol_point(self):
        if not self._patrol_points:
            return self.target_pos
        self._current_patrol_idx = (self._current_patrol_idx + 1) % len(self._patrol_points)
        return self._patrol_points[self._current_patrol_idx]

    # ---------------- MOVIMENTO/COLISÃO ----------------
    def _steer_away_from_walls(self, solids):
        """Feelers curtos para evitar ficar raspando eternamente."""
        if self.FEELER <= 0: 
            return
        p = pygame.math.Vector2(self.rect.center)
        fwd = self.dir
        right = pygame.math.Vector2(self.dir.y, -self.dir.x)
        feelers = [p + fwd*self.FEELER, p + (fwd+0.6*right)*self.FEELER, p + (fwd-0.6*right)*self.FEELER]
        adjust = pygame.math.Vector2(0, 0)
        for pt in feelers:
            for s in solids:
                if _rect_of(s).collidepoint(pt):
                    # empurra contrário
                    away = (pt - p)
                    if away.length_squared() > 1e-6:
                        adjust -= away.normalize()
        if adjust.length_squared() > 0:
            self.dir = (self.dir + 0.6*adjust).normalize()

    # ---------------- UPDATE ----------------
    def update(self, dt, player, solids=None, game_map=None):
        if solids is None: solids = []
        self.state_timer += dt
        self.path_recalc_cooldown -= dt
        if self.last_seen_timer  > 0: self.last_seen_timer  -= dt
        if self.last_heard_timer > 0: self.last_heard_timer -= dt

        if game_map:
            self._build_patrol(game_map)

        pos_vec = pygame.math.Vector2(self.rect.center)
        player_pos = pygame.math.Vector2(player.rect.center)
        player_tile = _pos_to_tile(player_pos)

        # --- percepção ---
        see = self.sees(player, solids)
        heard, heard_pos = self.hears(player)

        if see:
            self.state = 'chase'
            self.last_seen_pos   = pygame.math.Vector2(player_pos)
            self.last_seen_timer = 2.5
            self.path.clear()  # perseguição direta
        elif heard and self.state != 'chase' and self.last_seen_timer <= 0:
            # só muda para investigar se não estiver vendo
            self.state = 'investigate'
            self.last_heard_pos   = heard_pos
            self.last_heard_timer = 2.5

        # --- FSM principal ---
        if self.state == 'chase':
            # predição simples: aponta para onde o player deve estar em LEAD_TIME
            pv = pygame.math.Vector2(getattr(player, "vx", 0.0), getattr(player, "vy", 0.0))
            predicted = player_pos + pv * self.LEAD_TIME
            self.target_pos = predicted
            # se perdeu visão, transita para SEARCH
            if not see and self.last_seen_timer <= 0:
                self.state = 'search'
                self.state_timer = 0.0
                self.path.clear()

        elif self.state == 'investigate':
            if self.last_heard_timer <= 0 or self.last_heard_pos is None:
                # se chegou sem nada, muda para search na região
                self.state = 'search'
                self.state_timer = 0.0
            else:
                # vai até o ponto ouvido usando A*
                if game_map:
                    my_tile = _pos_to_tile(pos_vec)
                    goal_tile = _pos_to_tile(self.last_heard_pos)
                    if self._need_recalc(goal_tile, game_map):
                        raw = self._astar(my_tile, goal_tile, game_map)
                        self.path = self._smooth_path(pos_vec, raw, solids)
                        self.path_recalc_cooldown = self.PATH_RECALC_EVERY
                    wp = self._follow_path_target()
                    if wp is not None:
                        self.target_pos = wp
                        if (wp - pos_vec).length() <= self.WAYPOINT_EPS:
                            self.path.pop(0)

        elif self.state == 'search':
            # vasculha em volta da última posição visto/ouvido
            anchor = self.last_seen_pos or self.last_heard_pos or player_pos
            if self.state_timer > self.SEARCH_TIME:
                self.state = 'patrol'
                self.state_timer = 0.0
                self.path.clear()
            else:
                if game_map:
                    if not self.path:
                        # escolhe um tile aleatório em um raio
                        atx, aty = _pos_to_tile(anchor)
                        rt = self.SEARCH_RADIUS_TILES
                        goal = (random.randint(atx-rt, atx+rt), random.randint(aty-rt, aty+rt))
                        my_tile = _pos_to_tile(pos_vec)
                        raw = self._astar(my_tile, goal, game_map)
                        self.path = self._smooth_path(pos_vec, raw, solids)
                        self.path_recalc_cooldown = self.PATH_RECALC_EVERY
                    wp = self._follow_path_target()
                    if wp is not None:
                        self.target_pos = wp
                        if (wp - pos_vec).length() <= self.WAYPOINT_EPS:
                            self.path.pop(0)

        else:  # 'patrol'
            if self.pause_timer > 0:
                self.pause_timer -= dt
                # mantém alvo parado
                self.target_pos = pygame.math.Vector2(self.rect.center)
            else:
                if not self._patrol_points:
                    self.target_pos = player_pos  # fallback
                else:
                    cur_pt = self._patrol_points[self._current_patrol_idx]
                    if cur_pt.distance_to(pos_vec) <= self.WAYPOINT_EPS:
                        # chegou; pausa e escolhe próximo
                        self.pause_timer = random.uniform(*self.PATROL_PAUSE_MINMAX)
                        nxt = self._next_patrol_point()
                        self.target_pos = nxt
                        self.path.clear()
                    else:
                        # segue path até o ponto
                        if game_map:
                            my_tile = _pos_to_tile(pos_vec)
                            goal_tile = _pos_to_tile(cur_pt)
                            if self._need_recalc(goal_tile, game_map):
                                raw = self._astar(my_tile, goal_tile, game_map)
                                self.path = self._smooth_path(pos_vec, raw, solids)
                                self.path_recalc_cooldown = self.PATH_RECALC_EVERY
                            wp = self._follow_path_target()
                            if wp is not None:
                                self.target_pos = wp
                                if (wp - pos_vec).length() <= self.WAYPOINT_EPS:
                                    self.path.pop(0)

        # --- direção/velocidade ---
        to_target = self.target_pos - pos_vec
        if to_target.length() > 1e-3:
            target_dir = to_target.normalize()
            # leve steering de desvio de parede
            self._steer_away_from_walls(solids)
            # interpola direção
            self.dir = (self.dir.lerp(target_dir, clamp(self.turn_speed * dt, 0.0, 1.0))).normalize()
            self.vel = self.dir * self.move_speed
        else:
            self.vel.update(0, 0)

        # --- movimento com resolução por eixo ---
        # X
        self.rect.centerx += int(self.vel.x * dt)
        hit_x = False
        for s in solids:
            r = _rect_of(s)
            if r.colliderect(self.rect):
                hit_x = True
                if self.vel.x > 0: self.rect.right = r.left
                elif self.vel.x < 0: self.rect.left = r.right
        if hit_x:
            self.vel.x = 0
            self.dir.x *= 0.2

        # Y
        self.rect.centery += int(self.vel.y * dt)
        hit_y = False
        for s in solids:
            r = _rect_of(s)
            if r.colliderect(self.rect):
                hit_y = True
                if self.vel.y > 0: self.rect.bottom = r.top
                elif self.vel.y < 0: self.rect.top = r.bottom
        if hit_y:
            self.vel.y = 0
            self.dir.y *= 0.2

        # --- anti-stuck ---
        new_center = pygame.math.Vector2(self.rect.center)
        if (new_center - self.last_center).length_squared() < 0.25:
            self.stuck_timer += dt
        else:
            self.stuck_timer = 0.0
        self.last_center = new_center

        if self.stuck_timer > 0.35:
            self.dir = self.dir.rotate(90 if self.dir.x >= 0 else -90).normalize()
            self.path_recalc_cooldown = 0.0
            self.stuck_timer = 0.0

    # ---------------- DEBUG DRAW ----------------
    def draw_fov(self, surface):
        origin = pygame.math.Vector2(self.rect.center)
        base_angle = math.degrees(math.atan2(self.dir.y, self.dir.x))
        left_a  = math.radians(base_angle - self.FOV_DEGREES/2)
        right_a = math.radians(base_angle + self.FOV_DEGREES/2)
        left_vec  = (math.cos(left_a)*self.FOV_RANGE,  math.sin(left_a)*self.FOV_RANGE)
        right_vec = (math.cos(right_a)*self.FOV_RANGE, math.sin(right_a)*self.FOV_RANGE)
        pts = [origin, origin + left_vec, origin + right_vec]
        pygame.draw.polygon(surface, (255, 100, 100), pts, width=2)