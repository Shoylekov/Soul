import random
import pygame
import math

class SpineAttack:
    def __init__(self, boss, arena_rect):
        self.boss = boss
        self.arena_rect = arena_rect
        self.damage_sound = pygame.mixer.Sound("assets/music/damage_sound.mp3")