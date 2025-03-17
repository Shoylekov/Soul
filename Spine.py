import pygame

class Spine:
    def __init__(self, player_choice_for_spine=None, boss_name="Spine"):
        self.frames = [
            pygame.image.load("assets/sheets/Boss3.png").convert_alpha(),
            pygame.image.load("assets/sheets/Boss3-left.png").convert_alpha(),
            pygame.image.load("assets/sheets/Boss3.png").convert_alpha(),
            pygame.image.load("assets/sheets/Boss3-right.png").convert_alpha()
        ]
        self.boss_name = boss_name
        self.frames = [pygame.transform.scale(frame, (100, 100)) for frame in self.frames]  # Adjust size as needed
        self.current_frame = 0
        self.animation_speed = 500  # Change frame every 200ms
        self.last_update = pygame.time.get_ticks()
        self.rect = self.frames[0].get_rect()
        self.rect.topleft = (590, 110)  # Position Spine on the second map
        self.health = 1  # Add health attribute
        self.max_health = 1  # Add max health attribute

        if player_choice_for_spine == "Go Back":
            self.dialogue_lines = [
                "Go back? Now you want to run?",
                "After everything you've done?",
                "Pathetic!",
                "I thought you were strong…",
                "But you're just another coward!",
                "DIE!"
            ]
        else:
            self.dialogue_lines = [
                "Hey...",
                "Wanderer.",
                "My name is Spine.",
                'Some call me "The Blasphemer"!',
                "And I must say, I'm impressed.",
                "That's an unusual way to end up here...",
                "Solenn. That name suits you.",
                "You killed Path, didn't you?",
                "Huh?",
                "Maybe we're not so different after all.",
                "You don't think about consequences. You do whatever you want.",
                "You believe you're above everyone else,",
                "That no one can match you.",
                "But unfortunately, that won't last forever.",
                "Ha-Ha-Ha!",
                "Because... you've just died.",
                "And that means it's time...",
                "For your suffering!"
            ]

        # Ensure dialogue is set from dialogue_lines
        self.dialogue = "\n".join(self.dialogue_lines)

    def update(self):
        # Handle frame animation timing
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen):
        screen.blit(self.frames[self.current_frame], self.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 1)  # Red collision rectangle

    def draw_health_bar(self, screen, position, width=200, height=20):
        """Draws the boss's health bar with the boss's name on top and health numbers on the right side."""
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), (position[0], position[1], width, height))  # Red background
        pygame.draw.rect(screen, (0, 255, 0), (position[0], position[1], width * health_ratio, height))  # Green foreground
        pygame.draw.rect(screen, (255, 255, 255), (position[0], position[1], width, height), 2)  # White border

        font = pygame.font.SysFont('impact', 34)
        health_text = f"{int(self.health)}/{self.max_health}"
        text_surface = font.render(health_text, True, (255, 255, 255))

        # Move the health numbers to the right side
        text_rect = text_surface.get_rect(midleft=(position[0] + width + 10, position[1] + height // 2))
        screen.blit(text_surface, text_rect)

        # Draw the boss's name on top of the health bar
        name_surface = font.render(self.boss_name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(position[0] + width // 2, position[1] - 20))
        screen.blit(name_surface, name_rect)