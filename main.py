# main.py (Atualizado para Modo Infinito)
from game import Game
from procedural_map import ProceduralMapGenerator # <-- Importa o gerador
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE

if __name__ == "__main__":
    g = Game()
    
    map_to_play = None

    while g.running:
        if map_to_play is None:
            from ui import show_menu_screen, show_briefing_screen
            map_to_play, current_difficulty = show_menu_screen(g)
            
            if map_to_play:
                show_briefing_screen(g)

        if not g.running or not map_to_play:
            break

        # --- LÓGICA PARA CARREGAR O MAPA CORRETO ---
        if map_to_play == "procedural":
            # Define o tamanho do mapa procedural (pode ser ajustado)
            map_width = SCREEN_WIDTH // TILE + 20
            map_height = SCREEN_HEIGHT // TILE + 20
            
            print("Gerando mapa procedural...")
            generator = ProceduralMapGenerator(width=map_width, height=map_height)
            grid_data = generator.generate_map()
            g.new(grid_data=grid_data, difficulty=current_difficulty)
        else:
            # Carrega mapa estático
            g.new(map_file=map_to_play, difficulty=current_difficulty)
        # ---------------------------------------------

        action = g.run()

        if action == "restart":
            # Para o modo infinito, ele irá gerar um novo mapa a cada reinício
            if map_to_play == "procedural":
                map_to_play = "procedural" # Garante que o modo infinito continue
            continue 
        elif action == "menu":
            map_to_play = None
        elif action == "quit":
            break
            
    g.quit()