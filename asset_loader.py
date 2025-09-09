# asset_loader.py
import pygame
from utils import load_spritesheet_grid

def load_assets():
    """Carrega todas as fontes, imagens e sons do jogo."""
    assets = {}
    try:
        assets['title_font'] = pygame.font.Font("fonts/Pricedown_BL.otf", 60)
        assets['menu_font_normal'] = pygame.font.Font("fonts/Pricedown_BL.otf", 35)
        assets['menu_font_selected'] = pygame.font.Font("fonts/Pricedown_BL.otf", 40)
        assets['hud_font'] = pygame.font.Font("fonts/Pricedown_BL.otf", 20)
        assets['timer_font'] = pygame.font.Font("fonts/Pricedown_BL.otf", 28)
        assets['leaderboard_font'] = pygame.font.Font("fonts/Pricedown_BL.otf", 30)
    except FileNotFoundError:
        print("Aviso: Arquivo de fonte não encontrado. Usando fontes padrão.")
        assets['title_font'] = pygame.font.SysFont(None, 80)
        assets['menu_font_normal'] = pygame.font.SysFont(None, 45)
        assets['menu_font_selected'] = pygame.font.SysFont(None, 55)
        assets['hud_font'] = pygame.font.SysFont(None, 28)
        assets['timer_font'] = pygame.font.SysFont(None, 40)
        assets['leaderboard_font'] = pygame.font.SysFont(None, 45)

    try:
        assets['menu_nav_sound'] = pygame.mixer.Sound("assets/sound/menu_sound.wav")
    except pygame.error:
        assets['menu_nav_sound'] = None

    try:
        pygame.mixer.music.load('audio/background_music.mp3')
    except pygame.error as e:
        print(f"Aviso: Não foi possível carregar a música de fundo: {e}")

    try:
        assets['smoking_sound'] = pygame.mixer.Sound('audio/smoke_sound.mp3')
        assets['pullup_sound'] = pygame.mixer.Sound('audio/bar_sound.mp3')
        assets['jumpscare_sound'] = pygame.mixer.Sound('audio/jumpscare.mp3')
        assets['caught_sound'] = pygame.mixer.Sound('audio/death_scream.mp3')
    except pygame.error as e:
        print(f"Aviso: Não foi possível carregar um ou mais efeitos sonoros: {e}")

    assets['smoke_frames'] = load_spritesheet_grid("assets/smoke.png", 427, 240)
    assets['bar_frames'] = load_spritesheet_grid("assets/bar.png", 461, 240)
    assets['aura_image'] = pygame.image.load("assets/auratrollface.png").convert_alpha()
    
    return assets