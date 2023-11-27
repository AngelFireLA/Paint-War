import pygame, numpy as np

pygame.init()

player_image = pygame.image.load("images/default bucket.png")

player_array = pygame.surfarray.array3d(player_image)

new_color = (255, 0, 0)

white_pixel_indices = np.all(player_array == [255, 255, 255], axis=-1)

player_array[white_pixel_indices] = new_color

player_image = pygame.surfarray.make_surface(player_array)

pygame.image.save(player_image, "modified_player_image.png")
