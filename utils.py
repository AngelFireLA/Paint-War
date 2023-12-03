import numpy as np
import pygame
from PIL import Image

color_dict = {"black": [0, 0, 0], "red": [255, 0, 0], "green": [0, 255, 0], "blue": [0, 0, 255],
              "yellow": [255, 255, 0], "magenta": [255, 0, 255], "cyan": [0, 255, 255], "white": [255, 255, 255],
              "gray": [128, 128, 128], "light gray": [192, 192, 192], "dark gray": [64, 64, 64],
              "light red": [255, 64, 64], "light green": [64, 255, 64]}

def lighten_color(color, amount=100):
    r = [x + (amount * (255 - x)) // 255 for x in color]
    return r


def place_text(x, y, text, size, color=None, screen=None, border=False):
    font = pygame.font.Font(pygame.font.get_default_font(), size)
    lines = text.split('\n')

    # Define border and inner color
    border_color = (0, 0, 0) # Black color for border
    inner_color = color if color else (255, 255, 255) # White color for inner text

    for i, line in enumerate(lines):
        if border:
            # Render text with border color for outline
            for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                line_surface = font.render(line, True, border_color)
                line_rect = line_surface.get_rect(center=(x + dx, y + i * size + dy))
                screen.blit(line_surface, line_rect)

        # Render the actual text in designated color or default color
        line_surface = font.render(line, True, inner_color)
        line_rect = line_surface.get_rect(center=(x, y + i * size))
        screen.blit(line_surface, line_rect)
def make_new_player_image(player):
    img = Image.open("images/default bucket.png")

    new_color = (color_dict[player.color][0], color_dict[player.color][1],
                 color_dict[player.color][2])  # (R,G,B) No alpha information here

    img = img.convert("RGBA")

    data = np.array(img)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white and white-ish pixels with new_color
    white_areas = (red > 254) & (blue > 254) & (green > 254)
    data[..., :3][white_areas.T] = new_color  # Sets RGB values, leaves alpha value unchanged

    img = Image.fromarray(data)
    img.save("images/" + str(player.name) + ".png")
    player.image = pygame.image.load("images/" + str(player.name) + ".png").convert_alpha()