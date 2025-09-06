import pygame

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _rect_of(spr):
    # usa hitbox se existir (árvore tem hitbox menor), senão rect
    return getattr(spr, "hitbox", spr.rect)

def load_spritesheet_grid(path, fw, fh):
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