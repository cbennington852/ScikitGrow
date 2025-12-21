import sys
import PyQt5.QtWidgets as QtW
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QAction
from layout_colorwidget import Color
from GUI_libary_and_pipeline import GUILibarySubmodule , Pipeline , PipelineMother , GUILibary
from sklearn_libary import SubLibary 
from dataframe_viewer import DataframeViewer
import sklearn
import seaborn as sns
import image_resources
from PyQt5.QtGui import QIcon , QPixmap
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from plotter import Plotter
from parsel import Parsel
import pandas as pd



class MainWindow(QMainWindow):

    def __init__(self ):
        super().__init__()
        self.setWindowTitle("SciKit Grow")
        self.resize(800 , 600)
        #self.dataframe = sns.load_dataset("iris")

        # load dataframe from a non-internet source.
        self.dataframe = pd.read_csv("example_datasets/test.csv")

        self.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))

        self.libary = GUILibary(self.dataframe)
        self.dataframeViewer = DataframeViewer(self.dataframe)
        
        self.pipeline_mommy = PipelineMother()

        self.plotter = Plotter(self.pipeline_mommy , self.dataframe)
        
        self.render_menu_bar()

        dock_libary = QtW.QDockWidget(
            "Libary",
            self
        )
        dock_dataframe = QtW.QDockWidget(
            "Dataframe",
            self
        )
        dock_plot = QtW.QDockWidget(
            "Plots",
            self
        )

        dock_libary.setFeatures(dock_libary.features() & ~QtW.QDockWidget.DockWidgetClosable)
        dock_dataframe.setFeatures(dock_dataframe.features() & ~QtW.QDockWidget.DockWidgetClosable)
        dock_plot.setFeatures(dock_plot.features() & ~QtW.QDockWidget.DockWidgetClosable)

        dock_libary.setWidget(self.libary)
        dock_dataframe.setWidget(self.dataframeViewer)
        dock_plot.setWidget(self.plotter)

        self.addDockWidget(Qt.RightDockWidgetArea , dock_plot )
        self.addDockWidget(Qt.RightDockWidgetArea , dock_dataframe)
        self.addDockWidget(Qt.LeftDockWidgetArea ,  dock_libary)

        self.setCentralWidget(self.pipeline_mommy)


    def render_menu_bar(self):
        menu = self.menuBar()
        
        # for file related actions.
        file_menu = menu.addMenu("&File")
        
        # Save action
        save_action = QAction("Save Project" , self)
        save_action.triggered.connect(lambda : print("saving attempted"))
        file_menu.addAction(save_action)

        # Save action
        save_as_action = QAction("Save Project As" , self)
        save_as_action.triggered.connect(lambda : print("saving attempted"))
        file_menu.addAction(save_as_action)

        # Open action
        open_action = QAction("Open Project" , self)
        open_action.triggered.connect(lambda : print("opening attempted"))
        file_menu.addAction(open_action)

if __name__ == "__main__":
    app = QApplication(sys.argv) # Create the application instance
    pixmap = QPixmap(":/images/Full_logo_SciKit_Grow.svg")
    #splash = QtW.QSplashScreen(pixmap)
    #splash.show()
    window = MainWindow() # Create an instance of our custom window
    window.show() # Display the window
    #splash.finish(window)
    sys.exit(app.exec_()) # Start the application's event loop