# ui.py
import pygame
from settings import *

def get_player_name_input(game):
    player_name = ""
    input_active = True
    while input_active:
        game.screen.fill(BLACK)
        title_surf = game.title_font.render("Novo Recorde!", True, GREEN)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        game.screen.blit(title_surf, title_rect)

        prompt_surf = game.menu_font_normal.render("Digite seu nome:", True, WHITE)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        game.screen.blit(prompt_surf, prompt_rect)

        name_surf = game.menu_font_selected.render(player_name, True, YELLOW)
        name_rect = name_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        game.screen.blit(name_surf, name_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode
    return player_name

def draw_menu_options(game, options, selected_option, start_y, line_spacing=60):
    for i, option_text in enumerate(options):
        is_selected = (i == selected_option)
        
        font = game.menu_font_selected if is_selected else game.menu_font_normal
        arrow = "> " if is_selected else "  "

        if is_selected and (option_text in ["Sair", "Voltar ao Menu"]):
            color = RED
        elif is_selected:
            color = GREEN
        else:
            color = GRAY

        text_str = f"{arrow}Dificuldade: {game.difficulty}" if option_text == "Dificuldade" else f"{arrow}{option_text}"

        text_surf = font.render(text_str, True, color)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, start_y + i * line_spacing))
        game.screen.blit(text_surf, text_rect)

def show_briefing_screen(game):
    phrases = [
        "Você fumará todos os cigarros...",
        "Você usará todas as barras fixas...",
        "Mas o Geralzão não irá deixar barato!"
    ]
    displayed_phrases = []
    current_phrase_index = 0
    
    last_update_time = pygame.time.get_ticks()
    delay_ms = 3 * 1000

    skip_surf = game.hud_font.render("Pressione Enter para pular", True, GRAY)
    skip_rect = skip_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50))

    briefing_active = True
    while briefing_active:
        game.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                game.quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                briefing_active = False

        now = pygame.time.get_ticks()
        if now - last_update_time > delay_ms:
            if current_phrase_index < len(phrases):
                displayed_phrases.append(phrases[current_phrase_index])
                current_phrase_index += 1
                last_update_time = now
            else:
                briefing_active = False

        game.screen.fill(BLACK)
        
        start_y = SCREEN_HEIGHT / 2 - 100
        for i, text in enumerate(displayed_phrases):
            color = YELLOW if i == 2 else WHITE
            text_surf = game.menu_font_normal.render(text, True, color)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, start_y + i * 60))
            game.screen.blit(text_surf, text_rect)

        game.screen.blit(skip_surf, skip_rect)
        pygame.display.flip()

def show_menu_screen(game):
    title1_surf = game.title_font.render("Grand Theft Auto V: ", True, WHITE)
    title2_surf = game.title_font.render("INF Version", True, YELLOW)
    total_width = title1_surf.get_width() + title2_surf.get_width()
    start_x = (SCREEN_WIDTH - total_width) / 2
    title1_rect = title1_surf.get_rect(x=start_x, centery=SCREEN_HEIGHT / 4)
    title2_rect = title2_surf.get_rect(x=title1_rect.right, centery=SCREEN_HEIGHT / 4)
    
    options = ["Jogar Mapa 1", "Jogar Mapa 2", "Jogar Mapa 3", "Dificuldade", "Leaderboard", "Sair"]
    selected_option = 0

    while True:
        game.clock.tick(FPS)
        game.screen.fill(OXFORDBLUE)
        
        game.screen.blit(title1_surf, title1_rect)
        game.screen.blit(title2_surf, title2_rect)

        draw_menu_options(game, options, selected_option, start_y=SCREEN_HEIGHT / 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                return None, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    if game.menu_nav_sound: game.menu_nav_sound.play()
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                    if game.menu_nav_sound: game.menu_nav_sound.play()
                if event.key == pygame.K_RETURN:
                    if selected_option < 3:
                        return game.maps[selected_option], game.difficulty
                    elif options[selected_option] == "Dificuldade":
                        levels = list(DIFFICULTY_LEVELS.keys())
                        current_idx = levels.index(game.difficulty)
                        game.difficulty = levels[(current_idx + 1) % len(levels)]
                    elif options[selected_option] == "Leaderboard":
                        show_leaderboard_screen(game)
                    elif options[selected_option] == "Sair":
                        game.running = False
                        return None, None
        
        pygame.display.flip()

def show_leaderboard_screen(game):
    leaderboard_active = True
    while leaderboard_active:
        game.screen.fill(BLACK)
        title_surf = game.title_font.render("Leaderboard - Pesadelo", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 100))
        game.screen.blit(title_surf, title_rect)

        # --- CORREÇÃO APLICADA AQUI ---
        leaderboard_list = game.leaderboard_data.get("Pesadelo", [])
        # -------------------------------

        if not leaderboard_list:
            no_scores_surf = game.menu_font_normal.render("Ainda não há pontuações.", True, GRAY)
            no_scores_rect = no_scores_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            game.screen.blit(no_scores_surf, no_scores_rect)
        else:
            for i, entry in enumerate(leaderboard_list):
                score_text = f"{i + 1}. {entry['name']}: {entry['score']}"
                score_surf = game.leaderboard_font.render(score_text, True, YELLOW)
                score_rect = score_surf.get_rect(center=(SCREEN_WIDTH / 2, 200 + i * 50))
                game.screen.blit(score_surf, score_rect)

        back_surf = game.menu_font_selected.render("Voltar", True, RED)
        back_rect = back_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100))
        game.screen.blit(back_surf, back_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.quit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE):
                leaderboard_active = False

def death_screen(game):
    try:
        death_img = pygame.image.load("assets/itsover.png").convert_alpha()
    except pygame.error:
        death_img = game.title_font.render("VOCÊ FOI PEGO!", True, RED)
    
    death_rect = death_img.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.4))
    
    score_surf = game.menu_font_normal.render(f"Pontuação Final: {game.score}", True, WHITE)
    score_rect = score_surf.get_rect(center=(SCREEN_WIDTH / 2, death_rect.bottom + 60))
    
    opcoes_start_y = score_rect.bottom + 80

    options = ["Recomeçar", "Voltar ao Menu"]
    selected_option = 0
    
    while True:
        game.clock.tick(FPS)
        game.screen.fill(BLACK)
        
        game.screen.blit(death_img, death_rect)
        game.screen.blit(score_surf, score_rect)
        
        draw_menu_options(game, options, selected_option, start_y=opcoes_start_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % 2
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % 2
                if event.key == pygame.K_RETURN:
                    return "restart" if selected_option == 0 else "menu"

        pygame.display.flip()