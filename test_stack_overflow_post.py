# -- Source - https://stackoverflow.com/a
# -- Posted by ekhumoro, modified by community. See post 'Timeline' for change history
# -- Retrieved 2026-01-03, License - CC BY-SA 3.0
from PyQt5 import QtWidgets, QtCore

class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        layout = QtWidgets.QHBoxLayout(self)
        
        # Initialize the ToolButton
        self.button = QtWidgets.QToolButton(self)
        self.button.setText("Options")
        self.button.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        
        # Create the menu and the custom widget action
        self.button.setMenu(QtWidgets.QMenu(self.button))
        self.textBox = QtWidgets.QTextBrowser(self)
        self.textBox.setPlaceholderText("Type here...")
        
        action = QtWidgets.QWidgetAction(self.button)
        action.setDefaultWidget(self.textBox)
        self.button.menu().addAction(action)
        
        layout.addWidget(self.button)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.resize(200, 100)
    window.show()
    sys.exit(app.exec_())