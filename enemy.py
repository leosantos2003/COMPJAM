# enemy.py
import math
import random
import pygame
from settings import *
from utils import clamp, _rect_of, astar, smooth_path, _pos_to_tile, _tile_center, _has_clear_los, _blocked, _nearest_walkable

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
        original_image = pygame.image.load("assets/geralzao.png").convert_alpha()
        largura = int(TILE * 1.5)
        altura = int(TILE * 1.5)
        self.image = pygame.transform.smoothscale(original_image, (largura, altura))
        self.rect = self.image.get_rect(center=(x, y))

        self.name = "Geralzão"

        self.dir = pygame.math.Vector2(1, 0)
        self.vel = pygame.math.Vector2(0, 0)

        if difficulty is None:
            difficulty = DIFFICULTY_LEVELS["Normal"]

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

        self.target_pos = pygame.math.Vector2(self.rect.center)

        self.state = 'patrol'
        self.state_timer = 0.0
        self.pause_timer = 0.0

        self.last_seen_pos = None
        self.last_seen_timer = 0.0
        self.last_heard_pos = None
        self.last_heard_timer = 0.0

        self.path = []
        self.path_recalc_cooldown = 0.0

        self.last_center = pygame.math.Vector2(self.rect.center)
        self.stuck_timer = 0.0

        self._patrol_points = []
        self._current_patrol_idx = 0

        self.PATROL_PAUSE_MINMAX = globals().get('ENEMY_PATROL_PAUSE_MINMAX', (0.5, 1.2))
        self.WAYPOINT_EPS = TILE * 0.25

    def _need_recalc(self, player_tile):
        if not self.path:
            return True
        last_goal = self.path[-1]
        return last_goal != player_tile or self.path_recalc_cooldown <= 0.0

    def _follow_path_target(self):
        if not self.path:
            return None
        return _tile_center(*self.path[0])

    def has_line_of_sight(self, player, solids):
        return _has_clear_los(self.rect.center, player.rect.center, solids)

    def sees(self, player, solids):
        if not self.has_line_of_sight(player, solids):
            return False
        to_player = pygame.math.Vector2(player.rect.center) - self.rect.center
        dist = to_player.length()
        if dist > self.FOV_RANGE or dist == 0:
            return False
        to_player_n = to_player.normalize()
        dot = self.dir.dot(to_player_n)
        angle = math.degrees(math.acos(clamp(dot, -1, 1)))
        return angle <= self.FOV_DEGREES / 2

    def hears(self, player):
        speed = math.hypot(getattr(player, "vx", 0.0), getattr(player, "vy", 0.0))
        if speed <= 10: 
            return False, None
        hear_r = self.HEARING_BASE + (self.HEARING_RUN - self.HEARING_BASE) * clamp((speed / (PLAYER_SPEED+1e-6)), 0.0, 1.0)
        d = pygame.math.Vector2(player.rect.center).distance_to(self.rect.center)
        return d <= hear_r, pygame.math.Vector2(player.rect.center)

    def _build_patrol(self, game_map):
        if self._patrol_points:
            return
        gw = len(game_map.grid[0]); gh = len(game_map.grid)
        sectors = [
            (int(gw*0.2), int(gh*0.3)), (int(gw*0.5), int(gh*0.25)),
            (int(gw*0.8), int(gh*0.3)), (int(gw*0.8), int(gh*0.7)),
            (int(gw*0.5), int(gh*0.75)), (int(gw*0.2), int(gh*0.7)),
        ]
        pts = [_tile_center(*_nearest_walkable(tx, ty, game_map, max_r=8)) for tx, ty in sectors]
        random.shuffle(pts)
        self._patrol_points = pts

    def _next_patrol_point(self):
        if not self._patrol_points:
            return self.target_pos
        self._current_patrol_idx = (self._current_patrol_idx + 1) % len(self._patrol_points)
        return self._patrol_points[self._current_patrol_idx]

    def _steer_away_from_walls(self, solids):
        if self.FEELER <= 0: return
        p = pygame.math.Vector2(self.rect.center)
        fwd = self.dir
        right = pygame.math.Vector2(self.dir.y, -self.dir.x)
        feelers = [p + fwd*self.FEELER, p + (fwd+0.6*right)*self.FEELER, p + (fwd-0.6*right)*self.FEELER]
        adjust = pygame.math.Vector2(0, 0)
        for pt in feelers:
            for s in solids:
                if _rect_of(s).collidepoint(pt):
                    away = (pt - p)
                    if away.length_squared() > 1e-6:
                        adjust -= away.normalize()
        if adjust.length_squared() > 0:
            self.dir = (self.dir + 0.6*adjust).normalize()

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

        see = self.sees(player, solids)
        heard, heard_pos = self.hears(player)

        if see:
            self.state = 'chase'
            self.last_seen_pos   = player_pos
            self.last_seen_timer = 2.5
            self.path.clear()
        elif heard and self.state != 'chase' and self.last_seen_timer <= 0:
            self.state = 'investigate'
            self.last_heard_pos   = heard_pos
            self.last_heard_timer = 2.5

        if self.state == 'chase':
            pv = pygame.math.Vector2(getattr(player, "vx", 0.0), getattr(player, "vy", 0.0))
            predicted = player_pos + pv * self.LEAD_TIME
            self.target_pos = predicted
            if not see and self.last_seen_timer <= 0:
                self.state = 'search'
                self.state_timer = 0.0
                self.path.clear()

        elif self.state == 'investigate':
            if self.last_heard_timer <= 0 or self.last_heard_pos is None:
                self.state = 'search'
                self.state_timer = 0.0
            elif game_map:
                my_tile = _pos_to_tile(pos_vec)
                goal_tile = _pos_to_tile(self.last_heard_pos)
                if self._need_recalc(goal_tile):
                    raw = astar(my_tile, goal_tile, game_map)
                    self.path = smooth_path(pos_vec, raw, solids)
                    self.path_recalc_cooldown = self.PATH_RECALC_EVERY
                if (wp := self._follow_path_target()) is not None:
                    self.target_pos = wp
                    if (wp - pos_vec).length() <= self.WAYPOINT_EPS:
                        self.path.pop(0)

        elif self.state == 'search':
            anchor = self.last_seen_pos or self.last_heard_pos or player_pos
            if self.state_timer > self.SEARCH_TIME:
                self.state = 'patrol'
                self.state_timer = 0.0
                self.path.clear()
            elif game_map and not self.path:
                atx, aty = _pos_to_tile(anchor)
                rt = self.SEARCH_RADIUS_TILES
                goal = (random.randint(atx-rt, atx+rt), random.randint(aty-rt, aty+rt))
                my_tile = _pos_to_tile(pos_vec)
                raw = astar(my_tile, goal, game_map)
                self.path = smooth_path(pos_vec, raw, solids)
            if (wp := self._follow_path_target()) is not None:
                self.target_pos = wp
                if (wp - pos_vec).length() <= self.WAYPOINT_EPS:
                    self.path.pop(0)

        else:  # 'patrol'
            if self.pause_timer > 0:
                self.pause_timer -= dt
                self.target_pos = pos_vec
            elif self._patrol_points:
                cur_pt = self._patrol_points[self._current_patrol_idx]
                if cur_pt.distance_to(pos_vec) <= self.WAYPOINT_EPS:
                    self.pause_timer = random.uniform(*self.PATROL_PAUSE_MINMAX)
                    self.target_pos = self._next_patrol_point()
                    self.path.clear()
                elif game_map:
                    my_tile = _pos_to_tile(pos_vec)
                    goal_tile = _pos_to_tile(cur_pt)
                    if self._need_recalc(goal_tile):
                        raw = astar(my_tile, goal_tile, game_map)
                        self.path = smooth_path(pos_vec, raw, solids)
                        self.path_recalc_cooldown = self.PATH_RECALC_EVERY
                    if (wp := self._follow_path_target()) is not None:
                        self.target_pos = wp
                        if (wp - pos_vec).length() <= self.WAYPOINT_EPS:
                            self.path.pop(0)

        to_target = self.target_pos - pos_vec
        if to_target.length() > 1e-3:
            target_dir = to_target.normalize()
            self._steer_away_from_walls(solids)
            self.dir = self.dir.lerp(target_dir, clamp(self.turn_speed * dt, 0.0, 1.0)).normalize()
            self.vel = self.dir * self.move_speed
        else:
            self.vel.update(0, 0)

        self.rect.centerx += int(self.vel.x * dt)
        for s in solids:
            if _rect_of(s).colliderect(self.rect):
                if self.vel.x > 0: self.rect.right = _rect_of(s).left
                elif self.vel.x < 0: self.rect.left = _rect_of(s).right
                self.vel.x = 0; self.dir.x *= 0.2

        self.rect.centery += int(self.vel.y * dt)
        for s in solids:
            if _rect_of(s).colliderect(self.rect):
                if self.vel.y > 0: self.rect.bottom = _rect_of(s).top
                elif self.vel.y < 0: self.rect.top = _rect_of(s).bottom
                self.vel.y = 0; self.dir.y *= 0.2

        new_center = pygame.math.Vector2(self.rect.center)
        if (new_center - self.last_center).length_squared() < 0.25:
            self.stuck_timer += dt
        else:
            self.stuck_timer = 0.0
        self.last_center = new_center

        if self.stuck_timer > 0.35:
            self.dir.rotate_ip(90 if self.dir.x >= 0 else -90)
            self.path_recalc_cooldown = 0.0
            self.stuck_timer = 0.0

    def draw_fov(self, surface, solids):
        fov_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        origin = self.rect.center
        base_angle = math.degrees(math.atan2(self.dir.y, self.dir.x))
        
        light_points = [origin]
        num_rays = 50 
        
        start_angle = base_angle - self.FOV_DEGREES / 2
        end_angle = base_angle + self.FOV_DEGREES / 2
        
        for i in range(num_rays + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_rays
            rad_angle = math.radians(angle)
            
            end_point = (origin[0] + math.cos(rad_angle) * self.FOV_RANGE,
                         origin[1] + math.sin(rad_angle) * self.FOV_RANGE)
            
            closest_intersection = end_point
            min_dist_sq = self.FOV_RANGE**2

            for s in solids:
                if (clipped_line := _rect_of(s).clipline(origin, end_point)):
                    intersection_point = clipped_line[0]
                    dist_sq = (intersection_point[0] - origin[0])**2 + (intersection_point[1] - origin[1])**2
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        closest_intersection = intersection_point

            light_points.append(closest_intersection)
        
        if len(light_points) > 2:
            pygame.draw.polygon(fov_surface, (255, 255, 100, 80), light_points)
        
        surface.blit(fov_surface, (0, 0))