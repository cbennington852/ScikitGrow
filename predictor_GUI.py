from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
import PyQt5.QtCore as QtCore 
import pandas as pd
from sklearn_engine import EngineResults , Pipeline


class PredictionGUI(QtW.QScrollArea):
    def __init__(self, engine_results : EngineResults, dataframe : pd.DataFrame,  **kwargs):
        super().__init__(**kwargs)

        self.engine_results = engine_results
        self.dataframe = dataframe
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
        self.predict_button = QtW.QPushButton("Predict")
        self.predict_button.clicked.connect(self.run_all_predictions)

        # Assemble page
        self.my_layout.addWidget(x_cols_box)
        self.my_layout.addWidget(self.predict_button)
        self.my_layout.addWidget(pipeline_holder)
        self.setWidget(self.main)

    def run_all_predictions(self):
        # Get all of the x_values
        try:
            x_values = []
            for x_col in self.x_cols_ptr_lst:
                x_values.append(str(x_col.text()))

            res = self.engine_results.predict(x_values , self.dataframe)
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
        self.pred_value = QtW.QLabel("Exmaple prediction")
        self.my_layout.addWidget(self.pred_value)
