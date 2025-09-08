# hud.py
import pygame
from settings import *

def draw_hud(game):
    # Barra de Fôlego
    folego_bar_x = 15
    folego_bar_y = 15
    fill_width_folego = (game.cigs_level / MAX_STAT_LEVEL) * BAR_LENGTH
    pygame.draw.rect(game.screen, GRAY, pygame.Rect(folego_bar_x, folego_bar_y, BAR_LENGTH, BAR_HEIGHT))
    pygame.draw.rect(game.screen, RED, pygame.Rect(folego_bar_x, folego_bar_y, fill_width_folego, BAR_HEIGHT))
    folego_text = game.hud_font.render("Fume bastante!", True, WHITE)
    game.screen.blit(folego_text, (folego_bar_x + 5, folego_bar_y + 4))

    # Barra de Força
    gap_entre_barras = 10
    forca_bar_x = folego_bar_x + BAR_LENGTH + gap_entre_barras
    forca_bar_y = folego_bar_y
    fill_width_forca = (game.bars_level / MAX_STAT_LEVEL) * BAR_LENGTH
    pygame.draw.rect(game.screen, GRAY, pygame.Rect(forca_bar_x, forca_bar_y, BAR_LENGTH, BAR_HEIGHT))
    pygame.draw.rect(game.screen, CYAN, pygame.Rect(forca_bar_x, forca_bar_y, fill_width_forca, BAR_HEIGHT))
    forca_text = game.hud_font.render("Faça mais barras!", True, WHITE)
    game.screen.blit(forca_text, (forca_bar_x + 5, forca_bar_y + 4))

    # Efeito "Chapado"
    if HERB_ENABLED and game.chapado_effect_active:
        chapado_text = game.hud_font.render("CHAPADO", True, GREEN)
        game.screen.blit(chapado_text, (folego_bar_x, folego_bar_y + BAR_HEIGHT + 5))
        timer_chapado_text = game.hud_font.render(f"{game.chapado_timer:.1f}s", True, WHITE)
        game.screen.blit(timer_chapado_text, (forca_bar_x, forca_bar_y + BAR_HEIGHT + 5))

    # Timer
    timer_text = game.timer_font.render(f"Tempo: {game.score}", True, WHITE)
    timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH / 2, 30))
    game.screen.blit(timer_text, timer_rect)