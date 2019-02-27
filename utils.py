from random import randint

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from collections import defaultdict

from constants import *


class ScoreNumber(QLabel):
    def __init__(self, game, digit='0', *args, **kwargs):
        super(ScoreNumber, self).__init__(*args, **kwargs)

        self.game = game

        self.setFixedSize(UNIT, UNIT*2)
        self.setScaledContents(True)

        self.digit = digit
        self.set_state(ScoreNumberState.ZERO)

    def set_state(self, state: ScoreNumberState):
        self.state = state
        # TODO: Account for -
        img_path = IMAGE_PATH.format(image=IMAGES["BOARD_"+state.name])
        pixmap = QPixmap(img_path)
        self.setPixmap(pixmap)

    def update_digit(self, digit: str):
        self.digit = digit
        state = ScoreNumberState(int(digit))
        self.set_state(state)


class ScoreBoard(QWidget):

    def __init__(self, game, value=0, *args, **kwargs):
        super(ScoreBoard, self).__init__(*args, **kwargs)

        self.game = game

        self.numbers = [ScoreNumber(self.game), ScoreNumber(
            self.game), ScoreNumber(self.game)]

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignRight)
        self.setLayout(self.layout)

        for n in self.numbers:
            self.layout.addWidget(n)

        self.value = value

    def update_value(self, value: int):
        self.value = value

        digits = str(value)

        while len(digits) < 3:
            digits = '0' + digits

        for n in range(len(self.numbers)):
            self.numbers[n].update_digit(digits[n])

    def __add__(self, k):
        self.update_value(self.value + k)

    def increment(self):
        self += 1

    def decrement(self):
        self += -1


class ResetButton(QLabel):
    click_release = pyqtSignal()

    def __init__(self, game, *args, **kwargs):
        super(ResetButton, self).__init__(*args, **kwargs)

        self.game = game

        self.setFixedSize(UNIT*2, UNIT*2)
        self.setScaledContents(True)

        self.set_state(ResetButtonState.NORMAL)

        # Connections
        self.game.win_game.connect(
            lambda: self.set_state(ResetButtonState.WON))
        self.game.lose_game.connect(
            lambda: self.set_state(ResetButtonState.LOST))

    def set_state(self, state: ResetButtonState):
        self.state = state
        img_path = IMAGE_PATH.format(image=IMAGES["RESET_"+state.name])
        pixmap = QPixmap(img_path)
        self.setPixmap(pixmap)

    def press(self):
        self.set_state(ResetButtonState.PRESSED)

    def release(self):
        self.set_state(ResetButtonState.NORMAL)
        self.click_release.emit()

    def mousePressEvent(self, mouse):
        self.press()

    def mouseReleaseEvent(self, mouse):
        self.release()


class MenuSection(QWidget):
    def __init__(self, game, *args, **kwargs):
        super(MenuSection, self).__init__(*args, **kwargs)

        self.game = game

        self.score_board = ScoreBoard(self.game)
        self.reset_button = ResetButton(self.game)
        self.clock = ScoreBoard(self.game)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.score_board)
        self.layout.addStretch()
        self.layout.addWidget(self.reset_button)
        self.layout.addStretch()
        self.layout.addWidget(self.clock)


class Site(QLabel):
    click_hold = pyqtSignal()
    click_release = pyqtSignal([tuple])
    flag_added = pyqtSignal()
    flag_removed = pyqtSignal()

    def __init__(self, game, r, c, *args, **kwargs):
        super(Site, self).__init__(
            width=UNIT, height=UNIT, *args, **kwargs)

        self.game = game

        self.setFixedSize(UNIT, UNIT)
        self.setScaledContents(True)

        self.coord = (r, c)

        self.swept = False
        self.has_mine = False
        self.count = 0
        self.unmark()

        # Connections
        self.game.lose_game.connect(self.reveal)

    def place_mine(self):
        self.has_mine = True

    def set_state(self, state: SiteState):
        self.state = state
        self.setText(str(state.value))
        img_path = IMAGE_PATH.format(image=IMAGES["MINE_"+state.name])
        pixmap = QPixmap(img_path)
        self.setPixmap(pixmap)

    def show_mine(self):
        if self.has_mine:
            self.set_state(SiteState.MINE)

    def reveal(self):
        if self.has_mine and self.state not in (SiteState.FLAG, SiteState.EXPLOSION):
            self.show_mine()

    def sweep(self):
        if not self.swept:
            self.swept = True
            if self.has_mine:
                self.set_state(SiteState.EXPLOSION)
                self.game.lose_game.emit()
            else:
                self.set_state(SiteState(self.count))
                return self.count

    def mark(self):
        if not self.swept:
            if (self.state == SiteState.UNMARKED):
                self.set_state(SiteState.FLAG)
                self.flag_added.emit()
            elif (self.state == SiteState.FLAG):
                self.set_state(SiteState.QUESTION)
                self.flag_removed.emit()
            elif (self.state == SiteState.QUESTION):
                self.unmark()

    def unmark(self):
        self.set_state(SiteState.UNMARKED)

    def reset(self):
        self.swept = False
        self.has_mine = False
        self.count = 0
        self.unmark()

    def press(self):
        self.set_state(SiteState.NONE)
        self.click_hold.emit()

    def mousePressEvent(self, mouse):
        if not self.game.in_play:
            return
        if not self.swept:
            if mouse.button() == Qt.LeftButton:
                self.press()
            if mouse.button() == Qt.RightButton:
                self.mark()

    def mouseReleaseEvent(self, mouse):
        if not self.game.in_play:
            return
        if not self.swept:
            if mouse.button() == Qt.LeftButton:
                self.click_release.emit(self.coord)

        if all((site.swept or site.state == SiteState.FLAG) for site in self.game.game_section.mine_field.sites()):
            self.game.win_game.emit()


