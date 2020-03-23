#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""snake-on-pygame: A simple and fun snake game, playable by Human and AI.

This module is the implementation of the snake game on pygame, focusing on speed
and simplicity. It's playable by both humans and AI agents and it uses most of
pygame's optimizations to deliver a smooth experience in testing/playing.

Usage for human players
----------
    To play as a human, you only need to run this file, given you have the
    needed dependencies.

        $ python snake.py

Usage for AI agents
----------
    To use with AI agents, you need to integrate the game with the AI agent. An
    example usage is:

        >>> from snake-on-pygame import Game
        >>> game = Game(player = "ROBOT",
                        board_size = board_size,
                        local_state = local_state,
                        relative_pos = RELATIVE_POS)

    Useful properties:

        >>> print(game.nb_actions)
        5 # number of actions.

        >>> print(game.food_pos)
        (6, 5) # current position of food.

        >>> print(game.steps)
        10 # current number of steps in a given episode.

        >>> print(game.snake.length)
        4 # current length of the snake in a given episode.

    Possible methods:

        >>> state = game.reset()
          Reset the game and returns the game state right after resetting.

        >>> state = game.state()
          Get the current game state.

        >>> game.food_pos = game.generate_food()
          Update the food position.

        >>> state, reward, done, info = game.step(numerical_action)
          Play a numerical_action, obtaining state, reward, over and info.

        >>> game.render()
          Render the game in a pygame window.

TO DO
----------
    - Publish to pip.
