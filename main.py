import os
import time

import numpy as np
import pygame
from PIL import Image

pygame.init()
width, height = 1000, 1000
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Paint War")

background_image = pygame.image.load("images/gradient_background.png")  # images is 1000x1000

color_dict = {"black": [0, 0, 0], "red": [255, 0, 0], "green": [0, 255, 0], "blue": [0, 0, 255],
              "yellow": [255, 255, 0], "magenta": [255, 0, 255], "cyan": [0, 255, 255], "white": [255, 255, 255],
              "gray": [128, 128, 128], "light gray": [192, 192, 192], "dark gray": [64, 64, 64],
              "light red": [255, 64, 64], "light green": [64, 255, 64]}


GRID_SIZE = 8
GRID_SQUARE_SIZE = 80

def show_grid(grid):
    for line in grid:
        print(line)


class Game:
    def __init__(self):
        self.grid = [[] for _ in range(GRID_SIZE)]  # Create a 2D list to store the square
        self.init_grid()
        self.players = []

    def init_grid(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.grid[row].append(Square("white"))  # Set default color to white


class Square:
    def __init__(self, color):
        self.color = color

    def __repr__(self):
        return f"Square({self.color})"


class Player:
    def __init__(self, name, color, x, y):
        self.name = name
        self.color = color
        self.score = 0
        self.x, self.y = x, y
    def __repr__(self):
        return f"Player({self.name}, {self.color}, {self.x}, {self.y})"

    def move(self, x, y, game):
        if 0<=x+self.x<=7:
            self.x+=x
        if 0<=y+self.y<=7:
            self.y+=y
        game.grid[self.y][self.x].color = self.color

def lighten_color(color, amount=100):
    r = [x + (amount * (255 - x)) // 255 for x in color]
    return r
def draw_grid(game):
    grid_x = (width - GRID_SIZE * GRID_SQUARE_SIZE) // 2
    grid_y = (height - GRID_SIZE * GRID_SQUARE_SIZE) // 2

    place_text(grid_x - int(GRID_SQUARE_SIZE/2), grid_y - int(GRID_SQUARE_SIZE/2), game.players[0].name, 25, color_dict["black"])
    place_text(grid_x - int(GRID_SQUARE_SIZE/2), grid_y + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE/2), game.players[1].name, 25, color_dict["black"])
    place_text(grid_x + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE/2), grid_y - int(GRID_SQUARE_SIZE/2), game.players[2].name, 25, color_dict["black"])
    place_text(grid_x + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE/2), grid_y + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE/2), game.players[3].name, 25, color_dict["black"])

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            square_x = grid_x + col * GRID_SQUARE_SIZE
            square_y = grid_y + row * GRID_SQUARE_SIZE

            # Draw the square with a black border
            pygame.draw.rect(screen, lighten_color(color_dict[game.grid[row][col].color]),
                             (square_x, square_y, GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))
            pygame.draw.rect(screen, color_dict["black"],
                             (square_x, square_y, GRID_SQUARE_SIZE, GRID_SQUARE_SIZE), 1)

def place_text(x, y, text, size, color=None):
    font = pygame.font.Font(pygame.font.get_default_font(), size)
    if color:
        text = font.render(text, True, color)
    else:
        text = font.render(text, True, (150, 150, 150))
    screen.blit(text, text.get_rect(center=(x, y)))


def square_to_pos(col, row):
    grid_x = (width - GRID_SIZE * GRID_SQUARE_SIZE) // 2
    grid_y = (height - GRID_SIZE * GRID_SQUARE_SIZE) // 2

    square_x = grid_x + col * GRID_SQUARE_SIZE
    square_y = grid_y + row * GRID_SQUARE_SIZE

    center_x = square_x + GRID_SQUARE_SIZE // 2
    center_y = square_y + GRID_SQUARE_SIZE // 2

    return center_x, center_y


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


def start_game():
    global screen, width, height

    loading_image = pygame.image.load("images/loading.png")
    loading_image = pygame.transform.scale(loading_image, (width, height))
    screen.blit(loading_image, (0, 0))
    pygame.display.flip()
    game = Game()
    player1 = Player("Player 1", "red",0, 0)
    player2 = Player("Player 2", "blue", 0, GRID_SIZE-1)
    player3 = Player("Player 3", "green", GRID_SIZE-1, 0)
    player4 = Player("Player 4", "yellow", GRID_SIZE-1, GRID_SIZE-1)
    game.players.append(player1)
    game.players.append(player2)
    game.players.append(player3)
    game.players.append(player4)
    game.grid[0][0].color = player1.color
    game.grid[GRID_SIZE-1][0].color = player2.color
    game.grid[0][GRID_SIZE - 1].color = player3.color
    game.grid[GRID_SIZE - 1][GRID_SIZE - 1].color = player4.color
    make_new_player_image(player1)
    make_new_player_image(player2)
    make_new_player_image(player3)
    make_new_player_image(player4)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for player in game.players:
                    os.remove("images/"+str(player.name)+".png")
                pygame.quit()
                quit()
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player1.move(0, y=-1, game=game)
                elif event.key == pygame.K_DOWN:
                    player1.move(0, 1, game=game)
                elif event.key == pygame.K_LEFT:
                    player1.move(-1, 0, game=game)
                elif event.key == pygame.K_RIGHT:
                    player1.move(1, 0, game=game)


        screen.blit(pygame.transform.scale(background_image, (width, height)), (0, 0))
        draw_grid(game)
        for player in game.players:
            p_image = pygame.image.load("images/"+str(player.name)+".png").convert_alpha()
            p_image = pygame.transform.scale(p_image, (GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))
            p_rect = p_image.get_rect()
            p_rect.centerx, p_rect.centery = square_to_pos(player.x, player.y)
            screen.blit(p_image, p_rect)

        pygame.display.flip()


start_game()
