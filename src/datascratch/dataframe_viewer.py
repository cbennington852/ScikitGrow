from PyQt5.QtWidgets import QTableView, QApplication
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
import sys
import pandas as pd
import PyQt5.QtWidgets as QtW


class DataframeViewer(QtW.QTableView):
    """
    Small data frame class to view a dataframe.
    """
    def __init__(self, df, **kwargs):
        super().__init__(**kwargs)
        self.resize(800, 500)
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectRows)
        model = PandasModel(df)
        self.setModel(model)
        self.show()



class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe.columns)
        return 0
    
    def setData(self, index, value, role):
        """This allows us to edit the pandas dataframe

        Return true, to say is was edited.
        """
        try:
            if role == Qt.EditRole:
                new_type = self._dataframe.iloc[index.row(),index.column()].dtype
                print("New type" , new_type)
                new_value = new_type.type(value)
                self._dataframe.iloc[index.row(),index.column()] = new_value
                return True
        except Exception as e:
            print(str(e))
            return False
        
        
    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._dataframe.columns[section])

            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])

        return None