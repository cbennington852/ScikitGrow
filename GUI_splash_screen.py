import sys
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon , QPixmap
import image_resources


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setFixedSize(800 , 600)
        self.label = Qt.QLabel("Scikit Grow")
        pixmap = QPixmap(":/images/Full_logo_SciKit_Grow.svg")
        self.label.setPixmap(pixmap)
        self.setWindowIcon(QIcon(":/images/Mini_Logo_Lilac_Learn_2.svg"))
        layout.addWidget(self.label)
        self.example_datasets = QPushButton("Example Datasets")
        self.import_dataset = QPushButton("Import Dataset from file")
        layout.addWidget(self.example_datasets)
        layout.addWidget(self.import_dataset)
        self.setLayout(layout)

