from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
import PyQt5.QtGui as PGui
from PyQt5.QtGui import QDrag , QPixmap , QPainter , QPalette , QImage , QColor , QPolygon, QPen, QBrush, QIcon
import PyQt5.QtCore as QCore 
from colors_and_appearance import AppAppearance


# This is an abstract class BTW.
class Parameter(QtW.QWidget):
    def __init__(self):
        pass

    def text():
        pass

# QSpinBox for int's
# QDoubleSpinBox for doubles

class SingleLineParameter(QtW.QLineEdit):
    def __init__(self , name , value,  **kwargs):
        super().__init__(**kwargs) 
        self.setText(str(value))

class IntSingleLine(QtW.QSpinBox):
    def __init__(self , name , value,  **kwargs):
        super().__init__(**kwargs)
        self.setValue(value)

class FloatSingleLine(QtW.QDoubleSpinBox):
    def __init__(self , name , value,  **kwargs):
        super().__init__(**kwargs)
        self.setValue(value)

class BooleanSingleLine(QtW.QCheckBox):
    def __init__(self , name , value,  **kwargs):
        super().__init__(**kwargs)
        self.setChecked(value)

    def text(self):
        return str(self.isChecked())

def parameter_filter(name : str , value) -> Parameter:
    try:
        if type(value) is int:
            return IntSingleLine(name , value)
        elif type(value) is float:
            return FloatSingleLine(name, value)
        elif type(value) is bool:
            return BooleanSingleLine(name , value)
        else:
            return SingleLineParameter(name , value)
    except:
        return SingleLineParameter(name , value)