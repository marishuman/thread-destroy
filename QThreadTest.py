
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from time import sleep

DLY = 0.1

class Worker(QThread):

    update_signal = pyqtSignal(object)

    def __init__(self, idx):
        super().__init__()
        self.idx = idx
        self.cnt = 0
        self.running = False
        
    def run(self):
        self.running = True
        while self.running:
            sleep(DLY)
            self.update_signal.emit(f"pass {self.idx} cnt {self.cnt}")
            self.cnt += 1
            
    def quit(self):
        self.running = False
        
        
class Window(QMainWindow, QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
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


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
