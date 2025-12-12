import sys
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout
from layout_colorwidget import Color
from GUI_libary_and_pipeline import GUILibarySubmodule , Pipeline , PipelineMother , GUILibary
from sklearn_libary import SubLibary 
from dataframe_viewer import DataframeViewer
import sklearn
import seaborn as sns
import image_resources
from PyQt5.QtGui import QIcon , QPixmap


"""
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setFixedSize(800 , 600)
        self.label = Qt.QLabel("Scikit Grow")
        pixmap = QPixmap(":/images/Full_logo_SciKit_Grow.svg")
        self.label.setPixmap(pixmap)
        self.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))
        layout.addWidget(self.label)
        self.example_datasets = QPushButton("Example Datasets")
        self.import_dataset = QPushButton("Import Dataset from file")
        layout.addWidget(self.example_datasets)
        layout.addWidget(self.import_dataset)
        self.setLayout(layout)
        self.example_datasets.clicked.connect(SplashScreen.open_application_with_dataframe)

    def open_application_with_dataframe(dataframe):
        print(dataframe)
        dataframe = sns.load_dataset("iris")
        window = MainWindow(dataframe) # Create an instance of our custom window
        window.show() # Display the window
"""



class MainWindow(QMainWindow):

    def __init__(self ):
        super().__init__()
        self.setWindowTitle("My App")
        self.resize(800 , 600)
        self.dataframe = sns.load_dataset("iris")
        self.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))


        layout = QVBoxLayout()
        box = Qt.QGroupBox()
        box.setLayout(layout)


        # libary = GUILibarySubmodule(
        #     SubLibary.get_public_methods(sklearn.linear_model)
        # )
        libary = GUILibary()
        dataframeV = DataframeViewer(
            self.dataframe
        )
        

        scroll = Qt.QScrollArea()
        scroll.setWidget(libary)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(200)

        layout.addWidget(scroll)
        layout.addWidget(dataframeV)
        #layout.addWidget(Pipeline())
        layout.addWidget(PipelineMother())
        
        self.setCentralWidget(box)

if __name__ == "__main__":
    app = QApplication(sys.argv) # Create the application instance
    #splash = SplashScreen()
    #splash.show()
    window = MainWindow() # Create an instance of our custom window
    window.show() # Display the window
    sys.exit(app.exec_()) # Start the application's event loop