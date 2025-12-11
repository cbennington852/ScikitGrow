from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag
import PyQt5.QtCore as QCore 
from draggable import Draggable


class GUILibarySubmodule(QWidget):
    def __init__(self , sublibary : SubLibary , **kwargs):
        super().__init__(**kwargs) 
        self.layout = QVBoxLayout(self)
        self.setAcceptDrops(True)
        self.sublibary = sublibary
        self.layout.addWidget(QLabel(self.sublibary.library_name))
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

class PipelineSection(QtW.QWidget):
    def __init__(self , **kwargs):
        super().__init__( **kwargs)
        self.resize(300 , 300)
        self.setAcceptDrops(True)
        self.my_layout = QVBoxLayout()
        self.setLayout(self.my_layout)
        self.my_layout.addWidget(QtW.QLabel("HEllo, drag here"))

    def get_pipeline_objects():
        pass

    def dragEnterEvent(self, e):
        e.accept()
    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        # we can see the previous parent
        from_parent = widget.parentWidget()
        to_parent = self
        print(f"Prev Parent : {from_parent} , To Parent : {to_parent}")
        self.my_layout.addWidget(widget)
        if not isinstance(widget , Draggable):
            e.reject()
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
        my_layout.addWidget(PipelineSection())
        self.setWidget(main_box)
    def moveEvent(self, moveEvent):
        
        print(f"Pipeline Window : {moveEvent.pos()}")
        print(f"Pos : {self.my_parent.pos()} , Width : {self.my_parent.width()} , Length : {self.my_parent.height()}")
        return super().moveEvent(moveEvent)


class PipelineMother(QtW.QMainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowFlags(Qt.WindowType.Widget)
        self.resize(600 , 600)
        toolbar = QtW.QToolBar()
        add_pipeline_button = QtW.QPushButton("Add Pipeline")
        add_pipeline_button.clicked.connect(self.add_pipeline)
        toolbar.addWidget(add_pipeline_button)
        self.addToolBar(toolbar)

    def add_pipeline(self):
        new_pipeline = Pipeline(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,  new_pipeline)
        new_pipeline.setFloating(True)
        new_pipeline.resize(300 , 300)
