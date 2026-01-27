from .draggable import Draggable , DraggableData
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtGui import QDrag , QIcon , QPixmap , QCursor , QColor , QPolygon, QPen, QBrush, QIcon, QPainter
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from .column_pipeline import DraggableColumn , ColumnsSection
from .list_of_acceptable_sklearn_functions import SklearnAcceptableFunctions
from .colors_and_appearance import AppAppearance
from . import drag_and_drop_utility as dnd
from .draggable_pipeline import PipelineSection


class ColumnsSubmodule(QtW.QWidget):
    def __init__(self , lst_cols , **kwargs):
        """
        A part of the GUI library, this renders a group of draggable columns to the library. 

        Args:
            lst_cols (str): list of strings of the dataframe columns.
        """
        super().__init__(**kwargs)
        self.my_layout = QVBoxLayout(self)
        self.setAcceptDrops(True)
        self.setMinimumHeight(250)
        self.lst_cols = lst_cols
        for col in self.lst_cols:
            new_widget = DraggableColumn(col)
            self.my_layout.addWidget(new_widget)

    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        e.accept()

    def dropEvent(self, e):
        """
        An event where something is dropped onto the library. 

        Args:
            e (_type_): _description_
        """
        pos = e.pos()
        widget = e.source()
        from_parent = widget.parentWidget()
        to_parent = self
        if isinstance(from_parent , ColumnsSubmodule) and isinstance(to_parent , ColumnsSubmodule):
            e.accept()
        elif isinstance(from_parent , ColumnsSection) and (isinstance(to_parent , PipelineSubmodule) or isinstance(to_parent , ColumnsSubmodule)):
            e.accept()
            from_parent.layout().removeWidget(widget)
            widget.deleteLater()
            
        dnd.end_drag_and_drop_event(to_parent , from_parent)

class PipelineSubmodule(QtW.QGroupBox):
    
    def __init__(self , sublibary , render_type = "", hex_value = "",  **kwargs):
        super().__init__(**kwargs)
        self.my_layout = QVBoxLayout(self)
        self.setAcceptDrops(True)
        self.sublibary = sublibary
        self.setTitle(self.sublibary.library_name)
        if len(self.sublibary.function_calls) == 0:
            self.deleteLater()
        for sklearn in self.sublibary.function_calls:
            self.my_layout.addWidget(Draggable(
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
        print("From" , from_parent , " TO: " , to_parent)
        if isinstance(from_parent , PipelineSubmodule) and isinstance(to_parent , PipelineSubmodule):
            e.accept()
        elif isinstance(from_parent , PipelineSection) and (isinstance(to_parent , PipelineSubmodule) or isinstance(to_parent , ColumnsSubmodule)):
            e.accept()
            from_parent.layout().removeWidget(widget)
            widget.deleteLater()
        dnd.end_drag_and_drop_event(to_parent , from_parent)



