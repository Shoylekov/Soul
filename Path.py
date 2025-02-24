import pygame
from settings import WIDTH, HEIGHT, BLACK, WHITE

class Boss:
    def __init__(self, boss_name="Path"):
        self.sprite_sheet = pygame.image.load("assets/sheets/path.png").convert_alpha()
        self.scale_factor = 2  # Increase size
        self.boss_name = boss_name

        self.health = 1000  # Add health attribute
        self.max_health = 1000  # Add max health attribute

        self.frames = self.load_frames()  # FIXED: Removed incorrect argument (12)
        self.current_frame = 0
        self.animation_speed = 200  # Change frame every 200ms
        self.last_update = pygame.time.get_ticks()

        # Position
        self.x = 515
        self.y = 20

        # Collision rectangle scaling
        collision_scale_height = 0.6  # Adjust this value as needed
        collision_scale_width = 0.8
        frame_width = int(self.frames[0].get_width() * collision_scale_width)
        frame_height = int(self.frames[0].get_height() * collision_scale_height)

        # Store the frame width & height
        self.frame_width = frame_width
        self.frame_height = frame_height

        # Create the initial collision rectangle
        self.rect = pygame.Rect(self.x, self.y, frame_width, frame_height)
        
        # Boss dialogue lines
        self.dialogue_lines = [
            "Hello, stranger!...",
            "My name is Path.",
            "It's rare to see a living one wandering here.",
            "...",
            "But you… you are still alive.",
            "You do not belong in this place!",
            "I am the one who judges souls after death.",
            "And it's NOT your time yet!",
            "You must GO BACK to your realm before...!"
        ]

        self.dialogue = "\n".join(self.dialogue_lines)

    def load_frames(self):
        """Splits the sprite sheet into individual frames and scales them up."""
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()
        frame_width = sheet_width // 6   # 6 frames per row
        frame_height = sheet_height // 2 # 2 rows

        frames = []
        for row in range(2):  # Two rows
            for col in range(6):  # Six frames per row
                frame = self.sprite_sheet.subsurface(
                    pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                )
                # Scale up
                frame = pygame.transform.scale(frame, (frame_width * self.scale_factor, frame_height * self.scale_factor))
                frames.append(frame)
        return frames

    def draw_health_bar(self, screen, position, width=200, height=20):
        """Draws the boss's health bar with the boss's name on top."""
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), (position[0], position[1], width, height))  # Red background
        pygame.draw.rect(screen, (0, 255, 0), (position[0], position[1], width * health_ratio, height))  # Green foreground
        pygame.draw.rect(screen, (255, 255, 255), (position[0], position[1], width, height), 2)  # White border

        # Draw the boss's name on top of the health bar
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.boss_name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(position[0] + width // 2, position[1] - 20))
        screen.blit(text_surface, text_rect)

    def update(self):
        """Handles frame animation timing and updates position."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Ensure collision box follows sprite position
        self.rect.x = self.x + (self.frames[0].get_width() - self.frame_width) // 2
        self.rect.y = self.y + (self.frames[0].get_height() - self.frame_height) // 2

    def draw(self, screen):
        """Draws the current frame of the boss and its collision rectangle."""
        screen.blit(self.frames[self.current_frame], (self.x, self.y))  # FIXED: Uses self.x, self.y for proper positioning
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)  # Red collision rectangle
