from enum import Enum

IMAGE_PATH = "assets/png/{image}.png"

IMAGES = {
    # Number Board
    'BOARD_ZERO': "score_0",
    'BOARD_ONE': "score_1",
    'BOARD_TWO': "score_2",
    'BOARD_THREE': "score_3",
    'BOARD_FOUR': "score_4",
    'BOARD_FIVE': "score_5",
    'BOARD_SIX': "score_6",
    'BOARD_SEVEN': "score_7",
    'BOARD_EIGHT': "score_8",
    'BOARD_NINE': "score_9",

    # Reset Button
    'RESET_NORMAL': "smiley",
    'RESET_PRESSED': "smiley_pressed",
    'RESET_SWEEP': "smiley_surprised",
    'RESET_WON': "smiley_cool",
    'RESET_LOST': "smiley_rip",

    # Mine
    'MINE_NONE': "mine_pressed",
    'MINE_ONE': "mine_1",
    'MINE_TWO': "mine_2",
    'MINE_THREE': "mine_3",
    'MINE_FOUR': "mine_4",
    'MINE_FIVE': "mine_5",
    'MINE_SIX': "mine_6",
    'MINE_SEVEN': "mine_7",
    'MINE_EIGHT': "mine_8",
    'MINE_UNMARKED': "mine_unmarked",
    'MINE_FLAG': "flag",
    'MINE_QUESTION': "question",
    'MINE_MINE': "bomb",
    'MINE_EXPLOSION': "bomb_red",
    'MINE_NO_MINE': "bomb_x"
}

UNIT = 32

GAME_NAME = "Pynsweeper"


class ScoreNumberState(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9


class ResetButtonState(Enum):
    NORMAL = 1
    PRESSED = 2
    SWEEP = 3
    WON = 4
    LOST = 5


class SiteState(Enum):
    NONE = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    UNMARKED = 9
    FLAG = 10
    QUESTION = 11
    MINE = 12
    EXPLOSION = 13
    NO_MINE = 14
