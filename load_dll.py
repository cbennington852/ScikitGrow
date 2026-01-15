print("Loading DLL, this might take a moment. This step is not required, the GUI will do this automatically. ")
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5 import QtCore, QtWidgets

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setGeometry(100, 100, 300, 200) # x, y, width, height
    window.setWindowTitle('PyQt5 Example GUI')
    QtCore.QTimer.singleShot(50, lambda x : sys.exit(0) )
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()