# game.py

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

class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0

        self.load_assets()

        self.maps = ["map.txt", "map2.txt", "map3.txt"]
        self.score = 0
        self.start_time = 0
        self.difficulty = "Normal"
        self.leaderboard = self._load_leaderboard()

        self.game_over_sequence_active = False
        self.game_over_timer = 0.0
        
    def load_assets(self):
        try:
            self.title_font = pygame.font.Font("fonts/Pricedown_BL.otf", 60)
            self.menu_font_normal = pygame.font.Font("fonts/Pricedown_BL.otf", 35)
            self.menu_font_selected = pygame.font.Font("fonts/Pricedown_BL.otf", 40)
            self.hud_font = pygame.font.Font("fonts/Pricedown_BL.otf", 20)
            self.timer_font = pygame.font.Font("fonts/Pricedown_BL.otf", 28)
            self.leaderboard_font = pygame.font.Font("fonts/Pricedown_BL.otf", 30)
        except FileNotFoundError:
            print("Aviso: Arquivo de fonte não encontrado. Usando fontes padrão.")
            self.title_font = pygame.font.SysFont(None, 80)
            self.menu_font_normal = pygame.font.SysFont(None, 45)
            self.menu_font_selected = pygame.font.SysFont(None, 55)
            self.hud_font = pygame.font.SysFont(None, 28)
            self.timer_font = pygame.font.SysFont(None, 40)
            self.leaderboard_font = pygame.font.SysFont(None, 45)
            
        try:
            self.menu_nav_sound = pygame.mixer.Sound("assets/sound/menu_sound.wav")
        except pygame.error:
            print("Aviso: Arquivo de som do menu (menu_sound.wav) não encontrado.")
            self.menu_nav_sound = None

        self.smoke_frames = load_spritesheet_grid("assets/smoke.png", 427, 240)
        self.bar_frames = load_spritesheet_grid("assets/bar.png", 461, 240)
        self.aura_image = pygame.image.load("assets/auratrollface.png").convert_alpha()

        try:
            pygame.mixer.music.load('audio/background_music.mp3')
            pygame.mixer.music.set_volume(0.4)
        except pygame.error as e:
            print(f"Aviso: Não foi possível carregar a música de fundo: {e}")

        try:
            self.smoking_sound = pygame.mixer.Sound('audio/smoke_sound.mp3')
            self.smoking_sound.set_volume(0.6)
            self.pullup_sound = pygame.mixer.Sound('audio/bar_sound.mp3')
            self.pullup_sound.set_volume(0.6)
            self.jumpscare_sound = pygame.mixer.Sound('audio/jumpscare.mp3')
            self.jumpscare_sound.set_volume(0.7)
            self.caught_sound = pygame.mixer.Sound('audio/death_scream.mp3')
            self.caught_sound.set_volume(0.8)
        except pygame.error as e:
            print(f"Aviso: Não foi possível carregar um ou mais efeitos sonoros: {e}")
        
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

    def _load_leaderboard(self):
        try:
            with open('leaderboard.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"Pesadelo": []}

    def _save_leaderboard(self):
        with open('leaderboard.json', 'w') as f:
            json.dump(self.leaderboard, f, indent=4)

    def _is_high_score(self, score):
        if self.difficulty != "Pesadelo":
            return False
        leaderboard_list = self.leaderboard.get("Pesadelo", [])
        if len(leaderboard_list) < 5 or score > leaderboard_list[-1]['score']:
            return True
        return False

    def _add_high_score(self, name, score):
        leaderboard_list = self.leaderboard.get("Pesadelo", [])
        leaderboard_list.append({'name': name, 'score': score})
        leaderboard_list = sorted(leaderboard_list, key=lambda x: x['score'], reverse=True)[:5]
        self.leaderboard["Pesadelo"] = leaderboard_list
        self._save_leaderboard()

    def new(self, map_file, difficulty):
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.bars = pygame.sprite.Group()
        self.herbs = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        self.game_map = Map(map_file)
        self.solids = self.game_map.solids

        self.player = Player(self, 4, 5)
        self.all_sprites.add(self.player)

        for pos in self.game_map.cig_positions:
            c = Cigarette(*pos)
            self.items.add(c); self.all_sprites.add(c)
        for pos in self.game_map.bar_positions:
            b = PullUpBar(*pos)
            self.bars.add(b); self.all_sprites.add(b)

        enemy_settings = DIFFICULTY_LEVELS[difficulty]
        self.enemy = Enemy(800, 400, difficulty=enemy_settings)
        self.enemies.add(self.enemy); self.all_sprites.add(self.enemy)

        self.cigs_level = MAX_STAT_LEVEL
        self.bars_level = MAX_STAT_LEVEL
        self.playing = True
        self.result = None
        self.start_time = time.time()

        pygame.mixer.music.play(loops=-1)

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()

        if self.result == "lose":
            if self._is_high_score(self.score):
                player_name = get_player_name_input(self)
                self._add_high_score(player_name, self.score)
                show_leaderboard_screen(self)
            return death_screen(self)

        return "menu"

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
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

        if HERB_ENABLED and self.chapado_effect_active:
            self.chapado_timer -= self.dt
            if self.chapado_timer <= 0:
                self.chapado_effect_active = False
        else:
            self.cigs_level -= CIGS_DECAY_RATE * self.dt
            self.bars_level -= BARS_DECAY_RATE * self.dt

        if (self.cigs_level <= 0 or self.bars_level <= 0) and not self.result:
            if not self.game_over_sequence_active:
                self.game_over_sequence_active = True
                self.game_over_timer = 1.0
                pygame.mixer.music.fadeout(1000)
                if self.smoking_sound: self.smoking_sound.stop()
                if self.pullup_sound: self.pullup_sound.stop()

        self.player.update(self.dt, self.solids)
        self.enemy.update(self.dt, self.player, self.solids, self.game_map)

        was_smoking = self.is_smoking
        was_doing_pullups = self.is_doing_pullups

        self.is_smoking = bool(pygame.sprite.spritecollide(self.player, self.items, dokill=False))
        if self.is_smoking:
            self.cigs_level += CIGS_RECHARGE_RATE * self.dt

        self.is_doing_pullups = bool(pygame.sprite.spritecollide(self.player, self.bars, dokill=False))
        if self.is_doing_pullups:
            self.bars_level += BARS_RECHARGE_RATE * self.dt

        if self.is_smoking and not was_smoking and self.smoking_sound:
            self.smoking_sound.play(loops=-1)
        elif not self.is_smoking and was_smoking and self.smoking_sound:
            self.smoking_sound.stop()

        if self.is_doing_pullups and not was_doing_pullups and self.pullup_sound:
            self.pullup_sound.play(loops=-1)
        elif not self.is_doing_pullups and was_doing_pullups and self.pullup_sound:
            self.pullup_sound.stop()

        if HERB_ENABLED:
            if pygame.sprite.spritecollide(self.player, self.herbs, dokill=True):
                self.chapado_effect_active = True
                self.chapado_timer = self.chapado_duration

            if random.random() < HERB_SPAWN_CHANCE and not self.herbs:
                while True:
                    x = random.randint(50, SCREEN_WIDTH - 50)
                    y = random.randint(50, SCREEN_HEIGHT - 50)
                    temp_rect = pygame.Rect(0, 0, TILE, TILE)
                    temp_rect.center = (x, y)
                    if not any(temp_rect.colliderect(s.rect) for s in self.solids):
                        break
                h = Herb(x, y)
                self.all_sprites.add(h)
                self.herbs.add(h)

        if (self.is_smoking and not was_smoking) or \
           (self.is_doing_pullups and not was_doing_pullups):
            if not self.aura_active and random.randint(1, 14) == 1:
                self.aura_active = True
                self.aura_timer = self.aura_duration
                if self.jumpscare_sound:
                    self.jumpscare_sound.play()

        if self.aura_active:
            self.aura_timer -= self.dt
            if self.aura_timer <= 0:
                self.aura_active = False

        self.cigs_level = clamp(self.cigs_level, 0, MAX_STAT_LEVEL)
        self.bars_level = clamp(self.bars_level, 0, MAX_STAT_LEVEL)

        if self.enemy.sees(self.player, self.solids) and not self.result:
            if not self.game_over_sequence_active:
                self.game_over_sequence_active = True
                self.game_over_timer = 1.0
                pygame.mixer.music.fadeout(1000)
                if self.smoking_sound: self.smoking_sound.stop()
                if self.pullup_sound: self.pullup_sound.stop()
                if self.caught_sound:
                    self.caught_sound.play()
        
        if self.playing:
            self.score = int(time.time() - self.start_time)

    def draw(self):
        self.game_map.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.enemy.draw_fov(self.screen, self.solids)
        draw_hud(self)

        legenda_surface_inimigo = self.hud_font.render(self.enemy.name, True, WHITE)
        legenda_rect_inimigo = legenda_surface_inimigo.get_rect(midbottom=self.enemy.rect.midtop - pygame.math.Vector2(0, 5))
        self.screen.blit(legenda_surface_inimigo, legenda_rect_inimigo)

        texto_legenda_jogador = None
        animation_frame = None

        if self.is_smoking:
            texto_legenda_jogador = "Fumando..."
            animation_frame = update_smoke_animation(self)
        elif self.is_doing_pullups:
            texto_legenda_jogador = "Fazendo barra fixa..."
            animation_frame = update_bar_animation(self)

        if texto_legenda_jogador and animation_frame:
            legenda_surface_jogador = self.hud_font.render(texto_legenda_jogador, True, WHITE)
            legenda_rect_jogador = legenda_surface_jogador.get_rect(midbottom=self.player.rect.midtop - pygame.math.Vector2(0, 5))
            self.screen.blit(legenda_surface_jogador, legenda_rect_jogador)
            
            anim_size = (108, 84)
            scaled_frame = pygame.transform.smoothscale(animation_frame, anim_size)
            anim_rect = scaled_frame.get_rect(midbottom=legenda_rect_jogador.midtop - pygame.math.Vector2(0, 3))
            self.screen.blit(scaled_frame, anim_rect)

        if self.aura_active:
            aura_offset_y = 10
            aura_rect = self.aura_image.get_rect(midtop=(self.player.rect.centerx, self.player.rect.bottom + aura_offset_y))
            self.screen.blit(self.aura_image, aura_rect)

            text_offset_y = 5
            aura_text_surf = self.hud_font.render("+AURA +EGO", True, WHITE)
            aura_text_rect = aura_text_surf.get_rect(midtop=(aura_rect.centerx, aura_rect.bottom + text_offset_y))
            self.screen.blit(aura_text_surf, aura_text_rect)

        if HERB_ENABLED and self.chapado_effect_active:
            temp_surface = self.screen.copy()
            offset_x = int(math.sin(time.time() * 15) * 5)
            offset_y = int(math.cos(time.time() * 13) * 5)
            self.screen.fill(BLACK)
            self.screen.blit(temp_surface, (offset_x, offset_y))

        if self.game_over_sequence_active:
            player_image_copy = self.player.image.copy()
            player_image_copy.fill(RED, special_flags=pygame.BLEND_RGB_MULT)
            self.screen.blit(player_image_copy, self.player.rect)

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()