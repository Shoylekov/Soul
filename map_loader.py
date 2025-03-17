import pygame
import pytmx
from pytmx.util_pygame import load_pygame

def load_map(tmx_data, WIDTH, HEIGHT):
    scale_x = WIDTH / (tmx_data.width * tmx_data.tilewidth)
    scale_y = HEIGHT / (tmx_data.height * tmx_data.tileheight)
    obstacles = []
    special_areas = []

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
        elif isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid:
                    tile_rect = pygame.Rect(
                        x * tmx_data.tilewidth * scale_x, 
                        y * tmx_data.tileheight * scale_y, 
                        tmx_data.tilewidth * scale_x, 
                        tmx_data.tileheight * scale_y
                    )
                    if layer.name == "Fences" or layer.name == "border":
                        tile_rect.width *= 0.5
                        tile_rect.height *= 0.9
                        tile_rect.x += (tmx_data.tilewidth * scale_x - tile_rect.width) / 2
                        tile_rect.y += (tmx_data.tileheight * scale_y - tile_rect.height) / 2
                        obstacles.append(tile_rect)
                    elif layer.name == "enterance":
                        special_areas.append(tile_rect)
    return obstacles, special_areas