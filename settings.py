import pygame
import os
import ctypes
WIDTH = 1280  # New width
HEIGHT = 832

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Player settings
PLAYER_SIZE = 20
PLAYER_SPEED = 3


def initialize_game():
    pygame.init()
    pygame.mixer.init()

    # Center the Pygame window on the screen
    user32 = ctypes.windll.user32
    screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{(screen_width - WIDTH) // 2},{(screen_height - HEIGHT) // 2}"

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Solenn")
    return screen