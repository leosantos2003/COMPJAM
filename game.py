import pygame
import sys
import time
import random
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
        self.timer_font = pygame.font.SysFont(None, 40)

        # Carregar animações de status com as dimensões corretas
        self.smoke_frames = load_spritesheet_grid("assets/smoke.png", 427, 240)
        self.bar_frames = load_spritesheet_grid("assets/bar.png", 461, 240)
        self.is_smoking = False
        self.is_doing_pullups = False
        self.smoke_anim_index = 0
        self.bar_anim_index = 0
        self.smoke_anim_timer = 0
        self.bar_anim_timer = 0
        self.anim_speed = 0.1

        # Aura Troll Face
        self.aura_image = pygame.image.load("assets/auratrollface.png").convert_alpha()
        self.aura_active = False
        self.aura_timer = 0
        self.aura_duration = 1.0 # Duração em segundos

        self.maps = ["map.txt", "map2.txt", "map3.txt"]
        self.score = 0
        self.start_time = 0
        self.difficulty = "Normal" # Dificuldade padrão

    def show_menu_screen(self):
        self.screen.fill(BLACK)
        title_surf = self.title_font.render(TITLE, True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/6))
        self.screen.blit(title_surf, title_rect)

        # Opções do menu
        options = ["Jogar Mapa 1", "Jogar Mapa 2", "Jogar Mapa 3", "Dificuldade", "Sair"]
        selected_option = 0

        waiting_for_input = True
        while waiting_for_input:
            self.clock.tick(FPS)

            # Desenha as opções
            for i, option in enumerate(options):
                rect = pygame.Rect(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 - 80 + i * 60, 300, 50)
                
                is_quit_option = (option == "Sair")
                
                if i == selected_option:
                    color = RED if is_quit_option else GREEN
                else:
                    color = GRAY

                pygame.draw.rect(self.screen, color, rect)

                if option == "Dificuldade":
                    text_to_render = f"Dificuldade: {self.difficulty}"
                else:
                    text_to_render = option
                
                text_surf = self.font.render(text_to_render, True, BLACK)
                text_rect = text_surf.get_rect(center=rect.center)
                self.screen.blit(text_surf, text_rect)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False
                    self.running = False
                    return None, None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    if event.key == pygame.K_RETURN:
                        if selected_option < 3: # Opções de mapa
                            waiting_for_input = False
                            return self.maps[selected_option], self.difficulty
                        elif options[selected_option] == "Dificuldade":
                            # Cicla entre as dificuldades
                            difficulty_levels = list(DIFFICULTY_LEVELS.keys())
                            current_index = difficulty_levels.index(self.difficulty)
                            next_index = (current_index + 1) % len(difficulty_levels)
                            self.difficulty = difficulty_levels[next_index]
                        else: # Sair
                            waiting_for_input = False
                            self.running = False
                            return None, None

            pygame.display.flip()
        return None, None


    def new(self, map_file, difficulty):
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.bars = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # === MAPA COM ARVORES/PAREDES E ITENS ===
        self.game_map = Map(map_file)
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

        # Usa as configurações de dificuldade para criar o inimigo
        enemy_settings = DIFFICULTY_LEVELS[difficulty]
        self.enemy = Enemy(800, 400, difficulty=enemy_settings)
        self.enemies.add(self.enemy); self.all_sprites.add(self.enemy)

        self.cigs_level = MAX_STAT_LEVEL
        self.bars_level = MAX_STAT_LEVEL
        self.playing = True
        self.result = None
        self.start_time = time.time() # Inicia o timer

    def run(self):
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()
        
        # Quando o loop de jogo (self.playing) termina, decide o que fazer a seguir
        if self.result == "lose":
            return self.death_screen() # Retorna a ação escolhida pelo usuário ("restart", "menu" ou "quit")
        
        # Se o jogo terminou por outro motivo (ex: ESC), volta ao menu
        return "menu"


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing = False

    def update(self):
        self.cigs_level -= CIGS_DECAY_RATE * self.dt
        self.bars_level -= BARS_DECAY_RATE * self.dt
        if (self.cigs_level <= 0 or self.bars_level <= 0) and not self.result:
            self.result = "lose"; self.playing = False

        self.player.update(self.dt, self.solids)
        self.enemy.update(self.dt, self.player, self.solids, self.game_map)

        was_smoking = self.is_smoking
        was_doing_pullups = self.is_doing_pullups

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

        just_started_smoking = self.is_smoking and not was_smoking
        just_started_pullups = self.is_doing_pullups and not was_doing_pullups

        if just_started_smoking or just_started_pullups:
            if not self.aura_active and random.randint(1, 14) == 1:
                self.aura_active = True
                self.aura_timer = self.aura_duration

        if self.aura_active:
            self.aura_timer -= self.dt
            if self.aura_timer <= 0:
                self.aura_active = False

        self.cigs_level = clamp(self.cigs_level, 0, MAX_STAT_LEVEL)
        self.bars_level = clamp(self.bars_level, 0, MAX_STAT_LEVEL)

        if self.enemy.sees(self.player, self.solids) and not self.result:
            self.result = "lose"; self.playing = False
        
        # Atualiza a pontuação baseada no tempo
        if self.playing:
            self.score = int(time.time() - self.start_time)


    def draw_hud(self):
        BAR_LENGTH = 200; BAR_HEIGHT = 25
        
        folego_bar_x = 15; folego_bar_y = 15
        fill_width_folego = (self.cigs_level / MAX_STAT_LEVEL) * BAR_LENGTH
        pygame.draw.rect(self.screen, GRAY, pygame.Rect(folego_bar_x, folego_bar_y, BAR_LENGTH, BAR_HEIGHT))
        pygame.draw.rect(self.screen, RED, pygame.Rect(folego_bar_x, folego_bar_y, fill_width_folego, BAR_HEIGHT))
        folego_text = self.font.render("Fume bastante!", True, WHITE); self.screen.blit(folego_text, (folego_bar_x + 5, folego_bar_y + 4))

        gap_entre_barras = 10
        forca_bar_x = folego_bar_x + BAR_LENGTH + gap_entre_barras
        forca_bar_y = folego_bar_y

        fill_width_forca = (self.bars_level / MAX_STAT_LEVEL) * BAR_LENGTH
        pygame.draw.rect(self.screen, GRAY, pygame.Rect(forca_bar_x, forca_bar_y, BAR_LENGTH, BAR_HEIGHT))
        pygame.draw.rect(self.screen, CYAN, pygame.Rect(forca_bar_x, forca_bar_y, fill_width_forca, BAR_HEIGHT))
        forca_text = self.font.render("Faça mais barras!", True, WHITE); self.screen.blit(forca_text, (forca_bar_x + 5, forca_bar_y + 4))
        
        timer_text = self.timer_font.render(f"Tempo: {self.score}", True, WHITE)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH / 2, 30))
        self.screen.blit(timer_text, timer_rect)


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
            self.screen.blit(pygame.transform.smoothscale(frame, (150, 78)), (SCREEN_WIDTH - 165, 15))


    def draw(self):
        self.game_map.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.enemy.draw_fov(self.screen, self.solids)
        self.draw_hud()
        
        # --- Legenda do Inspetor ---
        texto_legenda_inimigo = self.enemy.name
        cor_legenda_inimigo = WHITE
        legenda_surface_inimigo = self.font.render(texto_legenda_inimigo, True, cor_legenda_inimigo)
        legenda_rect_inimigo = legenda_surface_inimigo.get_rect()
        legenda_rect_inimigo.midbottom = self.enemy.rect.midtop - pygame.math.Vector2(0, 5)
        self.screen.blit(legenda_surface_inimigo, legenda_rect_inimigo)
        
        # --- Legenda e Animação de Ação do Jogador ---
        texto_legenda_jogador = None
        animation_frame = None

        if self.is_smoking:
            texto_legenda_jogador = "Fumando..."
            # Lógica da animação de FUMAR movida para cá
            self.smoke_anim_timer += self.dt
            if self.smoke_anim_timer > self.anim_speed:
                self.smoke_anim_timer = 0
                total_smoke_frames = len(self.smoke_frames) * len(self.smoke_frames[0])
                self.smoke_anim_index = (self.smoke_anim_index + 1) % total_smoke_frames
            row = self.smoke_anim_index // len(self.smoke_frames[0])
            col = self.smoke_anim_index % len(self.smoke_frames[0])
            animation_frame = self.smoke_frames[row][col]

        elif self.is_doing_pullups:
            texto_legenda_jogador = "Fazendo barra fixa..."
            # Lógica da animação de BARRA movida para cá
            self.bar_anim_timer += self.dt
            if self.bar_anim_timer > self.anim_speed:
                self.bar_anim_timer = 0
                total_bar_frames = len(self.bar_frames) * len(self.bar_frames[0])
                self.bar_anim_index = (self.bar_anim_index + 1) % total_bar_frames
            row = self.bar_anim_index // len(self.bar_frames[0])
            col = self.bar_anim_index % len(self.bar_frames[0])
            animation_frame = self.bar_frames[row][col]

        if texto_legenda_jogador:
            # Desenha a legenda de texto
            cor_legenda_jogador = WHITE
            legenda_surface_jogador = self.font.render(texto_legenda_jogador, True, cor_legenda_jogador)
            legenda_rect_jogador = legenda_surface_jogador.get_rect()
            legenda_rect_jogador.midbottom = self.player.rect.midtop - pygame.math.Vector2(0, 5)
            self.screen.blit(legenda_surface_jogador, legenda_rect_jogador)
            
            # Se houver uma animação, desenha ela ACIMA da legenda de texto
            if animation_frame:
                # Define um tamanho menor para a animação sobre o jogador
                anim_size = (108, 84) 
                scaled_frame = pygame.transform.smoothscale(animation_frame, anim_size)
                anim_rect = scaled_frame.get_rect()
                # Posiciona a animação acima da legenda
                anim_rect.midbottom = legenda_rect_jogador.midtop - pygame.math.Vector2(0, 3)
                self.screen.blit(scaled_frame, anim_rect)

        # --- Aura e Texto Abaixo do Jogador ---
        if self.aura_active:
            # Posição da imagem da aura: abaixo do jogador
            aura_offset_y = 10 
            aura_rect = self.aura_image.get_rect(midtop=(self.player.rect.centerx, self.player.rect.bottom + aura_offset_y))
            self.screen.blit(self.aura_image, aura_rect)

            # Posição do texto da aura: abaixo da imagem da aura
            text_offset_y = 5 
            aura_text_surf = self.font.render("+AURA +EGO", True, WHITE)
            aura_text_rect = aura_text_surf.get_rect(midtop=(aura_rect.centerx, aura_rect.bottom + text_offset_y))
            self.screen.blit(aura_text_surf, aura_text_rect)

        pygame.display.flip()

    def death_screen(self):
        self.screen.fill(BLACK)
        try:
            death_img = pygame.image.load("assets/itsover.png").convert_alpha()
            death_rect = death_img.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
            self.screen.blit(death_img, death_rect)
        except pygame.error:
            title_surf = self.title_font.render("VOCÊ FOI PEGO!", True, RED)
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
            self.screen.blit(title_surf, title_rect)

        score_surf = self.font.render(f"Pontuação Final: {self.score}", True, WHITE)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
        self.screen.blit(score_surf, score_rect)

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
                        if selected_option == 0:
                            return "restart"
                        else:
                            return "menu"

            restart_color = GREEN if selected_option == 0 else GRAY
            menu_color = RED if selected_option == 1 else GRAY

            pygame.draw.rect(self.screen, restart_color, button_restart_rect)
            restart_text = self.font.render("Recomeçar", True, BLACK)
            self.screen.blit(restart_text, restart_text.get_rect(center=button_restart_rect.center))

            pygame.draw.rect(self.screen, menu_color, button_menu_rect)
            menu_text = self.font.render("Voltar ao Menu", True, BLACK)
            self.screen.blit(menu_text, menu_text.get_rect(center=button_menu_rect.center))

            pygame.display.flip()
        
        return "quit"

    def quit(self):
        pygame.quit(); sys.exit()