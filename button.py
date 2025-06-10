import pygame

class Button:
    def __init__(self, pos, image_path, hover_image_path):
        self.image = pygame.image.load(resource_path(image_path)).convert_alpha()
        self.hover_image = pygame.image.load(resource_path(hover_image_path)).convert_alpha()
        self.rect = self.image.get_rect(center=pos)

    def draw(self, screen):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            screen.blit(self.hover_image, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
        return False

