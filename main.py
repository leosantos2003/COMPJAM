# main.py
import pygame
import sys
from settings import *
from sprites import Player # Importa a nossa nova classe Player

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0 # Delta time: tempo entre um frame e outro

    def new(self):
        """
        Inicia um novo jogo, preparando todos os objetos.
        """
        # Cria um grupo para todos os sprites
        self.all_sprites = pygame.sprite.Group()
        # Instancia o jogador e o adiciona ao grupo de sprites
        self.player = Player(self, 10, 10) # Posição inicial (10, 10) no grid
        self.all_sprites.add(self.player)

    def run(self):
        """
        O Loop Principal do Jogo (Game Loop).
        """
        self.playing = True
        while self.playing:
            # dt é o tempo em segundos que o último frame levou para ser processado
            # Isso garante que o jogo rode na mesma velocidade em qualquer computador
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.playing:
                        self.playing = False
                    self.running = False

    def update(self):
        """
        Atualiza todos os objetos do jogo.
        """
        # O grupo de sprites atualiza todos os sprites que ele contém
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BLACK)
        # O grupo de sprites desenha todos os sprites que ele contém na tela
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
        
    def quit(self):
        """
        Encerra o Pygame e o programa.
        """
        pygame.quit()
        sys.exit()

# --- Ponto de Entrada do Programa ---
if __name__ == '__main__':
    g = Game()
    while g.running:
        g.new() # Inicia um novo jogo
        g.run() # Roda o loop principal
    g.quit()