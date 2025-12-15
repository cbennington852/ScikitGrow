from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
import PyQt5.QtCore as QtCore 

import sys
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import sklearn_engine
from GUI_libary_and_pipeline import PipelineMother , Pipeline


class Plotter(QtW.QTabWidget):
    def __init__(self , pipeline_mother : PipelineMother, **kwargs):
        super().__init__(**kwargs)
        self.pipeline_mother = pipeline_mother
        self.resize(400 , 400)
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.addTab(sc , "Example")

    def plot_pipeline(self):
        # 1. Gather nessicary components from the pipeline.
        # 1.1 Gather pipelines
        lst_ptrs_to_pipelines : list[Pipeline] = self.pipeline_mother.pipelines
        # 1.2 Gather columns
        x_value_draggables = self.pipeline_mother.x_columns.get_cols()
        y_value_draggables = self.pipeline_mother.y_columns.get_cols()

        # 2.1 load the components into the engine.
        lst_engine_pipelines = []
        for gui_pipeline in lst_ptrs_to_pipelines:
            list_tuples_pipe_sklearn_objs = []
            # 2.2 Pre-proccessors
            for pre_proccessor in gui_pipeline.preproccessor_pipe.get_pipeline_objects():
                list_tuples_pipe_sklearn_objs.append(f"{len(list_tuples_pipe_sklearn_objs)}" , pre_proccessor)

            # 2.3 Models
            for models in gui_pipeline.model_pipe.get_pipeline_objects():
                list_tuples_pipe_sklearn_objs.append(f"{len(list_tuples_pipe_sklearn_objs)}" , models)
            print("List pre-proccessors" , list_tuples_pipe_sklearn_objs)

            # 2.4 Gather the validator

            
            # 2.5 Assemble pipeline object

            # new_curr = sklearn_engine.Pipeline(
            #     sklearn_pipeline=
            #     name=
            #     validator=
            # ) 
            #lst_engine_pipelines.append(new_curr)
        # 2.2 start the engine on it's own thread.

        # 3. plot the results on the main GUI thread.



class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)