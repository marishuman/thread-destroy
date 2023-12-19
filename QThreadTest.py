import logging
import sys
import time
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

logging.basicConfig(format="%(message)s", level=logging.INFO)


class Worker(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, n, window_instance):
        super().__init__()
        self.n = n
        self.window_instance = window_instance

    def runTasks(window_instance, msg):
        thread_list = []

        for i in range(msg):
            worker = Worker(i, window_instance)
            worker.update_signal.connect(window_instance.update_label)
            worker.start()
            thread_list.append(worker)

        # Wait for all threads to finish
        for thread in thread_list:
            thread.wait()

        # Close the window after all threads finish
        window_instance.close()


class Window(QMainWindow, QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("QThread")
        self.resize(250, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.label = QLabel("Hello, World!")
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        countBtn = QPushButton("Click me!")

        layout = QVBoxLayout()
        textbox = QTextEdit()
        layout.addWidget(self.label)
        layout.addWidget(countBtn)
        layout.addWidget(textbox)
        self.centralWidget.setLayout(layout)

        countBtn.clicked.connect(lambda: on_clicked(textbox.toPlainText(), self))

    def closeEvent(self, event):
        print('Close event fired')
        event.accept()

    def update_label(self, msg):
        self.label.setText(msg)


def on_clicked(msg, window_instance):
    window_instance.label.setText("Change")
    runTasks(window_instance, int(msg))


def runTasks(window_instance, msg):
    for i in range(msg):
        worker = Worker(i, window_instance)
        worker.update_signal.connect(window_instance.update_label)
        worker.start()


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())