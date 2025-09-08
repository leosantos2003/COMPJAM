# animations.py
import pygame

def update_smoke_animation(game):
    game.smoke_anim_timer += game.dt
    if game.smoke_anim_timer > game.anim_speed:
        game.smoke_anim_timer = 0
        total_frames = len(game.smoke_frames) * len(game.smoke_frames[0])
        game.smoke_anim_index = (game.smoke_anim_index + 1) % total_frames
    
    row = game.smoke_anim_index // len(game.smoke_frames[0])
    col = game.smoke_anim_index % len(game.smoke_frames[0])
    return game.smoke_frames[row][col]

def update_bar_animation(game):
    game.bar_anim_timer += game.dt
    if game.bar_anim_timer > game.anim_speed:
        game.bar_anim_timer = 0
        total_frames = len(game.bar_frames) * len(game.bar_frames[0])
        game.bar_anim_index = (game.bar_anim_index + 1) % total_frames
        
    row = game.bar_anim_index // len(game.bar_frames[0])
    col = game.bar_anim_index % len(game.bar_frames[0])
    return game.bar_frames[row][col]