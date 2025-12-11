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
        
        if not isinstance(widget , Draggable):
            e.reject()
        # Sudo code:
            # Libary -> Libary
                # No replacement, only accept
            # Libary -> Pipeline
                # Yes replacement
            # Pipeline -> Libary
                # No replacement, only accept, remove from pipeline
            # Pipeline -> Pipeline
                # only accept
        


    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        from_parent = widget.parentWidget()
        to_parent = self
        #print(f"Prev Parent : {from_parent} , To Parent : {to_parent}")
        if isinstance(from_parent , GUILibarySubmodule) and isinstance(to_parent , GUILibarySubmodule):
            e.accept()
        elif isinstance(from_parent , Pipeline) and isinstance(to_parent , GUILibarySubmodule):
            e.accept()
            from_parent.layout().removeWidget(widget)
            widget.deleteLater()

class Pipeline(QtW.QWidget):
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
        #print(f"Prev Parent : {from_parent} , To Parent : {to_parent}")
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
        if isinstance(from_parent , GUILibarySubmodule) and isinstance(to_parent , Pipeline):
            e.accept()
            # Below adds a new widget copy of draggable to the library
            from_parent.layout.insertWidget(from_parent.layout.indexOf(widget) , widget.copy_self())
        elif isinstance(from_parent , Pipeline) and isinstance(to_parent , Pipeline):
            e.accept()
        #if isinstance(self.parentWidget() , GUILibarySubmodule):
                # insert a copy in the same position of the old one.
            #    self.parentWidget().layout.insertWidget(self.parentWidget().layout.indexOf(self) , self.copy_self())

