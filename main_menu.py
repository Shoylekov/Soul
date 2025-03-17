import pygame
import sys
from settings import *
from soul import Soul

pygame.init()

# Constants
FONT_SIZE = 36
MENU_ITEMS = ["Start Game", "Quit"]

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load font
font = pygame.font.Font(None, FONT_SIZE)

# Load background image
background_image = pygame.image.load("assets/sheets/Main menu.jpg").convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Load and scale soul sprite frames
soul_sprite_sheet = pygame.image.load("assets/sheets/summonIdle.png").convert_alpha()
soul_frames = []
sheet_width, sheet_height = soul_sprite_sheet.get_size()
frame_width = sheet_width // 4  # Assuming 4 frames in a single row
frame_height = sheet_height
scale_factor = 4  # Adjust this factor to make the Soul bigger
for i in range(4):
    frame = soul_sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
    soul_frames.append(pygame.transform.scale(frame, (frame.get_width() * scale_factor, frame.get_height() * scale_factor)))  # Scale frames

# Initialize the Soul object
arena_rect = pygame.Rect(417, -190, WIDTH, HEIGHT)  # Use the entire screen as the arena for the main menu
soul = Soul(arena_rect, soul_frames)

def draw_text(text, font, color, surface, x, y):
    """Draw text centered at (x, y) on the given surface."""
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def main_menu():
    selected_index = 0  # Which menu item is currently selected
    clock = pygame.time.Clock()

    pygame.mixer.music.load("assets/music/main_menu.mp3") 
    pygame.mixer.music.play(-1)  # Loop

    while True:
        screen.blit(background_image, (0, 0))  # Draw the background image

        # Update and draw the Soul
        soul.update()
        soul.draw(screen)

        # Draw each menu item
        for i, item in enumerate(MENU_ITEMS):
            # Highlight the selected item
            if i == selected_index:
                color = (255, 255, 0)  # Yellow for the selected item
            else:
                color = (255, 255, 255)  # White for non-selected items

            # Vertical spacing of 50 pixels between items
            y_pos = (HEIGHT // 2) + (i * 50)
            draw_text(item, font, color, screen, WIDTH // 2, y_pos)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                # Navigate menu
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(MENU_ITEMS)
                elif event.key == pygame.K_RETURN:
                    if MENU_ITEMS[selected_index] == "Start Game":
                        return "start_game"
                    elif MENU_ITEMS[selected_index] == "Quit":
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

if __name__ == "__main__":
    main_menu()