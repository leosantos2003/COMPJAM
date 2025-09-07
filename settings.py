# settings.py RESOLVIDO

# Configurações da tela
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FULLSCREEN = True  # Mude para False para jogar em modo janela
FPS = 60
TITLE = "Grand Theft Auto V: INF Version"

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY  = (120, 120, 120)
CYAN  = (0, 200, 200)
DARKBLUE = (0, 0, 139)
OXFORDBLUE = (0, 21, 64)

# Grid / sprites
TILE = 32

# HUD
BAR_LENGTH = 200
BAR_HEIGHT = 25

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

CIGS_DECAY_RATE = 8.0           # Pontos de "Fôlego" perdidos por segundo
BARS_DECAY_RATE = 8.0           # Pontos de "Força" perdidos por segundo

CIGS_RECHARGE_RATE = 25.0       # Pontos de "Fôlego" ganhos por segundo ao estar no cigarro
BARS_RECHARGE_RATE = 25.0       # Pontos de "Força" ganhos por segundo ao estar na barra

# --- Adicionado para o item "Herb" ---
HERB_ENABLED = True # Defina como False para desativar completamente o item "herb" e seus efeitos
HERB_SPAWN_CHANCE = 0.001 # Chance de um "Herb" aparecer por frame

# --- IA do Inimigo (MODO PESADELO) ---
ENEMY_HEARING_BASE = 320           # Ouve o jogador a uma distância muito maior
ENEMY_HEARING_RUN  = 450           # Correr agora é quase um convite para ser pego
ENEMY_LEAD_TIME    = 0.60          # Predição de movimento quase perfeita, antecipa muito bem as fugas
ENEMY_SEARCH_TIME  = 12.0          # Dobro do tempo de busca; ele não desiste fácil
ENEMY_SEARCH_RADIUS_TILES = 10     # Vasculha uma área enorme depois de perder o jogador
ENEMY_PATROL_PAUSE_MINMAX = (0.1, 0.2) # Praticamente não para de se mover durante a patrulha
ENEMY_PATH_RECALC  = 0.15          # Reage a mudanças de direção quase que instantaneamente
ENEMY_FEELER_LEN   = 22            # Mais eficiente em contornar obstáculos sem se prender

# --- Níveis de Dificuldade ---
DIFFICULTY_LEVELS = {
    "Fácil": {
        "ENEMY_SPEED": 150,                # mais lento
        "ENEMY_TURN_SPEED": 2.0,           # gira mais devagar
        "FOV_DEGREES": 65,                 # campo de visão menor
        "FOV_RANGE": 200,                  # enxerga menos longe
        "ENEMY_HEARING_BASE": 280,         # ouve menos
        "ENEMY_HEARING_RUN": 400,
        "ENEMY_LEAD_TIME": 0.30,           # antecipa menos
        "ENEMY_SEARCH_TIME": 8.0,          # procura por menos tempo
        "ENEMY_SEARCH_RADIUS_TILES": 8,    # área de busca menor
        "ENEMY_PATH_RECALC": 0.28,         # recalcula mais devagar
        "ENEMY_FEELER_LEN": 26,
    },
    "Normal": {
        "ENEMY_SPEED": 175,                # levemente mais rápido que o fácil
        "ENEMY_TURN_SPEED": 2.4,
        "FOV_DEGREES": 72,
        "FOV_RANGE": 225,
        "ENEMY_HEARING_BASE": 320,
        "ENEMY_HEARING_RUN": 450,
        "ENEMY_LEAD_TIME": 0.45,
        "ENEMY_SEARCH_TIME": 12.0,
        "ENEMY_SEARCH_RADIUS_TILES": 10,
        "ENEMY_PATH_RECALC": 0.20,
        "ENEMY_FEELER_LEN": 28,
    },
    "Pesadelo": {
        "ENEMY_SPEED": 220,
        "ENEMY_TURN_SPEED": 3.5,
        "FOV_DEGREES": 90,
        "FOV_RANGE": 280,
        "ENEMY_HEARING_BASE": 420,
        "ENEMY_HEARING_RUN": 550,
        "ENEMY_LEAD_TIME": 0.90,
        "ENEMY_SEARCH_TIME": 20.0,
        "ENEMY_SEARCH_RADIUS_TILES": 15,
        "ENEMY_PATH_RECALC": 0.05,
        "ENEMY_FEELER_LEN": 20,
    }
}
