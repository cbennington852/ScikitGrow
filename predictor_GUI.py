from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag , QIcon
import PyQt5.QtCore as QtCore 
import pandas as pd
import pickle
from sklearn_engine import EngineResults , Pipeline


class PredictionGUI(QtW.QScrollArea):
    def __init__(self, engine_results : EngineResults, hide_export_features = False, **kwargs):
        super().__init__(**kwargs)

        self.engine_results = engine_results
        # Setup layout
        self.main = QtW.QWidget()
        self.my_layout = QtW.QVBoxLayout()
        self.main.setLayout(self.my_layout)

        # GENERAL PLAN:
            # Have a GroupBox for the x_cols
            # Have an individual groupbox for each predictor.

        # 1. Remove all of the widgets from this page
        for child in self.main.findChildren(QtW.QWidget):
            child.deleteLater()

        # 2. Add Text entry for each of the x_cols
        x_cols_box = QtW.QGroupBox("X columns")
        x_cols_box_layout = QtW.QFormLayout()
        x_cols_box.setLayout(x_cols_box_layout)
        self.x_cols_ptr_lst = []
        for x_col in self.engine_results.x_cols:
            x_col_name = QtW.QLabel(x_col)
            x_col_entry = QtW.QLineEdit()
            self.x_cols_ptr_lst.append(x_col_entry)
            x_cols_box_layout.addRow(x_col_name , x_col_entry)

        # 3. Add Boxes, with each model being a prediction "box"
        pipeline_holder = QtW.QGroupBox("Pipelines")
        pipeline_holder_layout = QtW.QVBoxLayout()
        pipeline_holder.setLayout(pipeline_holder_layout)
        self.pipelines_groupbox_ptr = []
        for pipeline in self.engine_results.trained_models:
            curr_pipeline = PredictionGUIPipeline(pipeline)
            self.pipelines_groupbox_ptr.append(curr_pipeline)
            pipeline_holder_layout.addWidget(curr_pipeline)

        # 4. Add and connect a button to get each prediction.
            # NOTE : the backend for this will be handled by the 
        # 4. We could also try having it be on type.

        self.predict_button = QPushButton("Predict")
        self.predict_button.clicked.connect(self.run_all_predictions)

        self.export_as_software_button = QtW.QToolButton(self.main)
        self.export_as_software_button.setIcon(QIcon(":images/export_icon.svg"))
        self.export_as_software_button.setText("& Export")
        self.export_as_software_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.export_as_software_button.setPopupMode(QtW.QToolButton.InstantPopup)
        self.export_as_software_button.setMenu(QtW.QMenu(self.export_as_software_button))


        export_as_software_action = QtW.QAction("Export as software" , self.main)
        export_as_software_action.triggered.connect(lambda x : self.export_function_button_clicked(self.export_as_software , f"Scikit Grow Pipeline File (*{PredictionGUI.model_save_extension});;"))
        self.export_as_software_button.menu().addAction(export_as_software_action)

        export_as_pickle_action = QtW.QAction("Export as python pickle" , self.main)
        export_as_pickle_action.triggered.connect(lambda x : self.export_function_button_clicked(self.export_as_pickle , "Pickle  (*.pickle);;"))
        self.export_as_software_button.menu().addAction(export_as_pickle_action)


        # self.predict_button = QtW.QPushButton("Predict")
        # self.export_as_software_button = QtW.QPushButton("Export as software")
        # self.export_as_software_button.clicked.connect(self.export_as_software_button_clicked)
        # self.predict_button.clicked.connect(self.run_all_predictions)

        # Assemble page
        self.my_layout.addWidget(x_cols_box)
        self.my_layout.addWidget(self.predict_button)
        self.my_layout.addWidget(pipeline_holder)
        if hide_export_features == False:
            self.my_layout.addWidget(self.export_as_software_button)
        self.setWidget(self.main)

    model_save_extension = '.skgp'

    def export_as_pickle(self):
        if not file_name.endswith('.pickle'):
            file_name += '.pickle'

        with open(file_name, 'wb') as f:
            pickle.dump(self.engine_results, f)



    def export_function_button_clicked(self , function , file_type_string):
        
        # 1. Open a file dialog
        file_path, _ = QtW.QFileDialog.getSaveFileName(
                None, "Save Project", "",file_type_string 
            )
        if not file_path:
            return
        try:
            function(file_path)
        except Exception as e:
            QtW.QMessageBox.critical(
                        None,                        # Parent: Use None if not within a QWidget class
                        "Error Saving file",            # Title bar text
                        f"{str(e)}" # Main message
                    )

        

    def export_as_software(self , file_name : str):
        # 2. Save the Engine Results as a pickled file with special file extension.
        if not file_name.endswith(PredictionGUI.model_save_extension):
            file_name += PredictionGUI.model_save_extension

        with open(file_name, 'wb') as f:
            pickle.dump(self.engine_results, f)

    def run_all_predictions(self):
        # Get all of the x_values
        try:
            x_values = []
            for x_col in self.x_cols_ptr_lst:
                x_values.append(str(x_col.text()))

            res = self.engine_results.predict(x_values )
            for pipeline_ptr , value in res.items():
                for gui_pipe in self.pipelines_groupbox_ptr:
                    if pipeline_ptr == gui_pipe.pipeline:
                        gui_pipe.pred_value.setText(str(value))
            print(res)
        except Exception as e:
            QtW.QMessageBox.critical(
                 None,                        # Parent: Use None if not within a QWidget class
                 "Engine Prediction Error",            # Title bar text
                 f"{str(e)}" # Main message
            )
            print(e)

class PredictionGUIPipeline(QtW.QGroupBox):
    def __init__(self, pipeline : Pipeline, **kwargs):
        super().__init__(pipeline.name , **kwargs)
        self.pipeline = pipeline
        self.my_layout = QtW.QVBoxLayout()
        self.setLayout(self.my_layout)
        self.pred_value = QtW.QLabel("")
        self.my_layout.addWidget(self.pred_value)
