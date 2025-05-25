import pygame
import sys

from main import get_ADC
from settings import *
from world import World

pygame.init()
WIDTH, HEIGHT = pygame.display.get_desktop_sizes()[0]
print(str(HEIGHT) + " " + str(WIDTH))
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption("Raspberry Pi Console")
JOYSTICK_CENTER = 114
JOYSTICK_THRESHOLD = 20
class Platformer:
    def __init__(self, screen, width, height, button_pressed):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.button_pressed = button_pressed
        self.get_ADC = get_ADC

        self.bg_img = pygame.image.load('assets/terrain/bg.jpg')
        self.bg_img = pygame.transform.scale(self.bg_img, (width, height))

    def _read_joystick(self):
        # Read analog joystick values
        x_value = self.get_ADC(0)  # Assuming channel 0 is for X-axis
        y_value = self.get_ADC(1)  # Assuming channel 1 is for Y-axis

        # Map joystick values to directional inputs
        joystick_event = {
            "left": x_value < JOYSTICK_CENTER - JOYSTICK_THRESHOLD,
            "right": x_value > JOYSTICK_CENTER + JOYSTICK_THRESHOLD,
            "jump": y_value < JOYSTICK_CENTER - JOYSTICK_THRESHOLD,
        }
        return joystick_event

    def main(self):
        world = World(world_map, self.screen)
        while True:
            self.screen.blit(self.bg_img, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            player_event = {
                "left": self.button_pressed("left"),
                "jump": self.button_pressed("up"),  # GPIO5 for jumping
				"right": self.button_pressed("right"),
            }

            world.update(player_event)
            if world.player.sprite and world.player.sprite.game_over:
                pygame.time.wait(2000)  # Wait for 2 seconds
                return
            pygame.display.update()
            self.clock.tick(60)

def start_platformer(screen, button_pressed, get_ADC):
    game = Platformer(screen, WIDTH, HEIGHT, button_pressed, get_ADC)
    game.main()
