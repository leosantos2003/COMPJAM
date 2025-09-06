# main.py

from game import Game

if __name__ == "__main__":
    g = Game()
    
    # Variável para controlar o estado do jogo
    action = "menu"

    while g.running:
        if action == "menu":
            action = g.show_menu_screen()
        
        elif action == "play":
            g.new()
            action = g.run() # O jogo roda e retorna "restart" ou "menu"

        elif action == "restart":
            # Se a ação for recomeçar, mudamos para "play"
            # para que na próxima iteração do loop o jogo comece de novo
            action = "play"
        
        elif action == "quit":
            g.running = False
    
    g.quit()
