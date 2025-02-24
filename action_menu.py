import pygame

class ActionMenu:
    def __init__(self, x, y, w, h, options, font_size=40, text_color="white", bg_color="black", border_color="white", total_heals=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.selected_index = 0
        self.font = pygame.font.Font(None, font_size)
        self.text_color = pygame.Color(text_color)
        self.bg_color = pygame.Color(bg_color)
        self.border_color = pygame.Color(border_color)
        self.total_heals = total_heals  # Total available heals
        self.heals_used = 0  # Heals used initially set to 0
    
    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_index]
        return None

    def update(self, heals_used):
        self.heals_used = heals_used  # Update heals_used

    def draw(self, screen):
        # Draw the background and border of the menu
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 4)
        # Evenly space the menu options
        button_width = self.rect.width // len(self.options)
        for i, option in enumerate(self.options):
            btn_rect = pygame.Rect(self.rect.x + i * button_width, self.rect.y, button_width, self.rect.height)
            if i == self.selected_index:
                pygame.draw.rect(screen, (100, 100, 100), btn_rect)  # Highlight selected option
            else:
                pygame.draw.rect(screen, self.bg_color, btn_rect)
            text_surf = self.font.render(option, True, self.text_color)
            text_rect = text_surf.get_rect(center=btn_rect.center)
            screen.blit(text_surf, text_rect)
            
            # Draw yellow border around each button
            pygame.draw.rect(screen, (255, 255, 0), btn_rect, 2)  # Yellow border with 2px width
            
            # Draw heals left next to the "Heal" button
            if option == "Heal":
                heals_left = self.total_heals - self.heals_used  # Calculate heals left
                heals_text = f"{heals_left}"
                heals_surf = self.font.render(heals_text, True, self.text_color)
                heals_rect = heals_surf.get_rect(midleft=(text_rect.right + 10, text_rect.centery))
                screen.blit(heals_surf, heals_rect)