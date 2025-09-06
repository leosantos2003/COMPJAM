# game.py
import pygame
import sys
from settings import *
from player import Player
from enemy import Enemy
from items import Cigarette, PullUpBar
from map import Map
from utils import clamp # Importar a função clamp

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.font = pygame.font.SysFont(None, 28)

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.bars = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.game_map = Map()
        self.player = Player(self, 4, 5)
        self.all_sprites.add(self.player)

        # ... (código para criar cigarros e barras continua o mesmo) ...
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

        # VARIÁVEIS DE CONTROLE DE DIFICULDADE
        self.enemy_move_speed = ENEMY_SPEED
        self.enemy_turn_speed = ENEMY_TURN_SPEED

        self.cigs_collected = 0
        self.bars_done = 0
        self.time_left = ROUND_TIME
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
                
                # NOVOS CONTROLES DE DIFICULDADE
                # Altera velocidade de movimento
                if event.key == pygame.K_1:
                    self.enemy_move_speed -= 20
                if event.key == pygame.K_2:
                    self.enemy_move_speed += 20
                # Altera velocidade de giro
                if event.key == pygame.K_3:
                    self.enemy_turn_speed -= 0.5
                if event.key == pygame.K_4:
                    self.enemy_turn_speed += 0.5
                
                # Garante que os valores não fiquem negativos ou excessivamente baixos
                self.enemy_move_speed = clamp(self.enemy_move_speed, 40, 500)
                self.enemy_turn_speed = clamp(self.enemy_turn_speed, 1.0, 10.0)

    def update(self):
        self.time_left -= self.dt
        if self.time_left <= 0 and not self.result:
            self.result = "lose"
            self.playing = False

        # ATUALIZA AS VARIÁVEIS DO INIMIGO COM OS VALORES DO JOGO
        self.enemy.move_speed = self.enemy_move_speed
        self.enemy.turn_speed = self.enemy_turn_speed

        self.player.update(self.dt)
        self.items.update(self.dt)
        self.bars.update(self.dt)
        self.enemy.update(self.dt, self.player)

        # ... (resto da lógica de update continua o mesmo) ...
        got = pygame.sprite.spritecollide(self.player, self.items, dokill=True)
        if got:
            self.cigs_collected += len(got)

        colliding = pygame.sprite.spritecollide(self.player, self.bars, dokill=False)
        for bar in self.bars:
            if bar in colliding and bar.cooldown_timer <= 0:
                bar.hold += self.dt
                if bar.hold >= bar.hold_needed:
                    self.bars_done += 1
                    bar.on_count()
            else:
                if bar.cooldown_timer <= 0:
                    bar.hold = 0.0

        if self.enemy.sees(self.player) and not self.result:
            self.result = "lose"
            self.playing = False

        if (self.cigs_collected >= NEEDED_CIGS and self.bars_done >= NEEDED_BARS and not self.result):
            self.result = "win"
            self.playing = False

    # ... (função draw_bar_progress continua a mesma) ...
    def draw_bar_progress(self, bar):
        r = bar.rect
        w = TILE
        h = 6
        x = r.centerx - w // 2
        y = r.top - 12
        pygame.draw.rect(self.screen, (30, 30, 30), (x, y, w, h))
        prog = int(w * bar.progress_ratio())
        pygame.draw.rect(self.screen, (0, 180, 0), (x, y, prog, h))
        pygame.draw.rect(self.screen, (220, 220, 220), (x, y, w, h), 1)

    def draw_hud(self):
        # Texto principal do HUD
        txt = f"Cigarros: {self.cigs_collected}/{NEEDED_CIGS}  |  Barras: {self.bars_done}/{NEEDED_BARS}  |  Tempo: {int(self.time_left)}"
        surf = self.font.render(txt, True, WHITE)
        self.screen.blit(surf, (12, 10))
        
        # NOVO TEXTO PARA DIFICULDADE
        # Usamos :.1f para formatar o número com 1 casa decimal
        diff_txt = f"Dificuldade [Teclas 1-4]: Velocidade {self.enemy_move_speed} | Giro {self.enemy_turn_speed:.1f}"
        diff_surf = self.font.render(diff_txt, True, CYAN)
        # Posiciona abaixo da dica dos controles
        tip_rect = self.screen.blit(self.font.render("Controles: WASD/Setas.", True, GRAY), (12, 40))
        self.screen.blit(diff_surf, (12, tip_rect.bottom + 5))


    def draw(self):
        self.screen.fill((20, 20, 30))
        self.game_map.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.enemy.draw_fov(self.screen)
        for bar in self.bars:
            if bar.cooldown_timer <= 0 and bar.hold > 0:
                self.draw_bar_progress(bar)
        self.draw_hud()
        pygame.display.flip()

    # ... (funções end_screen e quit continuam as mesmas) ...
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
                    if event.key == pygame.K_RETURN:
                        waiting = False
                    if event.key == pygame.K_ESCAPE:
                        waiting = False; self.running = False
            self.clock.tick(30)

    def quit(self):
        pygame.quit()
        sys.exit()