from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
import PyQt5.QtGui as PGui
from PyQt5.QtGui import QDrag , QPixmap , QPainter , QPalette , QImage , QColor , QPolygon, QPen, QBrush
import PyQt5.QtCore as QCore 



class DraggableColumn(QPushButton):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs) 
        self.kwargs = kwargs
        self.name = name
        self.setText(self.name)

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

     def paintEvent(self, event):
        
        opt = QtW.QStyleOptionButton()
        self.initStyleOption(opt)

        rect = self.rect()

        painter = QPainter(self)

        self.style().drawControl(QtW.QStyle.CE_PushButtonBevel, opt, painter, self)

        if opt.state & QtW.QStyle.State_Sunken:
            rect.adjust(2,2,2,2)
        

        painter.setPen(QColor('#005489'))
        painter.setBrush(QColor('#005461'))

        # Top level input Calculations
        starting_x = 0
        starting_y = 0
        left_of_bevel_width = 20
        bevel_depth = 10
        bevel_width = 20
        bevel_slant_width = 10
        right_of_bevel_width  = self.label_inferred_width - left_of_bevel_width + 10
        block_height = 40

        top_of_left_bevel_x = starting_x + left_of_bevel_width 
        bottom_right_of_top_bevel_x = top_of_left_bevel_x + bevel_slant_width + bevel_width
        far_right_corner_x = bottom_right_of_top_bevel_x + bevel_slant_width + right_of_bevel_width

        block_with_bevel = QPolygon([
            QPoint(starting_x , starting_y), # Top Right point.

            # Top Bevel
            QPoint(top_of_left_bevel_x, starting_y), # top of top left bevel point.
            QPoint(top_of_left_bevel_x + bevel_slant_width , starting_y + bevel_depth), # bottom left of top bevel point
            QPoint(bottom_right_of_top_bevel_x , starting_y + bevel_depth), # bottom right of top bevel point
            QPoint(bottom_right_of_top_bevel_x + bevel_slant_width  , starting_y), # top right of top bevel point.

            
            QPoint(far_right_corner_x  , starting_y), # top right corner.
            QPoint(far_right_corner_x , block_height) , # bottom right corner
            
            # Bottom Bevel
            QPoint(bottom_right_of_top_bevel_x + bevel_slant_width  , starting_y + block_height), # top right of top bevel point.
            QPoint(bottom_right_of_top_bevel_x , starting_y + bevel_depth + block_height), # bottom right of top bevel point
            QPoint(top_of_left_bevel_x + bevel_slant_width , starting_y + bevel_depth + block_height), # bottom left of top bevel point
            QPoint(top_of_left_bevel_x, starting_y + block_height), # top of top left bevel point.

            QPoint(starting_x , block_height) # bottom left corner
        ])

        painter.drawPolygon(block_with_bevel)
        painter.setPen(QColor(Qt.white))
        start_y_for_text = int(self.size().height() / 2) + 5
        painter.drawText(15 , start_y_for_text, f"{self.name}")
     



# these are the draggable buttons
class Draggable(QPushButton):
    def __init__(self , name, sklearn_function ,  **kwargs):
        super().__init__(**kwargs) 
        self.kwargs = kwargs
        self.name = name
        #self._image = QImage(":/images/base_scratch_block_pink.svg")
        #self._image.height = 60
        #self._image.width = 60
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
        self.setFixedHeight(50)
        self.sklearn_function = sklearn_function
        self.parameters = SubLibary.get_sklearn_parameters(sklearn_function)
        self.setText(name)
        self.clicked.connect(self.on_button_clicked)


   
  
        


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
            sklearn_function=self.sklearn_function,
            **self.kwargs
        )
    
    def on_button_clicked(self):
        popover = ParameterPopup(
            sklearn_function=self.sklearn_function,
            parameters=self.parameters,
            parent=self
        )
        popover.exec()



class ParameterPopup(QtW.QDialog):
    def __init__(self , sklearn_function , parameters, parent : Draggable,  **kwargs):
        super().__init__(**kwargs) 
        self.my_parent = parent
        self.setWindowTitle("Small Dialog")
        self.setGeometry(100, 100, 200, 100)  # x, y, width, height
        self.all_widgets = []

        layout = QtW.QFormLayout()
        label = QLabel("This is a small dialog window.")
        layout.addWidget(label)

        for parameter_name , default_value in parameters:
            curr = QtW.QLineEdit()
            curr.setText(str(default_value))
            layout.addRow(
                parameter_name,
                curr
            )
            self.all_widgets.append((parameter_name , curr))

        close_button = QPushButton("Save")
        close_button.clicked.connect(self.save_parameters)  # Connect to accept() to close the dialog
        layout.addWidget(close_button)

        self.setLayout(layout)
    
    def save_parameters(self):
        new_parameters = []
        for parameter_name , q_line_edit in self.all_widgets:
            curr = None
            try:
                curr = (parameter_name , eval(q_line_edit.text()))
            except:
                curr = (parameter_name , eval(f'\'{q_line_edit.text()}\''))
            new_parameters.append(curr)
        self.my_parent.parameters = new_parameters
        self.accept()