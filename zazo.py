import pygame
from settings import WIDTH, HEIGHT, BLACK, WHITE

class Zazo:
    def __init__(self, boss_name="Zazo"):
        self.sprite_sheet = pygame.image.load("assets/sheets/ToxicFrogPurpleWhite_Idle.png").convert_alpha()
        self.scale_factor = 2  # Increase size
        self.boss_name = boss_name

        self.frames = self.load_frames(8)  # Assuming 10 frames in the sprite sheet
        self.current_frame = 0
        self.animation_speed = 200  # Change frame every 200ms
        self.last_update = pygame.time.get_ticks()

        # Position
        self.x = 1110
        self.y = 460

        # Reduce the rectangle size
        collision_scale_height = 0.8  # Adjust this value as needed
        collision_scale_width = 0.8
        frame_width = int(self.frames[0].get_width() * collision_scale_width)
        frame_height = int(self.frames[0].get_height() * collision_scale_height)

        # Center the rectangle inside the boss sprite
        rect_x = self.x + (self.frames[0].get_width() - frame_width) // 2
        rect_y = self.y + (self.frames[0].get_height() - frame_height) // 2

        print(self.current_frame)
        # Create the collision rectangle
        self.rect = pygame.Rect(rect_x, rect_y, frame_width, frame_height)
        
        # NEW: Store dialogue lines in the boss class
        self.dialogue_lines = [
            "Ribbit... Ribbit...",
            "I am Zazo, the Toxic Frog.",
            "...",
            "...",
            "You dare to approach me?",
            "Ribbit...",
            "...",
            "Beware...",
            "My GOODS might be very potent!",
            "If you wish to test yourself,",
            "ribbit.",
            "You can accept this Magic Mushroom!",
        ]

        # You can also store them as a single string if desired:
        self.dialogue = "\n".join(self.dialogue_lines)

    def load_frames(self, num_frames):
        """Splits the sprite sheet into individual frames and scales them up."""
        frame_width = self.sprite_sheet.get_width() // num_frames
        frame_height = self.sprite_sheet.get_height()

        frames = []
        for i in range(num_frames):
            frame = self.sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (frame_width * self.scale_factor, frame_height * self.scale_factor))
            frames.append(frame)
        return frames


    def update(self):
        """Handles frame animation timing."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen):
        """Draws the current frame of the boss and its collision rectangle."""
        # Flip the sprite horizontally to make it look to the left
        flipped_frame = pygame.transform.flip(self.frames[self.current_frame], True, False)
        
        # Draw the flipped frame
        screen.blit(flipped_frame, (self.rect.x, self.rect.y))

        # Remove or modify this line if you don't want the collision box drawn
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)  # Red collision rectangle


