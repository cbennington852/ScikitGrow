from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag , QIcon , QPixmap , QCursor
import PyQt5.QtCore as QtCore 
from draggable import Draggable , DraggableColumn
from sklearn.base import is_regressor, is_classifier
import sklearn

class GUILibary(QtW.QTabWidget):

    ###############################################
    # List of Filter / Accepting Functions
    ###############################################
    def model_filter(x):
        try:
            return is_classifier(x) or is_regressor(x)
        except:
            return False
    def regression_filter(x):
        try:
            return is_regressor(x)
        except:
            return False
    def classification_filter(x):
        try:
            return is_classifier(x)
        except:
            return False
    CLASSIFIER_FILTER = classification_filter
    PREPROCESSOR_FILTER = lambda x : hasattr(x, 'fit') and hasattr(x, 'transform') and (not hasattr(x , 'predict'))
    REGRESSOR_FILTER = regression_filter
    VALIDATOR_FILTER = lambda x : getattr(x, 'split', None) is not None and callable(getattr(x, 'split', None))
    MODEL_FILTER = model_filter





    def __init__(self , dataframe,  **kwargs):
        super().__init__(**kwargs)
        self.dataframe = dataframe
        sklearn_models = [
            (sklearn.linear_model,"#8F0177" , Draggable.BUBBLE),
            (sklearn.ensemble,"#360185" , Draggable.BUBBLE),
            (sklearn.preprocessing, "#301CA0" ,Draggable.INTERLOCK_RIGHT),
            (sklearn.tree ,"#DE1A58" , Draggable.BUBBLE),
            (sklearn.model_selection , "#235622" , Draggable.POINTY)
        ]

        def addModule(name , filter):    
            regressor_box = QtW.QWidget()
            regressor_layout = QtW.QVBoxLayout()
            regressor_box.setLayout(regressor_layout)
            for subsection , hex_color , render_type in sklearn_models:
                curr = GUILibarySubmodule(
                        sublibary=SubLibary.get_public_methods(
                            library=subsection,

                            filter_function=filter
                        ),
                        render_type=render_type,
                        hex_value=hex_color
                    )
                regressor_layout.addWidget(curr)
            scroll_regressor = QtW.QScrollArea()
            scroll_regressor.setWidget(regressor_box)
            scroll_regressor.setWidgetResizable(True)
            self.addTab(scroll_regressor , name)



        addModule("Regressors" , GUILibary.REGRESSOR_FILTER)
        addModule("Classifiers" , GUILibary.CLASSIFIER_FILTER)
        addModule("Pre-processors" , GUILibary.PREPROCESSOR_FILTER)
        addModule("Validators" , GUILibary.VALIDATOR_FILTER)



        self.addTab(self.cols_tab() , "Columns")

    def cols_tab(self):
        cols = ColumnsSubmodule(self.dataframe.columns.to_list())
        scroll = QtW.QScrollArea()
        scroll.setWidget(cols)
        scroll.setWidgetResizable(True)
        return scroll


class ColumnsSubmodule(QtW.QWidget):
    def __init__(self , lst_cols , **kwargs):
        super().__init__(**kwargs)
        self.layout = QVBoxLayout(self)
        self.setAcceptDrops(True)
        self.lst_cols = lst_cols
        for col in self.lst_cols:
            new_widget = DraggableColumn(col)
            self.layout.addWidget(new_widget)
    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        e.accept()
        
    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        from_parent = widget.parentWidget()
        to_parent = self
        if isinstance(from_parent , ColumnsSubmodule) and isinstance(to_parent , ColumnsSubmodule):
            e.accept()
        elif isinstance(from_parent , ColumnsSection) and isinstance(to_parent , ColumnsSubmodule):
            e.accept()
            from_parent.layout().removeWidget(widget)
            widget.deleteLater()

