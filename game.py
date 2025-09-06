import pygame
import sys
from settings import *
from player import Player
from enemy import Enemy
from items import Cigarette, PullUpBar
from map import Map  # Importa a classe Map

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
        # grupos
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.bars = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Inicializa o mapa
        self.game_map = Map() # Instancia a classe Map

        # jogador
        self.player = Player(self, 4, 5)  # posição em tiles
        self.all_sprites.add(self.player)

        # coloca cigarros
        cig_positions = [
            (200, 120), (630, 210), (900, 520), (140, 600), (500, 350)
        ]
        for pos in cig_positions:
            c = Cigarette(*pos)
            self.items.add(c); self.all_sprites.add(c)

        # barras fixas (não somem)
        bar_positions = [(320, 640), (780, 150), (820, 380)]
        for pos in bar_positions:
            b = PullUpBar(*pos)
            self.bars.add(b); self.all_sprites.add(b)

        # inimigo agora persegue o jogador
        # patrol = [(150,150), (900,150), (900,650), (150,650)] # Linha removida
        self.enemy = Enemy(800, 400) # Cria o inimigo em uma posição inicial (x, y)
        self.enemies.add(self.enemy); self.all_sprites.add(self.enemy)

        # objetivos e estado
        self.cigs_collected = 0
        self.bars_done = 0
        self.time_left = ROUND_TIME
        self.playing = True
        self.result = None  # "win" | "lose" | None

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()
        # tela de fim rápida
        self.end_screen()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.playing = False
                self.running = False

    def update(self):
        # contagem regressiva
        self.time_left -= self.dt
        if self.time_left <= 0 and not self.result:
            self.result = "lose"
            self.playing = False

        # atualiza sprites (passando dt)
        # self.all_sprites.update(self.dt)

        # Atualiza os sprites individualmente ou por grupos que não precisam de argumentos extras
        self.player.update(self.dt)
        self.items.update(self.dt)
        self.bars.update(self.dt)
        self.enemy.update(self.dt, self.player) # Passa o jogador para o inimigo

        # coleta de cigarros (pickup instantâneo)
        got = pygame.sprite.spritecollide(self.player, self.items, dokill=True)
        if got:
            self.cigs_collected += len(got)

        # usar barra: precisa ficar parado em cima por BAR_HOLD_SECONDS
        colliding = pygame.sprite.spritecollide(self.player, self.bars, dokill=False)
        for bar in self.bars:
            if bar in colliding and bar.cooldown_timer <= 0:
                bar.hold += self.dt
                if bar.hold >= bar.hold_needed:
                    self.bars_done += 1
                    bar.on_count()   # ativa cooldown e reseta hold
            else:
                # saiu da área da barra ou está em cooldown -> zera progresso
                if bar.cooldown_timer <= 0:
                    bar.hold = 0.0

        # visão do inimigo -> derrota
        if self.enemy.sees(self.player) and not self.result:
            self.result = "lose"
            self.playing = False

        # vitória?
        if (self.cigs_collected >= NEEDED_CIGS and
            self.bars_done >= NEEDED_BARS and not self.result):
            self.result = "win"
            self.playing = False

    def draw_bar_progress(self, bar):
        # desenha uma barra de progresso acima da PullUpBar
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
        txt = f"Cigarros: {self.cigs_collected}/{NEEDED_CIGS}  |  Barras: {self.bars_done}/{NEEDED_BARS}  |  Tempo: {int(self.time_left)}"
        surf = self.font.render(txt, True, WHITE)
        self.screen.blit(surf, (12, 10))
        tip = self.font.render("Controles: WASD/Setas. Fique na barra para encher o medidor. Fuja do cone!", True, GRAY)
        self.screen.blit(tip, (12, 40))

    def draw(self):
        self.screen.fill((20, 20, 30))
        # Desenha o mapa
        self.game_map.draw(self.screen)

        self.all_sprites.draw(self.screen)
        # desenha cone do inimigo
        self.enemy.draw_fov(self.screen)

        # desenha progresso nas barras quando o player está em cima e sem cooldown
        for bar in self.bars:
            if bar.cooldown_timer <= 0 and bar.hold > 0:
                self.draw_bar_progress(bar)

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
                    if event.key == pygame.K_RETURN:
                        waiting = False
                    if event.key == pygame.K_ESCAPE:
                        waiting = False; self.running = False
            self.clock.tick(30)

    def quit(self):
        pygame.quit()
        sys.exit()

