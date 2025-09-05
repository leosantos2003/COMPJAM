# sprites.py
# Este arquivo vai conter as classes para todos os objetos do nosso jogo.

import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        """
        Inicializa o jogador.
        - game: uma referência ao objeto principal do jogo
        - x, y: posição inicial do jogador (em formato de grid)
        """
        super().__init__()
        self.game = game
        self.image = pygame.Surface((32, 32)) # Cria uma superfície quadrada de 32x32 pixels
        self.image.fill(GREEN) # Pinta o quadrado de verde
        self.rect = self.image.get_rect() # Pega o retângulo (hitbox) da imagem
        self.rect.x = x * 32 # Define a posição x
        self.rect.y = y * 32 # Define a posição y

    def get_keys(self):
        """
        Verifica quais teclas estão pressionadas e move o jogador.
        """
        # Zera a velocidade a cada frame
        self.vx, self.vy = 0, 0
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy = -PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = PLAYER_SPEED
            
        # Corrigir movimento na diagonal para não ser mais rápido
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    def update(self):
        """
        Atualiza a posição do jogador a cada frame.
        """
        self.get_keys()
        self.rect.x += self.vx * self.game.dt
        self.rect.y += self.vy * self.game.dt