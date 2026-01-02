from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
import PyQt5.QtGui as PGui
from PyQt5.QtGui import QDrag , QPixmap , QPainter , QPalette , QImage , QColor , QPolygon, QPen, QBrush, QIcon
import PyQt5.QtCore as QCore 
from colors_and_appearance import AppAppearance
from draggable_parameter import parameter_filter , BANNED_PARAMETERS
import ast
import time

class DraggableColumn(QPushButton):
    BASE_HEIGHT = 50

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs) 
        self.kwargs = kwargs
        self.name = name
        self.setFlat(True)
        self.setStyleSheet("""  
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
            }
            QPushButton:hover {
               background-color: none; border-style: none; 
            }
            QPushButton:pressed {
                background-color: none;      /* Optional: style for when clicked */
            }
        """)    
        # calculate the minmum width from the text and then set it? 
        temp_label = QtW.QLabel(name)
        temp_label.adjustSize()
        required_text_width = temp_label.width()
        print(temp_label.width())
        self.label_inferred_width = temp_label.width()
        self.setMaximumWidth(required_text_width + 60)
        self.setFixedHeight(DraggableColumn.BASE_HEIGHT)

    def copy_self(self):
        return DraggableColumn(
            name=self.name,
            **self.kwargs
        )

    #
    # Below just makes it draggable, and renders whatever this looks like
    #
    def mouseMoveEvent(self, e):
        # Makes it draggable
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            # Render this while dragging
            pixmap = QPixmap(self.size())
            # Tell the button to drag in the center.
            drag.setHotSpot(self.drag_start_position) 
            #drag.setHotSpot(center)
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
        super(DraggableColumn, self).mousePressEvent(event)

    # Paint event options.
    left_of_bevel_width = 20
    bevel_depth = 10
    bevel_width = 20
    bevel_slant_width = 10
    block_height = 40
    starting_x = 0
    starting_y = 0


    def paintEvent(self, event):
        opt = QtW.QStyleOptionButton()
        self.initStyleOption(opt)

        rect = self.rect()

        painter = QPainter(self)

        self.style().drawControl(QtW.QStyle.CE_PushButtonBevel, opt, painter, self)

        if opt.state & QtW.QStyle.State_Sunken:
            rect.adjust(2,2,2,2)
        

        painter.setPen(QColor(AppAppearance.DRAGGABLE_COLOMN_BORDER_COLOR))
        painter.setBrush(QColor(AppAppearance.DRAGGABLE_COLUMN_COLOR))

        # Top level input Calculations
        right_of_bevel_width  = self.label_inferred_width - DraggableColumn.left_of_bevel_width + 10

        top_of_left_bevel_x = DraggableColumn.starting_x + DraggableColumn.left_of_bevel_width 
        bottom_right_of_top_bevel_x = top_of_left_bevel_x + DraggableColumn.bevel_slant_width + DraggableColumn.bevel_width
        far_right_corner_x = bottom_right_of_top_bevel_x + DraggableColumn.bevel_slant_width + right_of_bevel_width

        block_with_bevel = QPolygon([
            QPoint(DraggableColumn.starting_x , DraggableColumn.starting_y), # Top Right point.

            # Top Bevel
            QPoint(top_of_left_bevel_x, DraggableColumn.starting_y), # top of top left bevel point.
            QPoint(top_of_left_bevel_x + DraggableColumn.bevel_slant_width , DraggableColumn.starting_y + DraggableColumn.bevel_depth), # bottom left of top bevel point
            QPoint(bottom_right_of_top_bevel_x , DraggableColumn.starting_y + DraggableColumn.bevel_depth), # bottom right of top bevel point
            QPoint(bottom_right_of_top_bevel_x + DraggableColumn.bevel_slant_width  , DraggableColumn.starting_y), # top right of top bevel point.

            
            QPoint(far_right_corner_x  , DraggableColumn.starting_y), # top right corner.
            QPoint(far_right_corner_x , DraggableColumn.block_height) , # bottom right corner
            
            # Bottom Bevel
            QPoint(bottom_right_of_top_bevel_x + DraggableColumn.bevel_slant_width  , DraggableColumn.starting_y + DraggableColumn.block_height), # top right of top bevel point.
            QPoint(bottom_right_of_top_bevel_x , DraggableColumn.starting_y + DraggableColumn.bevel_depth + DraggableColumn.block_height), # bottom right of top bevel point
            QPoint(top_of_left_bevel_x + DraggableColumn.bevel_slant_width , DraggableColumn.starting_y + DraggableColumn.bevel_depth + DraggableColumn.block_height), # bottom left of top bevel point
            QPoint(top_of_left_bevel_x, DraggableColumn.starting_y + DraggableColumn.block_height), # top of top left bevel point.

            QPoint(DraggableColumn.starting_x , DraggableColumn.block_height) # bottom left corner
        ])

        painter.drawPolygon(block_with_bevel)
        painter.setPen(QColor(Qt.white))
        start_y_for_text = int(self.size().height() / 2) + 5
        painter.drawText(15 , start_y_for_text, f"{self.name}")
     


