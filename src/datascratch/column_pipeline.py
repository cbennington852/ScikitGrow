from .draggable import DraggableColumn
from PyQt5.QtWidgets import QVBoxLayout
import PyQt5.QtWidgets as QtW
from PyQt5.QtGui import QColor , QPolygon, QPainter , QResizeEvent
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt
from .colors_and_appearance import AppAppearance
from . import drag_and_drop_utility as dnd


class ColumnsSection(QtW.QGroupBox):
    def __init__(self , title, my_parent , max_num_cols = 100, **kwargs):
        """
        A droppable holder for the ColumnsMDI subwindow. 

        Args:
            title (str): The name of the holder.
            my_parent (pointer): pointer to the parent of this.
            max_num_cols (int, optional): Defaults to 100.
        """
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
        """
        Drag enter event, this checks to see if the object being dragged is a column
        """
        pos = e.pos()
        widget = e.source()
        if isinstance(widget , DraggableColumn):
            e.accept()
            self.hovering=True        
            self.repaint()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        """
        The item is leaving the object, this is part of the hover mechanic,
        """
        self.hovering = False
        self.repaint()
        e.accept() 
    
    def get_num_cols(self) -> int:
        """
        Returns:
            int: returns the number of columns.
        """
        return len(self.get_cols())
    
    def set_cols_as_string_list(self , str_lst : list[str]):
        """
        Changes this columns section to be a specified string list. Part of loading 
        from a file. 

        Args:
            str_lst (list[str]): list of strings
        """
        # Remove all prior draggable (If applicable). 
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , DraggableColumn):
                child.deleteLater()
        # now generate an add the new widgets. 
        for curr in str_lst:
            new_drag = DraggableColumn(curr)
            self.my_layout.addWidget(new_drag)
        
    
    def get_cols_as_string_list(self) -> list[str]:
        """Returns a list of strings representing the columns picked. 

        Returns:
            list[str]: _description_
        """
        return [drag_col.name for drag_col in self.get_cols()]
    

    
    def get_cols(self) -> list[DraggableColumn]:
        """
        Returns:
            list[DraggableColumn]: list of draggable columns for this area.
        """
        res_cols = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , DraggableColumn):
                res_cols.append(child)
        return res_cols
    
    # The 
    bevel_left_start = DraggableColumn.bevel_width + DraggableColumn.bevel_slant_width*2 + DraggableColumn.left_of_bevel_width
    bottom_right_of_top_bevel_x = bevel_left_start + DraggableColumn.bevel_slant_width + DraggableColumn.bevel_width
    width_from_start_mouth_to_left_side = 10
    height_between_top_mouth_and_top_bar = 30
    
    def paintEvent(self, event):
        """
        Paints the section to cover and fill the column descriptions.

        Args:
            event (_type_): _description_
        """
        painter = QPainter(self)
        
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
        """"
            Conducts a drop event.
        """
        pos = e.pos()
        widget = e.source()
        from_parent = widget.parentWidget()
        to_parent = self
        num_cols = self.get_num_cols()
        def check_is_correct_type():
            if not isinstance(widget , DraggableColumn):
                e.ignore()
                return
            
        def resize_self():
            base_addition = 100
            if self.max_num_cols == 1: # Y cols
                self.setFixedHeight(DraggableColumn.BASE_HEIGHT + base_addition)
            else: # X cols
                self.setFixedHeight(num_cols * DraggableColumn.BASE_HEIGHT + base_addition)
        
        def if_limit_remove_all_other_widgets():
            if (num_cols == self.max_num_cols):
                # Remove one the children from this
                for child in self.findChildren(QtW.QWidget):
                    if isinstance(child , DraggableColumn) and child != widget:
                        child.deleteLater()
            else:
                e.accept()
            
        check_is_correct_type()
        if_limit_remove_all_other_widgets()
        resize_self()
        # Handle replacement with parent module. If applicable
        if isinstance(from_parent , ColumnsSection) and isinstance(from_parent , ColumnsSection):
            self.my_layout.addWidget(widget)
        else:
            self.my_layout.addWidget(widget.copy_self())
        e.accept()
            
        self.hovering=False        
        dnd.end_drag_and_drop_event(to_parent , from_parent)