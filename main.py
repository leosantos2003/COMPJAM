# main.py
from game import Game

if __name__ == "__main__":
    g = Game()
    
    # --- VARIÁVEIS ATUALIZADAS ---
    map_to_play = None
    # ---------------------------

    while g.running:
        if map_to_play is None:
            from ui import show_menu_screen, show_briefing_screen
            map_to_play, current_difficulty = show_menu_screen(g)
            
            if map_to_play:
                show_briefing_screen(g)

        if not g.running or not map_to_play:
            break

        g.new(map_to_play, current_difficulty)
        action = g.run()

        if action == "restart":
            # Mantém o mapa atual para reiniciar
            continue 
        elif action == "menu":
            map_to_play = None # Volta ao menu
        elif action == "quit":
            break
            
    g.quit()