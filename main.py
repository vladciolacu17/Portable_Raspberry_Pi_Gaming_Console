import pygame
import sys
import random
import RPi.GPIO as GPIO
import time
import os
from main_platformer import start_platformer

# -------------------------
# GPIO Setup
# -------------------------
GPIO.setmode(GPIO.BCM)
PIN_CLK = 23
PIN_DO  = 16
PIN_DI  = 20
PIN_CS  = 24

# set up the SPI interface pins
GPIO.setup(PIN_DI,  GPIO.OUT)
GPIO.setup(PIN_DO,  GPIO.IN)
GPIO.setup(PIN_CLK, GPIO.OUT)
GPIO.setup(PIN_CS,  GPIO.OUT)

# read SPI data from ADC8032
def get_ADC(channel):
	# 1. CS LOW.
        GPIO.output(PIN_CS, True)      # clear last transmission
        GPIO.output(PIN_CS, False)     # bring CS low

	# 2. Start clock
        GPIO.output(PIN_CLK, False)  # start clock low

	# 3. Input MUX address
        for i in [1,1,channel]: # start bit + mux assignment
                 if (i == 1):
                         GPIO.output(PIN_DI, True)
                 else:
                         GPIO.output(PIN_DI, False)

                 GPIO.output(PIN_CLK, True)
                 GPIO.output(PIN_CLK, False)

        # 4. read 8 ADC bits
        ad = 0
        for i in range(8):
                GPIO.output(PIN_CLK, True)
                GPIO.output(PIN_CLK, False)
                ad <<= 1 # shift bit
                if (GPIO.input(PIN_DO)):
                        ad |= 0x1 # set first bit

        # 5. reset
        GPIO.output(PIN_CS, True)

        return ad

BUTTON_PINS = {
    "up": 26,
    "down": 19,
    "left": 13,
    "right": 6,
    "select": 5,
    "reset": 21
}

for pin in BUTTON_PINS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BUTTON_COOLDOWN = 200  # milliseconds
PLATFORMER_COOLDOWN = 20
last_pressed = {key: 0 for key in BUTTON_PINS}

def read_gpio_input():
    return {name: not GPIO.input(pin) for name, pin in BUTTON_PINS.items()}

def button_pressed(name):
    current_time = pygame.time.get_ticks()
    if read_gpio_input()[name] and current_time - last_pressed[name] > BUTTON_COOLDOWN:
        last_pressed[name] = current_time
        return True
    return False

def platformer_pressed(name):
    current_time = pygame.time.get_ticks()
    if read_gpio_input()[name] and current_time - last_pressed[name] > PLATFORMER_COOLDOWN:
        last_pressed[name] = current_time
        return True
    return False

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = pygame.display.get_desktop_sizes()[0]
print(str(HEIGHT) + " " + str(WIDTH))
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
pygame.display.set_caption("Raspberry Pi Console")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)

font = pygame.font.SysFont("Arial", 24)

