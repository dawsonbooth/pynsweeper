import argparse

from PyQt5.QtWidgets import QApplication, QStyleFactory

from utils import MainWindow

if __name__ == '__main__':
    app = QApplication([])
    win = MainWindow()
    app.setStyle(QStyleFactory.create('Windows'))
    win.show()
    app.exec_()
