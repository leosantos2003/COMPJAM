# game.py (versão refatorada)
import pygame
import sys
from settings import *
from player import Player
from enemy import Enemy
from items import Cigarette, PullUpBar
from map import Map
from utils import clamp
from assets import Assets  # NOVO
from ui import HUD, Menu   # NOVO

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
        # Inicia os novos módulos
        self.assets = Assets()
        self.hud = HUD(self.assets)
        self.menu = Menu(self.assets)

    def show_menu_screen(self):
        options = [("Jogar", "play"), ("Sair", "quit")]
        colors = [GREEN, RED]
        return self.menu.run(self.screen, self.clock, TITLE, WHITE, options, colors)

    def show_game_over_screen(self):
        options = [("Recomeçar", "restart"), ("Voltar ao Menu", "menu")]
        colors = [GREEN, CYAN]
        return self.menu.run(self.screen, self.clock, "Você morreu...", RED, options, colors)

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.bars = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.game_map = Map()
        
        # Passa as animações carregadas para o Player
        self.player = Player(self, 4, 5, self.assets.player_animations)
        self.all_sprites.add(self.player)

        # O resto do new() continua igual...
        cig_positions = [(200, 120), (630, 210), (900, 520), (140, 600), (500, 350)]
        for pos in cig_positions:
            c = Cigarette(*pos)
            self.items.add(c); self.all_sprites.add(c)
        bar_positions = [(320, 640), (780, 150), (820, 380)]
        for pos in bar_positions:
            b = PullUpBar(*pos)
            self.bars.add(b); self.all_sprites.add(b)
        self.enemy = Enemy(800, 400)
        self.enemies.add(self.enemy); self.all_sprites.add(self.enemy)
        
        self.cigs_level = MAX_STAT_LEVEL
        self.bars_level = MAX_STAT_LEVEL
        self.playing = True
        self.result = None

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()
        if self.running:
             return self.show_game_over_screen()
        return "quit"

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.playing = False
                self.running = False

    def update(self):
        # 1. APLICAR DECAIMENTO CONSTANTE
        self.cigs_level -= CIGS_DECAY_RATE * self.dt
        self.bars_level -= BARS_DECAY_RATE * self.dt

        # 2. VERIFICAR CONDIÇÃO DE DERROTA (se alguma barra zerar)
        if (self.cigs_level <= 0 or self.bars_level <= 0) and not self.result:
            self.result = "lose"
            self.playing = False
            
        # Atualiza o jogador e o inimigo
        self.player.update(self.dt)
        self.enemy.update(self.dt, self.player)

        # 3. VERIFICAR RECARGA DE RECURSOS
        # Checa colisão com cigarros para recarregar Fôlego
        # IMPORTANTE: dokill=False para que os itens não desapareçam
        cig_collisions = pygame.sprite.spritecollide(self.player, self.items, dokill=False)
        if cig_collisions:
            self.cigs_level += CIGS_RECHARGE_RATE * self.dt

        # Checa colisão com barras para recarregar Força
        bar_collisions = pygame.sprite.spritecollide(self.player, self.bars, dokill=False)
        if bar_collisions:
            self.bars_level += BARS_RECHARGE_RATE * self.dt

        # 4. GARANTIR QUE AS BARRAS NÃO ULTRAPASSEM OS LIMITES
        self.cigs_level = clamp(self.cigs_level, 0, MAX_STAT_LEVEL)
        self.bars_level = clamp(self.bars_level, 0, MAX_STAT_LEVEL)
        
        # visão do inimigo -> derrota (essa lógica continua igual)
        if self.enemy.sees(self.player) and not self.result:
            self.result = "lose"
            self.playing = False
        
        # A antiga condição de vitória foi removida, o jogo é de sobrevivência

    def draw(self):
        self.screen.fill((20, 20, 30))
        self.game_map.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.enemy.draw_fov(self.screen)
        # Chamada simplificada para o HUD
        self.hud.draw(self.screen, self.cigs_level, self.bars_level)
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()