class MineField(QWidget):
    def __init__(self, game, field_width=16, field_height=16, num_mines=40,
                 *args, **kwargs):
        super(MineField, self).__init__(*args, **kwargs)

        self.game = game

        self.setFixedSize(field_width*UNIT, field_height*UNIT)

        # Layout
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self.layout)

        # Variables
        self.field_width = field_width
        self.field_height = field_height
        self.num_mines = num_mines
        self.field = [[Site(self.game, r, c) for c in range(self.field_width)]
                      for r in range(self.field_height)]

        self.add_sites()

    def place_mines(self):
        for n in range(self.num_mines):
            r = randint(0, self.field_width - 1)
            c = randint(0, self.field_height - 1)
            while self.field[r][c].has_mine:
                r = randint(0, self.field_width - 1)
                c = randint(0, self.field_height - 1)
            self.field[r][c].place_mine()
            for site in self.neighbors(self.field[r][c]):
                site.count += 1

    def neighbors(self, site: Site):
        x, y = site.coord
        X, Y = self.field_width, self.field_height
        for x2 in range(x-1, x+2):
            for y2 in range(y-1, y+2):
                if ((x != x2 or y != y2) and (0 <= x2 < X) and (0 <= y2 < Y)):
                    yield self.field[x2][y2]

    def sites(self):
        for row in self.field:
            for site in row:
                yield site

    def add_sites(self):
        for r in range(self.field_width):
            for c in range(self.field_height):
                self.layout.addWidget(self.field[r][c], r, c)

    def reset_field(self):
        for site in self.sites():
            site.reset()


class GameSection(QWidget):
    def __init__(self, game, *args, **kwargs):
        super(GameSection, self).__init__(*args, **kwargs)

        self.game = game

        self.mine_field = MineField(self.game)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addStretch()
        self.layout.addWidget(self.mine_field)
        self.layout.addStretch()


class Game(QWidget):
    win_game = pyqtSignal()
    lose_game = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        # Setup
        self.menu_section = MenuSection(self)
        self.game_section = GameSection(self)

        # Format
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.menu_section)
        self.layout.addStretch()
        self.layout.addWidget(self.game_section)
        self.layout.addStretch()

        # Game Properties
        self.timer = QTimer()

        # Connections
        self.lose_game.connect(self.end_game)
        self.win_game.connect(self.end_game)
        self.timer.timeout.connect(self.menu_section.clock.increment)
        self.menu_section.reset_button.click_release.connect(self.reset_game)
        for r in self.game_section.mine_field.field:
            for m in r:
                m.click_release.connect(self.sweep_recursive)
                m.flag_added.connect(self.menu_section.score_board.decrement)
                m.flag_removed.connect(self.menu_section.score_board.increment)

    def sweep_recursive(self, coord):
        # TODO: Move to Site class
        x, y = coord
        site = self.game_section.mine_field.field[x][y]
        if site.swept:
            return
        site.sweep()
        if site.count == 0 and not site.has_mine:
            for neighbor in self.game_section.mine_field.neighbors(site):
                if not neighbor.has_mine:
                    self.sweep_recursive(neighbor.coord)

    def start_game(self):
        self.game_section.mine_field.reset_field()
        self.game_section.mine_field.place_mines()
        self.menu_section.score_board.update_value(
            self.game_section.mine_field.num_mines)
        self.timer.start(1000)
        self.in_play = True

    def end_game(self):
        self.timer.stop()
        self.in_play = False

    def reset_game(self):
        self.end_game()
        self.menu_section.clock.update_value(0)
        self.start_game()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.game = Game()
        self.setCentralWidget(self.game)
        self.setWindowTitle(GAME_NAME)

        self.game.start_game()
