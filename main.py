import pygame

pygame.init()
width, height = 1000, 1000
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Paint War")

background_image = pygame.image.load("image/gradient_background.png")  # image is 1000x1000

color_dict = {"black": (0, 0, 0), "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
              "yellow": (255, 255, 0), "magenta": (255, 0, 255), "cyan": (0, 255, 255), "white": (255, 255, 255),
              "gray": (128, 128, 128), "light gray": (192, 192, 192), "dark gray": (64, 64, 64),
              "light red": (255, 64, 64), "light green": (64, 255, 64)}

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


def draw_grid(game):
    grid_x = (width - GRID_SIZE * GRID_SQUARE_SIZE) // 2
    grid_y = (height - GRID_SIZE * GRID_SQUARE_SIZE) // 2

    place_text(grid_x - int(GRID_SQUARE_SIZE/2), grid_y - int(GRID_SQUARE_SIZE/2), game.players[0].name, 25, color_dict["black"])
    place_text(grid_x + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE/2), grid_y - int(GRID_SQUARE_SIZE/2), game.players[1].name, 25, color_dict["black"])
    place_text(grid_x - int(GRID_SQUARE_SIZE/2), grid_y + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE/2), game.players[2].name, 25, color_dict["black"])
    place_text(grid_x + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE/2), grid_y + GRID_SIZE * GRID_SQUARE_SIZE + int(GRID_SQUARE_SIZE/2), game.players[3].name, 25, color_dict["black"])

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            square_x = grid_x + col * GRID_SQUARE_SIZE
            square_y = grid_y + row * GRID_SQUARE_SIZE

            # Draw the square with a black border
            pygame.draw.rect(screen, color_dict[game.grid[row][col].color],
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


def square_to_pos(row, col, game):
    grid_x = (width - game.grid_size * game.grid_square_size) // 2
    grid_y = (height - game.grid_size * game.grid_square_size) // 2

    square_x = grid_x + col * game.grid_square_size
    square_y = grid_y + row * game.grid_square_size

    center_x = square_x + game.grid_square_size // 2
    center_y = square_y + game.grid_square_size // 2

    return center_x, center_y


def start_game():
    global screen, width, height
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
    game.grid[0][GRID_SIZE-1].color = player2.color
    game.grid[GRID_SIZE - 1][0].color = player3.color
    game.grid[GRID_SIZE - 1][GRID_SIZE - 1].color = player4.color


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        screen.blit(pygame.transform.scale(background_image, (width, height)), (0, 0))
        draw_grid(game)
        pygame.display.flip()


start_game()
