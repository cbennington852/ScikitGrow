import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint

class DraggableWidget(QLabel):
    """A custom QLabel that can be dragged within its parent."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        # Set window flags to FramelessWindowHint if it were a top-level window, 
        # but as a child widget, we just need to set its style.
        self.setStyleSheet("background-color: lightblue; border: 1px solid black;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resize(100, 50)
        self.offset = QPoint()

    def mousePressEvent(self, event):
        """Record the initial mouse position relative to the widget's top-left corner."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.pos()
            # Bring the dragged widget to the front of its siblings
            self.raise_() 

    def mouseMoveEvent(self, event):
        """Move the widget based on the mouse movement delta."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            # Calculate the new position relative to the parent widget
            # global position of mouse - global position of parent + the offset recorded in mousePressEvent
            # OR simpler: use mapToParent() with the current event position and subtract the initial offset
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        """Reset the offset when the mouse button is released."""
        self.offset = QPoint()

class ContainerWidget(QWidget):
    """A main widget that acts as a container for draggable widgets."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Draggable Widget Container")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: lightgray;")
        
        # Use a layout initially, but we will place children with absolute positioning
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Add draggable widgets (they ignore the layout because they call move())
        d_widget1 = DraggableWidget("Drag me 1", self)
        d_widget1.move(50, 50)
        
        d_widget2 = DraggableWidget("Drag me 2", self)
        d_widget2.move(200, 150)
        
        d_widget3 = DraggableWidget("Drag me 3", self)
        d_widget3.move(100, 300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContainerWidget()
    window.show()
    sys.exit(app.exec())
