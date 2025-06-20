import pygame
import threading
import random
from flask import Flask, request, send_from_directory
from utils import button_pressed
from PIL import Image
import io
import numpy as np

app = Flask(__name__, static_url_path='', static_folder='static')
player2_dir = 'LEFT'
latest_frame = None

@app.route('/set_dir', methods=['POST'])
def set_dir():
    global player2_dir
    player2_dir = request.form['dir']
    print("[WEB] Received direction:", player2_dir)
    return 'OK'

@app.route('/')
def controls():
    return send_from_directory('static', 'controls.html')

@app.route('/stream')
def stream():
    global latest_frame
    if latest_frame is None:
        return '', 200, {'Content-Type': 'image/jpeg'}
    buf = io.BytesIO()
    img = Image.fromarray(latest_frame)
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf.read(), 200, {'Content-Type': 'image/jpeg'}

def run_web_server():
    app.run(host='0.0.0.0', port=5000)

class Snake:
    def __init__(self, color, start_pos):
        self.body = [start_pos]
        self.direction = (1, 0)
        self.color = color

    def move(self):
        head = self.body[-1]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.append(new_head)
        self.body.pop(0)

    def grow(self):
        head = self.body[-1]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.append(new_head)

    def draw(self, screen, block_size):
        for segment in self.body:
            pygame.draw.rect(screen, self.color, pygame.Rect(segment[0]*block_size, segment[1]*block_size, block_size, block_size))

def show_game_over(screen, text, font):
    screen.fill((0, 0, 0))
    msg = font.render(text, True, (255, 0, 0))
    screen.blit(msg, (screen.get_width() // 2 - msg.get_width() // 2, screen.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

def run_slither_game(get_gpio_direction=None):
    global latest_frame

    flask_thread = threading.Thread(target=run_web_server, daemon=True)
    flask_thread.start()

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    block_size = 20
    cols = screen_width // block_size
    rows = screen_height // block_size
    pygame.display.set_caption("Slither Clone - 2 Player")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Show countdown
    for count in ["3", "2", "1", "GO!"]:
        screen.fill((0, 0, 0))
        msg = font.render(count, True, (255, 255, 255))
        screen.blit(msg, (screen.get_width() // 2 - msg.get_width() // 2,
                          screen.get_height() // 2 - msg.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(1000)

    score1, score2 = 0, 0
    winner = ""
    speed = 10
    food_eaten = 0

    snake1 = Snake((0, 255, 0), (5, 5))
    snake2 = Snake((0, 0, 255), (20, 15))
    food_items = [(random.randint(0, cols - 1), random.randint(0, rows - 1)) for _ in range(3)]

    running = True
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player 1 input
        if get_gpio_direction:
            dir1 = get_gpio_direction()
            if dir1 == 'UP': snake1.direction = (0, -1)
            elif dir1 == 'DOWN': snake1.direction = (0, 1)
            elif dir1 == 'LEFT': snake1.direction = (-1, 0)
            elif dir1 == 'RIGHT': snake1.direction = (1, 0)
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: snake1.direction = (0, -1)
            if keys[pygame.K_s]: snake1.direction = (0, 1)
            if keys[pygame.K_a]: snake1.direction = (-1, 0)
            if keys[pygame.K_d]: snake1.direction = (1, 0)

        # Player 2 input (web + keyboard)
        dir_map = {'UP': (0, -1), 'DOWN': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0)}
        if player2_dir:
            snake2.direction = dir_map.get(player2_dir.upper(), snake2.direction)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: snake2.direction = (0, -1)
        if keys[pygame.K_DOWN]: snake2.direction = (0, 1)
        if keys[pygame.K_LEFT]: snake2.direction = (-1, 0)
        if keys[pygame.K_RIGHT]: snake2.direction = (1, 0)

        snake1.move()
        snake2.move()

        for i, f in enumerate(food_items):
            if snake1.body[-1] == f:
                snake1.grow()
                score1 += 1
                food_eaten += 1
                food_items[i] = (random.randint(0, cols - 1), random.randint(0, rows - 1))
                if food_eaten % 5 == 0:
                    speed = min(speed + 1, 30)
            elif snake2.body[-1] == f:
                snake2.grow()
                score2 += 1
                food_eaten += 1
                food_items[i] = (random.randint(0, cols - 1), random.randint(0, rows - 1))
                if food_eaten % 5 == 0:
                    speed = min(speed + 1, 30)

        head1 = snake1.body[-1]
        head2 = snake2.body[-1]

        if head1 == head2:
            winner = "Draw!"
            running = False
        elif head1 in snake2.body:
            winner = "Player 2 Wins!"
            running = False
        elif head2 in snake1.body:
            winner = "Player 1 Wins!"
            running = False
        elif head1 in snake1.body[:-1] or not (0 <= head1[0] < cols and 0 <= head1[1] < rows):
            winner = "Player 2 Wins!"
            running = False
        elif head2 in snake2.body[:-1] or not (0 <= head2[0] < cols and 0 <= head2[1] < rows):
            winner = "Player 1 Wins!"
            running = False

        if button_pressed("reset"):
            print("Reset button pressed")
            return

        for f in food_items:
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(f[0]*block_size, f[1]*block_size, block_size, block_size))

        snake1.draw(screen, block_size)
        snake2.draw(screen, block_size)

        score_text = font.render(f"P1: {score1}   P2: {score2}   Speed: {speed}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

        # Capture frame for browser stream
        screen_array = pygame.surfarray.array3d(screen)
        screen_array = np.rot90(screen_array, 3)
        screen_array = np.flip(screen_array, axis=1)
        latest_frame = screen_array

        clock.tick(speed)

    show_game_over(screen, winner, font)
    pygame.quit()
