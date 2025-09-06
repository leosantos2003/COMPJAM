# main.py

import pygame
from game import Game

if __name__ == "__main__":
    g = Game()
    
    current_map = None

    while g.running:
        # Se não houver um mapa definido, mostra o menu para escolher um
        if current_map is None:
            current_map = g.show_menu_screen()

        # Se o menu foi fechado ou a opção "Sair" foi escolhida, encerra o loop
        if not g.running or not current_map:
            break

        # Inicia uma nova partida com o mapa atual
        g.new(current_map)
        # Executa a partida e recebe a ação do jogador ao final (restart, menu, quit)
        action = g.run()

        if action == "restart":
            # Mantém o 'current_map' para reiniciar o mesmo mapa na próxima iteração
            continue
        elif action == "menu":
            # Define 'current_map' como None para voltar ao menu na próxima iteração
            current_map = None
        elif action == "quit":
            # Interrompe o loop principal para fechar o jogo
            break
            
    # Sai do jogo
    g.quit()