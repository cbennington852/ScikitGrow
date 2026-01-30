from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QIcon
import PyQt5.QtCore as QtCore 
import multiprocessing
import sys
import time
import matplotlib
import traceback
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from . import sklearn_engine
import sklearn
import pandas as pd
import threading
from .GUI_libary_and_pipeline_mother import PipelineMother , Pipeline
import matplotlib.pyplot as plt
from .predictor_GUI import PredictionGUI
from .descriptor_statistics_GUI import DescriptorStatisticsGUI , GeneralDescriptor




class ScikitGrowEngineAssemblyError(Exception):
    pass



class Plotter(QtW.QTabWidget):

    TIME_DELAY_UNTIL_PROGRESS_WINDOW = 0.7


    def __init__(self , pipeline_mother : PipelineMother, dataframe : pd.DataFrame , **kwargs):
        super().__init__(**kwargs)
        self.pipeline_mother = pipeline_mother
        self.work_done = False
        self.pipeline_mother.train_models.clicked.connect(self.plot_pipeline)
        self.dataframe = dataframe

        fig, ax = plt.subplots(figsize=(2, 2))
        ax.grid(visible=True, color='white', linestyle='-', linewidth=0.5)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')

        fig2, ax2 = plt.subplots(figsize=(2, 2))
        ax2.grid(visible=True,  linestyle='-', linewidth=0.5)
        ax2.set_xlim(0, 10)
        ax2.set_ylim(0, 10)
        ax2.set_xlabel('X Axis')
        ax2.set_ylabel('Y Axis')

        self.visual_plot = FigureCanvasQTAgg(fig)
        self.accuracy_plot = FigureCanvasQTAgg(fig)

        self.prediction_tab = QWidget()
        self.descriptive_statistics = QWidget()
        
        self.addTab(self.visual_plot , "Visualization Plot")
        self.addTab(self.accuracy_plot , "Accuracy")
        self.addTab(self.prediction_tab , "Manual Predictions")
        self.addTab(self.descriptive_statistics , "Descriptive Statistics")


    def handle_thread_crashing(self):
        self.do_regardless()
        if hasattr(self , "worker_thread"):
            self.worker_thread.exit()
            self.worker_thread.wait()

    def do_regardless(self):
        self.ptr_to_train_models_button.setEnabled(True)
        try:
            self.prog_box.close()
        except:
            pass
        if hasattr(self , 'spinner_thread'):
            self.spinner_thread.join()
        if hasattr(self , 'worker'):
            self.worker.ptr_to_training_button.setEnabled(True)
        self.work_done = True
        

        
        
    @QtCore.pyqtSlot()
    def plot_pipeline(self):
        self.work_done = False
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
                    raise ScikitGrowEngineAssemblyError(f"{gui_pipeline.name_pipeline.text()} is missing a model")
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
            # TESTING : Make a small popup to for this. 
            
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

            # Start a popup with a dialog
            self.prog_box = QtW.QProgressDialog("Training Models...", "Abort", 0, 0, self)
            self.prog_box.canceled.connect(lambda : self.worker_thread.requestInterruption())
            self.prog_box.show()
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
        if (title == PlotterWorker.INTERRUPT_TITLE) and (message == PlotterWorker.INTERRUPT_MESSAGE):
            pass
        else:
            QtW.QMessageBox.critical(
                None,                        # Parent: Use None if not within a QWidget class
                f"{title}",            # Title bar text
                f"{message}" # Main message
            )
        self.handle_thread_crashing()
        
    def resolve_accuracy(self , engine_results):
        # scroller
        scroller = QtW.QScrollArea()
        # Main area
        main_area = QtW.QWidget()
        main_layout = QtW.QVBoxLayout()
        main_area.setLayout(main_layout)
        # The plot.
        # The stats section
        stats_box = QtW.QGroupBox("Relevant Statistics")
        stats_layout = QtW.QVBoxLayout()
        stats_box.setLayout(stats_layout)
        for pipeline in engine_results.trained_models:
            pipeline_group_box = QtW.QGroupBox()
            pipeline_group_box.setTitle(f"{pipeline.name}")
            pipeline_group_box_lay = QtW.QFormLayout()
            pipeline_group_box.setLayout(pipeline_group_box_lay)
            for stat_name , value in pipeline.model_results.relevant_statistical_results:
                print(f"stat: {stat_name} , Val:{value}")
                pipeline_group_box_lay.addRow(QtW.QLabel(stat_name) , QtW.QLabel(str(round(value , GeneralDescriptor.digit_rounding))))
            stats_layout.addWidget(pipeline_group_box)

        main_layout.addWidget(FigureCanvasQTAgg(engine_results.accuracy_plot))
        main_layout.addWidget(stats_box)
        scroller.setWidget(main_area)
        return scroller

    @QtCore.pyqtSlot()
    def plotting_finished(self):
        for i in range(0 , self.count()):
            widget = self.widget(i)
            widget.deleteLater()
        self.visual_plot = FigureCanvasQTAgg(self.worker.engine_results.visual_plot)
        try:
            self.accuracy_plot = self.resolve_accuracy(self.worker.engine_results)
        except Exception as e:
            traceback.print_exception(e)
            print(str(e))
            self.accuracy_plot = QtW.QWidget()
        try:
            self.prediction_tab = PredictionGUI(self.worker.engine_results)
        except Exception as e:
            print("ERROR PREDICTION GUI" , str(e))
            traceback.print_exception(e)
            self.prediction_tab = QtW.QWidget()
        try: 
            self.descriptive_statistics = DescriptorStatisticsGUI(self.worker.engine_results , self.dataframe)
            print("HIIIII" , self.descriptive_statistics)
        except Exception as e:
            traceback.print_exception(e)
            print("ERROR DESCRIPTOR STATS" , str(e))
            self.descriptive_statistics = QtW.QWidget()
        self.addTab(self.visual_plot , "Visualization Plot")
        self.addTab(self.accuracy_plot , "Accuracy")
        self.addTab(self.prediction_tab , "Manual Predictions")
        self.addTab(self.descriptive_statistics , "Descriptive Statistics")

        self.visual_plot.show()
        self.do_regardless()
        
        # Tell the predictor to re-render
        


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

    INTERRUPT_TITLE = "Ended"
    INTERRUPT_MESSAGE = "Process interrupted by user."

    @QtCore.pyqtSlot() # What does this do?
    def start_plotting(self):
        def runner_wrapper(queue , main_dataframe , curr_pipelines , pipeline_x_values , pipeline_y_values):
            try:
                curr_results = sklearn_engine.SklearnEngine.main_sklearn_pipe(
                    main_dataframe=main_dataframe,
                    curr_pipelines=curr_pipelines,
                    pipeline_x_values=pipeline_x_values,
                    pipeline_y_value=pipeline_y_values,
                )
                queue.put(curr_results)
            except Exception as e:
                queue.put("Major Issue: " + str(e))

        queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=runner_wrapper, args=(
            queue,
            self.dataframe,
            self.lst_engine_pipelines,
            self.x_cols,
            self.y_cols
        ))
        process.start()
        results = 0
        while process.is_alive():
            # Check for cancel option
            is_interruption = self.thread().isInterruptionRequested()
            print("Interruption status: " , is_interruption )
            if is_interruption == True:
                process.kill()
                self.crashed.emit(PlotterWorker.INTERRUPT_TITLE , PlotterWorker.INTERRUPT_MESSAGE)
                return
            
            # Check for the result
            if not queue.empty():
                print("Got results")
                results = queue.get()
            else:
                print("Results empty")
            print("Still alive")
        print("Exit code: ", process)
        print("Results: " , results)
        if isinstance(results , Exception):
            self.crashed.emit("Error" , str(results))
        else:
            self.engine_results = results
            self.finished.emit()




