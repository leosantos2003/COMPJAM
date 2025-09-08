# game_logic.py
import pygame
import random
import time
from settings import *
from items import Herb
from utils import clamp

def handle_player_interactions(game):
    """Gerencia as interações do jogador com itens e os efeitos sonoros."""
    was_smoking = game.is_smoking
    was_doing_pullups = game.is_doing_pullups

    # Interação com Cigarros
    game.is_smoking = bool(pygame.sprite.spritecollide(game.player, game.items, dokill=False))
    if game.is_smoking:
        game.cigs_level += CIGS_RECHARGE_RATE * game.dt
        if not was_smoking and game.assets.get('smoking_sound'):
            game.assets['smoking_sound'].play(loops=-1)
    elif was_smoking and game.assets.get('smoking_sound'):
        game.assets['smoking_sound'].stop()

    # Interação com Barras
    game.is_doing_pullups = bool(pygame.sprite.spritecollide(game.player, game.bars, dokill=False))
    if game.is_doing_pullups:
        game.bars_level += BARS_RECHARGE_RATE * game.dt
        if not was_doing_pullups and game.assets.get('pullup_sound'):
            game.assets['pullup_sound'].play(loops=-1)
    elif was_doing_pullups and game.assets.get('pullup_sound'):
        game.assets['pullup_sound'].stop()

    # Interação com Erva (Herb)
    if HERB_ENABLED and pygame.sprite.spritecollide(game.player, game.herbs, dokill=True):
        game.chapado_effect_active = True
        game.chapado_timer = game.chapado_duration

def handle_special_effects(game):
    """Gerencia a lógica da aura e do jumpscare."""
    just_started_action = (game.is_smoking and not game.was_smoking) or \
                          (game.is_doing_pullups and not game.was_doing_pullups)

    if just_started_action and not game.aura_active and random.randint(1, 14) == 1:
        game.aura_active = True
        game.aura_timer = game.aura_duration
        if game.assets.get('jumpscare_sound'):
            game.assets['jumpscare_sound'].play()

def handle_herb_spawning(game):
    """Gerencia o aparecimento aleatório do item Herb."""
    if HERB_ENABLED and random.random() < HERB_SPAWN_CHANCE and not game.herbs:
        while True:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            temp_rect = pygame.Rect(0, 0, TILE, TILE)
            temp_rect.center = (x, y)
            if not any(temp_rect.colliderect(s.rect) for s in game.solids):
                break
        h = Herb(x, y)
        game.all_sprites.add(h)
        game.herbs.add(h)

def update_timers_and_stats(game):
    """Atualiza todos os timers e as barras de status do jogador."""
    if game.chapado_effect_active:
        game.chapado_timer -= game.dt
        if game.chapado_timer <= 0:
            game.chapado_effect_active = False
    else:
        game.cigs_level -= CIGS_DECAY_RATE * game.dt
        game.bars_level -= BARS_DECAY_RATE * game.dt

    if game.aura_active:
        game.aura_timer -= game.dt
        if game.aura_timer <= 0:
            game.aura_active = False

    game.cigs_level = clamp(game.cigs_level, 0, MAX_STAT_LEVEL)
    game.bars_level = clamp(game.bars_level, 0, MAX_STAT_LEVEL)

def check_game_over_conditions(game):
    """Verifica as condições de fim de jogo (status zerado ou captura)."""
    status_zerado = game.cigs_level <= 0 or game.bars_level <= 0
    foi_capturado = game.enemy.sees(game.player, game.solids)

    if (status_zerado or foi_capturado) and not game.game_over_sequence_active:
        game.game_over_sequence_active = True
        game.game_over_timer = 1.0
        pygame.mixer.music.fadeout(1000)
        if game.assets.get('smoking_sound'): game.assets['smoking_sound'].stop()
        if game.assets.get('pullup_sound'): game.assets['pullup_sound'].stop()
        if foi_capturado and game.assets.get('caught_sound'):
            game.assets['caught_sound'].play()