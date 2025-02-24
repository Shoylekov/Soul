import pygame

class DialogBox:
    def __init__(self, x, y, w, h, text, boss_name="Path", options=None, font_size=50, 
                 text_color="white", bg_color="black", border_color="white"):
        # If text is provided as a list, join the lines with newlines.
        if isinstance(text, list):
            self.text = "\n".join(text)
        else:
            self.text = text

        self.rect = pygame.Rect(x, y, w, h)
        self.surf = pygame.Surface((w, h))
        self.surf.set_alpha(220)

        self.boss_name = boss_name

        self.font = pygame.font.Font(None, font_size)
        self.text_color = pygame.Color(text_color)
        self.bg_color = pygame.Color(bg_color)
        self.border_color = pygame.Color(border_color)

        # Process text into lines (one line at a time)
        self.lines = self.text.splitlines()
        self.total_lines = len(self.lines)
        self.current_line_index = 0
        self.current_char_index = 0

        self.state = "typing"
        
        self.char_delay = 35
        self.last_update_time = pygame.time.get_ticks()

        button_width = 150
        button_height = 50
        margin = 20

        self.options = options if options else ["Fight", "Go Back"]
        self.buttons = {}
        for i, option in enumerate(self.options):
            x_pos = w - margin - (button_width + margin) * (len(self.options) - i)
            y_pos = h - button_height - margin
            self.buttons[option] = pygame.Rect(x_pos, y_pos, button_width, button_height)

        self.selected_button = self.options[0]
        self.text_sound = pygame.mixer.Sound("assets/music/popup.mp3")

    def reset(self):
        """Resets the dialog box state."""
        self.current_line_index = 0
        self.current_char_index = 0
        self.state = "typing"
        self.text_sound.play()

    def update(self):
        """In typing mode, reveal the current line letter by letter."""
        if self.state == "typing":
            now = pygame.time.get_ticks()
            if now - self.last_update_time >= self.char_delay:
                self.current_char_index += 1
                current_line = self.lines[self.current_line_index]
                if self.current_char_index > len(current_line):
                    self.current_char_index = len(current_line)
                self.last_update_time = now

    def draw(self, screen):
        # Clear dialogue surface
        self.surf.fill(self.bg_color)
        pygame.draw.rect(self.surf, self.border_color, self.surf.get_rect(), 4)
        
        # Draw boss name at top left
        boss_name_surf = self.font.render(self.boss_name, True, self.text_color)
        self.surf.blit(boss_name_surf, (10, 10))
        
        # Determine where to draw the current line (we only show one line at a time)
        # For example, center it vertically below the boss name.
        y_offset = 70
        if self.current_line_index < self.total_lines:
            current_line = self.lines[self.current_line_index]
            # In typing mode, show only part of the line; in choice mode, show full line.
            if self.state == "typing":
                to_draw = current_line[:self.current_char_index]
            else:
                to_draw = current_line
            line_surf = self.font.render(to_draw, True, self.text_color)
            self.surf.blit(line_surf, (10, y_offset))
        
        # If in choice mode, draw buttons
        if self.state == "choice":
            for label, rect in self.buttons.items():
                # Button background (gray)
                pygame.draw.rect(self.surf, (100, 100, 100), rect)
                # Highlight the selected button
                if label == self.selected_button:
                    pygame.draw.rect(self.surf, (255, 255, 0), rect, 4)
                else:
                    pygame.draw.rect(self.surf, self.border_color, rect, 2)
                # Render button label centered
                btn_font = pygame.font.Font(None, 40)
                btn_surf = btn_font.render(label, True, self.text_color)
                btn_rect = btn_surf.get_rect(center=rect.center)
                self.surf.blit(btn_surf, btn_rect)
        
        # Blit dialogue box onto screen
        screen.blit(self.surf, self.rect)

    def process_event(self, event):
        """
        Processes key events.
        In typing mode:
            - Enter: if current line not complete, reveal full line; if complete, clear it and advance to next line.
        In choice mode:
            - Left/Right: toggle selection.
            - Enter: confirm selection and return it.
        Returns the chosen button label when confirmed in choice mode, otherwise None.
        """
        if event.type == pygame.KEYDOWN:
            if self.state == "typing":
                if event.key == pygame.K_RETURN:
                    current_line = self.lines[self.current_line_index]
                    # If current line is not fully revealed, reveal it instantly.
                    if self.current_char_index < len(current_line):
                        self.current_char_index = len(current_line)
                    else:
                        # Current line is complete; clear it (by advancing) so it no longer appears.
                        if self.current_line_index < self.total_lines - 1:
                            self.current_line_index += 1
                            self.current_char_index = 0
                            self.text_sound.play()  # Play the text sound effect
                        else:
                            # Last line completed; switch to choice mode.
                            self.state = "choice"
            elif self.state == "choice":
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    # Toggle selection
                    current_index = self.options.index(self.selected_button)
                    if event.key == pygame.K_LEFT:
                        current_index = (current_index - 1) % len(self.options)
                    elif event.key == pygame.K_RIGHT:
                        current_index = (current_index + 1) % len(self.options)
                    self.selected_button = self.options[current_index]
                elif event.key == pygame.K_RETURN:
                    return self.selected_button
        return None

    def handle_button_click(self, pos):
        """
        Given a global mouse position, convert to local coordinates and check button collisions.
        Returns the label of the button clicked, or None.
        """
        local_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)
        for label, rect in self.buttons.items():
            if rect.collidepoint(local_pos):
                return label
        return None