# leaderboard.py
import json

def load_leaderboard():
    """Carrega o placar de recordes de um arquivo JSON."""
    try:
        with open('leaderboard.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"Pesadelo": []}

def save_leaderboard(leaderboard_data):
    """Salva o placar de recordes em um arquivo JSON."""
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard_data, f, indent=4)

def is_high_score(leaderboard_data, score, difficulty):
    """Verifica se uma pontuação é um novo recorde para a dificuldade Pesadelo."""
    if difficulty != "Pesadelo":
        return False
    leaderboard_list = leaderboard_data.get("Pesadelo", [])
    if len(leaderboard_list) < 5 or score > leaderboard_list[-1]['score']:
        return True
    return False

def add_high_score(leaderboard_data, name, score):
    """Adiciona um novo recorde ao placar."""
    leaderboard_list = leaderboard_data.get("Pesadelo", [])
    leaderboard_list.append({'name': name, 'score': score})
    leaderboard_list = sorted(leaderboard_list, key=lambda x: x['score'], reverse=True)[:5]
    leaderboard_data["Pesadelo"] = leaderboard_list
    save_leaderboard(leaderboard_data)