class GUILibarySubmodule(QtW.QGroupBox):
    def __init__(self , sublibary : SubLibary , render_type = "", hex_value = "",  **kwargs):
        super().__init__(**kwargs)
        self.layout = QVBoxLayout(self)
        self.setAcceptDrops(True)
        self.sublibary = sublibary
        self.setTitle(self.sublibary.library_name)
        if len(self.sublibary.function_calls) == 0:
            self.deleteLater()
        for sklearn in self.sublibary.function_calls:
            self.layout.addWidget(Draggable(
                name=str(sklearn.__name__),
                sklearn_function=sklearn,
                render_type=render_type,
                hex_color=hex_value
            ))
        
    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        e.accept()
        
    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        from_parent = widget.parentWidget()
        to_parent = self
        if isinstance(from_parent , GUILibarySubmodule) and isinstance(to_parent , GUILibarySubmodule):
            e.accept()
        elif isinstance(from_parent , PipelineSection) and isinstance(to_parent , GUILibarySubmodule):
            e.accept()
            from_parent.layout().removeWidget(widget)
            widget.deleteLater()

class ColumnsSection(QtW.QGroupBox):
    def __init__(self , title, max_num_cols = 100, **kwargs):
        super().__init__( **kwargs)
        self.my_title = title
        self.max_num_cols = max_num_cols
        self.resize(200 , 90)
        self.setAcceptDrops(True)
        self.my_layout = QVBoxLayout()
        self.setLayout(self.my_layout)
        self.setTitle(self.my_title)

    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if isinstance(widget , DraggableColumn):
            e.accept()        
        else:
            e.ignore()
    def get_num_cols(self):
        num = 0
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , DraggableColumn):
                num += 1
        return num
    
    def get_cols(self) -> list[DraggableColumn]:
        res_cols = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , DraggableColumn):
                res_cols.append(child)
        return res_cols

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if (self.get_num_cols() == self.max_num_cols):
            # Remove one the children from this
            for child in self.findChildren(QtW.QWidget):
                if isinstance(child , DraggableColumn) and child != widget:
                    e.accept()
                    self.my_layout.addWidget(widget)
                    child.deleteLater()
                    return
        # we can see the previous parent
        from_parent = widget.parentWidget()
        to_parent = self
        self.my_layout.addWidget(widget)
        if not isinstance(widget , DraggableColumn):
            e.ignore()
            return
        if isinstance(from_parent , ColumnsSubmodule) and isinstance(to_parent , ColumnsSection):
            e.accept()
            # Below adds a new widget copy of draggable to the library
            from_parent.layout.insertWidget(from_parent.layout.indexOf(widget) , widget.copy_self())
        elif isinstance(from_parent , ColumnsSection) and isinstance(to_parent , ColumnsSection):
            e.accept()

class PipelineSection(QtW.QGroupBox):
    def __init__(self , accepting_function, title, max_num_models = 100,  **kwargs):
        super().__init__( **kwargs)
        self.setTitle(title)
        self.max_num_models = max_num_models
        self.accepting_function = accepting_function
        self.setAcceptDrops(True)
        self.my_layout = QVBoxLayout()
        self.setLayout(self.my_layout)

    def get_pipeline_objects(self):
        resulting_models = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , Draggable):
                parameters_as_dict = dict(child.parameters)
                curr = child.sklearn_function(**parameters_as_dict)
                resulting_models.append(curr)
        return resulting_models

    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if isinstance(widget , Draggable):
            # now check to see if it meets this submodule.
            if self.accepting_function(widget.sklearn_function):
                e.accept()        
                
        else:
            e.ignore()
    def get_num_models(self):
        num = 0
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , Draggable):
                num += 1
        return num
    
    def get_models(self) -> list[Draggable]:
        res_models = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , Draggable):
                res_models.append(child)
        return res_models

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if (self.get_num_models() == self.max_num_models):
            # Remove one the children from this
            for child in self.findChildren(QtW.QWidget):
                if isinstance(child , Draggable) and child != widget:
                    e.accept()
                    self.my_layout.addWidget(widget)
                    child.deleteLater()
                    return
        # we can see the previous parent
        from_parent = widget.parentWidget()
        to_parent = self
        self.my_layout.addWidget(widget)
        if not isinstance(widget , Draggable):
            e.ignore()
            return
        # Sudo code:
            # Libary -> Libary
                # No replacement, only accept
            # Libary -> Pipeline
                # Yes replacement
            # Pipeline -> Libary
                # No replacement, only accept
            # Pipeline -> Pipeline
                # only accept
        if isinstance(from_parent , GUILibarySubmodule) and isinstance(to_parent , PipelineSection):
            e.accept()
            # Below adds a new widget copy of draggable to the library
            from_parent.layout.insertWidget(from_parent.layout.indexOf(widget) , widget.copy_self())
        elif isinstance(from_parent , PipelineSection) and isinstance(to_parent , PipelineSection):
            e.accept()

