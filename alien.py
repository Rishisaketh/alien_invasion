import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """A class to represent a single alien in the fleet"""

    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen

        self.settings = ai_game.settings
        # load the alien image and set its rect attribute.
        
        original_image = pygame.image.load('/Users/avinashbabu/Downloads/pi5MegBi9 (1).png')


        self.image = pygame.transform.scale(original_image, (80, 80))

        self.rect = self.image.get_rect()

        # start each new alien near the top left of the screen
        self.rect.x = 0
        self.rect.y = 0

        # store the aliens exact horizontal position
        self.x = float(self.rect.x)

    def update(self):
        """move the alien right or left"""
        # self.x += self.settings.alien_speed 
        self.x += self.settings.alien_speed * self.settings.fleet_direction
        self.rect.x = self.x

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True
        return False