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
import sklearn
import pandas as pd
from GUI_libary_and_pipeline import PipelineMother , Pipeline


class Plotter(QtW.QTabWidget):
    def __init__(self , pipeline_mother : PipelineMother, dataframe : pd.DataFrame , **kwargs):
        super().__init__(**kwargs)
        print("Pipeline mother" , pipeline_mother)
        self.pipeline_mother = pipeline_mother
        self.resize(400 , 400)
        self.dataframe = dataframe
        width=5
        height=4
        dpi=100
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig1 = Figure(figsize=(width, height), dpi=dpi)
        
        self.visual_plot = FigureCanvasQTAgg(fig)
        self.accuracy_plot = FigureCanvasQTAgg(fig1)
        
        self.addTab(self.visual_plot , "Visualization Plot")
        self.addTab(self.accuracy_plot , "Accuracy")

    @QtCore.pyqtSlot()
    def plot_pipeline(self):
       
        # 1. Gather nessicary components from the pipeline.
        # 1.1 Gather pipelines
        lst_ptrs_to_pipelines : list[Pipeline] = self.pipeline_mother.pipelines
        # 1.2 Gather columns
        x_value_draggables = self.pipeline_mother.x_columns.get_cols()
        y_value_draggables = self.pipeline_mother.y_columns.get_cols()

        # 2.1 load the components into the engine.
        lst_engine_pipelines = []
        built_validator = None
        for gui_pipeline in lst_ptrs_to_pipelines:
            list_tuples_pipe_sklearn_objs = []
            # 2.2 Pre-proccessors
            for pre_proccessor in gui_pipeline.preproccessor_pipe.get_pipeline_objects():
                list_tuples_pipe_sklearn_objs.append((f"{len(list_tuples_pipe_sklearn_objs)}" , pre_proccessor))

            # 2.3 Models
            for models in gui_pipeline.model_pipe.get_pipeline_objects():
                list_tuples_pipe_sklearn_objs.append((f"{len(list_tuples_pipe_sklearn_objs)}" , models))
            print("List for pipeline" , list_tuples_pipe_sklearn_objs)

            # 2.4 Gather the validator
            if len(gui_pipeline.validator.get_pipeline_objects()) != 0:
                built_validator = gui_pipeline.validator.get_pipeline_objects()[0]
            else:
                built_validator = None
            
            # 2.5 Assemble pipeline object
            new_pipeline = sklearn_engine.Pipeline(
                sklearn_pipeline=sklearn.pipeline.Pipeline(list_tuples_pipe_sklearn_objs),
                name=gui_pipeline.name_pipeline,
                validator=built_validator
            )
            lst_engine_pipelines.append(new_pipeline)
        x_cols = [item.name for item in x_value_draggables]
        y_cols = [item.name for item in y_value_draggables]
        # 3. start the engine on it's own thread.
        print(lst_engine_pipelines)
         # 4. plot the results on the main GUI thread...
        self.worker_thread = QtCore.QThread()
        self.worker = PlotterWorker(
            lst_engine_pipelines=lst_engine_pipelines,
            x_cols=x_cols,
            y_cols=y_cols,
            dataframe=self.dataframe
        )
        self.worker.moveToThread(self.worker_thread)
    
        self.worker_thread.started.connect(self.worker.start_plotting)
        #self.worker.progress.connect(self.progress_bar.setValue) # Allows us to update it
        self.worker.finished.connect(self.plotting_finished)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)


        self.worker_thread.start()
    
    @QtCore.pyqtSlot()
    def plotting_finished(self):
        print("Hello! The plotting is finsihed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(self.worker.engine_results)
        for i in range(0 , self.count()):
            widget = self.widget(i)
            widget.deleteLater()
        self.visual_plot = FigureCanvasQTAgg(self.worker.engine_results.visual_plot)
        self.accuracy_plot = FigureCanvasQTAgg(self.worker.engine_results.accuracy_plot)
        self.addTab(self.visual_plot , "Visualization Plot")
        self.addTab(self.accuracy_plot , "Accuracy")
        print(self.visual_plot)
        self.visual_plot.show()
        del self.worker
        


class PlotterWorker(QtCore.QObject):
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()

    def __init__(self, lst_engine_pipelines , x_cols , y_cols , dataframe):
        super(PlotterWorker, self).__init__()
        self.lst_engine_pipelines = lst_engine_pipelines
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.dataframe = dataframe


    @QtCore.pyqtSlot() # What does this do?
    def start_plotting(self):
        print("Starting plotting, YAY!")
        self.engine_results = sklearn_engine.SklearnEngine.main_sklearn_pipe(
            main_dataframe=self.dataframe,
            curr_pipelines=self.lst_engine_pipelines,
            pipeline_x_values=self.x_cols,
            pipeline_y_value=self.y_cols,
        )
        self.finished.emit()





