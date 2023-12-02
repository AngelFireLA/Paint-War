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
clock = pygame.time.Clock()


def show_grid(grid):
    for line in grid:
        print(line)


class Game:
    def __init__(self):
        self.grid = [[] for _ in range(GRID_SIZE)]  # Create a 2D list to store the square
        self.init_grid()
        self.players = []
        self.timer = 5
        self.last_time_updated_timer = time.time()
        self.running = True

    def run(self):
        global screen, width, height

        while self.running:

            delta_time = clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    for player in self.players:
                        os.remove("images/" + str(player.name) + ".png")
                    pygame.quit()
                    quit()
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize
                    width, height = event.size
                    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

            self.players[0].try_to_move(self, delta_time)

            screen.blit(pygame.transform.scale(background_image, (width, height)), (0, 0))
            draw_grid(self)
            for player in self.players:
                player.image = pygame.transform.scale(player.img, (GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))

                p_rect = player.image.get_rect()
                p_rect.centerx, p_rect.centery = player.x, player.y
                screen.blit(player.image, p_rect)

            # update game timer
            place_text(width / 2, height / 8,
                       "Temps restant : " + str(int(self.timer) // 60) + ":" + str(int(self.timer) % 60), 30,
                       color_dict["black"])

            if self.timer >= 0:
                self.timer -= delta_time / 1000
            else:
                self.running = False
            pygame.display.flip()
        self.end_game()

    def end_game(self):
        global screen, width, height
        screen.blit(pygame.transform.scale(background_image, (width, height)), (0, 0))

        squares_count = {self.players[0].name: 0, self.players[1].name: 0, self.players[2].name: 0,
                         self.players[3].name: 0}
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].color == self.players[0].color:
                    squares_count[self.players[0].name] += 1
                elif self.grid[row][col].color == self.players[1].color:
                    squares_count[self.players[1].name] += 1
                elif self.grid[row][col].color == self.players[2].color:
                    squares_count[self.players[2].name] += 1
                elif self.grid[row][col].color == self.players[3].color:
                    squares_count[self.players[3].name] += 1

        sorted_scores = sorted(squares_count.items(), key=lambda x: x[1], reverse=True)
        leaderboard: str = f"Classement : \n 1 - {sorted_scores[0][0]} : {sorted_scores[0][1]} \n 2 - {sorted_scores[1][0]} : {sorted_scores[1][1]} \n 3 - {sorted_scores[2][0]} : {sorted_scores[2][1]} \n 4 - {sorted_scores[3][0]} : {sorted_scores[3][1]}"
        place_text(width / 2, height / 4, leaderboard, 50, color_dict["black"])
        place_text(width / 2, height / 6, "Le jeu est terminé", 50, color_dict["black"])

        pygame.display.flip()
        time.sleep(3)

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
    MOVEMENT_COOLDOWN = 10

    def __init__(self, name, color, x, y):
        self.name = name
        self.color = color
        self.score = 0
        self.x, self.y = x, y
        self.time_since_last_movement = 0
        self.img = None
        self.last_move = (0, 0)

    def __repr__(self):
        return f"Player({self.name}, {self.color}, {self.x}, {self.y})"

    def try_to_move(self, game, delta_time):
        self.time_since_last_movement += delta_time
        if self.time_since_last_movement >= self.MOVEMENT_COOLDOWN:
            move_multiplier = 1
            dx = dy = 0
            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:
                dy -= 10 * move_multiplier
            if keys[pygame.K_DOWN]:
                dy += 10 * move_multiplier
            if keys[pygame.K_LEFT]:
                dx -= 10 * move_multiplier
            if keys[pygame.K_RIGHT]:
                dx += 10 * move_multiplier

            if dx != 0 or dy != 0:  # Si l'une ou l'autre direction est activée, effectuez le mouvement.
                self.time_since_last_movement = 0
                self.move(dx, dy, game)
                self.last_move = (dx, dy)

    def move(self, x, y, game):
        if self.x + x < col_to_x(0) or self.x + x > col_to_x(GRID_SIZE - 1) or \
                self.y + y < row_to_y(0) or self.y + y > row_to_y(GRID_SIZE - 1):
            return

        self.x += x
        self.y += y
        self_mask = pygame.mask.from_surface(self.img)
        for player in game.players:
            if player.name != self.name:
                player.img = pygame.transform.scale(player.img, (GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))
                player_mask = pygame.mask.from_surface(player.img)
                offset_x = player.x - self.x
                offset_y = player.y - self.y

                overlap = self_mask.overlap(player_mask, (offset_x, offset_y))
                if overlap is not None:
                    self.x -= x
                    self.y -= y
                    return

        grid_x, grid_y = pos_to_square(self.x - (self.img.get_width() / 5), self.y + (self.img.get_height() / 5))

        game.grid[grid_y][grid_x].color = self.color


