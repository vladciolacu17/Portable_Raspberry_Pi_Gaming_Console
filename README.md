# Portable Raspberry Pi Gaming Console

A handheld gaming console project built with **Raspberry Pi**, **Python**, **Pygame**, GPIO buttons, and an analog joystick.  
The console includes a custom fullscreen game menu and multiple playable games, including **Snake**, **Tetris**, **a Platformer**, and a **Slither-style multiplayer prototype**.

## Overview

This project was created as a portable embedded gaming system that combines:

- Raspberry Pi hardware
- GPIO-based physical controls
- analog joystick input through an ADC
- Python game development with Pygame
- a custom graphical launcher for multiple games

The application starts in a fullscreen game menu and allows the user to launch different games directly from the console interface.

## Current Features

- Fullscreen graphical menu
- GPIO button input
- Analog joystick input using ADC
- Snake
- Tetris
- Platformer
- Slither-style game integration
- Exit to desktop and shutdown options from the menu
- Hard reset button support for returning to the main menu

## Repository Structure

```text
Portable_Raspberry_Pi_Gaming_Console/
├── assets/                  # images / sprites / terrain / player assets
├── static/                  # static files for the Slither web component
├── game.py
├── goal.py
├── main.py                  # main launcher and game menu
├── main_platformer.py       # platformer entry point
├── player.py                # platformer player logic and animation
├── settings.py              # world map, tile size, screen constants, joystick tuning
├── slither.py               # Slither-style game logic
├── support.py               # sprite import helpers
├── tile.py
├── trap.py
├── utils.py                 # GPIO + ADC input handling
└── world.py                 # platformer world generation and collisions
