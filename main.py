# main.py

import pygame
from game import Game

if __name__ == "__main__":
    g = Game()
    
    current_map = None
    current_difficulty = "Normal"

    while g.running:
        # Se não houver um mapa definido, mostra o menu para escolher um
        if current_map is None:
            current_map, current_difficulty = g.show_menu_screen()
            
            # --- ADIÇÃO IMPORTANTE AQUI ---
            # Se um mapa foi escolhido (ou seja, o jogador não fechou o jogo),
            # mostra a tela de briefing antes de continuar.
            if current_map:
                g.show_briefing_screen()
            # -------------------------------

        # Se o menu foi fechado ou a opção "Sair" foi escolhida, encerra o loop
        if not g.running or not current_map:
            break

        # Inicia uma nova partida com o mapa e dificuldade atuais
        g.new(current_map, current_difficulty)
        # Executa a partida e recebe a ação do jogador ao final (restart, menu, quit)
        action = g.run()

        if action == "restart":
            # Mantém 'current_map' e 'current_difficulty' para reiniciar
            continue
        elif action == "menu":
            # Define 'current_map' como None para voltar ao menu
            current_map = None
        elif action == "quit":
            # Interrompe o loop principal
            break
            
    # Sai do jogo
    g.quit()