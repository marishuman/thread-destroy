from asyncio import TimerHandle
import math
import threading
from qtpy import QtWidgets
from qt_thread_updater import get_updater
import time
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
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5 import QtCore
from time import sleep


import zmq


from radar_format import MAG_TYPE, MOMENT_PORT, unpackRadData
pg.setConfigOption('background', 'lightgray')

w= None
running = True

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
        
        # starts the subscriber thread to print data from simulation.py
        self.subscriber_thread = RadSubscriber()
        self.subscriber_thread.start()

        # setting configuration options
        pg.setConfigOptions(antialias=True)
 
        # creating image view object
        self.imv = pg.ImageView()
 
        # Create random 3D data set with noisy signals
        img = pg.gaussianFilter(np.random.normal(
            size=(200, 200)), (5, 5)) * 20 + 100
 
        # setting new axis to image
        img = img[np.newaxis, :, :]
 
        # # decay data
        # decay = np.exp(-np.linspace(0, 0.3, 200))[:, np.newaxis, np.newaxis]
    
        new_data = generate_new_data(self, self.subscriber_thread.latest_data)
        
        # random data
        # data = np.random.normal(size=(200, 200, 200))
        # data += img * decay
        # data += 2
        
        # Cartesian coordinates from data
        x_index = 0  # x column index
        y_index = 1  # y column index
        radius= new_data[x_index, :, :]
        theta = new_data[y_index, :, :]

        # Convert Cartesian to polar coordinates
        x_column = radius*np.cos(theta)
        y_column = radius*np.sin(theta)


        # Replace the original data with polar coordinates
        new_data[x_index, :, :] = x_column
        new_data[y_index, :, :] = y_column

        # Generate grid coordinates
        x, y = np.meshgrid(np.linspace(-1, 1, 200), np.linspace(-1, 1, 200))

        # Create a circular mask
        mask = x**2 + y**2 <= 1

        # Set values outside circle as NaN
        new_data[0][~mask] = np.nan

        # Set values outside circle as NaN
        new_data[1][~mask] = np.nan

        # Displaying the data and assign each frame a time value from 1.0 to 3.0
        self.imv.setImage(new_data)
 
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
        self.imv.setColorMap(cmap)

        # Disable scroll zooming
        self.imv.view.setMouseEnabled(x=False, y=False)

        # Disable the histogram (color bar)
        self.imv.ui.histogram.hide()

        # Disable the ROI button
        self.imv.ui.roiBtn.hide()

        # Disable the ROI plot
        self.imv.ui.roiPlot.hide()

        # Hide the menu
        self.imv.ui.menuBtn.hide()

        # Creating a grid layout
        layout = QGridLayout()
 
        # setting this layout to the widget
        self.centralWidget.setLayout(layout)

        # plot window goes on right side, spanning 3 rows
        layout.addWidget(self.imv, 0, 1, 3, 1)
 
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
        # Create a QTimer to update the colormap every 3 seconds
        self.timer = QtCore.QTimer(self)
        
        self.timer.timeout.connect(self.updateColormap)
        self.timer.start(3000)  # Update every 3 seconds

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

    def updateColormap(self):
        new_data = generate_new_data(self, self.subscriber_thread.latest_data)
        
         # Cartesian coordinates from data
        x_index = 0  # x column index
        y_index = 1  # y column index
        radius= new_data[x_index, :, :]
        theta = new_data[y_index, :, :]

        # Convert Cartesian to polar coordinates
        x_column = radius*np.cos(theta)
        y_column = radius*np.sin(theta)

        new_data[x_index, :, :] = x_column
        new_data[y_index, :, :] = y_column
        
        x, y = np.meshgrid(np.linspace(-1, 1, 200), np.linspace(-1, 1, 200))

        # Create a circular mask
        mask = x**2 + y**2 <= 1

        # Set values outside circle as NaN
        new_data[0][~mask] = np.nan

        # Set values outside circle as NaN
        new_data[1][~mask] = np.nan

        # Update the image view with the new colormap
        self.imv.setImage(new_data)

        return


def process_radar_data(data):
    
    return np.random.normal(size=(200, 200, 200))

def generate_new_data(self, radar_data):
    if radar_data is not None:
        # Process the radar data and generate new data array for colormap
        # Example: You can replace this with your actual data processing logic
        new_data = np.random.rand(3, 200, 200)
        return new_data
    else:
        # If no new data is available, return the existing data
        return self.imv.getImageItem().image 
    
#SUBSCRIBER PART
class RadSubscriber(threading.Thread):
    #sets up the subscriber to take in the publisher data from simulation.py
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.socket = zmq.Context().socket(zmq.SUB)
        self.socket.connect("tcp://localhost:%s" % MOMENT_PORT)
        self.socket.setsockopt(zmq.SUBSCRIBE, MAG_TYPE)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.latest_data = np.random.normal(size=(200, 200, 200))
        self.running = True

   
    #prints out the data published by the publisher in simulation.py in the format below
    def run(self):
        while running:
            rsv = dict(self.poller.poll(.5))
            if rsv:
                if rsv.get(self.socket) == zmq.POLLIN:
                    s = self.socket.recv()
                    s = s[len(MAG_TYPE)::]
                    [ant, azi, sec, tic, sps, data] = unpackRadData(s)
                    # print("ant %d,\tazimuth %f,\tsec %d,\ttic %d" % (ant, azi, sec, tic))
                    self.latest_data = process_radar_data(data)  # Implement this function to process radar data

    

    def get_latest_data(self):
        # return self.latest_data
        # Putting this dummy data in for debugging purposes
        return np.random.normal(size=(200, 200, 200))
    
    def stop(self):
        self.running = False
        self.socket.close()
        

app = QApplication(sys.argv)
window = Window()
window.show()

sys.exit(app.exec())
subscriber_thread.stop()