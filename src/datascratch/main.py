import sys
import PyQt5.QtWidgets as QtW
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QAction
from .GUI_libary_and_pipeline_mother import PipelineMother , GUILibary
from .sklearn_libary import SubLibary 
from .dataframe_viewer import DataframeViewer
import sklearn
import seaborn as sns
from . import image_resources
from PyQt5.QtGui import QIcon , QPixmap
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .plotter import Plotter
from .save_file import SaveFileException , SaveFile
import os
import pickle
import traceback
import time
import qdarktheme
import pandas as pd
from .settings_manager import DataScratchSettings
from .predictor_GUI import PredictionGUI
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

windows = []

class MainMenu(QMainWindow):


    def __init__(self ):
        super().__init__()

        self.setWindowTitle("DataScratchMain Menu")
        self.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))
        self.title_image = QtW.QLabel(pixmap=QPixmap(":images/Full_logo_SciKit_Grow.svg"))
        self.setMaximumWidth(self.title_image.width())

        # Set up basic ptrs
        my_layout = QtW.QVBoxLayout()
        main_box = QtW.QWidget()
        main_box.setLayout(my_layout)

        curr_toolbar = QtW.QToolBar()
        curr_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        import_dataset = QtW.QAction(QIcon(":images/import_dataset.svg") , "Import dataset" , self)
        import_dataset.triggered.connect(self.import_datasets_clicked)
        curr_toolbar.addAction(import_dataset)

        import_dataset = QtW.QAction(QIcon(":images/file_open.png") , "Open dataset" , self)
        import_dataset.triggered.connect(self.import_datasets_clicked)
        curr_toolbar.addAction(import_dataset)

        # Render example dataset list
        example_datasets = [
            "car_crashes",
            "diamonds",
            "iris",
            "random_data",
            "tips",
            "wine",
        ]

        def open_on_dataset(dataset_name):
            file = QFile(f":/example_datasets/{example_datasets[dataset_name.row()]}.csv")
            if file.open(QIODevice.ReadOnly):
                df = pd.read_csv(file)
                curr = MainMenu.open_main_window_on_dataset(df)
                curr.show()
                windows.append(curr)
                self.deleteLater()

        # Render all of the example datasets.
        list_widget = QListWidget()
        list_widget.addItems(example_datasets)
        list_widget.clicked.connect(open_on_dataset)


        settings = DataScratchSettings.getSettings()
        recent_files_opened = settings.value(DataScratchSettings.RECENT_FILES_KEY , [] , type=list)
        print("Recent files opened" , recent_files_opened)
        recent_list_widget = QListWidget()
        recent_list_widget.addItems(recent_files_opened)
        recent_list_widget.clicked.connect(lambda x : open_on_file_handle(recent_files_opened[x.row()]))


        recent_group_box = QtW.QGroupBox("Recent Datasets")
        recent_group_box.setLayout(QtW.QVBoxLayout())
        recent_group_box.layout().addWidget(recent_list_widget)


        group_box = QtW.QGroupBox("Example datasets")
        group_box.setLayout(QtW.QVBoxLayout())
        group_box.layout().addWidget(list_widget)

  
        # second_box
        second_box = QtW.QWidget()
        second_box_lay = QtW.QVBoxLayout()
        second_box.setLayout(second_box_lay)
        second_box_lay.addWidget(curr_toolbar)
        second_box_lay.addWidget(recent_group_box)
        second_box_lay.addWidget(group_box)

        # Hello Text.
        hello_text = QtW.QLabel("""Welcome to DataScratch! You can import datasets through the Open Dataset button. Supported file types include excel, csv, parquet, and pkl""")
        hello_text.setWordWrap(True)

        my_layout.addWidget(self.title_image)
        my_layout.addWidget(hello_text)
        my_layout.addWidget(second_box)
        self.setCentralWidget(main_box)


     
    def open_main_window_on_dataset(dataframe):
        pixmap = QPixmap(":/images/Full_logo_SciKit_Grow.svg")
        splash = QtW.QSplashScreen(pixmap)
        splash.show()
        my_window = MainWindow(dataframe) # Create an instance of our custom window
        splash.finish(my_window)
        return my_window

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

    def __init__(self , dataframe , file_path = None):
        super().__init__()
        if file_path is not None:
            self.setWindowTitle(f"{file_path}")
        else:
            self.setWindowTitle("SciKit Grow")
        self.file_path = file_path

        self.resize(MainWindow.BASE_WINDOW_WIDTH , MainWindow.BASE_WINDOW_HEIGHT)
        # start a parsel. 
        # load dataframe 
        self.dataframe = dataframe

        self.libary = GUILibary(self.dataframe)
        self.dataframeViewer = DataframeViewer(self.dataframe)
        
        self.pipeline_mother = PipelineMother()

        self.plotter = Plotter(self.pipeline_mother , self.dataframe)
        
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

        self.setCentralWidget(self.pipeline_mother)

    def save_function(self , file_name='data_2.pkl' , no_popup=False):
        print(f"Dataframe {self.dataframe}")
        print(f"file_name : {file_name}")
        if not no_popup:
            file_path, _ = QtW.QFileDialog.getSaveFileName(
                None, "Save Project", file_name, "Pickle Files (*.pkl);;All Files (*)"
            )
            if not file_path.endswith('.pkl'):
                file_path += '.pkl'
        else:
            file_path = file_name
        if file_path:
            try:
                # Prepare the data object
                save_file = SaveFile(
                    pipelines_data=self.pipeline_mother.get_data(),
                    dataframe=self.dataframe,
                    columns_data=self.pipeline_mother.get_columns_data()
                )

                # 2. Single 'wb' open. 
                # This TRUNCATES the file automatically (replaces existing content).
                with open(file_path, 'wb') as f:
                    pickle.dump(save_file, f)
                
                self.file_path = file_path

                self.setWindowTitle(self.file_path)
                
                print(f"Saved successfully to: {file_path}")
                # Also add this to the recently saved section.
                settings = DataScratchSettings.getSettings()
                curr_recently_opened = settings.value(DataScratchSettings.RECENT_FILES_KEY , [] , type=list)
                curr_recently_opened.append(file_path)
                settings.setValue(DataScratchSettings.RECENT_FILES_KEY , curr_recently_opened)
            except OSError as e:
                QMessageBox.critical(None, "File Error", f"Could not open file: {e}")
            except Exception as e:
                traceback.print_exc()


    def open_on_saved_file(file_name='data_2.pkl'):
        # basically open the file and then pass in all of the info for the things.
        with open(file_name, 'rb') as file:
            loaded_data = pickle.load(file)
            if not isinstance(loaded_data , SaveFile):
                raise SaveFileException("File did not unpickle as a save file type.")
        
            # 1. Retrieve the dataframe 
            df = loaded_data.dataframe
            if not isinstance(df , pd.DataFrame):
                raise SaveFileException("Pandas Dataframe could not be loaded.")
            # 2. Startup a new instance of a main window
            main_window = MainWindow(df , file_name)
            # 3. load the pipeline data into that main_window
            main_window.pipeline_mother.load_from_data(loaded_data.pipelines_data , loaded_data.columns_data)
            # 4. display the data.
            print(main_window)
            print("X cols" , main_window.pipeline_mother.x_columns.get_cols())
            return main_window


    def render_menu_bar(self):
        menu = self.menuBar()
        
        # for file related actions.
        file_menu = menu.addMenu("&File")
        #graph_settings = menu.addMenu("&Graph Settings")
        # Save action
        save_action = QAction("Save Project" , self)
        save_action.triggered.connect(lambda x : self.save_button_pressed())
        file_menu.addAction(save_action)

        # Save action
        save_as_action = QAction("Save Project As" , self)
        save_as_action.triggered.connect(lambda x : self.save_button_pressed())
        file_menu.addAction(save_as_action)

        # Open action
        open_action = QAction("Open Project" , self)
        open_action.triggered.connect(self.open_button_pressed)
        file_menu.addAction(open_action)

        # Add the ediatable thing
        # Later I want this toolbar to have a editable project name.



    def save_button_pressed(self):
        if self.file_path is not None:
            try: 
                self.save_function(
                    file_name=self.file_path,
                    no_popup=True
                )
            except:
                self.save_as_button_pressed()
        else:
            self.save_as_button_pressed()

    def save_as_button_pressed(self):
        self.save_function()

    def open_button_pressed(self):
        file_path, _ = QtW.QFileDialog.getOpenFileName(
                None, "Open Project",None ,f"All Files (*.pkl *.csv *.xls *{PredictionGUI.model_save_extension});; Pickle Files (*.pkl);; CSV Files (*.csv);; Excel Files (*.xls);; DataScratch Pipeline File (*{PredictionGUI.model_save_extension});; "
            )
        if file_path:
            open_on_file_handle(file_path)

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


