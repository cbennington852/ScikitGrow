from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag , QPixmap
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



# these are the draggable buttons
class Draggable(QPushButton):
    def __init__(self , name, sklearn_function , **kwargs):
        super().__init__(**kwargs) 
        self.kwargs = kwargs
        self.name = name
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
        print(self.parameters)
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
        print(self.my_parent.parameters)
        self.accept()