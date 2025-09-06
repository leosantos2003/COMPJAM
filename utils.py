def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _rect_of(spr):
    # usa hitbox se existir (árvore tem hitbox menor), senão rect
    return getattr(spr, "hitbox", spr.rect)