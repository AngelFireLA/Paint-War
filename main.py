import os
import random
import time

import pygame

from utils import place_text, lighten_color, make_new_player_image

pygame.init()
width, height = 1000, 900
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Paint War")

background_image = pygame.image.load("images/gradient_background.png")  # images is 1000x1000

color_dict = {"black": [0, 0, 0], "red": [255, 0, 0], "green": [0, 255, 0], "blue": [0, 0, 255],
              "yellow": [255, 255, 0], "magenta": [255, 0, 255], "cyan": [0, 255, 255], "white": [255, 255, 255],
              "gray": [128, 128, 128], "light gray": [192, 192, 192], "dark gray": [64, 64, 64],
              "light red": [255, 64, 64], "light green": [64, 255, 64]}

GRID_SIZE = 8
GRID_SQUARE_SIZE = 80
clock = pygame.time.Clock()


class Game:
    def __init__(self):
        self.grid = [[] for _ in range(GRID_SIZE)]  # Create a 2D list to store the square
        self.init_grid()
        self.players = []
        self.timer = 120
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = pause_menu()


            screen.blit(pygame.transform.scale(background_image, (width, height)), (0, 0))
            draw_grid(self)
            for player in self.players:
                player.image = pygame.transform.scale(player.image, (GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))

                p_rect = player.image.get_rect()
                p_rect.centerx, p_rect.centery = player.x, player.y
                screen.blit(player.image, p_rect)
                player.try_to_move(self, delta_time)

            if len(str(int(self.timer+1) % 60)) == 1:
                place_text(width / 2, height / 12,
                           "Temps restant : " + str(int(self.timer+1) // 60) + ":0" + str(int(self.timer+1) % 60), 30,
                           color_dict["black"], screen)
            else:
                place_text(width / 2, height / 12,
                           "Temps restant : " + str(int(self.timer+1) // 60) + ":" + str(int(self.timer+1) % 60), 30,
                           color_dict["black"], screen)

            if self.timer >= 0:
                self.timer -= delta_time / 1000
            else:
                self.running = False
            pygame.display.flip()
        self.end_game()


    def end_game(self):
        global screen, width, height

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

        button1 = Button('Continue', width / 2, height / 1.5)
        continuing = False
        while not continuing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button1.handle_event(event):
                        continuing = True
            screen.blit(pygame.transform.scale(background_image, (width, height)), (0, 0))

            place_text(width / 2, height / 4, leaderboard, 50, color_dict["black"], screen)
            place_text(width / 2, height / 6, "Le jeu est terminé", 50, color_dict["black"], screen)
            button1.draw(screen)
            pygame.display.flip()


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
    move_multiplier = 8
    MOVEMENT_COOLDOWN = 15*move_multiplier


    def __init__(self, name, color, x, y):
        self.name = name
        self.color = color
        self.x, self.y = x, y
        self.time_since_last_movement = 0
        self.image = None
        self.last_move = (0, 0)

    def __repr__(self):
        return f"Player({self.name}, {self.color}, {self.x}, {self.y})"

    def try_to_move(self, game, delta_time):
        self.time_since_last_movement += delta_time
        if self.time_since_last_movement >= self.MOVEMENT_COOLDOWN:
            dx = dy = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                dy -= 10 * self.move_multiplier
            if keys[pygame.K_DOWN]:
                dy += 10 * self.move_multiplier
            if keys[pygame.K_LEFT]:
                dx -= 10 * self.move_multiplier
            if keys[pygame.K_RIGHT]:
                dx += 10 * self.move_multiplier
            if dx != 0 or dy != 0:
                self.time_since_last_movement = 0
                self.move(dx, dy, game)
                self.last_move = (dx, dy)
    def get_current_painting_square(self, x, y):
        return pos_to_square(x - (self.image.get_width() / 5), y + (self.image.get_height() / 5))

    def can_move_to(self, new_x, new_y, game) -> bool:
        if new_x < col_to_x(0) or new_x > col_to_x(GRID_SIZE - 1) or \
                new_y < row_to_y(0) or new_y > row_to_y(GRID_SIZE - 1):
            return False

        self_mask = pygame.mask.from_surface(self.image)
        for player in game.players:
            if player.name != self.name:
                player.image = pygame.transform.scale(player.image, (GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))
                player_mask = pygame.mask.from_surface(player.image)
                offset_x = player.x - new_x
                offset_y = player.y - new_y

                overlap = self_mask.overlap(player_mask, (offset_x, offset_y))
                if overlap is not None:
                    return False
        return True

    def move(self, x, y, game):
        if not self.can_move_to(self.x+x, self.y+y, game):
            return

        self.x += x
        self.y += y


        grid_x, grid_y = self.get_current_painting_square(self.x, self.y)
        grid_color = game.grid[grid_y][grid_x].color
        # # ralenti le mouvement sur les cases des autres, à voir si on garde
        # if grid_color != "white" and grid_color != self.color:
        #     self.time_since_last_movement -= self.MOVEMENT_COOLDOWN
        game.grid[grid_y][grid_x].color = self.color

class Bot(Player):

    def __init__(self, name, color, x, y, intelligence="random"):
        self.intelligence = intelligence
        super().__init__(name, color, x, y)


    def __repr__(self):
        return f"Bot({self.name}, {self.color}, {self.x}, {self.y}, {self.intelligence})"

    def try_to_move(self, game, delta_time):
        self.time_since_last_movement += delta_time
        if self.time_since_last_movement >= self.MOVEMENT_COOLDOWN:

            vertical_moves = [0, 10 * self.move_multiplier, -10 * self.move_multiplier]
            horizontal_moves = [0, 10 * self.move_multiplier, -10 * self.move_multiplier]
            dx = dy = 0
            if self.intelligence == "random":

                dx = random.choice(horizontal_moves)
                dy = random.choice(vertical_moves)
            elif self.intelligence == "new_square_every_time":
                good_moves = []
                for v_move in vertical_moves:
                    for h_move in horizontal_moves:
                        dx, dy = h_move, v_move
                        grid_x, grid_y = self.get_current_painting_square(self.x+dx, self.y+dy)
                        if self.can_move_to(self.x + dx, self.y + dy, game) and game.grid[grid_y][grid_x].color != self.color:
                            good_moves.append((dx, dy))

                if not good_moves:
                    dx = random.choice(horizontal_moves)
                    dy = random.choice(vertical_moves)
                else:
                    dx, dy = random.choice(good_moves)

            if dx != 0 or dy != 0:
                self.time_since_last_movement = 0
                self.move(dx, dy, game)
                self.last_move = (dx, dy)

class Button:
    def __init__(self, text, x=0, y=0, color=(255, 165, 0),
                 highlight_color=(255, 190, 50), click_color=(255, 140, 0),
                 font_size=50, size=1):
        self.text = text
        self.x = x
        self.y = y

        self.font_size = font_size

        self.normal_color = color
        self.highlight_color = highlight_color
        self.click_color = click_color

        self.image_normal = pygame.Surface((200*size, 100*size))
        self.image_normal.fill(color)

        self.image_highlighted = pygame.Surface((200*size, 100*size))
        self.image_highlighted.fill(highlight_color)

        self.image_clicked = pygame.Surface((200*size, 100*size))
        self.image_clicked.fill(click_color)

        self.image = self.image_normal
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.font = pygame.font.Font(None, self.font_size)
        self.text_surface = self.font.render(self.text, 1, color_dict["white"])

        W = self.text_surface.get_width()
        H = self.text_surface.get_height()
        self.image_normal.blit(self.text_surface, ((200*size - W) // 2, (100*size - H) // 2))
        self.image_highlighted.blit(self.text_surface, ((200*size - W) // 2, (100*size - H) // 2))
        self.image_clicked.blit(self.text_surface, ((200*size - W) // 2, (100*size - H) // 2))

        self.click_start = 0
        self.click_duration = 200

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if event.button == 1:
                self.image = self.image_clicked
                self.click_start = pygame.time.get_ticks()
                return True
        if event.type == pygame.MOUSEBUTTONUP and self.rect.collidepoint(event.pos):
            if pygame.time.get_ticks() - self.click_start > self.click_duration:
                self.image = self.image_highlighted
        return False

    def draw(self, surface):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.image != self.image_clicked or (
                    self.image == self.image_clicked and pygame.time.get_ticks() - self.click_start > self.click_duration):
                self.image = self.image_highlighted
        else:
            self.image = self.image_normal

        bordered_image = self.image.copy()

        image_rect = bordered_image.get_rect()

        pygame.draw.rect(bordered_image, (0, 0, 0), image_rect, 2)

        surface.blit(bordered_image, self.rect)

def pause_menu():
    resume_button = Button("Resume", width // 2, height // 3)
    settings_button = Button("Settings", width // 2, height // 2)
    exit_button = Button("Exit", width // 2, height // 1.5 )
    buttons = [resume_button, exit_button, settings_button]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.handle_event(event):
                    return False
                if resume_button.handle_event(event):
                    return True

                if settings_button.handle_event(event):
                    settings_menu()
        screen.blit(pygame.transform.scale(background_image, (width, height)), (0, 0))
        place_text(width // 2, height // 5, "Pause Menu", 50, color_dict["black"], screen)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

def settings_menu():
    pass

def draw_grid(game):
    grid_x = (width - GRID_SIZE * GRID_SQUARE_SIZE) // 2
    grid_y = (height - GRID_SIZE * GRID_SQUARE_SIZE) // 2

    place_text(grid_x - int(GRID_SQUARE_SIZE / 2), grid_y - int(GRID_SQUARE_SIZE / 2), game.players[0].name, 25,
               color_dict["black"], screen)
    place_text(grid_x - int(GRID_SQUARE_SIZE / 2), grid_y + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE / 2),
               game.players[1].name, 25, color_dict["black"], screen)
    place_text(grid_x + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE / 2), grid_y - int(GRID_SQUARE_SIZE / 2),
               game.players[2].name, 25, color_dict["black"], screen)
    place_text(grid_x + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE / 2),
               grid_y + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE / 2), game.players[3].name, 25,
               color_dict["black"], screen)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            square_x = grid_x + col * GRID_SQUARE_SIZE
            square_y = grid_y + row * GRID_SQUARE_SIZE

            # Draw the square with a black border
            pygame.draw.rect(screen, lighten_color(color_dict[game.grid[row][col].color]),
                             (square_x, square_y, GRID_SQUARE_SIZE, GRID_SQUARE_SIZE))
            pygame.draw.rect(screen, color_dict["black"],
                             (square_x, square_y, GRID_SQUARE_SIZE, GRID_SQUARE_SIZE), 1)


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


def setup_players(game):
    for player in game.players:
        try:
            os.remove("images/" + str(player.name) + ".png")
        except:
            pass
    player1 = Player("Player", "red", col_to_x(0), row_to_y(0))
    player2 = Bot("Blue", "blue", col_to_x(0), row_to_y(GRID_SIZE - 1), intelligence="new_square_every_time")
    player3 = Bot("Green", "green", col_to_x(GRID_SIZE - 1), row_to_y(0))
    player4 = Bot("Yellow", "yellow", col_to_x(GRID_SIZE - 1), row_to_y(GRID_SIZE - 1))
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
    loading_image = pygame.image.load("images/loading.png")
    loading_image = pygame.transform.scale(loading_image, (width, height))
    screen.blit(loading_image, (0, 0))
    pygame.display.flip()
    clock.tick(60)
    game = Game()
    game.timer = 120

    setup_players(game)

    game.run()


def main_menu():
    button1 = Button('Start', width/2, height/3, size=1.5)
    button2 = Button('Settings', width/2, height/1.8, size=1.5)
    button3 = Button('Exit', width/2, height/1.3, size=1.5)

    buttons = [button1, button2, button3]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button1.handle_event(event):
                    start_game()
                elif button2.handle_event(event):
                    settings_menu()
                elif button3.handle_event(event):
                    pygame.quit()
                    exit()

        screen.blit(pygame.transform.scale(background_image, (width, height)), (0, 0))

        for button in buttons:
            button.draw(screen)
        place_text(width/2, height/7, "Paint War", 100, color_dict["white"], screen, border=True)
        pygame.display.flip()


if __name__ == "__main__":
    main_menu()
