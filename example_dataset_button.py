import PyQt5.QtWidgets as QtW
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QAction
from GUI_libary_and_pipeline_mother import PipelineMother , GUILibary


class ExampleDatasetButton(QtW.QGroupBox):
    def __init__(self , name , description , icon ):
        super().__init__("")
        #self.setFixedSize(300 , 300)
        my_layout = QtW.QHBoxLayout()
        my_layout.setSpacing(0)
        #icon.scaled(70 , 70)
        my_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(my_layout)

        # add icon
        image_label = QtW.QLabel(pixmap=icon)
        
        image_label.setScaledContents(True)
        my_layout.addWidget(image_label)

        # Text and descriptions to right
        right = QtW.QWidget()
        right_layout = QtW.QVBoxLayout()
        right.setLayout(right_layout)

        # add title
        title = QtW.QLabel(name)
        font = title.font()
        font.setBold(True)
        description_label = QtW.QLabel(description)
        right_layout.addWidget(title)
        right_layout.addWidget(description_label)
        my_layout.addWidget(right)