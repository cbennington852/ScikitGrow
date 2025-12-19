import pickle
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel, QAction
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag , QIcon , QPixmap , QCursor , QColor , QPolygon, QPen, QBrush, QIcon, QPainter
import PyQt5.QtCore as QtCore 
from draggable import Draggable , DraggableColumn
from sklearn.base import is_regressor, is_classifier
import sklearn



class Parsel():
    """
    This is a class of things that are savable and loadable to file.
    """

    parsel = None

    def __init__(self):
        # Singleton
        if Parsel.parsel is not None:
            return Parsel.parsel
        self.data = {}
        Parsel.parsel = self

    def add(self , key , thing):
        self.data[key] = thing

    def get(self , key):
        return self.data[key]
    
    def to_pickle(self, file_name):
        try:
            with open(file_name, 'wb') as f:
                pickle.dump(self.data, f)
        except:
            print(f"Failed to read file {file_name}")

    def from_pickle(self , file_name):
        try:
            with open(file_name, 'rb') as f:
                self.data = pickle.load(f)
        except:
            print(f"Failed to read file {file_name}")

    