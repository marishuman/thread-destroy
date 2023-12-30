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
    QTextEdit
)

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from time import sleep
from plotly.graph_objects import Figure, Scatter
import plotly

import numpy as np


DLY = 0.1

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
            sleep(DLY)
            self.update_signal.emit(f"pass {self.thread_id} cnt {self.cnt}")
            self.cnt += 1
    
    def quit(self):
        self.running = False


class Window(QMainWindow, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
                # some example data
        x = np.arange(1000)
        y = x**2

        # create the plotly figure
        fig = Figure(Scatter(x=x, y=y))

        # we create html code of the figure
        html = '<html><body>'
        html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
        html += '</body></html>'

        # we create an instance of QWebEngineView and set the html code
        plot_widget = QWebEngineView()
        plot_widget.setHtml(html)

        # set the QWebEngineView instance as main widget
        self.setCentralWidget(plot_widget)

        self.setupUi()
    
    def setupUi(self):
        self.working = False

        self.setWindowTitle("QThread")
        self.resize(250, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.label = QLabel("Hello, World!")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.countBtn = QPushButton("Start!")

        layout = QVBoxLayout()
        self.textbox = QTextEdit()
        layout.addWidget(self.label)
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


# def on_clicked(msg, window_instance):
#     window_instance.label.setText("Change")
#     runTasks(window_instance, int(msg))

# def runTasks(window_instance, msg):
#     thread_list = []

#     for i in range(msg):
#         worker = Worker(i, window_instance)
#         worker.update_signal.connect(window_instance.update_label)
#         worker.finished_signal.connect(lambda: thread_finished(worker, thread_list, window_instance))
#         worker.start()
#         thread_list.append(worker)


# def thread_finished(worker, thread_list, window_instance):
#     if worker in thread_list:
#         thread_list.remove(worker)
#         worker.deleteLater()

#         if not thread_list:
#             window_instance.close()

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
