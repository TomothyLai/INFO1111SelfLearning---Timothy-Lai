import pygame
class Bullet(pygame.Rect):
    VELOCITY = 10
    def __init__(self, left, top, width, height, direction):
        super().__init__(left, top, width, height)
        self.direction = direction

class Enemy(pygame.Rect):
    def __init__(self, left, top, width, height):
        super().__init__(left, top, width, height)
        self.health = 100
    def got_hit(self):
        self.health -= 10
    def get_health(self):
        return self.health