def draw_text(surface, text, x, y, color=WHITE):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def game_menu():
    menu_running = True
    selected = 0
    options = ["Snake", "Tetris", "Platformer", "Exit"]

    while menu_running:
        screen.fill(BLACK)
        draw_text(screen, "Select a Game", WIDTH // 3, 30, GREEN)

        for i, option in enumerate(options):
            color = GREEN if i == selected else WHITE
            draw_text(screen, option, WIDTH // 3, 80 + i * 40, color)

        pygame.display.flip()

        if button_pressed("down"):
            selected = (selected + 1) % len(options)
        elif button_pressed("up"):
            selected = (selected - 1) % len(options)
        elif button_pressed("select"):
            if options[selected] == "Exit":
                pygame.quit()
                sys.exit()
            return options[selected]

        if button_pressed("reset"):
            return None  # Hard reset to main menu

def snake_game():
    BLOCK_SIZE = 20
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (0, -BLOCK_SIZE)
    food = (random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE))
    running = True
    clock = pygame.time.Clock()
    score = 0
    speed = 5

    while running:
        screen.fill(BLACK)
        if button_pressed("up") and direction != (0, BLOCK_SIZE):
            direction = (0, -BLOCK_SIZE)
        elif button_pressed("down") and direction != (0, -BLOCK_SIZE):
            direction = (0, BLOCK_SIZE)
        elif button_pressed("left") and direction != (BLOCK_SIZE, 0):
            direction = (-BLOCK_SIZE, 0)
        elif button_pressed("right") and direction != (-BLOCK_SIZE, 0):
            direction = (BLOCK_SIZE, 0)
        elif button_pressed("reset"):
            return

        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        if new_head in snake or new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
            screen.fill(BLACK)
            draw_text(screen, f"Game Over! Score: {score}", WIDTH // 4, HEIGHT // 2)
            pygame.display.flip()
            pygame.time.wait(2000)
            return

        snake.insert(0, new_head)
        if new_head == food:
            score += 1
            food = (random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE))
            speed += 0.5
        else:
            snake.pop()

        pygame.draw.rect(screen, RED, (food[0], food[1], BLOCK_SIZE, BLOCK_SIZE))
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

        draw_text(screen, f"Score: {score}", 10, 10)
        pygame.display.flip()
        clock.tick(speed)

def tetris_game():
    grid_size = 20
    cols, rows = WIDTH // grid_size, HEIGHT // grid_size
    grid = [[BLACK for _ in range(cols)] for _ in range(rows)]
    tetrominoes = {
        'I': [[1, 1, 1, 1]],
        'O': [[1, 1], [1, 1]],
        'T': [[0, 1, 0], [1, 1, 1]],
        'S': [[0, 1, 1], [1, 1, 0]],
        'Z': [[1, 1, 0], [0, 1, 1]],
        'J': [[1, 0, 0], [1, 1, 1]],
        'L': [[0, 0, 1], [1, 1, 1]]
    }

    def rotate(shape):
        return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]

    def draw_grid():
        for y in range(rows):
            for x in range(cols):
                color = grid[y][x]
                pygame.draw.rect(screen, color, (x * grid_size, y * grid_size, grid_size - 1, grid_size - 1))

    def valid_position(shape, offset):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x, new_y = x + offset[0], y + offset[1]
                    if new_x < 0 or new_x >= cols or new_y >= rows or (new_y >= 0 and grid[new_y][new_x] != BLACK):
                        return False
        return True

    def merge_shape(shape, offset, color):
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    grid[y + offset[1]][x + offset[0]] = color

    def clear_lines():
        nonlocal grid, score
        new_grid = [row for row in grid if any(cell == BLACK for cell in row)]
        lines_cleared = rows - len(new_grid)
        score += lines_cleared * 10
        while len(new_grid) < rows:
            new_grid.insert(0, [BLACK for _ in range(cols)])
        grid = new_grid

    shape = random.choice(list(tetrominoes.values()))
    color = CYAN
    offset = [cols // 2 - len(shape[0]) // 2, 0]
    clock = pygame.time.Clock()
    fall_time = 0
    score = 0
    running = True

    while running:
        screen.fill(BLACK)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time > 500:
            offset[1] += 1
            if not valid_position(shape, offset):
                offset[1] -= 1
                merge_shape(shape, offset, color)
                clear_lines()
                shape = random.choice(list(tetrominoes.values()))
                offset = [cols // 2 - len(shape[0]) // 2, 0]
                if not valid_position(shape, offset):
                    draw_text(screen, f"Game Over! Score: {score}", WIDTH // 4, HEIGHT // 2)
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    return
            fall_time = 0

        if button_pressed("left"):
            offset[0] -= 1
            if not valid_position(shape, offset):
                offset[0] += 1
        elif button_pressed("right"):
            offset[0] += 1
            if not valid_position(shape, offset):
                offset[0] -= 1
        elif button_pressed("down"):
            offset[1] += 1
            if not valid_position(shape, offset):
                offset[1] -= 1
        elif button_pressed("select"):
            new_shape = rotate(shape)
            if valid_position(new_shape, offset):
                shape = new_shape
        elif button_pressed("reset"):
            return

        draw_grid()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, color, ((x + offset[0]) * grid_size, (y + offset[1]) * grid_size, grid_size - 1, grid_size - 1))

        draw_text(screen, f"Score: {score}", WIDTH - 120, 10)
        pygame.display.flip()

# Main loop
while True:
    selected_game = game_menu()
    if selected_game == "Snake":
        snake_game()
    elif selected_game == "Platformer":
        start_platformer(screen, platformer_pressed)
    elif selected_game == "Tetris":
        tetris_game()