class DraggableData():
        def __init__(self , sklearn_function , parameters , render_type, hex_color , name):
            self.sklearn_function = sklearn_function
            self.parameters = parameters
            self.render_type = render_type
            self.hex_color = hex_color
            self.name = name
# these are the draggable buttons
class Draggable(QPushButton):

    INTERLOCK_RIGHT = "interlock_right"
    POINTY = "pointy"
    BUBBLE = "bubble"
    BASE_HEIGHT = 50
    
    def __init__(self , name, sklearn_function , render_type, hex_color,   **kwargs):
        super().__init__(**kwargs) 
        self.kwargs = kwargs
        self.name = name
        self.render_type = render_type
        self.hex_color = hex_color
        self.setFlat(True) 
        # calculate the minmum width from the text and then set it? 
        temp_label = QtW.QLabel(name)
        temp_label.adjustSize()
        required_text_width = temp_label.width()
        print(temp_label.width())
        self.label_inferred_width = temp_label.width()
        self.setMaximumWidth(required_text_width + 60)
        self.setFixedHeight(Draggable.BASE_HEIGHT)
        self.data = DraggableData(
            sklearn_function=sklearn_function,
            parameters=SubLibary.get_sklearn_parameters(sklearn_function),
            render_type=render_type,
            hex_color=hex_color,
            name=name
        )
        self.setText(name)
        self.clicked.connect(self.on_button_clicked)

        # rendering the actual thing
        if render_type == Draggable.POINTY:
            self.arrow_icon = QIcon(":/images/dropdown_arrow.png")
        

    def get_data(self) -> DraggableData:
        return self.data
        
    POINTY_TRIANGLE_WIDTH = 20

    # Double Interlock specifications...
    space_in_between_two_bevels = 10
    second_bevel_width = 30
    block_height = 40
    bevel_depth = 10
    bevel_width = 20
    bevel_slant_width = 10
    left_of_bevel_width  = 20


    def paintEvent(self, event):
        if self.render_type == Draggable.POINTY:
            painter = QPainter(self)
            painter.setPen(QColor(self.hex_color))
            painter.setBrush(QColor(self.hex_color))

            # tunable parameters
            height_block = 40
            width_center_block = self.label_inferred_width + 10
            width_triangle = Draggable.POINTY_TRIANGLE_WIDTH
            triangle_mid_y_axis = int(height_block / 2)
            
            pointy_block = QPolygon([
                QPoint(0 , triangle_mid_y_axis), # end of left point.
                QPoint(width_triangle , 0), # Top Left corner of triangle / box
                QPoint(width_center_block + width_triangle , 0), # Top Right corner of triangle / box
                QPoint(width_center_block + 2*width_triangle , triangle_mid_y_axis), # end of right point.
                QPoint(width_center_block + width_triangle , height_block),
                QPoint(width_triangle , height_block),
            ])

            painter.drawPolygon(pointy_block)
            painter.setPen(QColor(Qt.white))
            start_y_for_text = int(self.size().height() / 2) + 5
            painter.drawText(width_triangle + 5 , start_y_for_text, f"{self.name}")

        elif self.render_type == Draggable.BUBBLE:
            painter = QPainter(self)
            painter.setPen(QColor(self.hex_color))
            painter.setBrush(QColor(self.hex_color))

            # tunable parameters
            height_block = 40
            width_center_block = self.label_inferred_width + 10
            width_triangle = Draggable.POINTY_TRIANGLE_WIDTH
            triangle_mid_y_axis = int(height_block / 2)

            painter.drawRoundedRect(
                0 , # x
                0 , # y
                self.width()-10, # w
                self.height()-10, # h
                10, # x radius
                10 # y radius

            )

            painter.setPen(QColor(Qt.white))
            start_y_for_text = int(self.size().height() / 2) + 5
            painter.drawText(width_triangle + 5 , start_y_for_text, f"{self.name}")

        elif self.render_type == Draggable.INTERLOCK_RIGHT:

            opt = QtW.QStyleOptionButton()
            self.initStyleOption(opt)
            rect = self.rect()
            painter = QPainter(self)
            self.style().drawControl(QtW.QStyle.CE_PushButtonBevel, opt, painter, self)
            if opt.state & QtW.QStyle.State_Sunken:
                rect.adjust(2,2,2,2)
            
            painter.setPen(QColor(AppAppearance.PREPROCESSOR_BORDER_COLOR))
            painter.setBrush(QColor(self.hex_color))

            # Top level input Calculations
            starting_x = 0
            starting_y = 0
            right_of_bevel_width = max(self.label_inferred_width - Draggable.left_of_bevel_width + 5,120)
            
            top_of_left_bevel_x = starting_x + Draggable.left_of_bevel_width 
            bottom_right_of_top_bevel_x = top_of_left_bevel_x + Draggable.bevel_slant_width + Draggable.bevel_width
            far_right_corner_x = bottom_right_of_top_bevel_x + Draggable.bevel_slant_width + right_of_bevel_width
            start_second_bevel = bottom_right_of_top_bevel_x + Draggable.bevel_slant_width + Draggable.space_in_between_two_bevels

            block_with_bevel = QPolygon([
                QPoint(starting_x , starting_y), # Top Right point.

                # Top Bevel
                QPoint(top_of_left_bevel_x, starting_y), # top of top left bevel point.
                QPoint(top_of_left_bevel_x + Draggable.bevel_slant_width , starting_y + Draggable.bevel_depth), # bottom left of top bevel point
                QPoint(bottom_right_of_top_bevel_x , starting_y + Draggable.bevel_depth), # bottom right of top bevel point
                QPoint(bottom_right_of_top_bevel_x + Draggable.bevel_slant_width  , starting_y), # top right of top bevel point.

                # second top bevel
                QPoint(start_second_bevel, starting_y), # top of top left bevel point.
                QPoint(start_second_bevel + Draggable.bevel_slant_width , starting_y + Draggable.bevel_depth), # bottom left of top bevel point
                QPoint(Draggable.second_bevel_width + start_second_bevel , starting_y + Draggable.bevel_depth), # bottom right of top bevel point
                QPoint(Draggable.second_bevel_width + Draggable.bevel_slant_width + start_second_bevel , starting_y), # top right of top bevel point.

                
                QPoint(far_right_corner_x  , starting_y), # top right corner.
                QPoint(far_right_corner_x , Draggable.block_height) , # bottom right corner
                
                # second bottom bevel
                QPoint(Draggable.second_bevel_width + Draggable.bevel_slant_width + start_second_bevel , starting_y + Draggable.block_height), # top right of top bevel point.E
                QPoint(Draggable.second_bevel_width + start_second_bevel , starting_y + Draggable.bevel_depth + Draggable.block_height), # bottom right of top bevel point
                QPoint(start_second_bevel + Draggable.bevel_slant_width , starting_y + Draggable.bevel_depth + Draggable.block_height), # bottom left of top bevel point
                QPoint(start_second_bevel, starting_y + Draggable.block_height), # top of top left bevel point.


                # Bottom Bevel
                QPoint(bottom_right_of_top_bevel_x + Draggable.bevel_slant_width  , starting_y + Draggable.block_height), # top right of top bevel point.
                QPoint(bottom_right_of_top_bevel_x , starting_y + Draggable.bevel_depth + Draggable.block_height), # bottom right of top bevel point
                QPoint(top_of_left_bevel_x + Draggable.bevel_slant_width , starting_y + Draggable.bevel_depth + Draggable.block_height), # bottom left of top bevel point
                QPoint(top_of_left_bevel_x, starting_y + Draggable.block_height), # top of top left bevel point.

                QPoint(starting_x , Draggable.block_height) # bottom left corner
            ])

            painter.drawPolygon(block_with_bevel)
            painter.setPen(QColor(Qt.white))
            start_y_for_text = int(self.size().height() / 2) + 5
            painter.drawText(15 , start_y_for_text, f"{self.name}")
        else:
            return super().paintEvent(event)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
        super(Draggable, self).mousePressEvent(event)

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            # Render this while dragging
            pixmap = QPixmap(self.size())
            # Tell the button to drag in the center.
            drag.setHotSpot(self.drag_start_position) 
            #drag.setHotSpot(center)
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)

    def copy_self(self):
        return Draggable(
            name=self.name,
            sklearn_function=self.data.sklearn_function,
            render_type=self.render_type,
            hex_color=self.hex_color,
            **self.kwargs
        )
    
    def new_draggable_from_data(data  : DraggableData):
        """Returns a new draggable from a data parsel.

        Args:
            data (DraggableData): _description_

        Returns:
            _type_: _description_
        """
        new_drag = Draggable(
            data.name,
            data.sklearn_function,
            data.render_type,
            data.hex_color,
        )
        new_drag.data.parameters = data.parameters
        return new_drag
    
    def on_button_clicked(self):
        popover = ParameterPopup(
            draggable_data=self.data,
            parent=self
        )
        popover.exec()

    def reset_parameters(self):
        self.data.parameters = SubLibary.get_sklearn_parameters(self.data.sklearn_function)



