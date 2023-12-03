import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))

import pygame

WHITE = (255, 255, 255)


class Button():
    def __init__(self, text, x=0, y=0, color=(73, 73, 73),
                 highlight_color=(189, 189, 189), click_color=(66, 135, 245),
                 font_size=50, width=200, height=100):
        self.text = text
        self.x = x
        self.y = y

        self.font_size = font_size

        self.normal_color = color
        self.highlight_color = highlight_color
        self.click_color = click_color

        self.image_normal = pygame.Surface((width, height))
        self.image_normal.fill(color)

        self.image_highlighted = pygame.Surface((width, height))
        self.image_highlighted.fill(highlight_color)

        self.image_clicked = pygame.Surface((width, height))
        self.image_clicked.fill(click_color)

        self.image = self.image_normal
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.font = pygame.font.Font(None, self.font_size)
        self.text_surface = self.font.render(self.text, 1, WHITE)

        W = self.text_surface.get_width()
        H = self.text_surface.get_height()
        self.image_normal.blit(self.text_surface, ((width - W) // 2, (height - H) // 2))
        self.image_highlighted.blit(self.text_surface, ((width - W) // 2, (height - H) // 2))
        self.image_clicked.blit(self.text_surface, ((width - W) // 2, (height - H) // 2))

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
        surface.blit(self.image, self.rect)

button1 = Button('button 1', 50, 50)
button2 = Button('button 2', 50, 160)
button3 = Button('button 3', 50, 270)

buttons = [button1, button2, button3]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if button1.handle_event(event):
                print("'button 1' has been clicked")
            elif button2.handle_event(event):
                print("'button 2' has been clicked")
            elif button3.handle_event(event):
                print("'button 3' has been clicked")

    screen.fill((30, 30, 30))

    for button in buttons:
        button.draw(screen)

    pygame.display.flip()