def lighten_color(color, amount=100):
    r = [x + (amount * (255 - x)) // 255 for x in color]
    return r


def draw_grid(game):
    grid_x = (width - GRID_SIZE * GRID_SQUARE_SIZE) // 2
    grid_y = (height - GRID_SIZE * GRID_SQUARE_SIZE) // 2

    place_text(grid_x - int(GRID_SQUARE_SIZE / 2), grid_y - int(GRID_SQUARE_SIZE / 2), game.players[0].name, 25,
               color_dict["black"])
    place_text(grid_x - int(GRID_SQUARE_SIZE / 2), grid_y + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE / 2),
               game.players[1].name, 25, color_dict["black"])
    place_text(grid_x + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE / 2), grid_y - int(GRID_SQUARE_SIZE / 2),
               game.players[2].name, 25, color_dict["black"])
    place_text(grid_x + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE / 2),
               grid_y + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE / 2), game.players[3].name, 25,
               color_dict["black"])

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
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_surface = font.render(line, True, color) if color else font.render(line, True, (150, 150, 150))
        line_rect = line_surface.get_rect(center=(x, y + i * size))
        screen.blit(line_surface, line_rect)


def square_to_pos(col, row):
    center_x = (((width - GRID_SIZE * GRID_SQUARE_SIZE) // 2) + col * GRID_SQUARE_SIZE) + GRID_SQUARE_SIZE // 2
    center_y = (((height - GRID_SIZE * GRID_SQUARE_SIZE) // 2) + row * GRID_SQUARE_SIZE) + GRID_SQUARE_SIZE // 2
    return center_x, center_y


def col_to_x(col):
    square_x = ((width - GRID_SIZE * GRID_SQUARE_SIZE) // 2) + col * GRID_SQUARE_SIZE
    return square_x + GRID_SQUARE_SIZE // 2


def row_to_y(row):
    square_y = ((height - GRID_SIZE * GRID_SQUARE_SIZE) // 2) + row * GRID_SQUARE_SIZE
    return square_y + GRID_SQUARE_SIZE // 2


def pos_to_square(x, y):
    grid_x = (x - (width - GRID_SIZE * GRID_SQUARE_SIZE) / 2) / GRID_SQUARE_SIZE
    grid_y = (y - (height - GRID_SIZE * GRID_SQUARE_SIZE) / 2) / GRID_SQUARE_SIZE
    return int(grid_x), int(grid_y)


def x_to_col(x):
    grid_x = (x - (width - GRID_SIZE * GRID_SQUARE_SIZE) / 2) / GRID_SQUARE_SIZE
    return int(grid_x)


def y_to_row(y):
    grid_y = (y - (height - GRID_SIZE * GRID_SQUARE_SIZE) / 2) / GRID_SQUARE_SIZE
    return int(grid_y)


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
    player.img = pygame.image.load("images/" + str(player.name) + ".png").convert_alpha()


def setup_players(game):
    for player in game.players:
        try:
            os.remove("images/" + str(player.name) + ".png")
        except:
            pass
    player1 = Player("Player 1", "red", col_to_x(0), row_to_y(0))
    player2 = Player("Player 2", "blue", col_to_x(0), row_to_y(GRID_SIZE - 1))
    player3 = Player("Player 3", "green", col_to_x(GRID_SIZE - 1), row_to_y(0))
    player4 = Player("Player 4", "yellow", col_to_x(GRID_SIZE - 1), row_to_y(GRID_SIZE - 1))
    game.players.append(player1)
    game.players.append(player2)
    game.players.append(player3)
    game.players.append(player4)
    game.grid[0][0].color = player1.color
    game.grid[GRID_SIZE - 1][0].color = player2.color
    game.grid[0][GRID_SIZE - 1].color = player3.color
    game.grid[GRID_SIZE - 1][GRID_SIZE - 1].color = player4.color
    make_new_player_image(player1)
    make_new_player_image(player2)
    make_new_player_image(player3)
    make_new_player_image(player4)


def start_game():
    while True:
        loading_image = pygame.image.load("images/loading.png")
        loading_image = pygame.transform.scale(loading_image, (width, height))
        screen.blit(loading_image, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        game = Game()
        print(game.timer)

        setup_players(game)

        game.run()


start_game()
