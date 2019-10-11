#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""text_block: A utility meant to create/render blocks in a pygame window.
"""

import pygame  # This is the engine used in the game

__author__ = "Victor Neves"
__license__ = "MIT"
__maintainer__ = "Victor Neves"
__email__ = "victorneves478@gmail.com"
__status__ = "Production"


class TextBlock:
    """Block of text class, used by pygame. Can be used to both text and menu.

    Attributes:
    ----------
    text: string
        The text to be displayed.
    pos: tuple of 2 * int
        Color of the tail. End of the body color gradient.
    window: pygame window object
        The screen where the text is drawn.
    scale: int, optional, default = 1 / 12
        Adaptive scale to resize if the board size changes.
    type: string, optional, default = "text"
        Assert whether the BlockText is a text or menu option.
    """

    def __init__(
        self,
        text,
        pos,
        window,
        canvas_size,
        font_path,
        scale=(1 / 12),
        block_type="text",
        background_color=None,
        hovered_color=(42, 42, 42),
        default_color=(152, 152, 152),
    ):
        """Initialize, set position of the rectangle and render the text block."""
        self.block_type = block_type
        self.hovered = False
        self.text = text
        self.pos = pos
        self.screen = window
        self.canvas_size = canvas_size
        self.font_path = font_path
        self.scale = scale
        self.hovered_color = hovered_color
        self.default_color = default_color
        self.background_color = background_color
        self.set_rect()
        self.draw()

    def draw(self):
        """Set what to render and blit on the pygame screen."""
        self.set_rend()
        self.screen.blit(self.rend, self.rect)

    def set_rend(self):
        """Set what to render (font, colors, sizes)"""
        font = pygame.font.Font(self.font_path, int((self.canvas_size) * self.scale))
        self.rend = font.render(
            self.text, True, self.get_color(), self.get_background()
        )

    def get_color(self):
        """Get color to render for text and menu (hovered or not).

        Return
        ----------
        color: tuple of 3 * int
            The color that will be rendered for the text block.
        """
        color = self.hovered_color

        if self.block_type == "menu" and not self.hovered:
            color = self.default_color

        return color

    def get_background(self):
        """Get background color to render for text (hovered or not) and menu.

        Return
        ----------
        color: tuple of 3 * int
            The color that will be rendered for the background of the text block.
        """
        color = self.background_color

        if self.block_type == "menu" and self.hovered:
            color = self.default_color

        return color

    def set_rect(self):
        """Set the rectangle and it's position to draw on the screen."""
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.center = self.pos


COLOR_INACTIVE = pygame.Color(152, 152, 152)
COLOR_ACTIVE = pygame.Color(42, 42, 42)


class InputBox:
    def __init__(self, x, y, w, h, window, font_path, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.screen = window
        self.font = pygame.font.Font(font_path, int(20))
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 15:
                        self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)

        return None

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self):
        # Blit the text.
        self.screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(self.screen, self.color, self.rect, 2)
