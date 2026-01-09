from draggable import DraggableColumn
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtGui import QDrag , QIcon , QPixmap , QCursor , QColor , QPolygon, QPen, QBrush, QIcon, QPainter
from PyQt5.QtCore import  QPoint , QRect
from PyQt5.QtCore import Qt, QMimeData
from colors_and_appearance import AppAppearance
import drag_and_drop_utility as dnd


class ColumnsSubmodule(QtW.QWidget):
    def __init__(self , lst_cols , **kwargs):
        super().__init__(**kwargs)
        self.layout = QVBoxLayout(self)
        self.setAcceptDrops(True)
        self.setMinimumHeight(250)
        
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
            
        dnd.end_drag_and_drop_event(to_parent , from_parent)

class ColumnsSection(QtW.QGroupBox):
    def __init__(self , title, my_parent , max_num_cols = 100, **kwargs):
        super().__init__( **kwargs)
        self.my_title = title
        self.my_parent = my_parent
        self.max_num_cols = max_num_cols
        self.resize(200 , 90)
        self.hovering = False
        self.setAcceptDrops(True)
        self.setContentsMargins(
            10 , # left
            60, # top
            0, # right
            0, # bottom
        )
        self.my_layout = QVBoxLayout()
        self.setStyleSheet("")
        self.my_layout.setSpacing(0);  
        self.setLayout(self.my_layout)
        self.setTitle(self.my_title)
        self.my_layout.addStretch()


    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if isinstance(widget , DraggableColumn):
            e.accept()
            self.hovering=True        
            self.repaint()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        self.hovering = False
        self.repaint()
        e.accept() 
    
    def get_num_cols(self):
        return len(self.get_cols())
    
    def set_cols_as_string_list(self , str_lst : list[str]):
        # Remove all prior draggable (If applicable). 
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , DraggableColumn):
                child.deleteLater()
        # now generate an add the new widgets. 
        for curr in str_lst:
            new_drag = DraggableColumn(curr)
            self.my_layout.addWidget(new_drag)
        
    
    def get_cols_as_string_list(self) -> list[str]:
        return [drag_col.name for drag_col in self.get_cols()]
    
    # re-doing the layout events
    def resizeEvent(self, a0):
        return super().resizeEvent(a0)
    
    def get_cols(self) -> list[DraggableColumn]:
        res_cols = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , DraggableColumn):
                res_cols.append(child)
        return res_cols
    
    bevel_left_start = DraggableColumn.bevel_width + DraggableColumn.bevel_slant_width*2 + DraggableColumn.left_of_bevel_width
    bottom_right_of_top_bevel_x = bevel_left_start + DraggableColumn.bevel_slant_width + DraggableColumn.bevel_width
    width_from_start_mouth_to_left_side = 10
    height_between_top_mouth_and_top_bar = 30
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        print(f"Curr height {self.max_num_cols} ... {self.geometry()}")

        painter.setPen(QColor(AppAppearance.PIPELINE_HOLDER_BORDER_COLOR))
        painter.setBrush(QColor(AppAppearance.PIPELINE_BACKGROUND_COLOR))

        if self.hovering == True:
            painter.fillRect(self.rect(), QColor(AppAppearance.PIPELINE_HOVER_COLOR))
        else:
            painter.fillRect(self.rect(), QColor(AppAppearance.PIPELINE_NOT_HOVER_COLOR))

        # Top level calculations
        width = self.width()
        height = self.height()

        #space_needed_for_mouth = height - ColumnsSection.height_between_top_mouth_and_top_bar*2
        space_needed_for_mouth = 0
        num_cols = self.get_num_cols()
        if self.max_num_cols != 1:
            # add a background space as well
            painter.drawRect( 0 , 0 , width , num_cols * DraggableColumn.block_height )
            space_needed_for_mouth = max((num_cols + 1) * DraggableColumn.block_height, DraggableColumn.block_height )
        else:
            space_needed_for_mouth = max(num_cols * DraggableColumn.block_height, DraggableColumn.block_height )

        # add a space that is one draggable high

        # where to start the bevel from the left. 
        holder_block = QPolygon([
            QPoint( 0 , 0),             # Left Top corner
            QPoint(width , 0),          # Right Top corner

            # right top of mouth
            QPoint(width , ColumnsSection.height_between_top_mouth_and_top_bar),

            QPoint(ColumnsSection.bevel_left_start + ColumnsSection.width_from_start_mouth_to_left_side, ColumnsSection.height_between_top_mouth_and_top_bar), # right start bevel.
            # Bottom right of bevel
            QPoint(
                ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth
                ),
            # Bottom left of bevel
            QPoint(
                ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth
                ),
            QPoint(
                ColumnsSection.bevel_left_start - (DraggableColumn.bevel_slant_width*2) - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                ColumnsSection.height_between_top_mouth_and_top_bar 
                ),

            # left top of mouth
            QPoint(ColumnsSection.width_from_start_mouth_to_left_side , ColumnsSection.height_between_top_mouth_and_top_bar),
             # Bottom of the mouth
            QPoint(ColumnsSection.width_from_start_mouth_to_left_side , ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth),

            QPoint(
                ColumnsSection.bevel_left_start - (DraggableColumn.bevel_slant_width*2) - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth
                ),
            QPoint(
                ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth + space_needed_for_mouth
                ),
            QPoint(
                ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth + space_needed_for_mouth
                ),
            QPoint(
                ColumnsSection.bevel_left_start + ColumnsSection.width_from_start_mouth_to_left_side, 
                ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth
                ), # right start bevel.
            
           
            QPoint(width , ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth),

            QPoint(width , height),     # Right Bottom corner
            QPoint(0 , height)          # Left Bottom corner
        ])

        painter.drawPolygon(holder_block)
        painter.setPen(QColor(Qt.black))
        painter.drawText(15 , 20 ,f"{self.my_title}")

        # 5 putting all of the children inside of each other
        # 5.1 gather list of children
        lst_of_children = []
        for i in range(0 , self.my_layout.count()):
            if isinstance(self.my_layout.itemAt(i) , QtW.QWidgetItem):
                temp_widget = self.my_layout.itemAt(i).widget()
                lst_of_children.append(temp_widget)
        # 5.2 Position the first child correctly. 
        if len(lst_of_children) >= 1:

            first_child = lst_of_children[0]
            first_child.move(ColumnsSection.width_from_start_mouth_to_left_side , ColumnsSection.height_between_top_mouth_and_top_bar)

        # 5.3 If more than one, move the bottoms inside of the ones on top of it.
            for i in range(1 , len(lst_of_children)):
                tmp  = lst_of_children[i]
                new_x = first_child.geometry().topLeft().x()
                new_y = first_child.geometry().topLeft().y() + i*DraggableColumn.block_height
                tmp.move(new_x , new_y)
        

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        from_parent = widget.parentWidget()
        to_parent = self
        def check_is_correct_type():
            if not isinstance(widget , DraggableColumn):
                e.ignore()
                return
        # remove the spacer ,and readadd to bottom.
        def remove_all_spacers():
            for i in range(0 , self.my_layout.count()):
                if isinstance(self.my_layout.itemAt(i) , QtW.QSpacerItem): 
                    temp_widget = self.my_layout.itemAt(i)
                    self.my_layout.removeItem(temp_widget)
                    del temp_widget
        
        def if_limit_remove_all_other_widgets():
            if (self.get_num_cols() == self.max_num_cols):
                # Remove one the children from this
                for child in self.findChildren(QtW.QWidget):
                    if isinstance(child , DraggableColumn) and child != widget:
                        child.deleteLater()
            else:
                e.accept()
            
        check_is_correct_type()
        remove_all_spacers()
        if_limit_remove_all_other_widgets()
        # Handle replacement with parent module. If applicable
        if isinstance(from_parent , ColumnsSubmodule) and isinstance(to_parent , ColumnsSection):
            self.my_layout.addWidget(widget.copy_self())
            e.accept()
        else:
            # accept
            e.accept()
            # Add the dang widget
            self.my_layout.addWidget(widget)
            
        # Re-center the height
        # add space to end of the layout to make it all squished to top.
        if self.max_num_cols != 1:
            self.my_layout.addStretch()
        # Remove hovering attribute.
        self.hovering=False        
        dnd.end_drag_and_drop_event(to_parent , from_parent)