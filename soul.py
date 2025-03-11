import pygame

class Soul:
    def __init__(self, arena_rect, soul_frames):
        self.arena_rect = arena_rect
        self.soul_frames = soul_frames
        self.current_frame = 0
        self.soul_pos = [arena_rect.centerx, arena_rect.centery]
        self.frame_timer = pygame.time.get_ticks()
        # Offset for drawing only; e.g., (0, -40) moves the sprite up by 40 pixels.
        self.sprite_offset = (0, -10)
        self.soul_collision_rect = self.get_collision_rect()
        self.is_being_pushed = False  # Flag to indicate if the player is being pushed

    def get_collision_rect(self):
        soul_frame = self.soul_frames[self.current_frame]
        # Do not apply the offset here!
        soul_rect = soul_frame.get_rect(center=(int(self.soul_pos[0]), int(self.soul_pos[1])))
        return soul_rect.inflate(-70, -70)  # Use your desired inflate values

    def update(self):
        if pygame.time.get_ticks() - self.frame_timer > 100:  # Change frame every 100ms
            self.current_frame = (self.current_frame + 1) % len(self.soul_frames)
            self.frame_timer = pygame.time.get_ticks()
        self.soul_collision_rect = self.get_collision_rect()

    def draw(self, screen):
        soul_frame = self.soul_frames[self.current_frame]
        # Apply the offset only when drawing the sprite.
        soul_rect = soul_frame.get_rect(
            center=(int(self.soul_pos[0] + self.sprite_offset[0]),
                    int(self.soul_pos[1] + self.sprite_offset[1]))
        )
        screen.blit(soul_frame, soul_rect.topleft)
        # Draw the collision rect for debugging (the green rectangle)
        pygame.draw.rect(screen, (0, 255, 0), self.soul_collision_rect, 2)

    def move(self, keys):
        if not self.is_being_pushed:  # Prevent movement if being pushed
            if keys[pygame.K_LEFT]:
                self.soul_pos[0] -= 5
            if keys[pygame.K_RIGHT]:
                self.soul_pos[0] += 5
            if keys[pygame.K_UP]:
                self.soul_pos[1] -= 5
            if keys[pygame.K_DOWN]:
                self.soul_pos[1] += 5
            self.clamp_position()

    def reset_position(self):
        self.soul_pos = [self.arena_rect.centerx, self.arena_rect.centery]
        
    def clamp_position(self):
        # Clamp based on the collision rectangle.
        soul_rect = self.get_collision_rect()
        clamped_rect = soul_rect.clamp(self.arena_rect)
        # Update the soul position (center) accordingly.
        self.soul_pos = [clamped_rect.centerx, clamped_rect.centery]