def open_on_file_handle(file_handle):
    print("Attempted open on file handle" , file_handle)
    if os.path.exists(file_handle):
        # parse command line argument
        if file_handle.endswith('.pkl'):
            try:
                # Make a splash 
                main_window = MainWindow.open_on_saved_file(file_handle)
                main_window.show()
                windows.append(main_window)
            except Exception as e:
                traceback.print_exc()
                QtW.QMessageBox.critical(
                        None,                        # Parent: Use None if not within a QWidget class
                        "Error opening Save file",            # Title bar text
                        f"{str(e)}" # Main message
                    )
        # This is exported / saved models / pipelines
        elif file_handle.endswith(PredictionGUI.model_save_extension):
            try:
                with open(file_handle, 'rb') as file:
                    loaded_data = pickle.load(file)
                    print("Opened and loaded pickle")
                    model_pred = PredictionGUI(loaded_data , True)
                    new_win = QMainWindow()
                    new_win.setWindowIcon(QIcon(":images/Mini_Logo_Alantis_2_Box.svg"))
                    new_win.setWindowTitle("DataScratch Pipeline File")
                    new_win.setCentralWidget(model_pred)
                    new_win.show()
                    windows.append(new_win)
                    print("new_win" , new_win)
            except Exception as e:
                    traceback.print_exc()
                    QtW.QMessageBox.critical(
                            None,                        # Parent: Use None if not within a QWidget class
                            "Error opening saved model file",            # Title bar text
                            f"{str(e)}" # Main message
                        )
        else:
            try:
                df = filter_command_line_argument_return_dataframe(file_handle)
                try:
                    main_window = MainMenu.open_main_window_on_dataset(df)
                    main_window.show()
                    windows.append(main_window)
                except Exception as e:
                    QtW.QMessageBox.critical(
                        None,                        # Parent: Use None if not within a QWidget class
                        "Internal Error opening file",            # Title bar text
                        f"{str(e)}" # Main message
                    )
            except Exception as e:
                QtW.QMessageBox.critical(
                        None,                        # Parent: Use None if not within a QWidget class
                        "File type not supported",            # Title bar text
                        f"{str(e)}" # Main message
                    )
    else:
        QtW.QMessageBox.critical(
                        None,                        # Parent: Use None if not within a QWidget class
                        "Error opening file. File does not exist.",            # Title bar text
                        f"File {file_handle} was not found." # Main message
                    )


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv) # Create the application instance
    app.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))
    # Below handles the opening of a main menu bar, 
    stylesheet = qdarktheme.load_stylesheet(theme='light') 
    app.setStyleSheet(stylesheet)
    if len(sys.argv) > 1:
        open_on_file_handle(sys.argv[1])
    else:
        main_menu = MainMenu()
        main_menu.show()
    sys.exit(app.exec_()) # Start the application's event loop


if __name__ == "__main__":
   main()