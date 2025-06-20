import pygame
import threading
import random
from flask import Flask, request, send_from_directory

# --- Flask Web Server for Player 2 Input ---
app = Flask(__name__, static_url_path='', static_folder='static')
player2_dir = 'LEFT'

@app.route('/set_dir', methods=['POST'])
def set_dir():
    global player2_dir
    player2_dir = request.form['dir']
    return 'OK'

@app.route('/')
def controls():
    return send_from_directory('static', 'controls.html')

def run_web_server():
    app.run(host='0.0.0.0', port=5000)

# --- Snake Class ---
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

# --- Main Game Function ---
def run_slither_game(get_gpio_direction=None):
    flask_thread = threading.Thread(target=run_web_server, daemon=True)
    flask_thread.start()

    pygame.init()
    screen_width, screen_height = 640, 480
    block_size = 20
    cols = screen_width // block_size
    rows = screen_height // block_size
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Slither Clone - 2 Player")

    clock = pygame.time.Clock()
    snake1 = Snake((0, 255, 0), (5, 5))
    snake2 = Snake((0, 0, 255), (20, 15))
    food = (random.randint(0, cols-1), random.randint(0, rows-1))

    running = True
    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- GPIO Input for Player 1 ---
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

        try:
            dir_map = {
                'UP': (0, -1), 'DOWN': (0, 1),
                'LEFT': (-1, 0), 'RIGHT': (1, 0)
            }
            snake2.direction = dir_map.get(player2_dir.upper(), snake2.direction)
        except:
            pass

        snake1.move()
        snake2.move()

        if snake1.body[-1] == food:
            snake1.grow()
            food = (random.randint(0, cols-1), random.randint(0, rows-1))
        elif snake2.body[-1] == food:
            snake2.grow()
            food = (random.randint(0, cols-1), random.randint(0, rows-1))

        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(food[0]*block_size, food[1]*block_size, block_size, block_size))
        snake1.draw(screen, block_size)
        snake2.draw(screen, block_size)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
