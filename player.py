import pygame
from settings import *
from sprites import SpriteSheet

class Player:
    def __init__(self):
        self.sprites = SpriteSheet(r"assets/sheets/hero.png")

        # Adjusted animation frames (assuming a 4x3 layout)
        self.animations = {
            "idle": [self.sprites.get_image(32, 0, 32, 32, 2)],
            "walk_down": [self.sprites.get_image(0, 0, 32, 32, 2), self.sprites.get_image(32, 0, 32, 32, 2), self.sprites.get_image(64, 0, 32, 32, 2)],
            "walk_left": [self.sprites.get_image(0, 32, 32, 32, 2), self.sprites.get_image(32, 32, 32, 32, 2), self.sprites.get_image(64, 32, 32, 32, 2)],
            "walk_right": [self.sprites.get_image(0, 64, 32, 32, 2), self.sprites.get_image(32, 64, 32, 32, 2), self.sprites.get_image(64, 64, 32, 32, 2)],
            "walk_up": [self.sprites.get_image(0, 96, 32, 32, 2), self.sprites.get_image(32, 96, 32, 32, 2), self.sprites.get_image(64, 96, 32, 32, 2)]
        }

        self.current_animation = "idle"
        self.frame = 0
        self.image = self.animations[self.current_animation][self.frame]
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        #Convo CD
        self.in_conversation = False
        self.conversation_cooldown = 0 
        # Define a smaller collision rectangle and move it down
        self.collision_rect = self.rect.inflate(-1, 0)  
        self.collision_rect.centery = self.rect.centery + 50

        self.damage_sound = pygame.mixer.Sound("assets/music/damage_sound.mp3")
        # Initialize health
        self.health = 99
        self.heals_used = 0
        self.alive = True

    def move(self, keys, obstacles):
        speed = PLAYER_SPEED
        moving = False
        new_animation = "idle"

        # Create a copy of the player's collision rect to test movement
        temp_rect = self.collision_rect.copy()

        if keys[pygame.K_LEFT]:
            temp_rect.x -= speed
            new_animation = "walk_left"
            moving = True
        if keys[pygame.K_RIGHT]:
            temp_rect.x += speed
            new_animation = "walk_right"
            moving = True
        if keys[pygame.K_UP]:
            temp_rect.y -= speed
            new_animation = "walk_up"
            moving = True
        if keys[pygame.K_DOWN]:
            temp_rect.y += speed
            new_animation = "walk_down"
            moving = True

        # Check for collisions with obstacles
        if not any(temp_rect.colliderect(obstacle) for obstacle in obstacles):
            # Check for screen boundaries
            if temp_rect.left >= 0 and temp_rect.right <= WIDTH and temp_rect.top >= 0 and temp_rect.bottom <= HEIGHT:
                self.rect.topleft = temp_rect.topleft  # Only move if no collision and within boundaries
                self.collision_rect.topleft = temp_rect.topleft

        # Set idle animation correctly when no keys are pressed
        if not moving and self.current_animation != "idle":
            self.current_animation = "idle"
            self.frame = 1  # Use second frame for idle

        # Change animation if needed
        if moving and new_animation != self.current_animation:
            self.current_animation = new_animation
            self.frame = 0  # Reset animation

    def animate(self):
        # If moving, cycle through the animation frames
        if self.current_animation != "idle":
            self.frame += 0.1
            if self.frame >= len(self.animations[self.current_animation]):
                self.frame = 0  # Reset frame to loop the animation
            self.image = self.animations[self.current_animation][int(self.frame)]
        else:
            # Set idle to the second frame instead of the first
            self.frame = 1  # Second frame in idle animation
            self.image = self.animations["idle"][0 if len(self.animations["idle"]) <= 1 else 1]

    def reset(self):
        """Resets the player's state."""
        self.health = 99
        self.heals_used = 0
        self.alive = True
        self.rect.center = (WIDTH // 2, HEIGHT // 2)  # Reset position to the center
        self.collision_rect.topleft = self.rect.topleft
        
    def update(self, keys, obstacles):
        self.move(keys, obstacles)
        self.animate()
        if self.conversation_cooldown > 0:
            self.conversation_cooldown -= 1  # Decrease cooldown

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
        # Draw player's collision rectangle for debugging
        pygame.draw.rect(screen, (0, 255, 0), self.collision_rect, 2)  # Green rectangle with 2px border
        self.draw_health_bar(screen)


    def draw_health_bar(self, screen, position=None):
        padding = 20  # Padding from the edges
        font = pygame.font.SysFont('impact', 34)
        health_text = f"Health: {int(self.health)}/99"
        text_surface = font.render(health_text, True, (255, 255, 255))
        text_shadow = font.render(health_text, True, (0, 0, 0))
        
        if position is None:
            # Default: right-align at the top right corner
            text_x = screen.get_width() - padding - text_surface.get_width()
            text_y = padding
        else:
            # Use the custom position as the top-left corner (left-aligned)
            text_x, text_y = position

        # Draw the black outline for the text
        offsets = [(-2, -2), (-2, 0), (-2, 2),
                (0, -2),           (0, 2),
                (2, -2),  (2, 0),  (2, 2)]
        for dx, dy in offsets:
            screen.blit(text_shadow, (text_x + dx, text_y + dy))
        
        # Draw the main white text
        screen.blit(text_surface, (text_x, text_y))

    def heal(self):
        if self.heals_used < 2:  # Allow healing only if less than 2 heals have been used
            self.health = 99  # Restore health to full
            self.heals_used += 1  # Increment the heal counter
            print(f"Healed to full health. Heals used: {self.heals_used}")
        else:
            print("No heals left.")

    def decrease_health(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
            self.alive = False
        self.damage_sound.play()

    def increase_health(self, amount):
        self.health += amount
        if self.health > 99:
            self.health = 99

    def is_alive(self):
        return self.alive