import pygame
import sys
from settings import *
from player import Player
from enemy import Enemy
from items import Cigarette, PullUpBar
from map import Map
from utils import clamp, load_spritesheet_grid

class Game:
    def __init__(self):
        pygame.init()
        # Lógica para TELA CHEIA
        if FULLSCREEN:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 80)

        # Carregar animações de status com as dimensões corretas
        self.smoke_frames = load_spritesheet_grid("assets/smoke.png", 427, 240)
        # CORREÇÃO FINAL COM AS SUAS DIMENSÕES: 461x240
        self.bar_frames = load_spritesheet_grid("assets/bar.png", 461, 240)
        self.is_smoking = False
        self.is_doing_pullups = False
        self.smoke_anim_index = 0
        self.bar_anim_index = 0
        self.smoke_anim_timer = 0
        self.bar_anim_timer = 0
        self.anim_speed = 0.1

    def show_menu_screen(self):
        self.screen.fill(BLACK)
        title_surf = self.title_font.render(TITLE, True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        self.screen.blit(title_surf, title_rect)

        # Ajustando a posição dos botões para serem reutilizáveis
        button_play_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2, 200, 50)
        button_quit_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 70, 200, 50)

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
                        if selected_option == 0: waiting_for_input = False # Inicia o jogo
                        else: # Sai do jogo
                            waiting_for_input = False
                            self.running = False

            play_color = GREEN if selected_option == 0 else GRAY
            quit_color = RED if selected_option == 1 else GRAY

            pygame.draw.rect(self.screen, play_color, button_play_rect)
            play_text = self.font.render("Jogar", True, BLACK)
            self.screen.blit(play_text, play_text.get_rect(center=button_play_rect.center))

            pygame.draw.rect(self.screen, quit_color, button_quit_rect)
            quit_text = self.font.render("Sair", True, BLACK)
            self.screen.blit(quit_text, quit_text.get_rect(center=button_quit_rect.center))

            pygame.display.flip()

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.bars = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # === MAPA COM ARVORES/PAREDES E ITENS ===
        self.game_map = Map("map.txt")
        self.solids = self.game_map.solids  # grupo de colisão

        # player nasce no spawn do mapa (fallback no próprio player se faltar)
        self.player = Player(self, 4, 5)
        self.all_sprites.add(self.player)

        # itens (agora carregados do mapa)
        for pos in self.game_map.cig_positions:
            c = Cigarette(*pos)
            self.items.add(c); self.all_sprites.add(c)
        for pos in self.game_map.bar_positions:
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
        if self.result == "lose":
            self.death_screen()
        else:
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
        self.enemy.update(self.dt, self.player, self.solids, self.game_map)

        self.is_smoking = False
        cig_collisions = pygame.sprite.spritecollide(self.player, self.items, dokill=False)
        if cig_collisions:
            self.cigs_level += CIGS_RECHARGE_RATE * self.dt
            self.is_smoking = True

        self.is_doing_pullups = False
        bar_collisions = pygame.sprite.spritecollide(self.player, self.bars, dokill=False)
        if bar_collisions:
            self.bars_level += BARS_RECHARGE_RATE * self.dt
            self.is_doing_pullups = True

        self.cigs_level = clamp(self.cigs_level, 0, MAX_STAT_LEVEL)
        self.bars_level = clamp(self.bars_level, 0, MAX_STAT_LEVEL)

        if self.enemy.sees(self.player, self.solids) and not self.result:
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

    def draw_status_animations(self):
        if self.is_smoking:
            self.smoke_anim_timer += self.dt
            if self.smoke_anim_timer > self.anim_speed:
                self.smoke_anim_timer = 0
                total_smoke_frames = len(self.smoke_frames) * len(self.smoke_frames[0])
                self.smoke_anim_index = (self.smoke_anim_index + 1) % total_smoke_frames

            row = self.smoke_anim_index // len(self.smoke_frames[0])
            col = self.smoke_anim_index % len(self.smoke_frames[0])
            frame = self.smoke_frames[row][col]
            self.screen.blit(pygame.transform.smoothscale(frame, (150, 84)), (SCREEN_WIDTH - 165, 15))

        if self.is_doing_pullups:
            self.bar_anim_timer += self.dt
            if self.bar_anim_timer > self.anim_speed:
                self.bar_anim_timer = 0
                total_bar_frames = len(self.bar_frames) * len(self.bar_frames[0])
                self.bar_anim_index = (self.bar_anim_index + 1) % total_bar_frames

            row = self.bar_anim_index // len(self.bar_frames[0])
            col = self.bar_anim_index % len(self.bar_frames[0])
            frame = self.bar_frames[row][col]
            # Novo tamanho de exibição para manter a proporção de 461:240
            self.screen.blit(pygame.transform.smoothscale(frame, (150, 78)), (SCREEN_WIDTH - 165, 15))

    def draw(self):
        self.game_map.draw(self.screen)  # fundo + tiles
        self.all_sprites.draw(self.screen)
        self.enemy.draw_fov(self.screen)
        self.draw_hud()
        self.draw_status_animations()

        # --- CÓDIGO ADICIONADO PARA DESENHAR A LEGENDA DO INSPETOR ---
        # 1. Define o texto e a cor da legenda
        texto_legenda = self.enemy.name
        cor_legenda = WHITE  # Você pode usar qualquer cor de 'settings.py'

        # 2. Renderiza o texto em uma superfície
        legenda_surface = self.font.render(texto_legenda, True, cor_legenda)
        legenda_rect = legenda_surface.get_rect()

        # 3. Posiciona a legenda um pouco acima do inspetor
        # O centro inferior (midbottom) da legenda ficará alinhado ao centro superior (midtop) do inspetor
        # O -5 serve para dar um pequeno espaço entre o nome e a cabeça do inspetor
        legenda_rect.midbottom = self.enemy.rect.midtop - pygame.math.Vector2(0, 5)

        # 4. Desenha a legenda na tela
        self.screen.blit(legenda_surface, legenda_rect)
        # --------------------------------------------------------------

        pygame.display.flip()

    def death_screen(self):
        self.screen.fill(BLACK)
        title_surf = self.title_font.render("VOCÊ FOI PEGO!", True, RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        self.screen.blit(title_surf, title_rect)

        button_restart_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2, 200, 50)
        button_menu_rect = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 70, 200, 50)

        selected_option = 0
        options = ["Recomeçar", "Voltar ao Menu"]
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
                        if selected_option == 0: # Recomeçar o jogo
                            waiting_for_input = False
                            self.new()
                            self.run()
                        else: # Voltar ao menu principal
                            waiting_for_input = False
                            self.show_menu_screen()
                            self.new() # Reinicia o jogo para o estado inicial para o menu
                            self.run()

            restart_color = GREEN if selected_option == 0 else GRAY
            menu_color = RED if selected_option == 1 else GRAY

            pygame.draw.rect(self.screen, restart_color, button_restart_rect)
            restart_text = self.font.render("Recomeçar", True, BLACK)
            self.screen.blit(restart_text, restart_text.get_rect(center=button_restart_rect.center))

            pygame.draw.rect(self.screen, menu_color, button_menu_rect)
            menu_text = self.font.render("Voltar ao Menu", True, BLACK)
            self.screen.blit(menu_text, menu_text.get_rect(center=button_menu_rect.center))

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