import pygame
from settings import *

screen = initialize_game()

def show_loading_screen(text):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 74)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    fade_surface = pygame.Surface((WIDTH, HEIGHT))  # Create a full-screen surface
    fade_surface.fill((0, 0, 0))  # Fill it with black
    clock = pygame.time.Clock()

    # Fade in
    for alpha in range(0, 256, 5):  # Increase alpha gradually
        screen.fill((0, 0, 0))  # Ensure background stays black
        screen.blit(text_surface, text_rect)  # Draw text
        fade_surface.set_alpha(255 - alpha)  # Adjust transparency
        screen.blit(fade_surface, (0, 0))  # Apply fade effect
        pygame.display.flip()
        clock.tick(30)  # Control fade speed

    pygame.time.delay(1000)  # Hold the screen for 1 second

    # Fade out
    for alpha in range(0, 256, 5):  # Decrease alpha gradually
        screen.fill((0, 0, 0))
        screen.blit(text_surface, text_rect)
        fade_surface.set_alpha(alpha)  # Increase transparency
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(30)