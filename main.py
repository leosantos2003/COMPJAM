# main.py

import pygame
from game import Game

if __name__ == "__main__":
    g = Game()
    
    while g.running:
        g.show_menu_screen() # 1. Mostra o menu e espera
        
        # Se o jogador não fechou o jogo no menu, inicia uma nova partida
        if g.running:
            g.new()          # 2. Prepara uma nova partida
            g.run()          # 3. Executa a partida até o fim
    
    # 4. Sai do jogo
    g.quit()
