import pygame
import os
import sys

GREEN = (173,204,96)
DARK_GREEN = (43,51,24)
LIGHT_GREEN = (100,120,80)


cell_size = 20
number_of_cell = 27
OFFSET = 75

screen = pygame.display.set_mode((2*OFFSET + cell_size*number_of_cell, 2*OFFSET + cell_size*number_of_cell))

def resource_path(relative_path):
    # Detects if the program is being run from a PyInstaller bundle
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

food_surface = pygame.image.load(resource_path("Graphics/final.png"))