import pygame
import os
import ctypes
from settings import *
from player import Player
from Path import Boss
from pytmx.util_pygame import load_pygame
import pytmx
from dialog import DialogBox
from battle import Battle
from zazo import Zazo
from map_loader import load_map
from Spine import Spine 
from loading_screen import show_loading_screen
from spine_battle import Spine_fight
from main_menu import main_menu
# Initialize Pygame
screen = initialize_game()

# Load and play background music
def play_chill_music():
    pygame.mixer.music.load("assets/music/rise_of_a_hero.wav") 
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)  # Loop

def spine_intro_music():
    pygame.mixer.music.load("assets/music/Spine intro.mp3") 
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)  # Loop

# Show the main menu and wait for the player's choice
choice = main_menu()
if choice == 'start_game':
    pygame.mixer.music.stop()
    show_loading_screen("The Valley of the End")
    play_chill_music()

    # Load Maps
    tmx_data_one = load_pygame(??)
    tmx_data_two = load_pygame(??)

    # Initial Map
    tmx_data = tmx_data_one

    game_state = "playing"
    if game_state == 'playing':
        player = Player()
        boss = Boss()
        zazo = Zazo()
        # Set the initial position of the player
        player.rect.topleft = (560, 740)  # Set the player's initial position
        player.collision_rect.topleft = player.rect.topleft  # Update collision rect position

        
    scale_x = WIDTH / (tmx_data.width * tmx_data.tilewidth)
    scale_y = HEIGHT / (tmx_data.height * tmx_data.tileheight)
    running = True
    clock = pygame.time.Clock()
    conversation = None
    battle = None
    boss_defeated = True
    transition_cooldown = 0  # Cooldown period to prevent immediate re-collision
    player_choice_for_path = "Fight"
    player_choice_for_spine = None
    spine = None

    obstacles, special_areas = load_map(tmx_data, WIDTH, HEIGHT)

    while running:
        screen.fill(BLACK)

        for layer in tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_image = tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        tile_image = pygame.transform.scale(tile_image, (int(tmx_data.tilewidth * scale_x), int(tmx_data.tileheight * scale_y)))
                        screen.blit(tile_image, (x * tmx_data.tilewidth * scale_x, y * tmx_data.tileheight * scale_y))

        for layer in tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    if obj.gid:
                        obj_image = tmx_data.get_tile_image_by_gid(obj.gid)
                        if obj_image:
                            obj_image = pygame.transform.scale(obj_image, (int(obj.width * scale_x), int(obj.height * scale_y)))
                            screen.blit(obj_image, (obj.x * scale_x, obj.y * scale_y))

        for obstacle in obstacles:
            pygame.draw.rect(screen, (255, 0, 0), obstacle, 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif game_state == "conversation":
                choice = conversation.process_event(event)
                if choice is not None:
                    if choice == "Fight" and conversation.boss_name == "Path":
                        game_state = "battle"
                        player_choice_for_path = "Fight"  # Store the player's choice
                        battle = Battle(player, boss, player_choice_for_path)
                    elif choice == "Fight" and conversation.boss_name == "Spine":
                        game_state = "battle"
                        player_choice_for_spine = "Fight"  # Store the player's choice
                        battle = Spine_fight(player, spine)
                    elif choice == "Accept" and conversation.boss_name == "Zazo":
                        player.decrease_health(1)
                        game_state = "playing"
                        player.in_conversation = False  # Reset the flag
                        player.conversation_cooldown = 450  # Add cooldown
                        conversation = None
                    elif choice == "Go Back" and conversation.boss_name == "Path":
                        player.decrease_health(1)
                        game_state = "battle"
                        player_choice_for_path = "Go Back"  # Store the player's choice
                        battle = Battle(player, boss if conversation.boss_name == "Path" else zazo, player_choice_for_path)
                    elif choice == "Go Back" and conversation.boss_name == "Spine":
                        game_state = "second_part"
                        player.in_conversation = False  # Reset the flag
                        player.conversation_cooldown = 450  # Add cooldown
                        spine = Spine(player_choice_for_spine="Go Back")  # Reinitialize Spine with "Go Back" choice
                        conversation = None
                    elif choice == "Go Back":
                        game_state = "playing"
                        player.in_conversation = False  # Reset the flag
                        player.conversation_cooldown = 450  # Add cooldown
                        conversation = None
            elif game_state == "battle":
                battle.process_event(event)

        if game_state in ["playing", "second_part"]:
            keys = pygame.key.get_pressed()
            player.update(keys, obstacles)
            if game_state == "playing" and not boss_defeated:
                boss.update()
            if tmx_data == tmx_data_one:
                zazo.update()
            
        
            if not player.in_conversation and player.conversation_cooldown == 0:
                if player.collision_rect.colliderect(boss.rect) and game_state == "playing" and not boss_defeated:
                    game_state = "conversation"
                    player.in_conversation = True  # Set the flag
                    dialogue_text = boss.dialogue
                    options = ["Fight", "Go Back"]  # Custom options for Path
                    conversation = DialogBox(0, HEIGHT - 250, WIDTH, 250, dialogue_text, boss_name="Path", options=options)
                    conversation.text_sound.play() 
                elif player.collision_rect.colliderect(zazo.rect):
                    game_state = "conversation"
                    player.in_conversation = True  # Set the flag
                    dialogue_text = zazo.dialogue
                    options = ["Accept", "Go Back"]  # Custom options for Zazo
                    conversation = DialogBox(0, HEIGHT - 250, WIDTH, 250, dialogue_text, boss_name="Zazo", options=options)
                for entrance in special_areas:
                    if entrance in special_areas and boss_defeated:
                        if player.collision_rect.colliderect(entrance) and transition_cooldown == 0:
                            pygame.mixer.music.stop()
                            if tmx_data == tmx_data_one:
                                show_loading_screen("The Judgment Hall")
                                tmx_data = tmx_data_two
                                player.rect.topleft = (600, 740)  # Set the player's position in the second map
                                spine_intro_music()
                            elif tmx_data == tmx_data_two:
                                show_loading_screen("The Valley of the End")
                                tmx_data = tmx_data_one
                                player.rect.topleft = (573, 105)  # Set the player's position in the first map
                                play_chill_music()  # Play Spine intro music
                            player.collision_rect.topleft = player.rect.topleft  # Update collision rect position
                            obstacles, special_areas = load_map(tmx_data, WIDTH, HEIGHT)
                            transition_cooldown = 60  # Set cooldown period to prevent immediate re-collision
            # SPINE
            if tmx_data == tmx_data_two and boss_defeated and player_choice_for_path == "Fight":
                if spine is None:  # Initialize Spine only once
                    spine = Spine()

                spine.update()

                if player.collision_rect.colliderect(spine.rect):
                    game_state = "conversation"
                    player.in_conversation = True
                    dialogue_text = spine.dialogue
                    options = ["Fight", "Go Back"]  # Options for Spine
                    conversation = DialogBox(0, HEIGHT - 250, WIDTH, 250, dialogue_text, boss_name="Spine", options=options)

                # Draw Spine if it exists
                if spine:
                    spine.draw(screen)

        elif game_state == "battle":
            battle.update(event)
            if battle.state == "victory":
                game_state = "second_part"  # Transition back to the main game loop
                player.in_conversation = False  # Reset the flag
                player.conversation_cooldown = 200  # Add cooldown
                battle = None  # Clear the battle instance
                boss_defeated = True  # Set the boss defeated flag
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                pygame.mixer.music.stop()
                play_chill_music()

        if game_state in ["playing", "second_part", "conversation"]:
            if game_state != "second_part" and not boss_defeated:
                boss.draw(screen)
            if tmx_data == tmx_data_one:
                zazo.draw(screen)
            player.draw(screen)

        if game_state == "conversation":
            conversation.update()
            conversation.draw(screen)
            if spine and tmx_data == tmx_data_two:
                spine.draw(screen)
        elif game_state == "battle":
            battle.draw()

        pygame.display.flip()
        clock.tick(60)

        if transition_cooldown > 0:
            transition_cooldown -= 1

    pygame.quit()
    pygame.mixer.quit()
