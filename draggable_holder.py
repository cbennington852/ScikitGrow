from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag , QIcon , QPixmap , QCursor , QColor , QPolygon, QPen, QBrush, QIcon, QPainter
import PyQt5.QtCore as QtCore 
from draggable import Draggable , DraggableColumn
from sklearn.base import is_regressor, is_classifier
import sklearn



class DragAndDropHolder(QtW.QGroupBox):
    def __init__(self , 
                title : str, 
                my_parent : QtW.QMdiSubWindow,
                holds_one_thing : bool, 
                type_draggable, 
                render_function,
                parent_submodule_type, 
                **kwargs
                ):
        """
        A general class to handle drop and dropping into things. From library tp draggable should have just been a copy operation.

        Args:
            title (str): The name to be displayed in the box, telling what goes here.
            my_parent (_type_): The subwindow parent, who should have a method called "resize_based_on_children"
            holds_one_thing (bool): States if it holds one thing
            type_draggable (_type_): Class of the draggable that this accepts
            render_function (_type_): Function to render this to the screen. This overrides paintEvent()
            parent_submodule_type (_type_): 
        """
        super().__init__( **kwargs)
        self.my_title = title
        self.parent_submodule_type = parent_submodule_type
        self.render_function = render_function
        self.type_draggable = type_draggable
        self.my_parent = my_parent
        self.holds_one_thing = holds_one_thing
        self.resize(200 , 90)
        self.setAcceptDrops(True)
        self.my_layout = QVBoxLayout()
        self.setLayout(self.my_layout)
        self.setTitle(self.my_title)


    def dragEnterEvent(self, e):
        widget = e.source()
        if isinstance(widget , self.type_draggable):
            e.accept()        
            self.model_hovering = True
        else:
            e.ignore()
        self.repaint()  
        

    def dragLeaveEvent(self, e):
        self.model_hovering = False
        self.repaint()
        e.accept() 

    def get_num_held(self) -> int:
        return len(self.get_held())
    
    def get_held(self) -> list:
        res_cols = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , self.type_draggable):
                res_cols.append(child)
        return res_cols

    def paintEvent(self, event):
        if self.render_function:
            self.render_function(event)
        else:
            return super().paintEvent(event)

    # def dropEvent(self, e):
    #     widget = e.source()        
    #     if (self.holds_one_thing == True):
    #         for child in self.findChildren(QtW.QWidget):
    #             if isinstance(child , self.type_draggable) and child != widget:
    #                 e.accept()
    #                 self.my_layout.addWidget(widget.copy_self())
    #                 child.deleteLater()
    #                 return
    #     else:
    #         self.my_layout.addWidget(widget.copy_self())


    def dropEvent(self , e):
        widget = e.source()
        parent = widget.parentWidget()     

        if self.holds_one_thing == True:
            # Remove all children, add a copy of this puppy.
            for child in self.findChildren(QtW.QWidget):
                child.deleteLater()
            self.my_layout.addWidget(widget.copy_self())
            e.accept()
        else:
            self.my_layout.addWidget(widget.copy_self())
            e.accept()


    def clean_up_parent(self, e , widget , from_parent, to_parent):
        # Below decides how and ifwe should make a copy in the parents box. 
        if not isinstance(widget , self.type_draggable):
            e.ignore()
            return
        
        if isinstance(from_parent , self.parent_submodule_type) and isinstance(to_parent , DragAndDropHolder):
            e.accept()
            self.my_parent.resize_based_on_children()
            # Below adds a new widget copy of draggable to the library
            from_parent.layout.insertWidget(from_parent.layout.indexOf(widget)-1 , widget.copy_self())

        elif isinstance(from_parent , DragAndDropHolder) and isinstance(to_parent , DragAndDropHolder):
            e.accept()
            self.my_parent.resize_based_on_children()

        else:
            raise ValueError("Unknown drag and drop operation.")