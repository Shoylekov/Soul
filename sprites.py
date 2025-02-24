import pygame

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height, scale=1):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (-x, -y))
        image = pygame.transform.scale(image, (width * scale, height * scale))  # Ensure correct scaling
        return image
