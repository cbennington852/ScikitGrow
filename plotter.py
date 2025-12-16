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


class ScikitGrowEngineAssemblyError(Exception):
    pass

class Plotter(QtW.QTabWidget):
    def __init__(self , pipeline_mother : PipelineMother, dataframe : pd.DataFrame , **kwargs):
        super().__init__(**kwargs)
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

    def handle_thread_crashing(self):
        self.ptr_to_train_models_button.setEnabled(True)
        if hasattr(self , "worker_thread"):
            self.worker_thread.exit()
            self.worker_thread.wait()
        
        

    @QtCore.pyqtSlot()
    def plot_pipeline(self):
        self.ptr_to_train_models_button = self.sender()
        
        try:
            # 1. Gather nessicary components from the pipeline.
            # 1.1 Gather pipelines
            lst_ptrs_to_pipelines : list[Pipeline] = self.pipeline_mother.pipelines
            # 1.2 Gather columns
            x_value_draggables = self.pipeline_mother.x_columns.get_cols()
            y_value_draggables = self.pipeline_mother.y_columns.get_cols()

            # 1.3 Validate with proper Error handling
            if x_value_draggables == []:
                raise ScikitGrowEngineAssemblyError("X values cannot be empty.")
            if y_value_draggables == []:
                raise ScikitGrowEngineAssemblyError("Y values cannot be empty")
            

            # 2.1 load the components into the engine.
            lst_engine_pipelines = []
            built_validator = None
            for gui_pipeline in lst_ptrs_to_pipelines:
                list_tuples_pipe_sklearn_objs = []
                # 2.2 Pre-proccessors
                for pre_proccessor in gui_pipeline.preproccessor_pipe.get_pipeline_objects():
                    list_tuples_pipe_sklearn_objs.append((f"{len(list_tuples_pipe_sklearn_objs)}" , pre_proccessor))

                # 2.3 Models
                model_pipeline_lst =  gui_pipeline.model_pipe.get_pipeline_objects()
                if model_pipeline_lst == []:
                    raise ScikitGrowEngineAssemblyError(f"Pipeline {gui_pipeline.name_pipeline} is missing a model")
                for models in model_pipeline_lst:
                    list_tuples_pipe_sklearn_objs.append((f"{len(list_tuples_pipe_sklearn_objs)}" , models))

                # 2.4 Gather the validator
                if len(gui_pipeline.validator.get_pipeline_objects()) != 0:
                    built_validator = gui_pipeline.validator.get_pipeline_objects()[0]
                else:
                    built_validator = None
                
                # 2.5 Assemble pipeline object
                new_pipeline = sklearn_engine.Pipeline(
                    sklearn_pipeline=sklearn.pipeline.Pipeline(list_tuples_pipe_sklearn_objs),
                    name=gui_pipeline.name_pipeline.text(),
                    validator=built_validator
                )
                lst_engine_pipelines.append(new_pipeline)
            x_cols = [item.name for item in x_value_draggables]
            y_cols = [item.name for item in y_value_draggables]
            # 3. start the engine on it's own thread.
            # 3.1 before we start the enngine, make sure to disable the button for this.
            self.ptr_to_train_models_button.setEnabled(False)
            self.worker_thread = QtCore.QThread()
            self.worker = PlotterWorker(
                lst_engine_pipelines=lst_engine_pipelines,
                ptr_to_training_button=self.ptr_to_train_models_button,
                x_cols=x_cols,
                y_cols=y_cols,
                dataframe=self.dataframe
            )
            self.worker.moveToThread(self.worker_thread)
        
            self.worker_thread.started.connect(self.worker.start_plotting)
            #self.worker.progress.connect(self.progress_bar.setValue) # Allows us to update it
            self.worker.finished.connect(self.plotting_finished)
            self.worker.crashed.connect(self.crashed_handler)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)
            self.worker_thread.start()
        except ScikitGrowEngineAssemblyError as e:
            self.handle_thread_crashing()
            QtW.QMessageBox.critical(
                 None,                        # Parent: Use None if not within a QWidget class
                 "Engine Assembly Error",            # Title bar text
                 f"{str(e)}" # Main message
            )
            print(e)
        except Exception as e:
            self.handle_thread_crashing()
            QtW.QMessageBox.critical(
                None,                        # Parent: Use None if not within a QWidget class
                "Unexpected Error",            # Title bar text
                f"Unexpected error : {str(e)}" # Main message
            )

    
        

    @QtCore.pyqtSlot(str , str)
    def crashed_handler(self , title, message):
        self.handle_thread_crashing()
        QtW.QMessageBox.critical(
                None,                        # Parent: Use None if not within a QWidget class
                f"{title}",            # Title bar text
                f"{message}" # Main message
            )
        
    
    @QtCore.pyqtSlot()
    def plotting_finished(self):
        for i in range(0 , self.count()):
            widget = self.widget(i)
            widget.deleteLater()
        self.visual_plot = FigureCanvasQTAgg(self.worker.engine_results.visual_plot)
        self.accuracy_plot = FigureCanvasQTAgg(self.worker.engine_results.accuracy_plot)
        self.addTab(self.visual_plot , "Visualization Plot")
        self.addTab(self.accuracy_plot , "Accuracy")
        self.visual_plot.show()
        self.worker.ptr_to_training_button.setEnabled(True)
        del self.worker
        


class PlotterWorker(QtCore.QObject):
    progress = QtCore.pyqtSignal(int)
    crashed = QtCore.pyqtSignal(str , str)
    finished = QtCore.pyqtSignal()

    def __init__(self, lst_engine_pipelines , x_cols , y_cols , dataframe , ptr_to_training_button):
        super(PlotterWorker, self).__init__()
        self.lst_engine_pipelines = lst_engine_pipelines
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.ptr_to_training_button = ptr_to_training_button
        self.dataframe = dataframe


    @QtCore.pyqtSlot() # What does this do?
    def start_plotting(self):
        try:
            self.engine_results = sklearn_engine.SklearnEngine.main_sklearn_pipe(
                main_dataframe=self.dataframe,
                curr_pipelines=self.lst_engine_pipelines,
                pipeline_x_values=self.x_cols,
                pipeline_y_value=self.y_cols,
            )
            self.finished.emit()
        except Exception as e:
            self.crashed.emit("Unknown error" , str(e))
        except sklearn_engine.InternalEngineError as e:        
            self.crashed.emit("Internal Engine Error", str(e))




