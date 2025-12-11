import sys
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout
from layout_colorwidget import Color
from GUI_libary import GUILibarySubmodule
import sklearn
import image_resources
from PyQt5.QtGui import QIcon , QPixmap


# This is for each "pipeline"
    # Small window with the model, preproccessor, validator

class Pipeline(Qt.QWidget):
    def __init__(self , **kwargs):
        super().__init__( **kwargs)
        self.resize(300 , 300)
        self.setAcceptDrops(True)
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(Qt.QLabel("HEllo, drag here"))

    def dragEnterEvent(self, e):
        e.accept()

