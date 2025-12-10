import sys
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout
from layout_colorwidget import Color
from GUI_libary import GUILibarySubmodule
from sklearn_libary import SubLibary 
from dataframe_viewer import DataframeViewer
from GUI_splash_screen import SplashScreen
import sklearn
import seaborn as sns


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.dataframe = sns.load_dataset("iris")

        layout = QVBoxLayout()
        box = Qt.QGroupBox()
        box.setLayout(layout)


        libary = GUILibarySubmodule(
            SubLibary.get_public_methods(sklearn.linear_model)
        )
        dataframeV = DataframeViewer(
            self.dataframe
        )
        

        scroll = Qt.QScrollArea()
        scroll.setWidget(libary)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(200)

        layout.addWidget(scroll)
        layout.addWidget(dataframeV)

        
        self.setCentralWidget(box)

if __name__ == "__main__":
    app = QApplication(sys.argv) # Create the application instance
    splash = SplashScreen()
    splash.show()
    #window = MainWindow() # Create an instance of our custom window
    #window.show() # Display the window
    sys.exit(app.exec_()) # Start the application's event loop