
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


        # # generate something to export
        # plt = pg.plot([1,5,2,4,3])

        # # create an exporter instance, as an argument give it
        # # the item you wish to export
        # exporter = pg.exporters.ImageExporter(plt.plotItem)

        # # set export parameters if needed
        # exporter.parameters()['width'] = 100   # (note this also affects height parameter)
        # global w
        # w = pg.ColorMapWidget()

        # export to widget
        # exporter = pg.exporters.ImageExporter( w.scene() )
        # self.worker = Worker(parent)

        self.setupUi()
        


    

    # def plot_polar_coordinate(self, x, y):
        # Convert individual x and y coordinates to polar coordinates
        # r = np.sqrt(x**2 + y**2)
        # theta = np.arctan2(y, x)

        # self.setWindowTitle("Heatmap")
        # self.setStyleSheet("background-color: lightgray;")
        # self.resize(500, 500)

        # layout = QVBoxLayout()  # Adjust layout for better organization

        # graphWidget = pg.ImageView()
        # # Generating a simple heatmap using the provided polar coordinates
        # data = np.random.rand(5, 5)
        # graphWidget.setImage(data)
        # # Defining a colormap for the heatmap
        # colors = [(0, 0, 0), (4, 5, 61), (84, 42, 55), (15, 87, 60), (208, 17, 141), (255, 255, 255)]
        # colormap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
        # graphWidget.setColorMap(colormap)

        # layout.addWidget(graphWidget)

        # widget = QWidget()
        # widget.setLayout(layout)

        # self.setCentralWidget(widget)

    # def add_points(self):
        # generate something to export
  
        # self.plot_polar_coordinate(1, 1)
            

    
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
        x_column = data[x_index, :, :]
        y_column = data[y_index, :, :]

        # Convert Cartesian to polar coordinates
        radius = np.sqrt(x_column**2 + y_column**2)
        theta = np.arctan2(y_column, x_column)

        # Replace the original data with polar coordinates
        data[x_index, :, :] = radius
        data[y_index, :, :] = theta

 
        # # adding time-varying signal
        # sig = np.zeros(data.shape[0])
        # sig[30:] += np.exp(-np.linspace(1, 10, 70))
        # sig[40:] += np.exp(-np.linspace(1, 10, 60))
        # sig[70:] += np.exp(-np.linspace(1, 10, 30))
 
        # sig = sig[:, np.newaxis, np.newaxis] * 3
        # data[:, 50:60, 30:40] += sig
 
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
