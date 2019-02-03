from random import randint

import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from collections import defaultdict

from constants import *


class ScoreNumber(QLabel):
    def __init__(self, digit='0', *args, **kwargs):
        super(ScoreNumber, self).__init__(*args, **kwargs)

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

    def __init__(self, value=0, *args, **kwargs):
        super(ScoreBoard, self).__init__(*args, **kwargs)

        self.numbers = [ScoreNumber(), ScoreNumber(), ScoreNumber()]

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
        self -= 1


class ResetButton(QLabel):
    click_release = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(ResetButton, self).__init__(*args, **kwargs)

        self.setFixedSize(UNIT*2, UNIT*2)
        self.setScaledContents(True)

        self.set_state(ResetButtonState.NORMAL)

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
    def __init__(self, *args, **kwargs):
        super(MenuSection, self).__init__(*args, **kwargs)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.scoreBoard = ScoreBoard()
        self.resetButton = ResetButton()
        self.clock = ScoreBoard()

        self.layout.addWidget(self.scoreBoard)
        self.layout.addStretch()
        self.layout.addWidget(self.resetButton)
        self.layout.addStretch()
        self.layout.addWidget(self.clock)


class Site(QLabel):
    click_hold = pyqtSignal()
    click_release = pyqtSignal([tuple])

    def __init__(self, r, c, *args, **kwargs):
        super(Site, self).__init__(
            width=UNIT, height=UNIT, *args, **kwargs)

        self.setFixedSize(UNIT, UNIT)
        self.setScaledContents(True)

        self.coord = (r, c)

        self.swept = False
        self.has_mine = False
        self.count = 0
        self.unmark()

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

    def sweep(self):
        if not self.swept:
            self.swept = True
            if self.has_mine:
                self.set_state(SiteState.EXPLOSION)
            else:
                self.set_state(SiteState(self.count))
                return self.count

    def mark(self):
        if not self.swept:
            if (self.state == SiteState.UNMARKED):
                self.flag()
            elif (self.state == SiteState.FLAG):
                self.question()
            elif (self.state == SiteState.QUESTION):
                self.unmark()

    def flag(self):
        self.set_state(SiteState.FLAG)
        # TODO: Increase some counter if mine (maybe in other class)

    def question(self):
        self.set_state(SiteState.QUESTION)

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
        if not self.swept:
            if mouse.button() == Qt.LeftButton:
                self.press()
            if mouse.button() == Qt.RightButton:
                self.mark()

    def mouseReleaseEvent(self, mouse):
        if not self.swept:
            if mouse.button() == Qt.LeftButton:
                self.click_release.emit(self.coord)


class MineField(QWidget):
    def __init__(self, field_width=16, field_height=16, num_mines=40, *args, **kwargs):
        super(MineField, self).__init__(*args, **kwargs)

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
        self.field = [[Site(r, c) for c in range(self.field_width)]
                      for r in range(self.field_height)]

        self.add_sites()

    def neighbors(self, site: Site):
        x, y = site.coord
        X, Y = self.field_width, self.field_height
        for x2 in range(x-1, x+2):
            for y2 in range(y-1, y+2):
                if ((x != x2 or y != y2) and (0 <= x2 < X) and (0 <= y2 < Y)):
                    yield self.field[x2][y2]

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

    def add_sites(self):
        for r in range(self.field_width):
            for c in range(self.field_height):
                self.layout.addWidget(self.field[r][c], r, c)

    def reset_field(self):
        for row in self.field:
            for site in row:
                site.reset()


class GameSection(QWidget):
    def __init__(self, *args, **kwargs):
        super(GameSection, self).__init__(*args, **kwargs)

        self.mineField = MineField()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addStretch()
        self.layout.addWidget(self.mineField)
        self.layout.addStretch()


class Game(QWidget):
    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        # Setup
        self.menuSection = MenuSection()
        self.gameSection = GameSection()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.menuSection)
        self.layout.addStretch()
        self.layout.addWidget(self.gameSection)
        self.layout.addStretch()

        # Game Properties
        self.timer = QTimer()
        self.in_play = False

        # Connections
        self.timer.timeout.connect(self.menuSection.clock.increment)
        self.menuSection.resetButton.click_release.connect(self.resetGame)
        for r in self.gameSection.mineField.field:
            for m in r:
                m.click_release.connect(self.sweep)

    def sweep(self, coord, prev=[]):
        x, y = coord
        site = self.gameSection.mineField.field[x][y]
        site.sweep()
        prev.append(coord)
        if site.count == 0 and not site.has_mine:
            for neighbor in self.gameSection.mineField.neighbors(site):
                if neighbor.coord not in prev and not neighbor.has_mine:
                    print(x, y)
                    self.sweep(neighbor.coord, prev)

    def startGame(self):
        self.gameSection.mineField.reset_field()
        self.gameSection.mineField.place_mines()
        self.menuSection.scoreBoard.update_value(
            self.gameSection.mineField.num_mines)
        self.timer.start(1000)
        self.in_play = True

    def endGame(self):
        # TODO: Reveal everything
        self.menuSection.clock.update_value(0)
        self.timer.stop()
        self.in_play = False

    def resetGame(self):
        self.endGame()
        self.startGame()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.game = Game()
        self.setCentralWidget(self.game)
        self.setWindowTitle(GAME_NAME)

        self.game.startGame()
