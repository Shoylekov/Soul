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
        # Draw the fight bar
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        # Draw the indicator
        indicator_rect = pygame.Rect(self.indicator_pos - 5, self.rect.top - 10, 10, self.rect.height + 20)
        pygame.draw.rect(screen, (255, 0, 0), indicator_rect)