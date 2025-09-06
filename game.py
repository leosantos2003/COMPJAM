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

        # OBJETIVOS E ESTADO (LÓGICA ALTERADA)
        self.cigs_level = MAX_STAT_LEVEL  # Começa com Fôlego no máximo
        self.bars_level = MAX_STAT_LEVEL  # Começa com Força no máximo
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

    def draw_hud(self):
        # --- Barra de Fôlego (Cigarros) ---
        BAR_LENGTH = 200
        BAR_HEIGHT = 25
        
        # Posição da barra de Fôlego
        folego_bar_x = 15
        folego_bar_y = 15

        # Calcula a largura da barra com base no nível atual
        fill_width_folego = (self.cigs_level / MAX_STAT_LEVEL) * BAR_LENGTH
        
        # Desenha o fundo e o preenchimento da barra
        background_rect_folego = pygame.Rect(folego_bar_x, folego_bar_y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect_folego = pygame.Rect(folego_bar_x, folego_bar_y, fill_width_folego, BAR_HEIGHT)

        pygame.draw.rect(self.screen, GRAY, background_rect_folego)
        pygame.draw.rect(self.screen, YELLOW, fill_rect_folego)
        
        # Texto da barra
        folego_text = self.font.render("Fôlego", True, WHITE)
        self.screen.blit(folego_text, (folego_bar_x + 5, folego_bar_y + 4))


        # --- Barra de Força (Barras Fixas) ---
        # Posição da barra de Força
        forca_bar_x = 15
        forca_bar_y = 50
        
        fill_width_forca = (self.bars_level / MAX_STAT_LEVEL) * BAR_LENGTH
        
        background_rect_forca = pygame.Rect(forca_bar_x, forca_bar_y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect_forca = pygame.Rect(forca_bar_x, forca_bar_y, fill_width_forca, BAR_HEIGHT)
        
        pygame.draw.rect(self.screen, GRAY, background_rect_forca)
        pygame.draw.rect(self.screen, CYAN, fill_rect_forca)
        
        forca_text = self.font.render("Força", True, WHITE)
        self.screen.blit(forca_text, (forca_bar_x + 5, forca_bar_y + 4))

        # Dica de controles
        tip = self.font.render("Fique nos itens para recuperar os status. Fuja do cone!", True, GRAY)
        self.screen.blit(tip, (12, 90))


    def draw(self):
        self.screen.fill((20, 20, 30))
        self.game_map.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.enemy.draw_fov(self.screen)
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