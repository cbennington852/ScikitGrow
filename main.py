import sys
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout
import sys
from layout_colorwidget import Color
from GUI_libary import GUILibarySubmodule
from sklearn_libary import SubLibary 
import sklearn

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")


        layout = QVBoxLayout()

        layout.addWidget(Color('red'))
        layout.addWidget(Color('green'))
        layout.addWidget(Color('blue'))
        layout.addWidget(GUILibarySubmodule(
            SubLibary.get_public_methods(sklearn.linear_model)
        ))

        widget = QWidget()
        widget.setLayout(layout)
        box = Qt.QGroupBox()
        box.setLayout(layout)
        scroll = Qt.QScrollArea()
        scroll.setWidget(box)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(200)
        self.setCentralWidget(scroll)

if __name__ == "__main__":
    app = QApplication(sys.argv) # Create the application instance
    window = MainWindow() # Create an instance of our custom window
    window.show() # Display the window
    sys.exit(app.exec_()) # Start the application's event loop