import random
import pygame
import time
from Ship import Player, Enemy


class Game:
	FPS = 60

	def __init__(self, window, background):
		self.window = window
		self.WIDTH = window.get_width()
		self.HEIGHT = window.get_height()
		self.BG = BackGround(background)
		self.main_player = Player(self.WIDTH // 2 - 50, self.HEIGHT - 150)
		self.enemies = []
		self.lasers = []
		self.level = 0
		self.lost = False
		self.all_texts = {
			"menu_text":     TextHUD(70, self.window),
			"game_hud_text": TextHUD(40, self.window),
			"lost_text":     TextHUD(60, self.window)
		}

	def start_game(self):
		try:
			self.main_menu()
		except Exception as e:
			if str(e) == "display Surface quit":
				pass

	def main_menu(self):
		run = True
		pygame.mouse.set_visible(True)
		pygame.event.set_grab(False)

		clock = pygame.time.Clock()
		while run:
			clock.tick(Game.FPS)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					self.gameplay()

			self.BG.draw(self.window)

			self.all_texts["menu_text"].draw("Click mouse to begin...", "half", "half")

			pygame.display.update()

	def gameplay(self):
		run = True

		pygame.mouse.set_visible(False)
		pygame.event.set_grab(True)
		mouse_click = False

		clock = pygame.time.Clock()
		while run:
			clock.tick(Game.FPS)
			self.redraw_window()

			if self.lost:
				pygame.mouse.set_visible(True)
				pygame.event.set_grab(False)
				time.sleep(3)
				run = False
				continue

			self.lost = self.check_game_lost()

			# move player based on mouse position
			mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
			self.main_player.move(mouse_pos_x - 50, mouse_pos_y - 50, self.WIDTH, self.HEIGHT)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					mouse_click = True
				if event.type == pygame.MOUSEBUTTONUP:
					mouse_click = False

			# shoot if left mouse is pressed
			if mouse_click:
				self.main_player.shoot(self)

			self.check_enemies()

			self.check_lasers()

		# clean memory after gameplay run
		# del self.main_player
		self.main_player = Player(self.WIDTH // 2 - 50, self.HEIGHT - 150)
		# del self.enemies
		self.enemies = []
		# del self.lasers
		self.lasers = []
		# del self.level
		self.level = 0
		# del self.lost
		self.lost = False
		pygame.mouse.set_visible(True)
		pygame.event.set_grab(False)

	def redraw_window(self):  # for gameplay, not main menu
		self.BG.draw(self.window)

		for enemy in self.enemies:
			enemy.draw(self.window)

		for laser in self.lasers:
			laser.draw(self.window)

		self.main_player.draw(self.window)
		# draw HUD
		self.all_texts["game_hud_text"].draw(f"lives: {self.main_player.lives}", 10, 10)
		level_hud_width = self.all_texts["game_hud_text"].get_width(f"level: {self.level}")
		self.all_texts["game_hud_text"].draw(f"level: {self.level}", self.WIDTH - level_hud_width - 10, 10)
		if self.lost:
			self.all_texts["lost_text"].draw("You Lost!", "half", "half")

		pygame.display.update()

	def check_game_lost(self):
		if self.main_player.lives <= 0 or self.main_player.health <= 0:
			return True
		return False

	def check_lasers(self):
		for laser in self.lasers[:]:
			laser.move()

			if self.off_screen(laser.y):
				self.lasers.remove(laser)
				del laser
				continue
			elif laser.color != "yellow" and Game.collide(laser, self.main_player):
				self.main_player.take_damage()
				self.lasers.remove(laser)
				del laser
				continue
			elif laser.color == "yellow":
				for enemy in self.enemies[:]:
					if Game.collide(laser, enemy):
						self.main_player.add_health()
						self.enemies.remove(enemy)
						self.lasers.remove(laser)
						del enemy
						del laser
						break

	def check_enemies(self):
		for enemy in self.enemies[:]:
			if enemy.off_screen(self.HEIGHT + 30):
				self.main_player.lose_a_life()
				self.enemies.remove(enemy)
				del enemy
				continue

			if Game.collide(enemy, self.main_player):
				self.main_player.take_damage()
				self.enemies.remove(enemy)
				del enemy
				continue

			enemy.move()
			enemy.shoot(self)

		if len(self.enemies) == 0:
			self.level += 1
			for i in range((self.level + 1) * 5):
				enemy = Enemy(
					random.randrange(50, self.WIDTH - 100),
					random.randrange(-1500 - ((self.level - 1) * 100), -100),
					random.choice(["red", "blue", "green"])
				)
				self.enemies.append(enemy)

	def off_screen(self, val):
		return not (-50 < val < self.HEIGHT + 50)

	@staticmethod
	def collide(obj1, obj2):
		offset_x = obj2.x - obj1.x
		offset_y = obj2.y - obj1.y
		return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


class BackGround:
	def __init__(self, background):
		self.background = background
		self.window_height = background.get_height()
		self.y1 = 0
		self.y2 = -self.window_height
		self.velocity = 0.5

	def draw(self, window):
		window.blit(self.background, (0, self.y1))
		window.blit(self.background, (0, self.y2))
		self.move()

	def move(self):
		self.y1 += self.velocity
		self.y2 += self.velocity
		if self.y1 >= self.window_height:
			self.y1, self.y2 = 0, -self.window_height


class TextHUD:
	def __init__(self, size, window, font_family="comicsans", color=(255, 255, 255)):
		self.text_font = pygame.font.SysFont(font_family, size)
		self.color = color
		self.window = window

	def draw(self, text, x, y):
		text_label = self.text_font.render(text, True, self.color)
		if x == "half":
			x = (self.window.get_width() - text_label.get_width()) // 2
		if y == "half":
			y = (self.window.get_height() - text_label.get_height()) // 2
		self.window.blit(text_label, (x, y))

	def get_width(self, text):
		text_label = self.text_font.render(text, True, self.color)
		return text_label.get_width()


