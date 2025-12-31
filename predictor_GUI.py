from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
import PyQt5.QtCore as QtCore 
from sklearn_engine import EngineResults


class PredictionGUI(QWidget):
    def __init__(self, engine_results : EngineResults, **kwargs):
        super().__init__(**kwargs)

        # Setup layout
        self.my_layout = QtW.QVBoxLayout()
        self.setLayout(self.my_layout)

        # GENERAL PLAN:
            # Have a GroupBox for the x_cols
            # Have an individual groupbox for each predictor.

        # 1. Remove all of the widgets from this page
        for child in self.findChildren(QtW.QWidget):
            child.deleteLater()

        # 2. Add Text entry for each of the x_cols
        x_cols_box = QtW.QGroupBox("X columns")
        x_cols_box_layout = QtW.QFormLayout()
        x_cols_box.setLayout(x_cols_box_layout)
        for x_col in engine_results.x_cols:
            x_col_name = QtW.QLabel(x_col)
            x_col_entry = QtW.QLineEdit()
            x_cols_box_layout.addRow(x_col_name , x_col_entry)
        

        # Assemble page
        self.my_layout.addWidget(x_cols_box)