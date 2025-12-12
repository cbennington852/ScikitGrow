from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
import PyQt5.QtCore as QCore 
from draggable import Draggable
from sklearn.base import is_regressor, is_classifier
import sklearn

class GUILibary(QtW.QTabWidget):
    def __init__(self , **kwargs):
        super().__init__(**kwargs)

        sklearn_models = [
            sklearn.linear_model,
            sklearn.ensemble,
        ]

        # Adding regressors.
        regressor_box = QtW.QWidget()
        regressor_layout = QtW.QVBoxLayout()
        regressor_box.setLayout(regressor_layout)
        for subsection in sklearn_models:
            regressor_layout.addWidget(
                GUILibarySubmodule(
                    SubLibary.get_public_methods(
                        library=subsection,
                        filter_function=lambda x : is_regressor(x)
                    )
                )
            )
        self.addTab(regressor_box , "Regressors")



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
        self.my_layout.addWidget(QtW.QLabel("drag here"))

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
            e.ignore()
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

class Pipeline(QtW.QDockWidget):
    def __init__(self, my_parent, **kwargs):
        super().__init__("Pipeline"  , **kwargs)
        main_box = QtW.QWidget()
        my_layout = QVBoxLayout()
        self.my_parent = my_parent
        main_box.setLayout(my_layout)
        self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)
        self.preproccessor_pipe = PipelineSection(
            title="Preproccessors",
            accepting_function=lambda x : x.__module__.startswith("preprocessing")

        )
        self.model_pipe = PipelineSection(
            title="Models",
            accepting_function=lambda x : is_classifier(x) or is_regressor(x),
            max_num_models=1
        )
        my_layout.addWidget(self.preproccessor_pipe)
        my_layout.addWidget(self.model_pipe)
        self.setWidget(main_box)

    def moveEvent(self, moveEvent):
        geo = self.my_parent.geometry()
        print(f"Pipeline Window : {moveEvent.pos()}")
        print(f"Pos : {self.my_parent.pos()} , Left : {self.my_parent.width()} , Right : {self.my_parent.height()}")
        return super().moveEvent(moveEvent)


class PipelineMother(QtW.QMainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowFlags(Qt.WindowType.Widget)
        self.resize(600 , 600)
        toolbar = QtW.QToolBar()
        self.add_pipeline_button = QtW.QPushButton("Add Pipeline")
        self.add_pipeline_button.clicked.connect(self.add_pipeline)
        toolbar.addWidget(self.add_pipeline_button)
        self.addToolBar(toolbar)
        self.add_pipeline()

    def add_pipeline(self):
        new_pipeline = Pipeline(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,  new_pipeline)
        new_pipeline.setFloating(True)
        new_pipeline.resize(300 , 300)
        print(f"Mother Pos : ({self.pos().x()},{self.pos().y()})")
        new_pipeline.move(
            self.pos().x(),
            self.pos().y()
        )
