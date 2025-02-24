import pygame
import os
import ctypes
from dialog import DialogBox
from fight_bar import FightBar
from Path import Boss
from player import Player
from soul import Soul
from Path_attack import BossAttack
from game_over import GameOverScreen
from action_menu import ActionMenu

# Get screen size
user32 = ctypes.windll.user32
screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# Window size
window_width, window_height = 900, 700

# Force Pygame to place the window in the center
os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

class Battle:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

        # Arena config
        side_length = min(window_width - 120, window_height - 400)
        x = (window_width - side_length) // 2
        y = (window_height - side_length - 80) // 2
        self.arena_rect = pygame.Rect(x, y, side_length, side_length)
        self.boss = Boss()  # Create an instance of the Boss class
        self.boss_attack = BossAttack(self.boss, self.arena_rect)
        # Create the battle window
        self.screen = pygame.display.set_mode((window_width, window_height), pygame.NOFRAME)
        pygame.display.set_caption("Battle")
        
        self.boss_attack_timer = pygame.time.get_ticks()
        self.boss_attack_interval = 3000  # Boss attacks every 3 seconds
        self.boss_projectiles = []  # List to store boss projectiles

        # Initial state: boss dialogue before the arena
        self.state = "boss_dialog"
        self.boss_dialog = DialogBox(
            x=50,
            y=window_height - 170,
            w=window_width - 100,
            h=170,
            text= ["So that is your nature!",
                   "To fight and kill!",
                   "To seek the easier way!",
                   "...",
                   "The path you've chosen...",
                   "Ha-Ha-Ha!",
                   "Will lead to your end!",
                   ],
            boss_name="Path",       # You can adjust the boss name as needed
            options=["Continue"],   # Single option to proceed
            font_size=50
        )
        # (Optionally) Play the dialogue sound immediately
        self.boss_dialog.text_sound.play()
        self.slash_sound = pygame.mixer.Sound("assets/music/slashing.mp3")
        self.dialog_music = pygame.mixer.Sound("assets/music/goated_music.mp3")
        self.game_over_sound = pygame.mixer.Sound("assets/music/gameover.mp3")
        
        # Load and scale soul sprite frames
        self.soul_sprite_sheet = pygame.image.load("assets/sheets/summonIdle.png").convert_alpha()
        self.soul_frames = self.load_frames(self.soul_sprite_sheet, 4, 1)  # Assuming 4 frames in a single row
        self.soul_frames = [pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2)) 
                            for frame in self.soul_frames]  # Scale frames
        self.soul = Soul(self.arena_rect, self.soul_frames)  # Create an instance of the Soul class
        
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

        # Load the image to overlay
        self.overlay_image = pygame.image.load("assets/sheets/path_idle.png").convert_alpha()
        # Scale the image
        self.overlay_image = pygame.transform.scale(self.overlay_image, (300, 300))  # Adjust the size as needed

        self.slash_image = pygame.image.load("assets/sheets/path_slash.png").convert_alpha()
        self.slash_image = pygame.transform.scale(self.slash_image, (300, 300))
        
        # Load the kill sprite sheet for the slash animation
        self.kill_sprite_sheet = pygame.image.load("assets/sheets/kill.png").convert_alpha()
        self.kill_frames = self.load_slash_frames(self.kill_sprite_sheet)
        # Optionally scale them
        self.kill_frames = [
            pygame.transform.scale(frame, (300, 300))
            for frame in self.kill_frames
        ]
        self.kill_current_frame = 0
        self.kill_frame_timer = pygame.time.get_ticks()
        self.slash_timer = 0  # Timer for the slash animation

        self.action_selected = False
        # Attack animation variables
        self.attack_timer = 0
        self.soul_appeared = False

        self.phase_completed = False

        self.fight_bar = FightBar(100, window_height - 200, window_width - 200, 20)
        self.reset_attack_sequence()

        self.game_over_screen = GameOverScreen(self.screen, window_width, window_height)  # Create an instance of GameOverScreen

    def reset_attack_sequence(self):
        """Resets the attack sequence for the boss."""
        self.boss_attack.reset_attacks()
        self.action_selected = False
        self.soul.reset_position()

    def reset_game(self):
        """Resets the game state to the initial state."""
        self.player.reset()  # Reset player stats and position
        self.boss = Boss()  # Recreate the boss instance to reset its state
        self.phase_completed = False
        self.state = "boss_dialog"
        self.boss_dialog.reset()  # Reset the boss dialog
        self.soul_appeared = False
        self.action_selected = False
        self.fight_processed = False
        self.kill_current_frame = 0
        self.attack_timer = 0
        self.slash_timer = 0
        self.boss_attack_timer = pygame.time.get_ticks()
        self.boss_projectiles.clear()
        self.game_over_sound.stop()
        self.boss_attack = BossAttack(self.boss, self.arena_rect)  # Reset boss attacks
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

    def load_slash_frames(self, sprite_sheet):
        """
        Extracts 5 frames from the top row, then 4 frames from the bottom row,
        returning a total of 9 frames.
        """
        frames = []
        sheet_width, sheet_height = sprite_sheet.get_size()
        
        # Each row is half the total height
        row_height = sheet_height // 2
        
        # 1) Extract 5 frames from the top row
        top_row_columns = 5
        top_frame_width = sheet_width // top_row_columns  # This divides the total width into 5 equal parts
        
        for col in range(top_row_columns):
            x = col * top_frame_width
            y = 0
            frame = sprite_sheet.subsurface((x, y, top_frame_width, row_height))
            frames.append(frame)
        
        # 2) Extract 4 frames from the bottom row
        bottom_row_columns = 4
        bottom_frame_width = sheet_width // bottom_row_columns  # Divides the total width into 4 equal parts
        
        for col in range(bottom_row_columns):
            x = col * bottom_frame_width
            y = row_height
            frame = sprite_sheet.subsurface((x, y, bottom_frame_width, row_height))
            frames.append(frame)

        return frames

    def process_event(self, event):
        if self.state == "boss_dialog":
            self.handle_boss_dialog_event(event)
        elif self.state == "fight_arena":
            self.handle_fight_arena_event(event)
        elif self.state == "fight":
            self.handle_fight_event(event)
        elif self.state == "choose_action":
            self.handle_choose_action_event(event)
        elif self.state == "game_over":
            self.handle_game_over_event(event)

    
    def update_enemy_attacks(self):
        self.player.health = self.boss_attack.update(self.soul, self.player.health)
        if self.player.health <= 0:
            self.player.health = 0
            self.player.alive = False
            print(f"[DEBUG] All attacks completed, state set to choose_action, action_selected reset to False")
            
    def handle_boss_dialog_event(self, event):
        choice = self.boss_dialog.process_event(event)
        if choice is not None:
            self.state = "boss_attack"
            self.attack_timer = pygame.time.get_ticks()  # Start attack animation

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
            self.state = "fight_arena"
            self.action_selected = True
              # Reset the flag after processing the fight

    def handle_player_action(self, action):
        if action == "Fight":
            self.state = "fight"
            self.fight_bar.start()
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
                
    def update(self, event):
        if self.state == "boss_dialog":
            self.boss_dialog.update()
            pygame.mixer.music.stop()
        elif self.state == "boss_attack":
            elapsed_time = pygame.time.get_ticks() - self.attack_timer
            if elapsed_time > 1000 and not self.soul_appeared:  # 1 second delay
                self.soul_appeared = True
            if elapsed_time > 1200:  # 2 seconds total
                self.state = "slash_kill"
                self.kill_current_frame = 0  # Start kill anim at frame 0
                self.slash_timer = pygame.time.get_ticks()
        elif self.state == "slash_kill":
            elapsed_time = pygame.time.get_ticks() - self.slash_timer
            self.dialog_music.stop()
            if not pygame.mixer.get_busy():
                self.slash_sound.play()
            if elapsed_time > 100:  # Change frame every 100ms
                self.kill_current_frame = (self.kill_current_frame + 1) % len(self.kill_frames)
                self.slash_timer = pygame.time.get_ticks()
            if self.kill_current_frame == len(self.kill_frames) - 1:
                self.state = "fight_arena"
                self.action_selected = False  # Reset the flag when entering the fight arena
                print(f"[DEBUG] Slash kill animation completed, state set to fight_arena, action_selected reset to False")
        elif self.state == "fight_arena":
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("assets/music/path_music.mp3")
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1)
            # Update the soul animation frame
            self.soul.update()

            if self.action_selected:  # Only allow movement if an action has been selected
                keys = pygame.key.get_pressed()
                self.soul.move(keys)
                # Update enemy attacks
                self.update_enemy_attacks()

            # Check if all attacks are completed
            if self.boss_attack.all_attacks_completed and not self.phase_completed:
                self.phase_completed = True
                self.state = "choose_action"
                self.reset_attack_sequence()  # Reset the attack sequence
                self.action_selected = False  # Reset the flag when choosing an action
                print(f"[DEBUG] All attacks completed, state set to choose_action, action_selected reset to False")
        elif self.state == "fight":
            self.fight_bar.update()
            if not self.fight_bar.active:
                damage = self.fight_bar.stop()
                print(f"Player deals {damage} damage!")
                self.boss.health -= damage
                if self.boss.health < 0:
                    self.boss.health = 0
                self.state = "fight_arena"
                self.action_selected = False  # Reset the flag after processing the fight
        elif self.state == "choose_action":
            if self.phase_completed:
                self.boss_attack.proceed_to_next_phase()
                self.phase_completed = False
                self.state = "fight_arena"
                print(f"[DEBUG] Phase completed, proceeding to next phase, action_selected reset to False")
        if not self.player.is_alive():
            if self.state != "game_over":
                self.state = "game_over"
                pygame.mixer.music.stop()  # Stop the music when the game is over
                self.game_over_sound.play()  # Play game over sound once
        self.action_menu.update(self.player.heals_used)  # Update heals_used

    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.state == "boss_dialog":
            self.boss_dialog.draw(self.screen)
            overlay_x = (window_width - self.overlay_image.get_width()) // 2
            overlay_y = (window_height - self.overlay_image.get_height()) // 2
            self.screen.blit(self.overlay_image, (overlay_x, overlay_y))  # Center the image
        elif self.state == "boss_attack":
            slash_x, slash_y = (window_width - 200) // 2, (window_height - 200) // 2
            self.screen.blit(self.slash_image, (slash_x, slash_y))
        elif self.state == "slash_kill":
            kill_frame = self.kill_frames[self.kill_current_frame]
            kill_x = (window_width - kill_frame.get_width()) // 2
            kill_y = (window_height - kill_frame.get_height()) // 2
            self.screen.blit(kill_frame, (kill_x, kill_y))
        elif self.state == "fight_arena":
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

            # Draw the boss projectiles
            self.boss_attack.draw(self.screen)
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
        elif self.state == "game_over":
            self.game_over_screen.draw()
        pygame.display.flip()