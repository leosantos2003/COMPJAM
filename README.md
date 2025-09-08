# CS Student Simulator

Welcome to the repository for "The Inspector's Round," a 2D survival and stealth game with a unique theme, developed in Python with the Pygame library.

## About

In "The Inspector's Round," you control a character who must survive in a hostile environment, not by fighting monsters, but by fighting their own "vices." The goal is to keep their status bars—Stamina and Strength—full while avoiding capture by the relentless Inspector General.

To recharge their status bars, the player must take risks by visiting cigarette and fixed bar locations scattered throughout the map. Each visit is a gamble, as it can put them directly in the inspector's crosshairs.

## Features

Unique Survival Mechanics: Manage two status bars that decay over time. If either reaches zero, it's game over.

Advanced Enemy AI: The Inspector General is no simple bot. He operates with a Finite State Machine (FSM) that allows him to:

Patrol predefined routes.

Investigate sounds made by the player.

Search the last area where the player was seen.

Actively pursue when there is visual contact.

Pathfinding with A*: The inspector intelligently navigates maps, avoiding obstacles to find the shortest path to his targets.

Complex Perception: The enemy has a cone of vision that takes obstacles into account (he cannot see through walls) and also a hearing system that reacts to the player's rapid movements.

Difficulty Levels: Play on Easy, Normal, or Nightmare modes. Each difficulty level changes crucial AI parameters, such as speed, view range, and reaction time.

Multiple Maps: The game features three different maps, each with its own unique layout challenges.

"Herb" Power-Up: Find a rare item that activates the "HIGH" effect, pausing status decay for a short period and applying a distorted visual effect to the screen.

Sound Effects and Soundtrack: The game features background music during gameplay and sound effects for player actions and important events, such as capture.

Interactive Menus and Cutscenes: Polished navigation menus, a pre-level briefing screen, and a dramatic game over sequence enhance immersion.

## Arquitecture

main.py: Game entry point, manages the main loop between menu and game.

game.py: Contains the main Game class, which orchestrates all the elements, states, and game logic.

player.py: Defines the Player class, its movements, and animations.

enemy.py: The heart of the project, where all of Inspector Geralzão's AI is implemented.

items.py: Defines the items the player interacts with (Cigarette, Pull-Up Bar, Herb).

map.py: Responsible for loading the map .txt files and rendering the scene.

settings.py: Central configuration file with all game constants (speeds, colors, difficulties, etc.).

utils.py: Auxiliary functions used in multiple files.

Folders:

assets/: Contains all images and sounds.

fonts/: Contains font files (.otf, .ttf).

## How to play

Requirements
Python 3.x

Pygame Library

Installation
Clone this repository to your local machine.

Install Pygame (if you don't already have it):

Bash

pip install pygame
Run the game from the main file:

Bash

python main.py
Controls
Arrow keys or W, A, S, D: Move the character.

Enter: Select options in menus and skip the briefing screen.

ESC: Exit the game and return to the main menu.

## Screenshots

## Video Demo

## License

## Contact
