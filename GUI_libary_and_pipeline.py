from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
import PyQt5.QtCore as QtCore 
from draggable import Draggable , DraggableColumn
from sklearn.base import is_regressor, is_classifier
import sklearn

class GUILibary(QtW.QTabWidget):
    def __init__(self , dataframe,  **kwargs):
        super().__init__(**kwargs)
        self.dataframe = dataframe
        sklearn_models = [
            sklearn.linear_model,
            sklearn.ensemble,
        ]

        # Adding regressors.
        regressor_box = QtW.QWidget()
        regressor_layout = QtW.QVBoxLayout()
        
        regressor_box.setLayout(regressor_layout)
        for subsection in sklearn_models:
            curr = GUILibarySubmodule(
                    SubLibary.get_public_methods(
                        library=subsection,
                        filter_function=lambda x : is_regressor(x)
                    )
                )
            regressor_layout.addWidget(curr)
        scroll_regressor = QtW.QScrollArea()
        scroll_regressor.setWidget(regressor_box)
        scroll_regressor.setWidgetResizable(True)
        self.addTab(scroll_regressor , "Regressors")
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
        print(f"Prev Parent : {from_parent} , To Parent : {to_parent}")
        if isinstance(from_parent , ColumnsSubmodule) and isinstance(to_parent , ColumnsSubmodule):
            e.accept()
        elif isinstance(from_parent , ColumnsSection) and isinstance(to_parent , ColumnsSubmodule):
            e.accept()
            from_parent.layout().removeWidget(widget)
            widget.deleteLater()

class GUILibarySubmodule(QtW.QGroupBox):
    def __init__(self , sublibary : SubLibary , **kwargs):
        super().__init__(**kwargs)
        self.layout = QVBoxLayout(self)
        self.setAcceptDrops(True)
        self.sublibary = sublibary
        self.setTitle(self.sublibary.library_name)
        for sklearn in self.sublibary.function_calls:
            self.layout.addWidget(Draggable(
                str(sklearn.__name__),
                sklearn
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
        print(f"Prev Parent : {from_parent} , To Parent : {to_parent}")
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
        print("Col enter : " , widget)
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

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if (self.get_num_cols() == self.max_num_cols):
            print("Hello, max limit hit")
            # Remove one the children from this
            for child in self.findChildren(QtW.QWidget):
                if isinstance(child , DraggableColumn) and child != widget:
                    print("Times called" , child , widget)
                    e.accept()
                    self.my_layout.addWidget(widget)
                    child.deleteLater()
                    return
        # we can see the previous parent
        from_parent = widget.parentWidget()
        to_parent = self
        print(f"Prev Parent : {from_parent} , To Parent : {to_parent}")
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
        self.resize(300 , 300)
        self.setTitle(title)
        self.max_num_models = max_num_models
        self.accepting_function = accepting_function
        self.setAcceptDrops(True)
        self.my_layout = QVBoxLayout()
        self.setLayout(self.my_layout)

    def get_pipeline_objects(self):
        resulting_models = []
        for child in self.findChildren():
            if isinstance(child , Draggable):
                curr = child.sklearn_function(**child.parameters)
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

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if (self.get_num_models() == self.max_num_models):
            print("Hello, max limit hit")
            # Remove one the children from this
            for child in self.findChildren(QtW.QWidget):
                if isinstance(child , Draggable) and child != widget:
                    print("Times called" , child , widget)
                    e.accept()
                    self.my_layout.addWidget(widget)
                    child.deleteLater()
                    return
        # we can see the previous parent
        from_parent = widget.parentWidget()
        to_parent = self
        print(f"Prev Parent : {from_parent} , To Parent : {to_parent}")
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

class Pipeline(QtW.QGroupBox):
    def __init__(self, my_parent, GUI_parent ,  **kwargs):
        super().__init__(GUI_parent, **kwargs)
        my_layout = QVBoxLayout()
        self.my_parent = my_parent
        self.setLayout(my_layout)
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(300 , 300)
        self.preproccessor_pipe = PipelineSection(
            title="Preproccessors",
            accepting_function=lambda x : x.__module__.startswith("preprocessing")

        )
        self.model_pipe = PipelineSection(
            title="Models",
            accepting_function=lambda x : is_classifier(x) or is_regressor(x),
            max_num_models=1
        )
        self.close_pipeline_button = QtW.QPushButton("Close pipeline")
        self.close_pipeline_button.clicked.connect(self.remove_pipeline)
        my_layout.addWidget(self.close_pipeline_button)
        my_layout.addWidget(self.preproccessor_pipe)
        my_layout.addWidget(self.model_pipe)

    def remove_pipeline(self):
        for x in range(0 , len(PipelineMother.pipelines)):
            if PipelineMother.pipelines[x] == self:
                del PipelineMother.pipelines[x]
        self.deleteLater()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()
            # Bring the dragged widget to the front of its siblings
            self.raise_() 

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            # Calculate the new position relative to the parent widget
            # global position of mouse - global position of parent + the offset recorded in mousePressEvent
            # OR simpler: use mapToParent() with the current event position and subtract the initial offset
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        self.offset = QPoint()


    def moveEvent(self, moveEvent):
        geo = self.my_parent.geometry()
        #print(f"Pipeline Window : {moveEvent.pos()}")
        #print(f"Pos : {self.my_parent.pos()} , Left : {self.my_parent.width()} , Right : {self.my_parent.height()}")
        return super().moveEvent(moveEvent)


class PipelineMother(QtW.QMainWindow):
    pipelines = []
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowFlags(Qt.WindowType.Widget)
        self.resize(600 , 600)
        toolbar = QtW.QToolBar()
        self.main_thing = QtW.QWidget()
        self.add_pipeline_button = QtW.QPushButton("Add Pipeline")
        self.add_pipeline_button.clicked.connect(self.add_pipeline)

        # X cols
        self.x_columns = ColumnsSection(
            "X axis",
            max_num_cols=400
        )
        self.y_columns = ColumnsSection(
            "Y axis",
            max_num_cols=1
        )

        self.train_models = QtW.QPushButton(
            "Train Models"
        )
        self.train_models.clicked.connect(self.train_models_pressed)

        toolbar.addWidget(self.add_pipeline_button)
        toolbar.addWidget(self.train_models)
        toolbar.addWidget(self.x_columns)
        toolbar.addWidget(self.y_columns)

        self.setCentralWidget(self.main_thing)
        self.addToolBar(toolbar)
        self.add_pipeline()

    def train_models_pressed(self):
        pass


    def add_pipeline(self):
        new_pipeline = Pipeline(self , self.main_thing)
        new_pipeline.move(30 , 30)
        new_pipeline.show()
        self.pipelines.append(new_pipeline)
        print(f"Mother Pos : ({self.pos().x()},{self.pos().y()})")
        print(f"Pipeline Pos : ({new_pipeline.pos().x()},{new_pipeline.pos().y()})")
