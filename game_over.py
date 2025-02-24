import pygame

class GameOverScreen:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.window_width = window_width
        self.window_height = window_height
        self.font = pygame.font.SysFont('impact', 80)
        self.try_again_font = pygame.font.SysFont('impact', 40)

        self.text = self.font.render("Game Over", True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(window_width // 2, window_height // 2))

        self.try_again_text = self.try_again_font.render("Try Again", True, (255, 255, 255))
        self.try_again_text_rect = self.try_again_text.get_rect(center=(window_width // 2, window_height // 2 + 100))

        self.alpha = 0  # Initial alpha value for fade-in effect
        self.fade_in_speed = 5  # Speed of fade-in effect

    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background

        # Create a copy of the text surfaces with the current alpha value
        text_surface = self.text.copy()
        text_surface.set_alpha(self.alpha)
        try_again_surface = self.try_again_text.copy()
        try_again_surface.set_alpha(self.alpha)

        # Blit the text surfaces onto the screen
        self.screen.blit(text_surface, self.text_rect)
        self.screen.blit(try_again_surface, self.try_again_text_rect)

        # Increase the alpha value for the fade-in effect
        if self.alpha < 255:
            self.alpha += self.fade_in_speed

        pygame.display.flip()

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.try_again_text_rect.collidepoint(mouse_pos):
                return True
        return False