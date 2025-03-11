import pygame

class FightBar:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.indicator_pos = self.rect.left
        self.indicator_speed = 10
        self.active = False
        self.bar_sound = pygame.mixer.Sound("assets/music/glitch.mp3")  # Load the sound in the constructor

    def start(self):
        self.active = True
        self.indicator_pos = self.rect.left

    def stop(self):
        self.active = False
        hit_position = self.indicator_pos
        bar_center = self.rect.centerx
        damage = max(0, 100 - abs(hit_position - bar_center) // 2)  # Calculate damage based on hit position
        self.bar_sound.play()  # Play the sound when the bar stops
        return damage

    def update(self):
        if self.active:
            self.indicator_pos += self.indicator_speed
            if self.indicator_pos > self.rect.right or self.indicator_pos < self.rect.left:
                self.indicator_speed = -self.indicator_speed

    def draw(self, screen):
        shadow_offset = 4
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 120), shadow_surf.get_rect(), border_radius=10)
        screen.blit(shadow_surf, (self.rect.x + shadow_offset, self.rect.y + shadow_offset))

        # ---------------------------
        gradient_surf = pygame.Surface((self.rect.width, self.rect.height))
        screen.blit(gradient_surf, self.rect.topleft)
        
        # ---------------------------
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3, border_radius=10)
        
        # ---------------------------
        center_x = self.rect.centerx
        # Center line (green)
        pygame.draw.line(screen, (0, 255, 0), (center_x, self.rect.top), (center_x, self.rect.bottom), 3)
        # Optimal hit zone (yellow lines)
        area_width = 20
        pygame.draw.line(screen, (255, 255, 0), (center_x - area_width, self.rect.top), (center_x - area_width, self.rect.bottom), 2)
        pygame.draw.line(screen, (255, 255, 0), (center_x + area_width, self.rect.top), (center_x + area_width, self.rect.bottom), 2)
        
        # ---------------------------
        indicator_width = 10
        indicator_height = self.rect.height + 20
        indicator_rect = pygame.Rect(self.indicator_pos - indicator_width // 2, self.rect.top - 10, indicator_width, indicator_height)
        
        # Indicator drop shadow
        indicator_shadow_surf = pygame.Surface((indicator_rect.width, indicator_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(indicator_shadow_surf, (0, 0, 0, 120), indicator_shadow_surf.get_rect(), border_radius=5)
        screen.blit(indicator_shadow_surf, (indicator_rect.x + 3, indicator_rect.y + 3))
        
        # Indicator glow effect
        glow_rect = indicator_rect.inflate(10, 10)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 100, 100, 120), glow_surf.get_rect(), border_radius=5)
        screen.blit(glow_surf, glow_rect.topleft)
        
        # Main indicator
        pygame.draw.rect(screen, (255, 0, 0), indicator_rect, border_radius=5)
