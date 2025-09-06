# Configurações da tela
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FULLSCREEN = True  # Mude para False para jogar em modo janela
FPS = 60
TITLE = "A Ronda do Inspetor"

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY  = (120, 120, 120)
CYAN  = (0, 200, 200)

# Grid / sprites
TILE = 32

# Jogador
PLAYER_SPEED = 300  # px/s

# Inimigo (inspetor)
ENEMY_SPEED = 170     # px/s
FOV_DEGREES = 70       # ângulo do cone de visão
FOV_RANGE   = 220      # alcance do cone de visão em pixels

# IA do Inimigo
ENEMY_RETARGET_SECONDS = 2  # Tempo em segundos para o inimigo recalcular a rota até o jogador

ENEMY_TURN_SPEED = 2.5  # Velocidade de giro do inimigo (radianos/s). Valores maiores = giro mais rápido

# Objetivos e Mecânicas de Sobrevivência (NOVAS REGRAS)
MAX_STAT_LEVEL = 100.0          # O valor máximo das barras de Fôlego e Força

CIGS_DECAY_RATE = 6.5           # Pontos de "Fôlego" perdidos por segundo
BARS_DECAY_RATE = 6.0           # Pontos de "Força" perdidos por segundo

CIGS_RECHARGE_RATE = 20.0       # Pontos de "Fôlego" ganhos por segundo ao estar no cigarro
BARS_RECHARGE_RATE = 25.0       # Pontos de "Força" ganhos por segundo ao estar na barra

# --- IA do Inimigo (opcionais; já têm defaults no enemy.py) ---
ENEMY_HEARING_BASE = 220           # raio de audição parado/andando
ENEMY_HEARING_RUN  = 340           # raio de audição correndo (player rápido)
ENEMY_LEAD_TIME    = 0.35          # segundos à frente para predição do alvo
ENEMY_SEARCH_TIME  = 6.0           # quanto tempo vasculha após perder o player
ENEMY_SEARCH_RADIUS_TILES = 6      # raio (em tiles) do “círculo” de busca
ENEMY_PATROL_PAUSE_MINMAX = (0.5, 1.2)
ENEMY_PATH_RECALC  = 0.35          # recálculo de A* (s)
ENEMY_FEELER_LEN   = 18            # comprimento dos “bigodes” anti-raspagem
