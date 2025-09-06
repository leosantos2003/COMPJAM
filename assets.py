# assets.py
import pygame

# Função para carregar spritesheets que já estava em player.py
def load_spritesheet_grid(path, fw, fh):
    """Corta um spritesheet em grade fwxfh e retorna frames em [linhas][colunas]."""
    sheet = pygame.image.load(path).convert_alpha()
    sw, sh = sheet.get_size()
    cols, rows = sw // fw, sh // fh
    frames = []
    for r in range(rows):
        row = []
        for c in range(cols):
            rect = pygame.Rect(c*fw, r*fh, fw, fh)
            row.append(sheet.subsurface(rect).copy())
        frames.append(row)
    return frames

# Classe para gerenciar todos os assets
class Assets:
    def __init__(self):
        # Fontes
        self.font_small = pygame.font.SysFont(None, 28)
        self.font_title = pygame.font.SysFont(None, 80)
        
        # Imagens e Animações do Jogador
        player_spritesheet = load_spritesheet_grid("assets/maleBase/full/advnt_full.png", 32, 64)
        self.player_animations = {
            "idle": [player_spritesheet[0][0]],
            "walk": player_spritesheet[0][1:7]
        }
        
        print("Assets carregados com sucesso.")