class Pipeline(QtW.QMdiSubWindow):
    all_pipelines = []

    def __init__(self, my_parent, GUI_parent ,  **kwargs):
        super().__init__(GUI_parent, **kwargs)
        my_layout = QVBoxLayout()
        main_thing = QtW.QWidget()
        self.my_parent = my_parent
        main_thing.setLayout(my_layout)
        self.resize(400 , 400)
        self.name_pipeline = QtW.QLineEdit()
        self.name_pipeline.setText(f"pipeline {1 + len(self.my_parent.pipelines)}")
        self.preproccessor_pipe = PipelineSection(
            title="Preproccessors",
            accepting_function=GUILibary.PREPROCESSOR_FILTER

        )
        self.model_pipe = PipelineSection(
            title="Models",
            accepting_function=GUILibary.MODEL_FILTER,
            max_num_models=1
        )
        self.validator = PipelineSection(
            title="Validator",
            # Makes sure this is a validator by checking if it has a 'split' function which is required.
            accepting_function=GUILibary.VALIDATOR_FILTER,
            max_num_models=1
        )
        my_layout.addWidget(self.name_pipeline)
        my_layout.addWidget(self.preproccessor_pipe)
        my_layout.addWidget(self.model_pipe)
        my_layout.addWidget(self.validator)
        self.setWidget(main_thing)

    def get_name_pipeline(self) -> str:
        return self.name_pipeline.text

    def closeEvent(self, event):
        for x in range(0 , len(self.my_parent.pipelines)):
            if self.my_parent.pipelines[x] == self:
                del self.my_parent.pipelines[x]
                self.deleteLater()
                super(QtW.QMdiSubWindow, self).closeEvent(event)
                return




class PipelineMother(QtW.QMainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowFlags(Qt.WindowType.Widget)
        self.pipelines = []
        self.train_models = None

        toolbar = QtW.QToolBar()
        self.main_thing = QtW.QMdiArea()
        self.main_thing.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))
        my_layout = QtW.QVBoxLayout()
        self.main_thing.setLayout(my_layout)
        self.add_pipeline_button = QtW.QPushButton("Add Pipeline")
        self.add_pipeline_button.setFixedSize(150 ,60)
        self.add_pipeline_button.setIcon(QIcon(":/images/add_pipeline.svg"))
        self.add_pipeline_button.clicked.connect(self.add_pipeline)
        toolbar.addWidget(self.add_pipeline_button)
        self.setCentralWidget(self.main_thing)
        self.addToolBar(toolbar)

        self.add_pipeline()

        self.render_x_y_train_sub_window()

    def render_x_y_train_sub_window(self):
        sub_window = QtW.QMdiSubWindow(self.main_thing)
        sub_window.resize(400 , 300)
        main_widget = QtW.QWidget()
        mayo = QtW.QVBoxLayout()
        main_widget.setLayout(mayo)
        sub_window.setWidget(main_widget)


        self.train_models = QtW.QPushButton(
            "Train Models"
        )
        play_icon = self.style().standardIcon(QtW.QStyle.SP_MediaPlay)
        
        # Set the icon on the button
        self.train_models.setIcon(play_icon)


        self.x_columns = ColumnsSection(
            "X axis",
            max_num_cols=400
        )
        self.y_columns = ColumnsSection(
            "Y axis",
            max_num_cols=1
        )

        mayo.addWidget(self.train_models)
        mayo.addWidget(self.x_columns)
        mayo.addWidget(self.y_columns)

        sub_window.show()

    def add_pipeline(self):
        new_pipeline = Pipeline(self , self.main_thing)
        new_pipeline.move(30 , 30)
        new_pipeline.show()
        self.pipelines.append(new_pipeline)
