import pygame
import sys
from settings import *
from player import Player
from enemy import Enemy
from items import Cigarette, PullUpBar
from map import Map
from utils import clamp

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 80)

    def show_menu_screen(self):
        self.screen.fill(BLACK)
        title_surf = self.title_font.render(TITLE, True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        self.screen.blit(title_surf, title_rect)
        play_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2, 200, 50)
        quit_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 70, 200, 50)
        selected_option = 0
        options = ["Jogar", "Sair"]
        waiting_for_input = True
        while waiting_for_input:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN: selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_UP: selected_option = (selected_option - 1) % len(options)
                    if event.key == pygame.K_RETURN:
                        if selected_option == 0: waiting_for_input = False
                        else:
                            waiting_for_input = False
                            self.running = False
            play_color = GREEN if selected_option == 0 else GRAY
            quit_color = RED if selected_option == 1 else GRAY
            pygame.draw.rect(self.screen, play_color, play_button_rect)
            play_text = self.font.render("Jogar", True, BLACK)
            self.screen.blit(play_text, play_text.get_rect(center=play_button_rect.center))
            pygame.draw.rect(self.screen, quit_color, quit_button_rect)
            quit_text = self.font.render("Sair", True, BLACK)
            self.screen.blit(quit_text, quit_text.get_rect(center=quit_button_rect.center))
            pygame.display.flip()

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.bars = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # === MAPA COM ARVORES/PAREDES ===
        self.game_map = Map("map.txt")
        self.solids = self.game_map.solids  # grupo de colisão

        # player nasce no spawn do mapa (fallback no próprio player se faltar)
        self.player = Player(self, 4, 5)
        self.all_sprites.add(self.player)

        # itens (mesmos de antes)
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

        self.enemy_move_speed = ENEMY_SPEED
        self.enemy_turn_speed = ENEMY_TURN_SPEED
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
        self.end_screen()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing = False
                    self.running = False
                if event.key == pygame.K_1: self.enemy_move_speed -= 20
                if event.key == pygame.K_2: self.enemy_move_speed += 20
                if event.key == pygame.K_3: self.enemy_turn_speed -= 0.5
                if event.key == pygame.K_4: self.enemy_turn_speed += 0.5
                self.enemy_move_speed = clamp(self.enemy_move_speed, 40, 500)
                self.enemy_turn_speed = clamp(self.enemy_turn_speed, 1.0, 10.0)

    def update(self):
        self.cigs_level -= CIGS_DECAY_RATE * self.dt
        self.bars_level -= BARS_DECAY_RATE * self.dt
        if (self.cigs_level <= 0 or self.bars_level <= 0) and not self.result:
            self.result = "lose"; self.playing = False

        # passa colisões
        self.player.update(self.dt, self.solids)
        # aplica as variáveis de dificuldade no inimigo e atualiza com colisão
        self.enemy.move_speed = self.enemy_move_speed
        self.enemy.turn_speed = self.enemy_turn_speed
        self.enemy.update(self.dt, self.player, self.solids)

        cig_collisions = pygame.sprite.spritecollide(self.player, self.items, dokill=False)
        if cig_collisions: self.cigs_level += CIGS_RECHARGE_RATE * self.dt
        bar_collisions = pygame.sprite.spritecollide(self.player, self.bars, dokill=False)
        if bar_collisions: self.bars_level += BARS_RECHARGE_RATE * self.dt
        self.cigs_level = clamp(self.cigs_level, 0, MAX_STAT_LEVEL)
        self.bars_level = clamp(self.bars_level, 0, MAX_STAT_LEVEL)

        if self.enemy.sees(self.player) and not self.result:
            self.result = "lose"; self.playing = False

    def draw_hud(self):
        BAR_LENGTH = 200; BAR_HEIGHT = 25
        folego_bar_x = 15; folego_bar_y = 15
        fill_width_folego = (self.cigs_level / MAX_STAT_LEVEL) * BAR_LENGTH
        pygame.draw.rect(self.screen, GRAY, pygame.Rect(folego_bar_x, folego_bar_y, BAR_LENGTH, BAR_HEIGHT))
        pygame.draw.rect(self.screen, YELLOW, pygame.Rect(folego_bar_x, folego_bar_y, fill_width_folego, BAR_HEIGHT))
        folego_text = self.font.render("Fôlego", True, WHITE); self.screen.blit(folego_text, (folego_bar_x + 5, folego_bar_y + 4))

        forca_bar_x = 15; forca_bar_y = 50
        fill_width_forca = (self.bars_level / MAX_STAT_LEVEL) * BAR_LENGTH
        pygame.draw.rect(self.screen, GRAY, pygame.Rect(forca_bar_x, forca_bar_y, BAR_LENGTH, BAR_HEIGHT))
        pygame.draw.rect(self.screen, CYAN, pygame.Rect(forca_bar_x, forca_bar_y, fill_width_forca, BAR_HEIGHT))
        forca_text = self.font.render("Força", True, WHITE); self.screen.blit(forca_text, (forca_bar_x + 5, forca_bar_y + 4))
        tip = self.font.render("Fique nos itens para recuperar os status. Fuja do cone!", True, GRAY)
        self.screen.blit(tip, (12, 90))

    def draw(self):
        self.game_map.draw(self.screen)  # fundo + tiles
        self.all_sprites.draw(self.screen)
        self.enemy.draw_fov(self.screen)
        self.draw_hud()
        pygame.display.flip()

    def end_screen(self):
        msg = "VOCÊ VENCEU!" if self.result == "win" else "VOCÊ PERDEU!"
        sub = "Enter para jogar novamente | Esc para sair"
        shade = GREEN if self.result == "win" else RED
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.screen.blit(overlay, (0,0))
        title = pygame.font.SysFont(None, 64).render(msg, True, shade)
        rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        self.screen.blit(title, rect)
        subtx = self.font.render(sub, True, WHITE)
        self.screen.blit(subtx, subtx.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))
        pygame.display.flip()
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False; self.running = False
                if event.type == pygame.KEYDOWN:
                    waiting = False
            self.clock.tick(30)

    def quit(self):
        pygame.quit(); sys.exit()
