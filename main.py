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

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Center the Pygame window on the screen
user32 = ctypes.windll.user32
screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{(screen_width - WIDTH) // 2},{(screen_height - HEIGHT) // 2}"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Soul!")

# Load and play background music
pygame.mixer.music.load("assets/music/rise_of_a_hero.wav")  # Replace with the path to your music file
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)  # Loop

# Load Map
tmx_data = load_pygame("lvl_one.tmx")
object_layer = tmx_data.get_layer_by_name('Objects')

scale_x = WIDTH / (tmx_data.width * tmx_data.tilewidth)
scale_y = HEIGHT / (tmx_data.height * tmx_data.tileheight)

player = Player()
boss = Boss()
zazo = Zazo()

obstacles = []
for layer in tmx_data.visible_layers:
    if isinstance(layer, pytmx.TiledObjectGroup):
        for obj in layer:
            if obj.gid:
                obj_rect = pygame.Rect(obj.x * scale_x, obj.y * scale_y, obj.width * scale_x, obj.height * scale_y)
                if obj.name and "tree" in obj.name.lower():
                    obj_rect.width *= 0.5
                    obj_rect.height *= 0.4
                    obj_rect.x += (obj.width * scale_x - obj_rect.width) / 2
                    obj_rect.y += (obj.height * scale_y - obj_rect.height) / 2
                obstacles.append(obj_rect)
    elif isinstance(layer, pytmx.TiledTileLayer) and layer.name == "Fences":
        for x, y, gid in layer:
            if gid:
                tile_rect = pygame.Rect(
                    x * tmx_data.tilewidth * scale_x, 
                    y * tmx_data.tileheight * scale_y, 
                    tmx_data.tilewidth * scale_x, 
                    tmx_data.tileheight * scale_y
                )
                tile_rect.width *= 0.5
                tile_rect.height *= 0.9
                tile_rect.x += (tmx_data.tilewidth * scale_x - tile_rect.width) / 2
                tile_rect.y += (tmx_data.tileheight * scale_y - tile_rect.height) / 2
                obstacles.append(tile_rect)

running = True
clock = pygame.time.Clock()
game_state = "playing"
conversation = None
battle = None

while running:
    screen.fill(WHITE)

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
                if choice == "Fight":
                    game_state = "battle"
                    battle = Battle(player, boss if conversation.boss_name == "Path" else zazo)
                elif choice == "Go Back":
                    game_state = "playing"
                    player.in_conversation = False  # Reset the flag
                    player.conversation_cooldown = 30  # Add cooldown
                    conversation = None
                elif choice == "Accept" and conversation.boss_name == "Zazo":
                    player.decrease_health(1)
                    game_state = "playing"
                    player.in_conversation = False  # Reset the flag
                    player.conversation_cooldown = 600  # Add cooldown
                    conversation = None
        elif game_state == "battle":
            battle.process_event(event)

    if game_state == "playing":
        keys = pygame.key.get_pressed()
        player.update(keys, obstacles)
        boss.update()
        zazo.update()
        
        if not player.in_conversation and player.conversation_cooldown == 0:
            if player.collision_rect.colliderect(boss.rect):
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
                conversation.text_sound.play() 

    elif game_state == "battle":
        battle.update(event)

    if game_state in ["playing", "conversation"]:
        boss.draw(screen)
        zazo.draw(screen)
        player.draw(screen)

    if game_state == "conversation":
        conversation.update()
        conversation.draw(screen)
    elif game_state == "battle":
        battle.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
pygame.mixer.quit()
