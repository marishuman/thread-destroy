
import pyqtgraph as pg

from pyqtgraph import PlotWidget
import pyqtgraph.exporters


import logging
import numpy as np
from vispy import app, gloo
from vispy.util.transforms import perspective, translate, rotate
from vispy.geometry import meshdata as md
from vispy.geometry import generation as gen
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit, 
    QHBoxLayout,
    QGridLayout
)

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from time import sleep

class Window(QMainWindow, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        window = QMainWindow()
        centralWidget = QWidget()

        pg.setConfigOption('background', 'lightgray')
        # Generate grid coordinates
        x, y = np.meshgrid(np.linspace(-1, 1, 100), np.linspace(-1, 1, 100))

        # Create a circular mask
        mask = x**2 + y**2 <= 1

        # Generate data
        data = np.random.rand(100, 100)  # Sample random data

        # Set values outside circle as NaN
        data[~mask] = np.nan

        # Create an ImageView widget
        imv = pg.ImageView()

        # Display circular heatmap
        imv.setImage(data)

        # Optionally set color map, labels, etc.
        imv.show()
        layout = QVBoxLayout()
        layout.addWidget(imv)
        centralWidget.setLayout(layout)
        window.setCentralWidget(centralWidget)

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())