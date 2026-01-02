from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag , QIcon , QPixmap , QCursor , QColor , QPolygon, QPen, QBrush, QIcon, QPainter
import PyQt5.QtCore as QtCore 
from draggable import Draggable , DraggableColumn , DraggableData
from sklearn.base import is_regressor, is_classifier
import sklearn
from column_pipeline import ColumnsSection , ColumnsSubmodule
from draggable_pipeline import DraggableColumn , PipelineSection, Pipeline, PipelineData, GUILibarySubmodule
from list_of_acceptable_sklearn_functions import SklearnAcceptableFunctions
from colors_and_appearance import AppAppearance

class ColumnsWindowData():
    def __init__(self , x_cols : list[str] , y_cols : list[str]):
        self.x_cols = x_cols
        self.y_cols = y_cols

class GUILibary(QtW.QTabWidget):
    def __init__(self , dataframe,  **kwargs):
        super().__init__(**kwargs)
        self.dataframe = dataframe
      
        # Styling
        self.setTabPosition(QtW.QTabWidget.West)

        self.curr_index = 0
        def addModule(name , q_widget_list):    
            scroll_regressor = QtW.QScrollArea()
            scroll_regressor.setWidget(q_widget_list)
            scroll_regressor.setWidgetResizable(True)
            if isinstance(name , QIcon):
                self.addTab(scroll_regressor , "")
                self.setTabIcon(self.curr_index , name)
                self.setIconSize(QtCore.QSize(90 , 90))
            else:
                self.addTab(scroll_regressor , name)
            self.curr_index += 1



        ########################################################
        # REGRESSORS
        ########################################################

        regressor_box = QtW.QWidget()
        regressor_layout = QtW.QVBoxLayout()
        regressor_box.setLayout(regressor_layout)

        # make sublibaries from the picked out lists. 
        lin_reg = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.REGRESSORS_LINEAR,
                "Linear Models"
            ),
            render_type=Draggable.BUBBLE,
            hex_value=AppAppearance.REGRESSOR_LINEAR_COLOR
        ) 
        lin_ens = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.REGRESSORS_ENSEMBLE,
                "Ensemble Models"
            ),
            render_type=Draggable.BUBBLE,
            hex_value=AppAppearance.REGRESSOR_ENSEMBLE_COLOR
        ) 
        lin_neu = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.REGRESSORS_NEURAL_NETWORK,
                "Neural Network Models"
            ),
            render_type=Draggable.BUBBLE,
            hex_value=AppAppearance.REGRESSOR_NEURAL_COLOR
        ) 
        lin_tre = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.REGRESSORS_TREE,
                "Tree Models"
            ),
            render_type=Draggable.BUBBLE,
            hex_value=AppAppearance.REGRESSOR_TREE_COLOR
        ) 
        regressor_layout.addWidget(lin_reg)
        regressor_layout.addWidget(lin_ens)
        regressor_layout.addWidget(lin_tre)
        regressor_layout.addWidget(lin_neu)

        ########################################################
        # CLASSIFIERS 
        ########################################################

        classifier_box = QtW.QWidget()
        classifier_layout = QtW.QVBoxLayout()
        classifier_box.setLayout(classifier_layout)
        cla_reg = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.CLASSIFIERS_LINEAR,
                "Linear Models"
            ),
            render_type=Draggable.BUBBLE,
            hex_value=AppAppearance.CLASSIFIER_LINEAR_COLOR
        ) 
        cla_ens = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.CLASSIFIERS_ENSEMBLE,
                "Ensemble Models"
            ),
            render_type=Draggable.BUBBLE,
            hex_value=AppAppearance.CLASSIFIER_ENSEMBLE_COLOR
        ) 
        cla_neu = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.CLASSIFIERS_NEURAL,
                "Neural Network Models"
            ),
            render_type=Draggable.BUBBLE,
            hex_value=AppAppearance.CLASSIFIER_NEURAL_COLOR
        ) 
        cla_tre = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.CLASSIFIERS_TREE,
                "Tree Models"
            ),
            render_type=Draggable.BUBBLE,
            hex_value=AppAppearance.CLASSIFIER_TREE_COLOR
        ) 
        classifier_layout.addWidget(cla_reg)
        classifier_layout.addWidget(cla_ens)
        classifier_layout.addWidget(cla_tre)
        classifier_layout.addWidget(cla_neu)


        ########################################################
        # PRE_PROCESSORS
        ########################################################
        preproccessor_box = QtW.QWidget()
        preproccessor_layout = QtW.QVBoxLayout()
        preproccessor_box.setLayout(preproccessor_layout)
        pre_sub_module = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.PREPROCESSORS,
                ""
            ),
            render_type=Draggable.INTERLOCK_RIGHT,
            hex_value=AppAppearance.PREPROCESSOR_COLOR
        ) 
        preproccessor_layout.addWidget(pre_sub_module)


        ########################################################
        # VALIDATORS
        ########################################################

        validator_box = QtW.QWidget()
        validator_layout = QtW.QVBoxLayout()
        validator_box.setLayout(validator_layout)
        vali_submodule = GUILibarySubmodule(
            sublibary=SubLibary(
                SklearnAcceptableFunctions.VALIDATORS,
                ""
            ),
            render_type=Draggable.POINTY,
            hex_value=AppAppearance.VALIDATOR_COLOR
        ) 
        validator_layout.addWidget(vali_submodule)

        addModule(QIcon(":/images/reggessor_icon.svg") , regressor_box)
        addModule(QIcon(":/images/classification_icon.svg") , classifier_box)
        addModule(QIcon(":/images/preproccessor_icon.svg") , preproccessor_box)
        addModule(QIcon(":/images/validators_icon.svg") , validator_box)


        self.addTab(self.cols_tab() ,"")
        self.setTabIcon(self.curr_index , QIcon(":/images/columns_icon.svg"))

        curr_index = 0

    def cols_tab(self):
        cols = ColumnsSubmodule(self.dataframe.columns.to_list())
        scroll = QtW.QScrollArea()
        scroll.setWidget(cols)
        scroll.setWidgetResizable(True)
        return scroll



