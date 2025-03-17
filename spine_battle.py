import pygame
import os
import ctypes
from dialog import DialogBox
from fight_bar import FightBar
from player import Player
from soul import Soul
from game_over import GameOverScreen
from action_menu import ActionMenu
from Spine import Spine
from Spine_attack import SpineAttack

user32 = ctypes.windll.user32
screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# Window size
window_width, window_height = 900, 700

# Force Pygame to place the window in the center
os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()


class Spine_fight:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

        # Arena config
        side_length = min(window_width - 120, window_height - 400)
        x = (window_width - side_length) // 2
        y = (window_height - side_length - 80) // 2
        self.arena_rect = pygame.Rect(x, y, side_length, side_length)
        self.boss = Spine()
        self.boss_attack = SpineAttack(self.boss, self.arena_rect)
        self.screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)
        pygame.display.set_caption("Battle")

        # Load and scale soul sprite frames
        self.soul_sprite_sheet = pygame.image.load("assets/sheets/summonIdle.png").convert_alpha()
        self.soul_frames = self.load_frames(self.soul_sprite_sheet, 4, 1)  # Assuming 4 frames in a single row
        self.soul_frames = [pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2)) 
                            for frame in self.soul_frames]  # Scale frames
        self.soul = Soul(self.arena_rect, self.soul_frames)  # Create an instance of the Soul class

        self.state = "fight_arena"
         # Create the action menu (which remains visible at the bottom in the arena)
        menu_width = 350  
        menu_height = 80  
        self.action_menu = ActionMenu(
            (window_width - menu_width) // 2,  # Centered horizontally
            window_height - menu_height - 20,  # Near the bottom
            menu_width,
            menu_height,
            ["Fight", "Heal"],
            total_heals=2  # Set the total available heals
        )

        self.fight_bar = FightBar(100, window_height - 200, window_width - 200, 20)
        self.reset_attack_sequence()

        self.game_over_screen = GameOverScreen(self.screen, window_width, window_height)  # Create an instance of GameOverScreen

        self.fight_disabled = False

        self.music_started = False
        
    def start_music(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load("assets/music/K.O. SPINE.mp3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        self.music_started = True  # Set the flag to indicate the music has been started

    def reset_attack_sequence(self):
        """Resets the attack sequence for the boss."""
        self.action_selected = False
        self.soul.reset_position()


    def load_frames(self, sprite_sheet, num_frames, num_rows):
        frames = []
        sheet_width, sheet_height = sprite_sheet.get_size()
        frame_width = sheet_width // num_frames
        frame_height = sheet_height // num_rows
        for row in range(num_rows):
            for col in range(num_frames):
                frame = sprite_sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                frames.append(frame)
        return frames
    
    def process_event(self, event):
        if self.state == "fight_arena":
            self.handle_fight_arena_event(event)
        elif self.state == "fight":
            self.handle_fight_event(event)
        elif self.state == "choose_action":
            self.handle_choose_action_event(event)
        elif self.state == "game_over":
            self.handle_game_over_event(event)

    def update(self, event):
        if self.state == "fight_arena":
            if not self.music_started:
                self.start_music()
            # Update the soul animation frame
            self.soul.update()

            if self.action_selected:  # Only allow movement if an action has been selected
                keys = pygame.key.get_pressed()
                self.soul.move(keys)
                # Update enemy attacks
                self.update_enemy_attacks()
        elif self.state == "fight":
            self.fight_bar.update()
            if not self.fight_bar.active:
                damage = self.fight_bar.stop()
                print(f"Player deals {damage} damage!")
                self.boss.health -= damage
                if self.boss.health <= 0:
                    self.boss.health = 0
                    self.state = "boss_defeat"
                    self.defeat_animation_timer = pygame.time.get_ticks()  # Start the defeat animation timer
                    self.defeat_animation_frame = 0  # Start the defeat animation at frame 0
                    print(f"[DEBUG] Boss defeated, state set to boss_defeat")
                else:
                    self.state = "fight_arena"
                    self.action_selected = False  # Reset the flag after processing the fight
        elif self.state == "choose_action":
            if self.phase_completed:
                self.boss_attack.proceed_to_next_phase()
                self.phase_completed = False
                self.state = "fight_arena"
                print(f"[DEBUG] Phase completed, proceeding to next phase, action_selected reset to False")
        elif self.state == "boss_defeat":
            elapsed_time = pygame.time.get_ticks() - self.defeat_animation_timer
            if elapsed_time > 100:  # Change frame every 100ms
                if not pygame.mixer.get_busy():
                    self.slash_sound.play()
                self.defeat_animation_frame += 1
                self.defeat_animation_timer = pygame.time.get_ticks()
            if self.defeat_animation_frame >= len(self.kill_frames):
                self.state = "victory"  # Transition to game over or victory screen
                print(f"[DEBUG] Boss defeat animation completed, state set to victory")
        if not self.player.is_alive():
            if self.state != "game_over":
                self.state = "game_over"
                pygame.mixer.music.stop()  # Stop the music when the game is over
                self.game_over_sound.play()  # Play game over sound once
        self.action_menu.update(self.player.heals_used)  # Update heals_used

    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background

        if self.state == "fight_arena":
            pygame.draw.rect(self.screen, (30, 30, 30), self.arena_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), self.arena_rect, 4)

            # Draw the soul
            self.soul.draw(self.screen)

            # Draw UI elements
            self.action_menu.draw(self.screen)
            padding = 20
            health_bar_position = (padding, window_height - padding - 34)
            self.player.draw_health_bar(self.screen, position=health_bar_position)

            boss_health_bar_position = (window_width // 2 - 100, window_height - 150)
            self.boss.draw_health_bar(self.screen, position=boss_health_bar_position)
            self.draw_x_fight_button()

        elif self.state == "fight":
            self.fight_bar.draw(self.screen)
        elif self.state == "choose_action":
            # Draw the action menu and health bars when choosing an action
            self.action_menu.draw(self.screen)
            padding = 20
            health_bar_position = (padding, window_height - padding - 34)
            self.player.draw_health_bar(self.screen, position=health_bar_position)

            boss_health_bar_position = (window_width // 2 - 100, window_height - 150)
            self.boss.draw_health_bar(self.screen, position=boss_health_bar_position)
        elif self.state == "boss_defeat":
            # Draw the boss defeat animation
            if self.defeat_animation_frame < len(self.kill_frames):
                defeat_frame = self.kill_frames[self.defeat_animation_frame]
                defeat_x = (window_width - defeat_frame.get_width()) // 2
                defeat_y = (window_height - defeat_frame.get_height()) // 2
                self.screen.blit(defeat_frame, (defeat_x, defeat_y))
        elif self.state == "game_over":
            self.game_over_screen.draw()
        pygame.display.flip()


#HADLES

    def handle_fight_arena_event(self, event):
            if not self.action_selected:  # Only process action menu events if no action has been selected
                action = self.action_menu.process_event(event)
                if action:
                    self.handle_player_action(action)
                    self.action_selected = True  # Set the flag to indicate an action has been selected

    def handle_fight_event(self, event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN 
                and not getattr(self, 'fight_processed', False)):
            self.fight_processed = True  # Prevent further processing until reset
            damage = self.fight_bar.stop()
            print(f"Player deals {damage} damage!")
            self.boss.health -= damage
            if self.boss.health < 0:
                self.boss.health = 0
                self.state = "boss_defeat"
                self.defeat_animation_timer = pygame.time.get_ticks()  # Start the defeat animation timer
                self.defeat_animation_frame = 0  # Start the defeat animation at frame 0
                print(f"[DEBUG] Boss defeated, state set to boss_defeat")
            else:
                self.state = "fight_arena"
                self.action_selected = True
              # Reset the flag after processing the fight

    def handle_player_action(self, action):
        if action == "Fight":
            if not self.fight_disabled:
                self.fight_disabled = True  # Disable the "Fight" button
                self.state = "fight_arena"
                self.fight_processed = False  # Reset for each new fight sequence
                print(f"[DEBUG] Player attack initiated, state set to fight")
        elif action == "Heal":
            self.player_act()

    def player_attack(self):
        self.state = "fight"
        self.fight_bar.start()
        self.fight_processed = False  # Reset for each new fight sequence
        print(f"[DEBUG] Player attack initiated, state set to fight")

    def player_act(self):
        if self.player.heals_used < 2:
            self.player.heal()
            self.state = "fight_arena"  # Transition back after healing
            self.action_selected = False  # Reset the flag after healing
            print(f"[DEBUG] Player healed, state set to fight_arena, action_selected reset to False")
        else:
            print("No heals left.")
            # Automatically switch to a fight action since healing isn’t available
            self.player_attack()
            self.action_selected = False
            print(f"[DEBUG] No heals left, switching to attack, action_selected reset to False")

    def handle_choose_action_event(self, event):
        if not self.action_selected:  # Only process action menu events if no action has been selected
            action = self.action_menu.process_event(event)
            if action:
                self.handle_player_action(action)
                self.action_selected = True  # Set the flag to indicate an action has been selected
                print(f"[DEBUG] Action selected: {action}, action_selected set to True")


    def handle_game_over_event(self, event):
        if self.game_over_screen.process_event(event):
            self.reset_game()  # Reset the game state
            return True  # Indicate that the game should restart
        
    def update_enemy_attacks(self):
        #self.player.health = self.boss_attack.update(self.soul, self.player.health)
        if self.player.health <= 0:
            self.player.health = 0
            self.player.alive = False


    def draw_x_fight_button(self):
        if self.fight_disabled:
            # Get the position and size of the "Fight" button
            fight_button_rect = self.action_menu.get_button_rect("Fight")
            
            # Draw a red "X" on top of the "Fight" button
            pygame.draw.line(self.screen, (255, 0, 0), fight_button_rect.topleft, fight_button_rect.bottomright, 5)
            pygame.draw.line(self.screen, (255, 0, 0), fight_button_rect.topright, fight_button_rect.bottomleft, 5)