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
    finished_signal = pyqtSignal()

    def __init__(self, thread_id, window_instance):
        super().__init__()
        self.thread_id = thread_id
        self.window_instance = window_instance

    def run(self):
        for i in range(5):
            logging.info(f"Working in thread {self.thread_id}, step {i + 1}/5")
            time.sleep(1)

        self.update_signal.emit(f"Thread {self.thread_id} completed.")
        self.finished_signal.emit()


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
    thread_list = []

    for i in range(msg):
        worker = Worker(i, window_instance)
        worker.update_signal.connect(window_instance.update_label)
        worker.finished_signal.connect(lambda: thread_finished(worker, thread_list, window_instance))
        worker.start()
        thread_list.append(worker)


def thread_finished(worker, thread_list, window_instance):
    if worker in thread_list:
        thread_list.remove(worker)
        worker.deleteLater()

        if not thread_list:
            window_instance.close()

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())