"""

import sys  # To close the window when the game is over
from array import array  # Efficient numeric arrays
from os import environ, path  # To center the game window the best possible
import random  # Random numbers used for the food
import logging  # Logging function for movements and errors
import json  # For file handling (leaderboards)
from itertools import tee  # For the color gradient on snake

import pygame  # This is the engine used in the game
import numpy as np  # Used in calculations and math
import pandas as pd  # Used to manage the leaderboards data

from utilities.text_block import TextBlock, InputBox  # Textblocks for pygame

__author__ = "Victor Neves"
__license__ = "MIT"
__maintainer__ = "Victor Neves"
__email__ = "victorneves478@gmail.com"
__status__ = "Production"

# Actions, options and forbidden moves
OPTIONS = {
    "QUIT": 0,
    "PLAY": 1,
    "BENCHMARK": 2,
    "LEADERBOARDS": 3,
    "MENU": 4,
    "ADD_TO_LEADERBOARDS": 5,
}
RELATIVE_ACTIONS = {"LEFT": 0, "FORWARD": 1, "RIGHT": 2}
ABSOLUTE_ACTIONS = {"LEFT": 0, "RIGHT": 1, "UP": 2, "DOWN": 3, "IDLE": 4}
FORBIDDEN_MOVES = [(0, 1), (1, 0), (2, 3), (3, 2)]

# Possible rewards in the game
REWARDS = {"MOVE": -0.005, "GAME_OVER": -1, "SCORED": 1}

# Types of point in the board
POINT_TYPE = {"EMPTY": 0, "FOOD": 1, "BODY": 2, "HEAD": 3, "DANGEROUS": 4}

# Speed levels possible to human players. MEGA HARDCORE starts with MEDIUM and
# increases with snake size
LEVELS = [" EASY ", " MEDIUM ", " HARD ", " MEGA HARDCORE "]
SPEEDS = {"EASY": 80, "MEDIUM": 60, "HARD": 40, "MEGA_HARDCORE": 65}

# Set the constant FPS limit for the game. Smoothness depend on this.
GAME_FPS = 100


class GlobalVariables:
    """Global variables to be used while drawing and moving the snake game.

    Attributes
    ----------
    board_size: int, optional, default = 30
        The size of the board.
    block_size: int, optional, default = 20
        The size in pixels of a block.
    head_color: tuple of 3 * int, optional, default = (42, 42, 42)
        Color of the head. Start of the body color gradient.
    tail_color: tuple of 3 * int, optional, default = (152, 152, 152)
        Color of the tail. End of the body color gradient.
    food_color: tuple of 3 * int, optional, default = (200, 0, 0)
        Color of the food.
    game_speed: int, optional, default = 10
        Speed in ticks of the game. The higher the faster.
    benchmark: int, optional, default = 10
        Ammount of matches to benchmark and possibly go to leaderboards.
    """

    def __init__(
        self,
        board_size=30,
        block_size=20,
        head_color=(42, 42, 42),
        tail_color=(152, 152, 152),
        food_color=(200, 0, 0),
        game_speed=80,
        benchmark=1,
    ):
        """Initialize all global variables. Updated with argument_handler."""
        self.board_size = board_size
        self.block_size = block_size
        self.head_color = head_color
        self.tail_color = tail_color
        self.food_color = food_color
        self.game_speed = game_speed
        self.benchmark = benchmark

        if self.board_size > 50:  # Warn the user about performance
            LOGGER.warning("WARNING: BOARD IS TOO BIG, IT MAY RUN SLOWER.")

    @property
    def canvas_size(self):
        """Canvas size is updated with board_size and block_size."""
        return self.board_size * self.block_size


class Snake:
    """Player (snake) class which initializes head, body and board.

    The body attribute represents a list of positions of the body, which are in-
    cremented when moving/eating on the position [0]. The orientation represents
    where the snake is looking at (head) and collisions happen when any element
    is superposed with the head.

    Attributes
    ----------
    head: list of 2 * int, default = [board_size / 4, board_size / 4]
        The head of the snake, located according to the board size.
    body: list of lists of 2 * int
        Starts with 3 parts and grows when food is eaten.
    previous_action: int, default = 1
        Last action which the snake took.
    length: int, default = 3
        Variable length of the snake, can increase when food is eaten.
    """

    def __init__(self):
        """Inits Snake with 3 body parts (one is the head) and pointing right"""
        self.head = [int(VAR.board_size / 4), int(VAR.board_size / 4)]
        self.body = [
            [self.head[0], self.head[1]],
            [self.head[0] - 1, self.head[1]],
            [self.head[0] - 2, self.head[1]],
        ]
        self.previous_action = 1
        self.length = 3

    def is_movement_invalid(self, action):
        """Check if the movement is invalid, according to FORBIDDEN_MOVES."""
        invalid = False

        if (
            action,
            self.previous_action,
        ) in FORBIDDEN_MOVES or action == ABSOLUTE_ACTIONS["IDLE"]:
            invalid = True

        return invalid

    def move(self, action, food_pos):
        """According to orientation, move 1 block. If the head is not positioned
        on food, pop a body part. Else, return without popping.

        Return
        ----------
        ate_food: boolean
            Flag which represents whether the snake ate or not food.
        """
        ate_food = False

        if self.is_movement_invalid(action):
            action = self.previous_action
        else:
            self.previous_action = action

        if action == ABSOLUTE_ACTIONS["LEFT"]:
            self.head[0] -= 1
        elif action == ABSOLUTE_ACTIONS["RIGHT"]:
            self.head[0] += 1
        elif action == ABSOLUTE_ACTIONS["UP"]:
            self.head[1] -= 1
        elif action == ABSOLUTE_ACTIONS["DOWN"]:
            self.head[1] += 1

        self.body.insert(0, list(self.head))

        if self.head == food_pos:
            LOGGER.info("EVENT: FOOD EATEN")
            self.length = len(self.body)

            ate_food = True
        else:
            self.body.pop()

        return ate_food


class FoodGenerator:
    """Generate and keep track of food.

    Attributes
    ----------
    pos:
        Current position of food.
    is_food_on_screen:
        Flag for existence of food.
    """

    def __init__(self, body):
        """Initialize a food piece and set existence flag."""
        self.is_food_on_screen = False
        self.pos = self.generate_food(body)

    def generate_food(self, body):
        """Generate food and verify if it's on a valid place.

        Return
        ----------
        pos: tuple of 2 * int
            Position of the food that was generated. It can't be in the body.
        """
        if not self.is_food_on_screen:
            while True:
                food = [
                    int((VAR.board_size - 1) * random.random()),
                    int((VAR.board_size - 1) * random.random()),
                ]

                if food in body:
                    continue
                else:
                    self.pos = food
                    break

            LOGGER.info("EVENT: FOOD APPEARED")
            self.is_food_on_screen = True

        return self.pos


class Game:
    """Hold the game window and functions.

    Attributes
    ----------
    window: pygame display
        Pygame window to show the game.
    fps: pygame time clock
        Define Clock and ticks in which the game will be displayed.
    snake: object
        The actual snake who is going to be played.
    food_generator: object
        Generator of food which responds to the snake.
    food_pos: tuple of 2 * int
        Position of the food on the board.
    game_over: boolean
        Flag for game_over.
    player: string
        Define if human or robots are playing the game.
    board_size: int, optional, default = 30
        The size of the board.
    local_state: boolean, optional, default = False
        Whether to use or not game expertise (used mostly by robots players).
    relative_pos: boolean, optional, default = False
        Whether to use or not relative position of the snake head. Instead of
        actions, use relative_actions.
    screen_rect: tuple of 2 * int
        The screen rectangle, used to draw relatively positioned blocks.
    """

    def __init__(
        self, player="HUMAN", board_size=30, local_state=False, relative_pos=False
    ):
        """Initialize window, fps and score. Change nb_actions if relative_pos"""
        VAR.board_size = board_size
        self.local_state = local_state
        self.relative_pos = relative_pos
        self.player = player

        if player == "ROBOT":
            if self.relative_pos:
                self.nb_actions = 3
            else:
                self.nb_actions = 5

            self.action_space = self.nb_actions
            self.observation_space = np.empty(shape=(board_size ** 2,))

            self.reset()

        self.font_path = self.resource_path("resources/fonts/product_sans_bold.ttf")
        self.logo_path = self.resource_path("resources/images/ingame_snake_logo.png")

    def reset(self):
        """Reset the game environment."""
        self.steps = 0
        self.snake = Snake()
        self.food_generator = FoodGenerator(self.snake.body)
        self.food_pos = self.food_generator.pos
        self.scored = False
        self.game_over = False

        return self.state()

    def create_window(self):
        """Create a pygame display with board_size * block_size dimension."""
        pygame.init()
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.window = pygame.display.set_mode((VAR.canvas_size, VAR.canvas_size), flags)
        self.window.set_alpha(None)

        self.screen_rect = self.window.get_rect()
        self.fps = pygame.time.Clock()

    def cycle_menu(
        self,
        menu_options,
        list_menu,
        dictionary,
        img=None,
        img_rect=None,
        leaderboards=False,
    ):
        """Cycle through a given menu, waiting for an option to be clicked."""
        selected = False
        selected_option = None

        while not selected:
            pygame.event.pump()
            events = pygame.event.get()

            self.window.fill(pygame.Color(225, 225, 225))

            for i, option in enumerate(menu_options):
                if option is not None:
                    option.draw()
                    option.hovered = False

                    if (
                        option.rect.collidepoint(pygame.mouse.get_pos())
                        and option.block_type != "text"
                    ):
                        option.hovered = True

                        for event in events:
                            if event.type == pygame.MOUSEBUTTONUP:
                                if leaderboards:
                                    opt = list_menu[i]

                                    if opt == "MENU":
                                        return dictionary[opt], None
                                    else:
                                        pages = len(opt.rstrip("0123456789"))
                                        page = int(opt[pages:])
                                        selected_option = dictionary[opt[:pages]]

                                        return selected_option, page
                                else:
                                    selected_option = dictionary[list_menu[i]]

            if selected_option is not None:
                selected = True
            if img is not None:
                self.window.blit(img, img_rect.bottomleft)

            pygame.display.update()

        return selected_option

    def cycle_matches(self, n_matches, mega_hardcore=False):
        """Cycle through matches until the end."""
        score = array("i")
        step = array("i")

        for _ in range(n_matches):
            self.reset()
            self.start_match(wait=3)
            current_score, current_step = self.single_player(mega_hardcore)
            score.append(current_score)
            step.append(current_step)

        return score, step

    def menu(self):
        """Main menu of the game.

        Return
        ----------
        selected_option: int
            The selected option in the main loop.
        """
        pygame.display.set_caption("snake-on-pygame | PLAY NOW!")

        img = pygame.image.load(self.logo_path).convert()
        img = pygame.transform.scale(img, (VAR.canvas_size, int(VAR.canvas_size / 3)))
        img_rect = img.get_rect()
        img_rect.center = self.screen_rect.center
        list_menu = ["PLAY", "BENCHMARK", "LEADERBOARDS", "QUIT"]
        menu_options = [
            TextBlock(
                text=" PLAY GAME ",
                pos=(self.screen_rect.centerx, 4 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 12),
                block_type="menu",
            ),
            TextBlock(
                text=" BENCHMARK ",
                pos=(self.screen_rect.centerx, 6 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 12),
                block_type="menu",
            ),
            TextBlock(
                text=" LEADERBOARDS ",
                pos=(self.screen_rect.centerx, 8 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 12),
                block_type="menu",
            ),
            TextBlock(
                text=" QUIT ",
                pos=(self.screen_rect.centerx, 10 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 12),
                block_type="menu",
            ),
        ]
        selected_option = self.cycle_menu(
            menu_options, list_menu, OPTIONS, img, img_rect
        )

        return selected_option

    def start_match(self, wait):
        """Create some wait time before the actual drawing of the game."""
        for i in range(wait):
            self.window.fill(pygame.Color(225, 225, 225))
            time = " {:d} ".format(wait - i)

            # Game starts in 3, 2, 1
            text = [
                TextBlock(
                    text=" Game starts in ",
                    pos=(self.screen_rect.centerx, 4 * self.screen_rect.centery / 10),
                    canvas_size=VAR.canvas_size,
                    font_path=self.font_path,
                    window=self.window,
                    scale=(1 / 12),
                    block_type="text",
                ),
                TextBlock(
                    text=time,
                    pos=(self.screen_rect.centerx, 12 * self.screen_rect.centery / 10),
                    canvas_size=VAR.canvas_size,
                    font_path=self.font_path,
                    window=self.window,
                    scale=(1 / 1.5),
                    block_type="text",
                ),
            ]

            for text_block in text:
                text_block.draw()

            pygame.display.update()
            pygame.display.set_caption(
                "snake-on-pygame  |  Game starts in " + time + " second(s) ..."
            )
            pygame.time.wait(1000)

        LOGGER.info("EVENT: GAME START")

    def start(self):
        """Use menu to select the option/game mode."""
        opt = self.menu()

        while True:
            page = 1

            if opt == OPTIONS["QUIT"]:
                pygame.quit()
                sys.exit()
            elif opt == OPTIONS["PLAY"]:
                VAR.game_speed, mega_hardcore = self.select_speed()
                score, _ = self.cycle_matches(n_matches=1, mega_hardcore=mega_hardcore)
                opt = self.over(score, None)
            elif opt == OPTIONS["BENCHMARK"]:
                VAR.game_speed, mega_hardcore = self.select_speed()
                score, steps = self.cycle_matches(
                    n_matches=VAR.benchmark, mega_hardcore=mega_hardcore
                )
                opt = self.over(score, steps)
            elif opt == OPTIONS["LEADERBOARDS"]:
                while page is not None:
                    opt, page = self.view_leaderboards(page)
            elif opt == OPTIONS["MENU"]:
                opt = self.menu()
            if opt == OPTIONS["ADD_TO_LEADERBOARDS"]:
                self.add_to_leaderboards(int(np.mean(score)), int(np.mean(steps)))
                opt, page = self.view_leaderboards()

    def over(self, score, step):
        """If collision with wall or body, end the game and open options.

        Return
        ----------
        selected_option: int
            The selected option in the main loop.
        """
        score_option = None

        if len(score) == VAR.benchmark:
            score_option = TextBlock(
                text=" ADD TO LEADERBOARDS ",
                pos=(self.screen_rect.centerx, 8 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 15),
                block_type="menu",
            )

        text_score = "SCORE: " + str(int(np.mean(score)))
        list_menu = ["PLAY", "MENU", "ADD_TO_LEADERBOARDS", "QUIT"]
        menu_options = [
            TextBlock(
                text=" PLAY AGAIN ",
                pos=(self.screen_rect.centerx, 4 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 15),
                block_type="menu",
            ),
            TextBlock(
                text=" GO TO MENU ",
                pos=(self.screen_rect.centerx, 6 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 15),
                block_type="menu",
            ),
            score_option,
            TextBlock(
                text=" QUIT ",
                pos=(self.screen_rect.centerx, 10 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 15),
                block_type="menu",
            ),
            TextBlock(
                text=text_score,
                pos=(self.screen_rect.centerx, 15 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 10),
                block_type="text",
            ),
        ]
        pygame.display.set_caption(
            "snake-on-pygame  |  " + text_score + "  |  GAME OVER..."
        )
        LOGGER.info("EVENT: GAME OVER | FINAL %s", text_score)
        selected_option = self.cycle_menu(menu_options, list_menu, OPTIONS)

        return selected_option

    def select_speed(self):
        """Speed menu, right before calling start_match.

        Return
        ----------
        speed: int
            The selected speed in the main loop.
        """
        list_menu = ["EASY", "MEDIUM", "HARD", "MEGA_HARDCORE"]
        menu_options = [
            TextBlock(
                text=LEVELS[i],
                pos=(
                    self.screen_rect.centerx,
                    4 * (i + 1) * self.screen_rect.centery / 10,
                ),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 10),
                block_type="menu",
            )
            for i in range(len(list_menu))
        ]

        speed = self.cycle_menu(menu_options, list_menu, SPEEDS)
        mega_hardcore = False

        if speed == SPEEDS["MEGA_HARDCORE"]:
            mega_hardcore = True

        return speed, mega_hardcore

    def single_player(self, mega_hardcore=False):
        """Game loop for single_player (HUMANS).

        Return
        ----------
        score: int
            The final score for the match (discounted of initial length).
        """
        # The main loop, it pump key_presses and update the board every tick.
        previous_size = self.snake.length  # Initial size of the snake
        current_size = previous_size  # Initial size
        color_list = self.gradient([(VAR.head_color), (VAR.tail_color)], previous_size)

        # Main loop, where snakes moves after elapsed time is bigger than the
        # move_wait time. The last_key pressed is recorded to make the game more
        # smooth for human players.
        elapsed = 0
        last_key = self.snake.previous_action
        move_wait = VAR.game_speed

        while not self.game_over:
            elapsed += self.fps.get_time()  # Get elapsed time since last call.

            if mega_hardcore:  # Progressive speed increments, the hardest level.
                move_wait = VAR.game_speed - (2 * (self.snake.length - 3))

            key_input = self.handle_input()  # Receive inputs with tick.

            if key_input == "Q":
                return current_size - 3, self.steps
            if key_input is not None:
                last_key = key_input

            if elapsed >= move_wait:  # Move and redraw
                elapsed = 0
                self.play(last_key)
                current_size = self.snake.length  # Update the body size

                if current_size > previous_size:
                    color_list = self.gradient(
                        [(VAR.head_color), (VAR.tail_color)], current_size
                    )

                    previous_size = current_size

                self.draw(color_list)

            pygame.display.update()
            self.fps.tick(GAME_FPS)  # Limit FPS to 100

        score = current_size - 3  # After the game is over, record score

        return score, self.steps

    def check_collision(self):
        """Check wether any collisions happened with the wall or body.

        Return
        ----------
        collided: boolean
            Whether the snake collided or not.
        """
        collided = False

        if self.snake.head[0] > (VAR.board_size - 1) or self.snake.head[0] < 0:
            LOGGER.info("EVENT: WALL COLLISION")
            collided = True
        elif self.snake.head[1] > (VAR.board_size - 1) or self.snake.head[1] < 0:
            LOGGER.info("EVENT: WALL COLLISION")
            collided = True
        elif self.snake.head in self.snake.body[1:]:
            LOGGER.info("EVENT: BODY COLLISION")
            collided = True

        return collided

    def is_won(self):
        """Verify if the score is greater than 0.

        Return
        ----------
        won: boolean
            Whether the score is greater than 0.
        """
        return self.snake.length > 3

    def generate_food(self):
        """Generate new food if needed.

        Return
        ----------
        food_pos: tuple of 2 * int
            Current position of the food.
        """
        food_pos = self.food_generator.generate_food(self.snake.body)

        return food_pos

    def handle_input(self):
        """After getting current pressed keys, handle important cases.

        Return
        ----------
        action: int
            Handle human input to assess the next action.
        """
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
        keys = pygame.key.get_pressed()
        pygame.event.pump()
        action = None

        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            LOGGER.info("ACTION: KEY PRESSED: ESCAPE or Q")
            action = "Q"
        elif keys[pygame.K_LEFT]:
            LOGGER.info("ACTION: KEY PRESSED: LEFT")
            action = ABSOLUTE_ACTIONS["LEFT"]
        elif keys[pygame.K_RIGHT]:
            LOGGER.info("ACTION: KEY PRESSED: RIGHT")
            action = ABSOLUTE_ACTIONS["RIGHT"]
        elif keys[pygame.K_UP]:
            LOGGER.info("ACTION: KEY PRESSED: UP")
            action = ABSOLUTE_ACTIONS["UP"]
        elif keys[pygame.K_DOWN]:
            LOGGER.info("ACTION: KEY PRESSED: DOWN")
            action = ABSOLUTE_ACTIONS["DOWN"]

        return action

    def state(self):
        """Create a matrix of the current state of the game.

        Return
        ----------
        canvas: np.array of size board_size**2
            Return the current state of the game in a matrix.
        """
        canvas = np.zeros((VAR.board_size, VAR.board_size))

        if self.game_over:
            pass
        else:
            body = self.snake.body

            for part in body:
                canvas[part[0], part[1]] = POINT_TYPE["BODY"]

            canvas[body[0][0], body[0][1]] = POINT_TYPE["HEAD"]

            if self.local_state:
                canvas = self.eval_local_safety(canvas, body)

            canvas[self.food_pos[0], self.food_pos[1]] = POINT_TYPE["FOOD"]

        return canvas

    def relative_to_absolute(self, action):
        """Translate relative actions to absolute.

        Return
        ----------
        action: int
            Translated action from relative to absolute.
        """
        if action == RELATIVE_ACTIONS["FORWARD"]:
            action = self.snake.previous_action
        elif action == RELATIVE_ACTIONS["LEFT"]:
            if self.snake.previous_action == ABSOLUTE_ACTIONS["LEFT"]:
                action = ABSOLUTE_ACTIONS["DOWN"]
            elif self.snake.previous_action == ABSOLUTE_ACTIONS["RIGHT"]:
                action = ABSOLUTE_ACTIONS["UP"]
            elif self.snake.previous_action == ABSOLUTE_ACTIONS["UP"]:
                action = ABSOLUTE_ACTIONS["LEFT"]
            else:
                action = ABSOLUTE_ACTIONS["RIGHT"]
        else:
            if self.snake.previous_action == ABSOLUTE_ACTIONS["LEFT"]:
                action = ABSOLUTE_ACTIONS["UP"]
            elif self.snake.previous_action == ABSOLUTE_ACTIONS["RIGHT"]:
                action = ABSOLUTE_ACTIONS["DOWN"]
            elif self.snake.previous_action == ABSOLUTE_ACTIONS["UP"]:
                action = ABSOLUTE_ACTIONS["RIGHT"]
            else:
                action = ABSOLUTE_ACTIONS["LEFT"]

        return action

    def play(self, action):
        """Move the snake to the direction, eat and check collision."""
        self.scored = False
        self.steps += 1
        self.food_pos = self.generate_food()

        if self.relative_pos:
            action = self.relative_to_absolute(action)

        if self.snake.move(action, self.food_pos):
            self.scored = True
            self.food_generator.is_food_on_screen = False

        if self.player == "HUMAN":
            if self.check_collision():
                self.game_over = True
        elif self.check_collision() or self.steps > 50 * self.snake.length:
            self.game_over = True

    def get_reward(self):
        """Return the current reward. Can be used as the reward function.

        Return
        ----------
        reward: float
            Current reward of the game.
        """
        reward = REWARDS["MOVE"]

        if self.game_over:
            reward = REWARDS["GAME_OVER"]
        elif self.scored:
            reward = self.snake.length

        return reward

    def draw(self, color_list):
        """Draw the game, the snake and the food using pygame."""
        self.window.fill(pygame.Color(225, 225, 225))

        for part, color in zip(self.snake.body, color_list):
            pygame.draw.rect(
                self.window,
                color,
                pygame.Rect(
                    (part[0] * VAR.block_size),
                    part[1] * VAR.block_size,
                    VAR.block_size,
                    VAR.block_size,
                ),
            )

        pygame.draw.rect(
            self.window,
            VAR.food_color,
            pygame.Rect(
                self.food_pos[0] * VAR.block_size,
                self.food_pos[1] * VAR.block_size,
                VAR.block_size,
                VAR.block_size,
            ),
        )

        pygame.display.set_caption(
            "snake-on-pygame  |  Score: " + str(self.snake.length - 3)
        )

    def step(self, action):
        """Play the action and returns state, reward and if over."""
        self.play(action)

        return self.state(), self.get_reward(), self.game_over, None

    def render(self):
        if not hasattr(self, "window"):
            self.create_window()

        size = self.snake.length  # Size of the snake
        color_list = self.gradient([VAR.head_color, VAR.tail_color], size)
        self.draw(color_list)

        pygame.display.update()
        self.fps.tick(60)  # Limit FPS to 100

    def get_name(self):
        """See test.py in my desktop, for a textinput_box input in pygame"""
        done = False
        input_box = InputBox(
            x=200,
            y=300,
            w=140,
            h=32,
            window=self.window,
            font_path=self.resource_path("resources/fonts/product_sans_bold.ttf"),
        )

        text_block = TextBlock(
            text=" YOUR NAME ",
            pos=(self.screen_rect.centerx, 0.9 * self.screen_rect.centery),
            canvas_size=VAR.canvas_size,
            font_path=self.font_path,
            window=self.window,
            scale=(1 / 24),
            block_type="text",
        )

        while not done:
            pygame.event.pump()
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    done = True

                text = input_box.handle_event(event)

                if text is not None:
                    done = True

            input_box.update()
            self.window.fill(pygame.Color(225, 225, 225))
            input_box.draw()
            text_block.draw()

            pygame.display.update()

        return text

    def add_to_leaderboards(self, score, step):
        file_path = self.resource_path("resources/scores.json")

        name = self.get_name()
        new_score = {"name": str(name), "ranking_data": {"score": score, "step": step}}

        if not path.isfile(file_path):
            data = []
            data.append(new_score)

            with open(file_path, mode="w") as leaderboards_file:
                json.dump(data, leaderboards_file, indent=4)
        else:
            with open(file_path) as leaderboards_file:
                data = json.load(leaderboards_file)

            data.append(new_score)
            data.sort(key=lambda e: e["ranking_data"]["score"], reverse=True)

            with open(file_path, mode="w") as leaderboards_file:
                json.dump(data, leaderboards_file, indent=4)

    def view_leaderboards(self, page=1):
        file_path = self.resource_path("resources/scores.json")

        with open(file_path, "r") as leaderboards_file:
            scores_data = json.loads(leaderboards_file.read())

        dataframe = pd.DataFrame.from_dict(scores_data)
        dataframe = pd.concat(
            [
                dataframe.drop(["ranking_data"], axis=1),
                dataframe["ranking_data"].apply(pd.Series),
            ],
            axis=1,
        )  # Separate 'ranking_data' into 2 cols
        ammount_of_players = len(dataframe.index)
        players_per_page = 5
        number_of_pages = -(-ammount_of_players // players_per_page)
        score_page = []
        score_header = "  POS       NAME                       SCORE         STEP  "

        list_menu = ["LEADERBOARDS"]
        menu_options = [
            TextBlock(
                text=" LEADERBOARDS ",
                pos=(self.screen_rect.centerx, 2 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 12),
                block_type="text",
            )
        ]

        list_menu.append("HEADER")
        menu_options.append(
            TextBlock(
                text=score_header,
                pos=(self.screen_rect.centerx, 4 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 24),
                block_type="text",
                background_color=(152, 152, 152),
            )
        )

        # Adding pages to the loop
        for i in range(1, number_of_pages + 1):
            score_page.append(
                dataframe.loc[dataframe.index.intersection(range(5 * (i - 1), 5 * i))]
            )

            list_menu.append(("LEADERBOARDS{:d}".format(i)))
            menu_options.append(
                TextBlock(
                    text=(" {:d} ".format(i)),
                    pos=(
                        (2 * self.screen_rect.centerx / (number_of_pages + 1) * i),
                        (13 * self.screen_rect.centery / 10),
                    ),
                    canvas_size=VAR.canvas_size,
                    font_path=self.font_path,
                    window=self.window,
                    scale=(1 / 18),
                    block_type="menu",
                )
            )

        for i, row in score_page[page - 1].iterrows():
            list_menu.append(("RANK{:d}".format(i)))

            pos = "{0: <5}         ".format(1 + i)
            name = "{0: <25}      ".format(row["name"])
            score = "{0: <5}               ".format(row["score"])
            step = "{0: <5}  ".format(row["step"])
            data = pos + name + score + step
            menu_options.append(
                TextBlock(
                    text=data,
                    pos=(
                        self.screen_rect.centerx,
                        (
                            (5 + 1.5 * (i - (page - 1) * 5))
                            * (self.screen_rect.centery / 10)
                        ),
                    ),
                    canvas_size=VAR.canvas_size,
                    font_path=self.font_path,
                    window=self.window,
                    scale=(1 / 24),
                    block_type="text",
                )
            )

        list_menu.append("MENU")
        menu_options.append(
            TextBlock(
                text=" MENU ",
                pos=(self.screen_rect.centerx, 16 * self.screen_rect.centery / 10),
                canvas_size=VAR.canvas_size,
                font_path=self.font_path,
                window=self.window,
                scale=(1 / 12),
                block_type="menu",
            )
        )

        selected_option, page = self.cycle_menu(
            menu_options, list_menu, OPTIONS, leaderboards=True
        )

        return selected_option, page

    @staticmethod
    def format_scores(scores, ammount):
        scores = scores[-ammount:]

    @staticmethod
    def eval_local_safety(canvas, body):
        """Evaluate the safety of the head's possible next movements.

        Return
        ----------
        canvas: np.array of size board_size**2
            After using game expertise, change canvas values to DANGEROUS if true.
        """
        if (body[0][0] + 1) > (VAR.board_size - 1) or (
            [body[0][0] + 1, body[0][1]]
        ) in body[1:]:
            canvas[VAR.board_size - 1, 0] = POINT_TYPE["DANGEROUS"]
        if (body[0][0] - 1) < 0 or ([body[0][0] - 1, body[0][1]]) in body[1:]:
            canvas[VAR.board_size - 1, 1] = POINT_TYPE["DANGEROUS"]
        if (body[0][1] - 1) < 0 or ([body[0][0], body[0][1] - 1]) in body[1:]:
            canvas[VAR.board_size - 1, 2] = POINT_TYPE["DANGEROUS"]
        if (body[0][1] + 1) > (VAR.board_size - 1) or (
            [body[0][0], body[0][1] + 1]
        ) in body[1:]:
            canvas[VAR.board_size - 1, 3] = POINT_TYPE["DANGEROUS"]

        return canvas

    @staticmethod
    def gradient(colors, steps, components=3):
        """Function to create RGB gradients given 2 colors and steps. If
        component is changed to 4, it does the same to RGBA colors.

        Return
        ----------
        result: list of steps length of tuple of 3 * int (if RGBA, 4 * int)
            List of colors of calculated gradient from start to end.
        """

        def linear_gradient(start, finish, substeps):
            yield start

            for substep in range(1, substeps):
                yield tuple(
                    [
                        (
                            start[component]
                            + (float(substep) / (substeps - 1))
                            * (finish[component] - start[component])
                        )
                        for component in range(components)
                    ]
                )

        def pairs(seq):
            first_color, second_color = tee(seq)
            next(second_color, None)

            return zip(first_color, second_color)

        result = []
        substeps = int(float(steps) / (len(colors) - 1))

        for first_color, second_color in pairs(colors):
            for gradient_color in linear_gradient(first_color, second_color, substeps):
                result.append(gradient_color)

        return result

    @staticmethod
    def resource_path(relative_path):
        """Function to return absolute paths. Used while creating .exe file."""
        if hasattr(sys, "_MEIPASS"):
            return path.join(sys._MEIPASS, relative_path)

        return path.join(path.dirname(path.realpath(__file__)), relative_path)


VAR = GlobalVariables()  # Initializing GlobalVariables
LOGGER = logging.getLogger(__name__)  # Setting logger
environ["SDL_VIDEO_CENTERED"] = "1"  # Centering the window

if __name__ == "__main__":
    # The main function where the game will be executed.
    logging.basicConfig(
        format="%(asctime)s %(module)s %(levelname)s: %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level=logging.INFO,
    )
    GAME = Game(player="HUMAN")
    GAME.create_window()
    GAME.start()
