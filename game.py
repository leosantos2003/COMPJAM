# game.py (Atualizado com Câmera Condicional e Correção de Desenho do FOV)

import pygame
import sys
import time
import random
import math
import json
from settings import *
from player import Player
from enemy import Enemy
from items import Cigarette, PullUpBar, Herb
from map import Map
from utils import clamp, load_spritesheet_grid
from ui import show_leaderboard_screen, death_screen, get_player_name_input
from hud import draw_hud
from animations import update_smoke_animation, update_bar_animation
from asset_loader import load_assets
import leaderboard
import game_logic
from camera import Camera

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

        if FULLSCREEN:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        self.assets = load_assets()
        self.map_assets_to_attributes()

        self.volume = INITIAL_VOLUME
        self.set_volume(self.volume)

        self.maps = ["map.txt", "map2.txt", "map3.txt"]
        self.score = 0
        self.start_time = 0
        self.difficulty = "Normal"
        self.leaderboard_data = leaderboard.load_leaderboard()

        self.game_over_sequence_active = False
        self.game_over_timer = 0.0

    def map_assets_to_attributes(self):
        for key, value in self.assets.items():
            setattr(self, key, value)

    def set_volume(self, new_volume):
        self.volume = clamp(new_volume, 0.0, 1.0)
        pygame.mixer.music.set_volume(self.volume)
        for asset in self.assets.values():
            if isinstance(asset, pygame.mixer.Sound):
                asset.set_volume(self.volume)

    def new(self, map_file=None, grid_data=None, difficulty="Normal"):
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.bars = pygame.sprite.Group()
        self.herbs = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # --- LÓGICA DA CÂMERA CONDICIONAL ---
        self.is_procedural_map = grid_data is not None
        # ------------------------------------

        if map_file:
            self.game_map = Map(map_file=map_file)
        elif grid_data:
            self.game_map = Map(grid_data=grid_data)
        
        self.solids = self.game_map.solids

        self.player = Player(self, 4, 5)
        self.all_sprites.add(self.player)

        for pos in self.game_map.cig_positions:
            c = Cigarette(*pos)
            self.all_sprites.add(c); self.items.add(c)
        for pos in self.game_map.bar_positions:
            b = PullUpBar(*pos)
            self.all_sprites.add(b); self.bars.add(b)

        floor_tiles = []
        for j, row in enumerate(self.game_map.grid):
            for i, char in enumerate(row):
                if char == '.':
                    player_dist_sq = (i - self.game_map.spawn_tile[0])**2 + (j - self.game_map.spawn_tile[1])**2
                    if player_dist_sq > 100:
                        floor_tiles.append((i * TILE + TILE // 2, j * TILE + TILE // 2))
        
        if floor_tiles:
            enemy_pos = random.choice(floor_tiles)
        else:
            enemy_pos = (self.game_map.width_px / 2, self.game_map.height_px / 2)

        self.enemy = Enemy(enemy_pos[0], enemy_pos[1], difficulty=DIFFICULTY_LEVELS[difficulty])
        self.all_sprites.add(self.enemy); self.enemies.add(self.enemy)
        
        self.camera = Camera(self.game_map.width_px, self.game_map.height_px)

        self.cigs_level = MAX_STAT_LEVEL
        self.bars_level = MAX_STAT_LEVEL
        self.playing = True
        self.result = None
        self.start_time = time.time()
        
        self.is_smoking = False
        self.is_doing_pullups = False
        self.smoke_anim_index = 0
        self.bar_anim_index = 0
        self.smoke_anim_timer = 0
        self.bar_anim_timer = 0
        self.anim_speed = 0.1
        self.aura_active = False
        self.aura_timer = 0
        self.aura_duration = 1.0
        self.chapado_effect_active = False
        self.chapado_timer = 0
        self.chapado_duration = 5.0

        pygame.mixer.music.play(loops=-1)

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()

        if self.result == "lose":
            if leaderboard.is_high_score(self.leaderboard_data, self.score, self.difficulty):
                player_name = get_player_name_input(self)
                if player_name:
                    leaderboard.add_high_score(self.leaderboard_data, player_name, self.score)
                show_leaderboard_screen(self)
            return death_screen(self)
        return "menu"

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.playing = False
                pygame.mixer.music.fadeout(1000)

    def update(self):
        if self.game_over_sequence_active:
            self.game_over_timer -= self.dt
            if self.game_over_timer <= 0:
                self.game_over_sequence_active = False
                self.result = "lose"
                self.playing = False
            return

        self.was_smoking = self.is_smoking
        self.was_doing_pullups = self.is_doing_pullups

        self.player.update(self.dt, self.solids)
        self.enemy.update(self.dt, self.player, self.solids, self.game_map)
        
        # --- ATUALIZA A CÂMERA APENAS SE NECESSÁRIO ---
        if self.is_procedural_map:
            self.camera.update(self.player)
        # ---------------------------------------------

        game_logic.handle_player_interactions(self)
        game_logic.handle_special_effects(self)
        game_logic.handle_herb_spawning(self)
        game_logic.update_timers_and_stats(self)
        game_logic.check_game_over_conditions(self)
        
        if self.playing:
            self.score = int(time.time() - self.start_time)

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.game_map.static_surface, self.camera.apply_rect(self.game_map.static_surface.get_rect()))

        for sprite in sorted(self.all_sprites, key=lambda s: s.rect.centery):
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        
        # --- DESENHO DO FOV CORRIGIDO ---
        self.enemy.draw_fov(self.screen, self.solids, self.camera)
        # --------------------------------
        
        draw_hud(self)

        legenda_surface_inimigo = self.hud_font.render(self.enemy.name, True, WHITE)
        legenda_rect_inimigo = legenda_surface_inimigo.get_rect(midbottom=self.enemy.rect.midtop - pygame.math.Vector2(0, 5))
        self.screen.blit(legenda_surface_inimigo, self.camera.apply_rect(legenda_rect_inimigo))

        texto_legenda_jogador, animation_frame = None, None
        if self.is_smoking:
            texto_legenda_jogador = "Fumando..."
            animation_frame = update_smoke_animation(self)
        elif self.is_doing_pullups:
            texto_legenda_jogador = "Fazendo barra fixa..."
            animation_frame = update_bar_animation(self)
        
        if texto_legenda_jogador and animation_frame:
            legenda_surf = self.hud_font.render(texto_legenda_jogador, True, WHITE)
            legenda_rect = legenda_surf.get_rect(midbottom=self.player.rect.midtop - pygame.math.Vector2(0, 5))
            self.screen.blit(legenda_surf, self.camera.apply_rect(legenda_rect))
            
            scaled_frame = pygame.transform.smoothscale(animation_frame, (108, 84))
            anim_rect = scaled_frame.get_rect(midbottom=legenda_rect.midtop - pygame.math.Vector2(0, 3))
            self.screen.blit(scaled_frame, self.camera.apply_rect(anim_rect))

        if self.aura_active:
            aura_rect = self.aura_image.get_rect(midtop=(self.player.rect.centerx, self.player.rect.bottom + 10))
            self.screen.blit(self.aura_image, self.camera.apply_rect(aura_rect))
            aura_text_surf = self.hud_font.render("+AURA +EGO", True, WHITE)
            aura_text_rect = aura_text_surf.get_rect(midtop=(aura_rect.centerx, aura_rect.bottom + 5))
            self.screen.blit(aura_text_surf, self.camera.apply_rect(aura_text_rect))

        if HERB_ENABLED and self.chapado_effect_active:
            temp_surface = self.screen.copy()
            offset_x = int(math.sin(time.time() * 15) * 5)
            offset_y = int(math.cos(time.time() * 13) * 5)
            self.screen.fill(BLACK)
            self.screen.blit(temp_surface, (offset_x, offset_y))

        if self.game_over_sequence_active:
            player_image_copy = self.player.image.copy()
            player_image_copy.fill(RED, special_flags=pygame.BLEND_RGB_MULT)
            self.screen.blit(player_image_copy, self.camera.apply(self.player))

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()