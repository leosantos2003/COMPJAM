# ui.py
import pygame
from settings import *

# --- Funções Genéricas de Desenho ---
def draw_text(surface, text, font, color, center_pos):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    surface.blit(text_surf, text_rect)

def draw_bar(surface, x, y, width, height, color, current_value, max_value):
    fill_width = (current_value / max_value) * width
    background_rect = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill_width, height)
    pygame.draw.rect(surface, GRAY, background_rect)
    pygame.draw.rect(surface, color, fill_rect)

# --- Classes de UI ---
class HUD:
    def __init__(self, assets):
        self.assets = assets

    def draw(self, screen, cigs_level, bars_level):
        # Barra de Fôlego
        draw_bar(screen, 15, 15, 200, 25, YELLOW, cigs_level, MAX_STAT_LEVEL)
        draw_text(screen, "Fôlego", self.assets.font_small, WHITE, (15 + 100, 15 + 13))
        
        # Barra de Força
        draw_bar(screen, 15, 50, 200, 25, CYAN, bars_level, MAX_STAT_LEVEL)
        draw_text(screen, "Força", self.assets.font_small, WHITE, (15 + 100, 50 + 13))
        
        tip = "Fique nos itens para recuperar. Fuja do cone!"
        draw_text(screen, tip, self.assets.font_small, GRAY, (SCREEN_WIDTH / 2, 25))

class Menu:
    def __init__(self, assets):
        self.assets = assets

    def run(self, screen, clock, title, title_color, options, option_colors):
        selected_option = 0
        
        waiting = True
        while waiting:
            clock.tick(FPS)
            
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(options)
                    if event.key == pygame.K_RETURN:
                        return options[selected_option][1] # Retorna a ação da opção

            # Desenho
            screen.fill(BLACK)
            draw_text(screen, title, self.assets.font_title, title_color, (SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
            
            for i, option in enumerate(options):
                text, action = option
                y_pos = SCREEN_HEIGHT/2 + i * 70
                rect = pygame.Rect(SCREEN_WIDTH/2 - 100, y_pos, 200, 50)
                
                color = option_colors[i] if selected_option == i else GRAY
                pygame.draw.rect(screen, color, rect)
                draw_text(screen, text, self.assets.font_small, BLACK, rect.center)

            pygame.display.flip()
        return "quit"