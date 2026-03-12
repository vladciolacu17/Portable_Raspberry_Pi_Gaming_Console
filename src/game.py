import pygame
from settings import HEIGHT, WIDTH

pygame.font.init()

class Game:
	def __init__(self, screen):
		self.screen = screen
		self.font = pygame.font.SysFont("impact", 70)
		self.message_color = pygame.Color("darkorange")

	# if player ran out of life or fell below the platform
	def _display_message(self, message):
		self.screen.fill((0, 0, 0))  # Clear the screen
		text = self.font.render(message, True, self.message_color)
		self.screen.blit(text, (WIDTH // 4, HEIGHT // 2))
		pygame.display.flip()
		pygame.time.wait(2000)  # Wait for 2 seconds

	def _game_lose(self, player):
		player.game_over = True
		self._display_message("You Lose...")

	def _game_win(self, player):
		player.game_over = True
		player.win = True
		self._display_message("You Win!!")

	def game_state(self, player, goal):
		if player.life <= 0 or player.rect.y >= HEIGHT:
			self._game_lose(player)
		elif player.rect.colliderect(goal.rect):
			self._game_win(player)
		else:
			None

	def show_life(self, player):
		life_size = 30
		img_path = "assets/life/life.png"
		life_image = pygame.image.load(img_path)
		life_image = pygame.transform.scale(life_image, (life_size, life_size))
		# life_rect = life_image.get_rect(topleft = pos)
		indent = 0
		for life in range(player.life):
			indent += life_size
			self.screen.blit(life_image, (indent, life_size))