class PipelineMDIArea(QtW.QMdiArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))
        my_layout = QtW.QVBoxLayout()
        self.setLayout(my_layout)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        #Disable below, as not essental.
        return super().dropEvent(e)



class PipelineMother(QtW.QMainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowFlags(Qt.WindowType.Widget)
        self.pipelines : Pipeline = []
        self.train_models = None

        toolbar = QtW.QToolBar()
        self.main_thing = PipelineMDIArea(self)
        
        self.add_pipeline_button = QtW.QPushButton("Add Pipeline")
        self.add_pipeline_button.setFixedSize(150 ,60)
        self.add_pipeline_button.setIcon(QIcon(":/images/add_pipeline.svg"))
        self.add_pipeline_button.clicked.connect(self.add_pipeline)
        toolbar.addWidget(self.add_pipeline_button)
        self.setCentralWidget(self.main_thing)
        self.addToolBar(toolbar)

        self.add_pipeline()

        self.columns_subwindow = ColumnsMDIWindow(self.main_thing)
        
        self.x_columns = self.columns_subwindow.x_columns
        self.y_columns = self.columns_subwindow.y_columns
        self.train_models = self.columns_subwindow.train_models

    def get_columns_data(self) -> ColumnsWindowData:
        return self.columns_subwindow.save_data()
      
    def get_data(self) -> list[PipelineData]:
        # Only really need to save the pipelines ... and maybe also the column sections.
        lst_pipeline_data = []
        for pipeline in self.pipelines:
            lst_pipeline_data.append(pipeline.get_pipeline_data())
        return lst_pipeline_data
    
    def load_from_data(self , pipelines_data : list[PipelineData] , cols_data : ColumnsWindowData):
        # Make sure to remove the starter pipeline
        for pipeline in self.pipelines:
            pipeline.close()
        # Simply loop thru the parsel, and re-populate the pipelines.
        for pipe_data in pipelines_data:
            curr = Pipeline.pipeline_from_data(
                my_parent=self, 
                GUI_parent=self.main_thing,
                data=pipe_data,
            )
            self.pipelines.append(curr)
        #also tell the cols to re-populate
        self.columns_subwindow.load_data(cols_data)


    def add_pipeline(self):
        new_pipeline = Pipeline(self , self.main_thing)
        new_pipeline.move(30 , 30)
        new_pipeline.show()
        self.pipelines.append(new_pipeline)



class ColumnsMDIWindow(QtW.QMdiSubWindow):
    BASE_HEIGHT = 300
    BASE_WIDTH = 400
    def __init__(self, parent , **kwargs):
        super().__init__(parent, **kwargs)
        self.setFixedSize(ColumnsMDIWindow.BASE_WIDTH , ColumnsMDIWindow.BASE_HEIGHT)
        main_widget = QtW.QWidget()
        mayo = QtW.QVBoxLayout()
        main_widget.setLayout(mayo)
        self.setWidget(main_widget)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint , False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint , False)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        self.setStyleSheet(f"background-color:{AppAppearance.PIPELINE_BACKGROUND_COLOR}")

        self.train_models = QtW.QPushButton(
            "Train Models"
        )
        play_icon = self.style().standardIcon(QtW.QStyle.SP_MediaPlay)
        
        # Set the icon on the button
        self.train_models.setIcon(play_icon)


        self.x_columns = ColumnsSection(
            "X axis",
            my_parent=self,
            max_num_cols=400
        )
        self.y_columns = ColumnsSection(
            "Y axis",
            my_parent=self,
            max_num_cols=1
        )

        mayo.addWidget(self.train_models)
        mayo.addWidget(self.x_columns)
        #mayo.addStretch(1)
        mayo.addWidget(self.y_columns)
        self.show()

    def save_data(self):
        return ColumnsWindowData(
            self.x_columns.get_cols_as_string_list(),
            self.y_columns.get_cols_as_string_list()
        )
    
    def load_data(self , data : ColumnsWindowData):
        self.x_columns.set_cols_as_string_list(data.x_cols)
        self.y_columns.set_cols_as_string_list(data.y_cols)

    def closeEvent(self, event):
        event.ignore()
    
    def resize_based_on_children(self):
        # get the number of pre-proccessors and their height, default to zero if one or below. 
        y_col_height = max((self.x_columns.get_num_cols()-1) * DraggableColumn.BASE_HEIGHT , 0)
        print(f"Suggested y_col_height : {y_col_height}")
        # Resize the pipeline based on the children size n_stuff.
        self.setFixedHeight(ColumnsMDIWindow.BASE_HEIGHT + y_col_height)