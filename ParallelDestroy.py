import logging
import random
import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtCore import QRunnable, Qt, QThreadPool
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logging.basicConfig(format="%(message)s", level=logging.INFO)

# 1. Subclass QRunnable
class Runnable(QRunnable):
    def __init__(self, n, window_instance):
        super().__init__()
        self.n = n
        self.window_instance = window_instance

    def run(self):
        # Long running task
        for i in range(5):
            logging.info(f"Working in thread {self.n}, step {i + 1}/5")
            time.sleep(random.randint(700, 2500) / 1000)
   
            # self.window_instance.changeLabel("aaaa")

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("QThreadPool + QRunnable")
        self.resize(250, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # Create and connect widgets
        self.label = QLabel("Hello, World!")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        countBtn = QPushButton("Click me!")
        # countBtn.clicked.connect(self.runTasks)
        
        # Set the layout
        layout = QVBoxLayout()
        textbox = QTextEdit()
        layout.addWidget(self.label)
        layout.addWidget(countBtn)
        layout.addWidget(textbox)
        self.centralWidget.setLayout(layout)

        countBtn.clicked.connect(lambda: on_clicked(textbox.toPlainText(), self))

    def changeLabel(msg, self):
        self.textbox.setText(msg)
    def closeEvent(self, event):
        print('Close event fired')
    

def runTasks(self, msg):
    threadCount = QThreadPool.globalInstance().maxThreadCount()
    self.label.setText(f"Running {msg} Threads")
    pool = QThreadPool.globalInstance()
    for i in range(msg):
        # 2. Instantiate the subclass of QRunnable
        runnable = Runnable(i, self)
        # 3. Call start()
        pool.start(runnable)

def on_clicked(msg, self):
    self.label.setText("Change")
    runTasks(self, int(msg))


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())