import pygame
import os
from Game import Game

pygame.font.init()
pygame.display.set_caption("Space Invaders")
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


def main():
	game = Game(WIN, BG)
	game.start_game()


if __name__ == "__main__":
	main()
