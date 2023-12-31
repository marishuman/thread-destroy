
import math
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
pg.setConfigOption('background', 'lightgray')

w= None

class Worker(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, thread_id):
        super().__init__()
        self.thread_id = thread_id
        self.cnt = 0
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.update_signal.emit(f"pass {self.thread_id} cnt {self.cnt}")
            self.cnt += 1
    
    def quit(self):
        self.running = False

class Window(QMainWindow, QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi()
            
    def setupUi(self):
        self.working = False
        # creating a widget object
        
        self.setWindowTitle("QThread")
        self.resize(250, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        
        # widget = QWidget()

        # setting configuration options
        pg.setConfigOptions(antialias=True)
 
        # creating image view object
        imv = pg.ImageView()
 
        # Create random 3D data set with noisy signals
        img = pg.gaussianFilter(np.random.normal(
            size=(200, 200)), (5, 5)) * 20 + 100
 
        # setting new axis to image
        img = img[np.newaxis, :, :]
 
        # decay data
        decay = np.exp(-np.linspace(0, 0.3, 200))[:, np.newaxis, np.newaxis]
    

        # random data
        data = np.random.normal(size=(200, 200, 200))
        data += img * decay
        data += 2
        
        # Cartesian coordinates from data
        x_index = 0  # x column index
        y_index = 1  # y column index
        radius= data[x_index, :, :]
        theta = data[y_index, :, :]

        # Convert Cartesian to polar coordinates
        x_column = radius*np.cos(theta)
        y_column = radius*np.sin(theta)


        # Replace the original data with polar coordinates
        data[x_index, :, :] = x_column
        data[y_index, :, :] = y_column

        # Generate grid coordinates
        x, y = np.meshgrid(np.linspace(-1, 1, 200), np.linspace(-1, 1, 200))

        # Create a circular mask
        mask = x**2 + y**2 <= 1

        # Set values outside circle as NaN
        data[0][~mask] = np.nan

        # Set values outside circle as NaN
        data[1][~mask] = np.nan

        # Displaying the data and assign each frame a time value from 1.0 to 3.0
        imv.setImage(data)
 
        # Set a custom color map
        colors = [
            (0, 0, 0),
            (4, 5, 61),
            (84, 42, 55),
            (15, 87, 60),
            (208, 17, 141),
            (255, 255, 255)
        ]
 
        # color map
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)

        # setting color map to the image view
        imv.setColorMap(cmap)

        # Disable scroll zooming
        imv.view.setMouseEnabled(x=False, y=False)

        # Disable the histogram (color bar)
        imv.ui.histogram.hide()

        # Disable the ROI button
        imv.ui.roiBtn.hide()

        # Disable the ROI plot
        imv.ui.roiPlot.hide()

        # Hide the menu
        imv.ui.menuBtn.hide()

        # Creating a grid layout
        layout = QGridLayout()
 
        # setting this layout to the widget
        self.centralWidget.setLayout(layout)

        # plot window goes on right side, spanning 3 rows
        layout.addWidget(imv, 0, 1, 3, 1)
 
        # setting this widget as central widget of the main window
        self.setCentralWidget(self.centralWidget)

        # self.add_points()
        
    
        self.label = QLabel("Hello, World!")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.countBtn = QPushButton("Start!")

        layout = QVBoxLayout()
        self.textbox = QTextEdit()
        layout.addWidget(self.label)
        layout.addWidget(w)
        layout.addWidget(self.countBtn)
        layout.addWidget(self.textbox)
        self.centralWidget.setLayout(layout)
        self.countBtn.clicked.connect(self.countBtnClicked)

        self.cnts = 0

    def closeEvent(self, event):
        if self.working:
            self.stopWorker()
        print('Close event fired')
        event.accept()

    def update_label(self, msg):
        self.textbox.setText(msg)
        
    def startWorker(self):
        self.worker = Worker(self.cnts)
        self.worker.update_signal.connect(self.update_label)
        self.worker.start()
        self.working = True

    def stopWorker(self):
        self.worker.quit()
        self.worker.wait()
        self.cnts += 1
        self.working = False
                        
    def countBtnClicked(self):
        if not self.working:
            self.startWorker()
            self.countBtn.setText("Stop!")
        else:
            self.stopWorker()
            self.countBtn.setText("Start!")

    

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
