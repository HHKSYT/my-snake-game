import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Enter Username")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 40)
input_box = pygame.Rect(200, 200, 240, 50)  # Fixed width
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive

active = False
username = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box
            if input_box.collidepoint(event.pos):
                active = True
                color = color_active
            else:
                active = False
                color = color_inactive

        if event.type == pygame.KEYDOWN and active:
            if event.key == pygame.K_RETURN:
                print("Username entered:", username)
                running = False  # You can also start your game here
            elif event.key == pygame.K_BACKSPACE:
                username = username[:-1]
            else:
                username += event.unicode

    screen.fill((30, 30, 30))

    # Draw the input box
    pygame.draw.rect(screen, color, input_box, 2)

    # Render text and clip if it overflows
    full_text = font.render(username, True, pygame.Color('white'))
    text_width = full_text.get_width()
    max_text_width = input_box.w - 10  # Padding for box

    if text_width > max_text_width:
        offset = text_width - max_text_width
        clipped_text_surface = full_text.subsurface((offset, 0, max_text_width, full_text.get_height()))
    else:
        clipped_text_surface = full_text

    screen.blit(clipped_text_surface, (input_box.x + 5, input_box.y + 5))

    pygame.display.flip()
    clock.tick(30)

