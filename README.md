<div align="center">
  <img width="641" height="552" alt="geralzao" src="https://github.com/user-attachments/assets/e730f2ae-c695-49c3-91df-c5af1fc4f813" />
  
  # CS Student Simulator
  
</div>

## About

In "Computer Science Student Simulator", you control a character who must survive in a hostile environment, not by fighting monsters, but by fighting their own "vices". The goal is to keep their status bars—Stamina and Strength—full while avoiding capture by the relentless Inspector General.

To recharge their status bars, the player must take risks by visiting cigarettes and pull-up bars scattered throughout the map. Each visit is a gamble, as it can put them directly in the inspector's crosshairs.

## Features

* **Unique Survival Mechanics**: Manage two status bars that decay over time. If either reaches zero, it's game over.

* **Advanced Enemy AI**: The Inspector General is no simple bot. He operates with a Finite State Machine (FSM) that allows him to:

  * Patrol predefined routes.

  * Investigate sounds made by the player.

  * Search the last area where the player was seen.

  * Actively pursue when there is visual contact.

* **Pathfinding with A**: The inspector intelligently navigates maps, avoiding obstacles to find the shortest path to his targets.

* **Complex Perception**: The enemy has a cone of vision that takes obstacles into account (he cannot see through walls) and also a hearing system that reacts to the player's rapid movements.

* **Difficulty Levels**: Play on Easy, Normal, or Nightmare modes. Each difficulty level changes crucial AI parameters, such as speed, view range, and reaction time.

* **Multiple Maps**: The game features three different maps, each with its own unique layout challenges.

* **"Herb" Power-Up**: Find a rare item that activates the "high" effect, pausing status decay for a short period and applying a distorted visual effect to the screen.

* **Sound Effects and Soundtrack**: The game features background music during gameplay and sound effects for player actions and important events, such as capture.

* **Interactive Menus and Cutscenes**: Polished navigation menus, a pre-level briefing screen, and a dramatic game over screen enhance immersion.

* **Interactive Leaderboard**: The player can get his name into the Leaderboard when achieving Top-5 scores.

## Arquitecture

* `main.py`: Game entry point, manages the main loop between menu and game.

* `game.py`: Contains the main Game class, which orchestrates all the elements, states, and game logic.

* `player.py`: Defines the Player class, its movements, and animations.
  
* `enemy.py`: The heart of the project, where all of Inspector Geralzão's AI is implemented.

* `items.py`: Defines the items the player interacts with (Cigarette, Pull-Up Bar, Herb).

* `map.py`: Responsible for loading the map .txt files and rendering the scene.

* `settings.py`: Central configuration file with all game constants (speeds, colors, difficulties, etc.).

* `utils.py`: Auxiliary functions used in multiple files.

* **Folders**:

  * `assets/`: Contains all images.

  * `audio/`: Contains all sounds.

  * `fonts/`: Contains font files (.otf, .ttf).

## How to play

* **Requirements**:

  * Python 3.x

  * Pygame Library

* Installation:
  
1. Clone this repository to your local machine.

```bash
git clone https://github.com/leosantos2003/CS-Student-Simulator
```

2. Install Pygame (if you don't already have it):

```bash
pip install pygame
```

3. Run the game from the main file:

```bash
python main.py
```

* **Controls**:

  * Arrow keys or W, A, S, D: Move the character.

  * Enter: Select options in menus and skip the briefing screen.

  * ESC: Exit the game and return to the main menu.

## Screenshots

<div style="display: flex; justify-content: center;">
  <img style="width: 48%;" width="1814" height="1016" alt="Captura de tela 2025-09-07 235027" src="https://github.com/user-attachments/assets/171f1c91-0ea6-4d50-b56e-8a003fa2316d" />
  <img style="width: 48%;" width="1792" height="1017" alt="Captura de tela 2025-09-07 235144" src="https://github.com/user-attachments/assets/456424fe-8f01-41fa-a467-3a1bd0833ffe" />
</div>

<div style="display: flex; justify-content: center;">
  <img style="width: 48%;" width="1808" height="1019" alt="Captura de tela 2025-09-07 234933" src="https://github.com/user-attachments/assets/6ea60776-8684-4d2b-9847-308051590000" />
  <img style="width: 48%;" width="1785" height="1015" alt="Captura de tela 2025-09-07 235254" src="https://github.com/user-attachments/assets/36b8fd8a-7651-4343-acc2-3803382f98e0" />
</div>

## Video Demo

https://github.com/user-attachments/assets/99acb532-b5d2-43cd-835f-dcf418309c4d

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

## Contact

Leonardo Santos - <leorsantos2003@gmail.com>
Erik Ratzlaff - <erikdr0404@gmail.com>
