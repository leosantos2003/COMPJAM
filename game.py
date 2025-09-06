# game.py RESOLVIDO

import pygame
import sys
import time
import random
import math
from settings import *
from player import Player
from enemy import Enemy
from items import Cigarette, PullUpBar, Herb
from map import Map
from utils import clamp, load_spritesheet_grid

class Game:
    def __init__(self):
        # --- ALTERAÇÃO FEITA AQUI (Otimização de áudio) ---
        # Pré-inicializa o mixer com um buffer menor para reduzir a latência do som
        pygame.mixer.pre_init(44100, -16, 2, 512)
        # ---------------------------------------------------
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

        # Carregando as fontes
        try:
            self.title_font = pygame.font.Font("fonts/Pricedown_BL.otf", 60)
            self.menu_font_normal = pygame.font.Font("fonts/Pricedown_BL.otf", 35)
            self.menu_font_selected = pygame.font.Font("fonts/Pricedown_BL.otf", 40)
            self.hud_font = pygame.font.Font("fonts/Pricedown_BL.otf", 20)
            self.timer_font = pygame.font.Font("fonts/Pricedown_BL.otf", 28)
        except FileNotFoundError:
            print("Aviso: Arquivo de fonte não encontrado. Usando fontes padrão.")
            self.title_font = pygame.font.SysFont(None, 80)
            self.menu_font_normal = pygame.font.SysFont(None, 45)
            self.menu_font_selected = pygame.font.SysFont(None, 55)
            self.hud_font = pygame.font.SysFont(None, 28)
            self.timer_font = pygame.font.SysFont(None, 40)
            
        try:
            self.menu_nav_sound = pygame.mixer.Sound("assets/sound/menu_sound.wav")
        except pygame.error:
            print("Aviso: Arquivo de som do menu (menu_sound.wav) não encontrado.")
            self.menu_nav_sound = None

        # Carregar animações de status
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

        # Efeito "CHAPADO"
        self.chapado_effect_active = False
        self.chapado_timer = 0
        self.chapado_duration = 5.0 # 5 segundos

        self.maps = ["map.txt", "map2.txt", "map3.txt"]
        self.score = 0
        self.start_time = 0
        self.difficulty = "Normal" # Dificuldade padrão

        # --- CÓDIGO NOVO PARA CARREGAR A MÚSICA ---
        try:
            pygame.mixer.music.load('audio/background_music.mp3')
            pygame.mixer.music.set_volume(0.4) # Ajuste o volume (0.0 a 1.0)
            print("Música de fundo carregada com sucesso.")
        except pygame.error as e:
            print(f"Aviso: Não foi possível carregar a música de fundo: {e}")
        # -------------------------------------------

        # --- CÓDIGO NOVO PARA CARREGAR OS EFEITOS SONOROS ---
        self.smoking_sound = None
        self.pullup_sound = None
        self.jumpscare_sound = None # <-- Adicione esta linha
        try:
            self.smoking_sound = pygame.mixer.Sound('audio/smoke_sound.mp3')
            self.smoking_sound.set_volume(0.6)
            self.pullup_sound = pygame.mixer.Sound('audio/bar_sound.mp3')
            self.pullup_sound.set_volume(0.6)
            self.jumpscare_sound = pygame.mixer.Sound('audio/jumpscare.mp3') # <-- Adicione esta linha
            self.jumpscare_sound.set_volume(0.7) # <-- Adicione esta linha
            self.caught_sound = pygame.mixer.Sound('audio/death_scream.mp3') # <-- Adicione esta linha
            self.caught_sound.set_volume(0.8) # <-- Adicione esta linha (pode ajustar o volume)
            print("Efeitos sonoros carregados.")
        except pygame.error as e:
            print(f"Aviso: Não foi possível carregar um ou mais efeitos sonoros: {e}")
        # ---------------------------------------------------

        # --- Variáveis para a nova sequência de Game Over ---
        self.game_over_sequence_active = False
        self.game_over_timer = 0.0
        # --------------------------------------------------
        

    def _draw_menu_options(self, options, selected_option, start_y, line_spacing=70):
        """
        Desenha uma lista de opções de menu na tela, aplicando efeitos de seleção
        e diferenciando cores para "Sair" e "Voltar ao Menu".
        """
        for i, option_text in enumerate(options):
            is_selected = (i == selected_option)
            
            # Define a fonte e o texto base
            if is_selected:
                font = self.menu_font_selected
                arrow = "> " # Seta branca
            else:
                font = self.menu_font_normal
                arrow = "  " # Espaço para alinhar

            # Define a cor
            if is_selected and (option_text == "Sair" or option_text == "Voltar ao Menu"):
                color = RED # Opções de saída ficam vermelhas quando selecionadas
            elif is_selected:
                color = GREEN # Outras opções ficam verdes quando selecionadas
            else:
                color = GRAY # Opções não selecionadas ficam cinzas

            # Constrói a string de texto com a seta/espaço e o valor da dificuldade
            if option_text == "Dificuldade":
                text_str = f"{arrow}Dificuldade: {self.difficulty}"
            else:
                text_str = f"{arrow}{option_text}"

            # Renderiza o texto
            text_surf = font.render(text_str, True, color)
            
            # Posiciona o texto
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, start_y + i * line_spacing))
            
            # Desenha na tela
            self.screen.blit(text_surf, text_rect)

    def show_briefing_screen(self):
        """
        Mostra uma tela preta com frases sequenciais antes do início da partida.
        Permite pular a cena com a tecla Enter.
        """
        phrases = [
            "Você fumará todos os cigarros...",
            "Você usará todas as barras fixas...",
            "Mas o Geralzão não irá deixar barato!"
        ]
        displayed_phrases = []
        current_phrase_index = 0
        
        last_update_time = pygame.time.get_ticks()
        delay_seconds = 3
        delay_ms = delay_seconds * 1000

        # Prepara o texto de "pular" uma vez fora do loop
        skip_font = self.hud_font # Usando uma fonte menor para a dica
        skip_surf = skip_font.render("Pressione Enter para pular", True, GRAY)
        skip_rect = skip_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))

        briefing_active = True
        while briefing_active:
            self.clock.tick(FPS)

            # --- ALTERAÇÃO NO LOOP DE EVENTOS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    # Permite sair com ESC
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
                    # Permite pular com ENTER
                    if event.key == pygame.K_RETURN:
                        briefing_active = False
            # --- FIM DA ALTERAÇÃO ---

            now = pygame.time.get_ticks()
            if now - last_update_time > delay_ms:
                if current_phrase_index < len(phrases):
                    displayed_phrases.append(phrases[current_phrase_index])
                    current_phrase_index += 1
                    last_update_time = now
                else:
                    briefing_active = False

            self.screen.fill(BLACK)
            
            # Desenha as frases do briefing
            start_y = SCREEN_HEIGHT / 2 - 100
            line_spacing = 60
            for i, text in enumerate(displayed_phrases):
                if i == 2:
                    color = YELLOW
                else:
                    color = WHITE
                
                text_surf = self.menu_font_normal.render(text, True, color)
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, start_y + i * line_spacing))
                self.screen.blit(text_surf, text_rect)

            # --- ADICIONADO: Desenha o texto para pular ---
            self.screen.blit(skip_surf, skip_rect)
            # --------------------------------------------

            pygame.display.flip()

    def show_menu_screen(self):
        self.screen.fill(BLACK)
        title_surf = self.title_font.render(TITLE, True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        
        options = ["Jogar Mapa 1", "Jogar Mapa 2", "Jogar Mapa 3", "Dificuldade", "Sair"]
        selected_option = 0

        waiting_for_input = True
        while waiting_for_input:
            self.clock.tick(FPS)
            self.screen.fill(OXFORDBLUE) #*************************
            self.screen.blit(title_surf, title_rect)

            self._draw_menu_options(options, selected_option, start_y=SCREEN_HEIGHT / 2)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False; self.running = False; return None, None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                        if self.menu_nav_sound:
                            self.menu_nav_sound.play()
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                        if self.menu_nav_sound:
                            self.menu_nav_sound.play()
                    if event.key == pygame.K_RETURN:
                        if selected_option < 3:
                            return self.maps[selected_option], self.difficulty
                        elif options[selected_option] == "Dificuldade":
                            levels = list(DIFFICULTY_LEVELS.keys())
                            current_idx = levels.index(self.difficulty)
                            self.difficulty = levels[(current_idx + 1) % len(levels)]
                        else:
                            waiting_for_input = False; self.running = False; return None, None
            
            pygame.display.flip()
        return None, None


    def new(self, map_file, difficulty):
        self.all_sprites = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.bars = pygame.sprite.Group()
        self.herbs = pygame.sprite.Group() # Grupo para o novo item
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

        # --- CÓDIGO NOVO PARA TOCAR A MÚSICA ---
        # O argumento loops=-1 faz a música tocar continuamente
        pygame.mixer.music.play(loops=-1)
        # --------------------------------------

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
                    pygame.mixer.music.fadeout(1000) # <-- ADICIONE AQUI

    def update(self):
        # --- LÓGICA DA SEQUÊNCIA DE GAME OVER ---
        # Se a sequência estiver ativa, apenas o timer é contado.
        if self.game_over_sequence_active:
            self.game_over_timer -= self.dt
            if self.game_over_timer <= 0:
                # O tempo acabou, então o jogo realmente termina
                self.game_over_sequence_active = False
                self.result = "lose"
                self.playing = False
            return # Pula o resto da lógica de update para "congelar" o jogo
        # ----------------------------------------
        # Lógica do efeito "CHAPADO" (só ativa se HERB_ENABLED for True)
        if HERB_ENABLED and self.chapado_effect_active:
            self.chapado_timer -= self.dt
            if self.chapado_timer <= 0:
                self.chapado_effect_active = False
        else:
            # Só decai as barras se não estiver "chapado"
            self.cigs_level -= CIGS_DECAY_RATE * self.dt
            self.bars_level -= BARS_DECAY_RATE * self.dt

        if (self.cigs_level <= 0 or self.bars_level <= 0) and not self.result:
            # Perder por status inicia a sequência também
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

        self.is_smoking = False
        if pygame.sprite.spritecollide(self.player, self.items, dokill=False):
            self.cigs_level += CIGS_RECHARGE_RATE * self.dt
            self.is_smoking = True

        self.is_doing_pullups = False
        if pygame.sprite.spritecollide(self.player, self.bars, dokill=False):
            self.bars_level += BARS_RECHARGE_RATE * self.dt
            self.is_doing_pullups = True

        # --- LÓGICA DE CONTROLE DOS EFEITOS SONOROS ---
        # Fumar
        if self.is_smoking and not was_smoking and self.smoking_sound:
            self.smoking_sound.play(loops=-1) # Começa a tocar em loop
        elif not self.is_smoking and was_smoking and self.smoking_sound:
            self.smoking_sound.stop() # Para imediatamente

        # Barra Fixa
        if self.is_doing_pullups and not was_doing_pullups and self.pullup_sound:
            self.pullup_sound.play(loops=-1) # Começa a tocar em loop
        elif not self.is_doing_pullups and was_doing_pullups and self.pullup_sound:
            self.pullup_sound.stop() # Para imediatamente
        # -----------------------------------------------

        # Lógica do Herb (só executa se HERB_ENABLED for True)
        if HERB_ENABLED:
            # Colisão com o Herb
            herb_collisions = pygame.sprite.spritecollide(self.player, self.herbs, dokill=True)
            if herb_collisions:
                self.chapado_effect_active = True
                self.chapado_timer = self.chapado_duration

            # Spawn aleatório do Herb com verificação de colisão
            if random.random() < HERB_SPAWN_CHANCE:
                if len(self.herbs) == 0:
                    
                    # Loop para encontrar uma posição válida
                    while True:
                        x = random.randint(50, SCREEN_WIDTH - 50)
                        y = random.randint(50, SCREEN_HEIGHT - 50)
                        
                        # Cria um retângulo de teste na posição aleatória
                        temp_rect = pygame.Rect(0, 0, TILE, TILE)
                        temp_rect.center = (x, y)
                        
                        # Verifica se há colisão com algum sólido
                        collides = False
                        for solid in self.solids:
                            if temp_rect.colliderect(solid.rect):
                                collides = True
                                break
                        
                        # Se não houver colisão, a posição é válida e o loop termina
                        if not collides:
                            break
                            
                    # Cria o item na posição válida encontrada
                    h = Herb(x, y)
                    self.all_sprites.add(h)
                    self.herbs.add(h)

        just_started_smoking = self.is_smoking and not was_smoking
        just_started_pullups = self.is_doing_pullups and not was_doing_pullups

        if just_started_smoking or just_started_pullups:
            if not self.aura_active and random.randint(1, 14) == 1:
                self.aura_active = True
                self.aura_timer = self.aura_duration
                # --- TOQUE O SOM DE SUSTO AQUI ---
                if self.jumpscare_sound:
                    self.jumpscare_sound.play()
                # ---------------------------------

        if self.aura_active:
            self.aura_timer -= self.dt
            if self.aura_timer <= 0:
                self.aura_active = False

        self.cigs_level = clamp(self.cigs_level, 0, MAX_STAT_LEVEL)
        self.bars_level = clamp(self.bars_level, 0, MAX_STAT_LEVEL)

        # Se o inimigo vê o jogador, a sequência começa
        if self.enemy.sees(self.player, self.solids) and not self.result:
            if not self.game_over_sequence_active:
                self.game_over_sequence_active = True
                self.game_over_timer = 1.0 # Duração de 1 segundo
                
                # Para todos os sons
                pygame.mixer.music.fadeout(1000)
                if self.smoking_sound: self.smoking_sound.stop()
                if self.pullup_sound: self.pullup_sound.stop()
                # if self.jumpscare_sound: self.jumpscare_sound.play() # Um bom lugar para o susto!

                # --- ALTERAÇÃO FEITA AQUI ---
                # Trocamos o som de susto pelo novo som de captura
                if self.caught_sound:
                    self.caught_sound.play()
                # ----------------------------
        # ----------------------------------------
        
        # Atualiza a pontuação baseada no tempo
        if self.playing:
            self.score = int(time.time() - self.start_time)


    def draw_hud(self):
        # A definição de BAR_LENGTH foi movida para settings.py
        
        folego_bar_x = 15; folego_bar_y = 15
        fill_width_folego = (self.cigs_level / MAX_STAT_LEVEL) * BAR_LENGTH
        pygame.draw.rect(self.screen, GRAY, pygame.Rect(folego_bar_x, folego_bar_y, BAR_LENGTH, BAR_HEIGHT))
        pygame.draw.rect(self.screen, RED, pygame.Rect(folego_bar_x, folego_bar_y, fill_width_folego, BAR_HEIGHT))
        folego_text = self.hud_font.render("Fume bastante!", True, WHITE); self.screen.blit(folego_text, (folego_bar_x + 5, folego_bar_y + 4))

        gap_entre_barras = 10
        forca_bar_x = folego_bar_x + BAR_LENGTH + gap_entre_barras
        forca_bar_y = folego_bar_y

        fill_width_forca = (self.bars_level / MAX_STAT_LEVEL) * BAR_LENGTH
        pygame.draw.rect(self.screen, GRAY, pygame.Rect(forca_bar_x, forca_bar_y, BAR_LENGTH, BAR_HEIGHT))
        pygame.draw.rect(self.screen, CYAN, pygame.Rect(forca_bar_x, forca_bar_y, fill_width_forca, BAR_HEIGHT))
        forca_text = self.hud_font.render("Faça mais barras!", True, WHITE); self.screen.blit(forca_text, (forca_bar_x + 5, forca_bar_y + 4))

        # HUD do efeito "CHAPADO" (só desenha se HERB_ENABLED for True)
        if HERB_ENABLED and self.chapado_effect_active:
            chapado_text = self.hud_font.render("CHAPADO", True, GREEN)
            self.screen.blit(chapado_text, (folego_bar_x, folego_bar_y + BAR_HEIGHT + 5))
            
            timer_chapado_text = self.hud_font.render(f"{self.chapado_timer:.1f}s", True, WHITE)
            self.screen.blit(timer_chapado_text, (forca_bar_x, forca_bar_y + BAR_HEIGHT + 5))

        timer_text = self.timer_font.render(f"Tempo: {self.score}", True, WHITE)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH / 2, 30))
        self.screen.blit(timer_text, timer_rect)


    def draw(self):
        self.game_map.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.enemy.draw_fov(self.screen, self.solids)
        self.draw_hud()

        # --- Legenda do Inspetor ---
        texto_legenda_inimigo = self.enemy.name
        legenda_surface_inimigo = self.hud_font.render(texto_legenda_inimigo, True, WHITE)
        legenda_rect_inimigo = legenda_surface_inimigo.get_rect()
        legenda_rect_inimigo.midbottom = self.enemy.rect.midtop - pygame.math.Vector2(0, 5)
        self.screen.blit(legenda_surface_inimigo, legenda_rect_inimigo)

        # --- Legenda e Animação de Ação do Jogador ---
        texto_legenda_jogador = None
        animation_frame = None

        if self.is_smoking:
            texto_legenda_jogador = "Fumando..."
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
            self.bar_anim_timer += self.dt
            if self.bar_anim_timer > self.anim_speed:
                self.bar_anim_timer = 0
                total_bar_frames = len(self.bar_frames) * len(self.bar_frames[0])
                self.bar_anim_index = (self.bar_anim_index + 1) % total_bar_frames
            row = self.bar_anim_index // len(self.bar_frames[0])
            col = self.bar_anim_index % len(self.bar_frames[0])
            animation_frame = self.bar_frames[row][col]

        if texto_legenda_jogador:
            legenda_surface_jogador = self.hud_font.render(texto_legenda_jogador, True, WHITE)
            legenda_rect_jogador = legenda_surface_jogador.get_rect()
            legenda_rect_jogador.midbottom = self.player.rect.midtop - pygame.math.Vector2(0, 5)
            self.screen.blit(legenda_surface_jogador, legenda_rect_jogador)
            
            # Se houver uma animação, desenha ela ACIMA da legenda de texto
            if animation_frame:
                # Define um tamanho menor para a animação sobre o jogador
                anim_size = (108, 84)
                scaled_frame = pygame.transform.smoothscale(animation_frame, anim_size)
                anim_rect = scaled_frame.get_rect()
                anim_rect.midbottom = legenda_rect_jogador.midtop - pygame.math.Vector2(0, 3)
                self.screen.blit(scaled_frame, anim_rect)

        if self.aura_active:
            # Posição da imagem da aura: abaixo do jogador
            aura_offset_y = 10
            aura_rect = self.aura_image.get_rect(midtop=(self.player.rect.centerx, self.player.rect.bottom + aura_offset_y))
            self.screen.blit(self.aura_image, aura_rect)

            # Posição do texto da aura: abaixo da imagem da aura
            text_offset_y = 5
            aura_text_surf = self.hud_font.render("+AURA +EGO", True, WHITE)
            aura_text_rect = aura_text_surf.get_rect(midtop=(aura_rect.centerx, aura_rect.bottom + text_offset_y))
            self.screen.blit(aura_text_surf, aura_text_rect)

        # Efeito "wiggly" da tontura (só aplica se HERB_ENABLED for True)
        if HERB_ENABLED and self.chapado_effect_active:
            temp_surface = self.screen.copy()
            offset_x = int(math.sin(time.time() * 15) * 5) # Ondulação horizontal
            offset_y = int(math.cos(time.time() * 13) * 5) # Ondulação vertical
            # Limpa a tela antes de desenhar a cópia deslocada para evitar rastros
            self.screen.fill(BLACK)
            self.screen.blit(temp_surface, (offset_x, offset_y))

        # --- EFEITO VERMELHO NO JOGADOR DURANTE O GAME OVER ---
        if self.game_over_sequence_active:
            # Cria uma cópia da imagem atual do jogador
            player_image_copy = self.player.image.copy()
            # Pinta a cópia de vermelho, mantendo a transparência
            player_image_copy.fill(RED, special_flags=pygame.BLEND_RGB_MULT)
            # Desenha a versão vermelha por cima da original
            self.screen.blit(player_image_copy, self.player.rect)
        # ----------------------------------------------------

        pygame.display.flip()


    def death_screen(self):
        # --- PREPARAÇÃO DOS ELEMENTOS ---

        # Imagem "itsover" ou texto "VOCÊ FOI PEGO!"
        try:
            death_img = pygame.image.load("assets/itsover.png").convert_alpha()
        except pygame.error:
            death_img = self.title_font.render("VOCÊ FOI PEGO!", True, RED)
        death_rect = death_img.get_rect() # Posição será definida abaixo

        # Texto "Você foi banido..."
        font_banido = self.menu_font_normal
        parte1_surf = font_banido.render("Você foi ", True, WHITE)
        parte2_surf = font_banido.render("banido", True, RED)
        parte3_surf = font_banido.render(" do Geralzão.", True, WHITE)
        total_width_banido = parte1_surf.get_width() + parte2_surf.get_width() + parte3_surf.get_width()
        start_x_banido = (SCREEN_WIDTH - total_width_banido) / 2

        # Texto "Pontuação Final"
        score_surf = self.menu_font_normal.render(f"Pontuação Final: {self.score}", True, WHITE)
        score_rect = score_surf.get_rect() # Posição será definida abaixo

        # --- LÓGICA DE LAYOUT VERTICAL ---
        # Define a ordem e o espaçamento dos elementos de cima para baixo
        
        # 1. Posiciona o texto "Você foi banido..." no topo
        pos_y_banido = SCREEN_HEIGHT * 0.15
        
        # 2. Posiciona a imagem "itsover" abaixo do texto, com um espaçamento
        death_rect.center = (SCREEN_WIDTH / 2, pos_y_banido + font_banido.get_height() + 100)
        
        # 3. Posiciona a pontuação final abaixo da imagem, com um espaçamento
        score_rect.center = (SCREEN_WIDTH / 2, death_rect.bottom + 60)
        
        # 4. Define a posição inicial das opções interativas ("Recomeçar", etc.)
        opcoes_start_y = score_rect.bottom + 80

        # --- LOOP DA TELA DE MORTE ---
        options = ["Recomeçar", "Voltar ao Menu"]
        selected_option = 0
        waiting_for_input = True
        
        while waiting_for_input:
            self.clock.tick(FPS)
            self.screen.fill(BLACK)
            
            # Desenha os elementos na ordem e posições calculadas
            self.screen.blit(parte1_surf, (start_x_banido, pos_y_banido))
            self.screen.blit(parte2_surf, (start_x_banido + parte1_surf.get_width(), pos_y_banido))
            self.screen.blit(parte3_surf, (start_x_banido + parte1_surf.get_width() + parte2_surf.get_width(), pos_y_banido))
            
            self.screen.blit(death_img, death_rect)
            self.screen.blit(score_surf, score_rect)
            
            self._draw_menu_options(options, selected_option, start_y=opcoes_start_y)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting_for_input = False; self.running = False; return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN: selected_option = (selected_option + 1) % 2
                    elif event.key == pygame.K_UP: selected_option = (selected_option - 1) % 2
                    if event.key == pygame.K_RETURN:
                        return "restart" if selected_option == 0 else "menu"

            pygame.display.flip()
        
        return "quit"

    def quit(self):
        pygame.quit(); sys.exit()
