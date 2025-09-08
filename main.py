# main.py
from game import Game

if __name__ == "__main__":
    g = Game()
    
    current_map = None
    current_difficulty = "Normal"

    while g.running:
        if current_map is None:
            from ui import show_menu_screen, show_briefing_screen
            current_map, current_difficulty = show_menu_screen(g)
            
            if current_map:
                show_briefing_screen(g)

        if not g.running or not current_map:
            break

        g.new(current_map, current_difficulty)
        action = g.run()

        if action == "restart":
            continue
        elif action == "menu":
            current_map = None
        elif action == "quit":
            break
            
    g.quit()