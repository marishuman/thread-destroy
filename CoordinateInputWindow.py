import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import zmq
from time import sleep

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://127.0.0.1:2000')

messages = [100, 200, 300]
curMsg = 0

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 textbox - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 140
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        # Create textbox
        self.textbox1 = QLineEdit(self)
        self.textbox2 = QLineEdit(self)
        self.textbox1.move(20, 20)
        self.textbox1.resize(100,40)
        self.textbox2.move(200, 20)
        self.textbox2.resize(100,40)
        
        # Create a button in the window
        self.button = QPushButton('Show text', self)
        self.button.move(20,80)
        
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()
    
    @pyqtSlot()
    def on_click(self):
        textboxValue1 = self.textbox1.text()
        textboxValue2 = self.textbox2.text()
        print(textboxValue1)
        socket.send_pyobj({textboxValue1:[textboxValue1], textboxValue2:[textboxValue2]})

        QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + textboxValue1 + " and " + textboxValue2, QMessageBox.Ok, QMessageBox.Ok)
        self.textbox1.setText("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())