class ParameterPopup(QtW.QDialog):
    def __init__(self , draggable_data  : DraggableData , parent : Draggable,  **kwargs):
        super().__init__(**kwargs) 
        self.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))
        self.my_parent = parent
        self.draggable_data = draggable_data
        
        self.setWindowTitle(f"{parent.name} hyper parameters")
        self.setGeometry(100, 100, 200, 100)  # x, y, width, height


        self.my_layout = QtW.QFormLayout()
        self.render_layout()
        self.my_layout.addWidget(self.reset_button)
        self.setLayout(self.my_layout)

    def render_layout(self):
        self.all_widgets = []
        for parameter_name , default_value in self.draggable_data.parameters:
            curr = parameter_filter(parameter_name , default_value)
            self.my_layout.addRow(
                parameter_name,
                curr
            )
            self.all_widgets.append((parameter_name , curr))
        self.reset_button = QtW.QPushButton("Reset Parameters")
        self.reset_button.clicked.connect(self.reset_parameters)
        self.my_layout.addWidget(self.reset_button)
        
        
    def closeEvent(self, a0):
        self.save_parameters()
        return super().closeEvent(a0)
    
    def reset_parameters(self):
        self.my_parent.reset_parameters()
        # Remove all things in layout
        while self.my_layout.rowCount() > 0:
            self.my_layout.removeRow(0)
        
        time.sleep(0.05)
        self.render_layout()
    
    def save_parameters(self):
        new_parameters = []
        for parameter_name , q_line_edit in self.all_widgets:
            curr = None
            try:
                curr = (parameter_name , ast.literal_eval(q_line_edit.text()))
            except:
                curr = (parameter_name , ast.literal_eval(f'\'{q_line_edit.text()}\''))
            new_parameters.append(curr)
        self.my_parent.data.parameters = new_parameters
        self.accept()





