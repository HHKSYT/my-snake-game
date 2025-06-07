import pygame
from pygame.math import Vector2
import os
import sys
import random
from settings import resource_path,cell_size,number_of_cell,screen,OFFSET,DARK_GREEN,GREEN

class Snake:
    def __init__(self):
        self.body = [Vector2(6,9), Vector2(5,9), Vector2(4,9)]
        self.direction = Vector2(1,0)
        self.add_segment = False
        self.eat_sound = pygame.mixer.Sound(resource_path("Sounds/eat.mp3"))
        self.wall_hit_sound = pygame.mixer.Sound(resource_path("Sounds/wall.mp3"))
    def draw(self):
        for segment in self.body:
            segment_rect = (OFFSET + segment.x *cell_size, OFFSET + segment.y*cell_size, cell_size, cell_size)
            pygame.draw.rect(screen,DARK_GREEN,segment_rect, 0,7)
    def update(self):
        self.body.insert(0,self.body[0] + self.direction)
        if self.add_segment == True:

            self.add_segment = False
        else:
            self.body = self.body[:-1]
    def reset(self):
        self.body = [Vector2(6,9), Vector2(5,9), Vector2(4,9)]
        self.direction = Vector2(1,0)