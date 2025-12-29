import sys
import PyQt5.QtWidgets as QtW
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QAction
from layout_colorwidget import Color
from GUI_libary_and_pipeline_mother import PipelineMother , GUILibary
from sklearn_libary import SubLibary 
from dataframe_viewer import DataframeViewer
import sklearn
import seaborn as sns
import image_resources
from PyQt5.QtGui import QIcon , QPixmap
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from plotter import Plotter
from save_file import SaveFileException , SaveFile
import os
import pickle
import traceback

import pandas as pd



class MainMenu(QMainWindow):

    curr_window = None

    def __init__(self ):
        super().__init__()
        MainMenu.curr_window = self

        self.setWindowTitle("SciKit Grow Main Menu")
        self.resize(MainWindow.BASE_WINDOW_WIDTH , MainWindow.BASE_WINDOW_HEIGHT)
        self.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))

        # Set up basic ptrs
        self.my_layout = QtW.QVBoxLayout()
        self.main = QtW.QWidget()
        self.main.setLayout(self.my_layout)
        self.setCentralWidget(self.main)

        # add the example datasets button
        self.example_datasets_button = QtW.QPushButton("Example datasets")
        self.import_dataset_button = QtW.QPushButton("Import datasets")
        self.title_image = QtW.QLabel(pixmap=QPixmap(":images/Full_logo_SciKit_Grow.svg"))
        self.import_dataset_button.clicked.connect(self.import_datasets_clicked)

        self.example_datasets_button.clicked.connect(lambda : self.open_main_window_on_sns_dataset(pd.read_csv("example_datasets/test.csv")))

        self.my_layout.addWidget(self.title_image)
        self.my_layout.addWidget(self.example_datasets_button)
        self.my_layout.addWidget(self.import_dataset_button)



    def open_main_window_on_sns_dataset(self, dataframe):
        splash = QtW.QSplashScreen(pixmap)
        splash.show()
        self.my_window = MainWindow(dataframe) # Create an instance of our custom window
        self.my_window.show()
        self.hide()
        splash.finish(self.my_window)

    def import_datasets_clicked(self):
        fileName, _ = QtW.QFileDialog.getOpenFileName(self, "Open File", "",
                                                  "All Files (*);; CSV file (*.csv);; Parquet file (*.parquet);; Exel format (*.xl*)",
                                                  options=QtW.QFileDialog.Options())
        if fileName:
            print("File name: " , fileName)
            open_on_file_handle(fileName)
            self.hide()
        else:
            print("No file selected")




class MainWindow(QMainWindow):

    BASE_WINDOW_WIDTH = 1200
    BASE_WINDOW_HEIGHT = 800

    def __init__(self , dataframe ):
        super().__init__()
        self.setWindowTitle("SciKit Grow")
        self.resize(MainWindow.BASE_WINDOW_WIDTH , MainWindow.BASE_WINDOW_HEIGHT)
        # start a parsel. 
        # load dataframe 
        self.dataframe = dataframe

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

    def save_button_pressed(self):
        save_file = SaveFile(
            pipelines_data=self.pipeline_mommy.get_data(),
            dataframe=self.dataframe
        )
        with open('data.pkl', 'wb') as file:
            # Use 'wb' mode for writing binary
            pickle.dump(save_file, file)
        print(save_file)

    def load_button_pressed(self , file_name='data.pkl'):
        raise ValueError("Not working yet")

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
        save_as_action.triggered.connect(self.save_button_pressed)
        file_menu.addAction(save_as_action)

        # Open action
        open_action = QAction("Open Project" , self)
        open_action.triggered.connect(self.load_button_pressed)
        file_menu.addAction(open_action)

def filter_command_line_argument_return_dataframe(file_path) -> pd.DataFrame:
    # NOTE: We can later expand this to work on HTML tables and later SQL databases.
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.parquet'):
        return pd.read_parquet(file_path)
    excel_endings = ['.xls' , '.xlsx' , '.xlsm' , '.xlsb' , '.odf' , '.odt']
    for ending in excel_endings:
        if file_path.endswith(ending):
            return pd.read_excel(file_path)
    # Else implied
    raise ValueError("Does not end in a valid file extension format")

def open_on_saved_file(file_handle):
    # basically open the file and then pass in all of the info for the things.
    with open('data.pkl', 'rb') as file_handle:
        loaded_data = pickle.load(file_handle)
        if not isinstance(loaded_data , SaveFile):
            raise SaveFileException("File did not unpickle as a save file type.")
        
        #   self.pipeline_mommy.load_from_data(save_file.pipelines_data)
        # TODO:
        # 1. Retrieve the dataframe 
        df = loaded_data.dataframe
        if not isinstance(df , pd.DataFrame):
            raise SaveFileException("Pandas Dataframe could not be loaded.")
        # 2. Startup a new instance of a main window
        main_window = MainWindow(df)
        # 3. load the pipeline data into that main_window
        main_window.pipeline_mommy.load_from_data(loaded_data.pipelines_data)
        # 4. display the data.
        print(main_window)
        return main_window




    


def open_on_file_handle(file_handle):
    if os.path.exists(file_handle):
        # parse command line argument
        if file_handle.endswith('.pkl'):
            try:
                # Make a splash 
                splash_screen = MainMenu()
                splash_screen.main_window = open_on_saved_file(file_handle)
                splash_screen.main_window.show()
                splash_screen.hide()
            except Exception as e:
                traceback.print_exc()
                QtW.QMessageBox.critical(
                        None,                        # Parent: Use None if not within a QWidget class
                        "Error opening Save file",            # Title bar text
                        f"{str(e)}" # Main message
                    )
        else:
            try:
                df = filter_command_line_argument_return_dataframe(file_handle)
                main_menu = MainMenu()
                try:
                    main_menu.open_main_window_on_sns_dataset(df)
                except Exception as e:
                    QtW.QMessageBox.critical(
                        None,                        # Parent: Use None if not within a QWidget class
                        "Internal Error opening file",            # Title bar text
                        f"{str(e)}" # Main message
                    )
                    sys.exit()
            except Exception:
                QtW.QMessageBox.critical(
                        None,                        # Parent: Use None if not within a QWidget class
                        "File type not supported",            # Title bar text
                        f"{str(e)}" # Main message
                    )
                sys.exit()
    else:
        QtW.QMessageBox.critical(
                        None,                        # Parent: Use None if not within a QWidget class
                        "Error opening file. File does not exist.",            # Title bar text
                        f"{str(e)}" # Main message
                    )
        sys.exit()
        

if __name__ == "__main__":
    app = QApplication(sys.argv) # Create the application instance
    pixmap = QPixmap(":/images/Full_logo_SciKit_Grow.svg")
    # Below handles the opening of a main menu bar, 
    if len(sys.argv) > 1:
        open_on_file_handle(sys.argv[1])
    else:
        main_menu = MainMenu()
        main_menu.show()
    sys.exit(app.exec_()) # Start the application's event loop