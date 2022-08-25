import pygame
import os
import threading
import time
import random

# load assets
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "ship_blue_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "ship_yellow.png"))
RED_LASER = pygame.image.load(os.path.join("assets", "laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "laser_yellow.png"))


class Ship:
	COLOR_MAP = {
		"yellow": YELLOW_SPACE_SHIP,
		"red":    RED_SPACE_SHIP,
		"blue":   BLUE_SPACE_SHIP,
		"green":  GREEN_SPACE_SHIP,
	}

	def __init__(self, x, y, color):
		self.x = x
		self.y = y
		self.color = color
		self.img = Ship.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.img)
		self.laser_velocity = 5
		self.cooldown = 0.5  # seconds
		self.on_cooldown = False

	def get_width(self):
		return self.img.get_width()

	def get_height(self):
		return self.img.get_height()

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def shoot(self, game):
		if not self.on_cooldown:
			laser_pos_x = self.x + ((self.get_width() - 100) // 2)  # 100 is the width of lasers' img
			laser = Laser(laser_pos_x, self.y, self.laser_velocity, self.color)
			self.on_cooldown = True
			cooldown_thread = threading.Thread(target=self.wait_for_cooldown)
			cooldown_thread.start()
			game.lasers.append(laser)

	def wait_for_cooldown(self):
		time.sleep(self.cooldown)
		self.on_cooldown = False


class Player(Ship):
	def __init__(self, x, y, color="yellow"):
		super().__init__(x, y, color)
		self.health = self.max_health = 100
		self.lives = 5
		self.laser_velocity = -10
		self.cooldown = 0.15  # second

	def move(self, x, y, max_width, max_height):
		self.x = max(0, x)
		self.x = min(max_width - self.get_width(), self.x)
		self.y = max(0, y)
		self.y = min(max_height - self.get_height(), self.y)

	def draw(self, window):
		super().draw(window)
		# draw health bar
		pos_y = self.y + self.get_height() + 4
		remaining_health = int(self.health / self.max_health * self.get_width())
		pygame.draw.rect(window, (61, 17, 17), pygame.Rect(self.x, pos_y, self.get_width(), 8))
		pygame.draw.rect(window, (13, 64, 20), pygame.Rect(self.x, pos_y, remaining_health, 8))

	def take_damage(self, amount=10):
		self.health -= amount

	def add_health(self, amount=10):
		self.health += amount
		self.health = min(self.max_health, self.health)

	def lose_a_life(self):
		self.lives -= 1


class Enemy(Ship):
	def __init__(self, x, y, color):
		super().__init__(x, y, color)
		self.move_velocity = 1

	def move(self):
		self.y += self.move_velocity

	def off_screen(self, max_height):
		return self.y > max_height

	def wait_for_cooldown(self):
		super().wait_for_cooldown()
		self.cooldown = (random.randrange(10, 25)) / 10.0


class Laser:
	COLOR_MAP = {
		"yellow": YELLOW_LASER,
		"red":    RED_LASER,
		"blue":   BLUE_LASER,
		"green":  GREEN_LASER,
	}

	def __init__(self, x, y, laser_velocity, color):
		self.x = x
		self.y = y
		self.vel = laser_velocity
		self.color = color
		self.img = Laser.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.img)

	def move(self):
		self.y += self.vel

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))
