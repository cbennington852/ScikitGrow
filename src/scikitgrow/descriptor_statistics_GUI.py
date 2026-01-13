from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag , QIcon
import PyQt5.QtCore as QtCore 
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from .sklearn_engine import EngineResults , Pipeline

class DescriptorStatisticsGUI(QtW.QScrollArea):

    def __init__(self, engine_results : EngineResults, dataframe : pd.DataFrame, **kwargs):
        """
        A GUI class to show general statistics about the data, and plot those statistics, 
        this is to help with the general data visualization goal.

        Args:
            engine_results (EngineResults):
            dataframe (pd.DataFrame): 
        """
        super().__init__(**kwargs)
        self.engine_results = engine_results
        self.dataframe = dataframe

        self.main = QtW.QWidget()
        self.cols = []
        self.main_lay = QtW.QVBoxLayout()
        self.main.setLayout(self.main_lay)


        for col in engine_results.x_cols:
            print("x_col"  , col)
            try:
                new_col = ColumnDescriptor(
                    column_name=col , 
                    dataframe=self.dataframe
                    )
                self.cols.append(new_col)
                self.main_lay.addWidget(new_col)
            except Exception as e:
                print(str(e))
        print("y_col" , self.engine_results.y_col)
        try:
            new_col = ColumnDescriptor(
                column_name=self.engine_results.y_col[0] ,
                dataframe=self.dataframe
                )
            self.cols.append(new_col)
            self.main_lay.addWidget(new_col)
        except Exception as e:
            print(str(e))

        self.setWidget(self.main)




class ColumnDescriptor(QtW.QGroupBox):
    digit_rounding = 5

    def __init__(self , dataframe : pd.DataFrame , column_name : str, **kwargs):
        """
        A subclass which renders each individual column data information, this gives general stats,
        as well as a bar chart to show data skew.s

        Two sections L | R
            L ... shows Statistics
                - min
                - max
            R ... shows bar graph

        """
        super().__init__(**kwargs)
        self.setTitle(column_name)
        self.dataframe = dataframe
        self.column_name = column_name
        self.main_layout = QtW.QHBoxLayout()
        self.setLayout(self.main_layout)
        
        self.render_left()
        self.render_right()


    def render_left(self):
        """
        renders left side of the GUI components
        """
        self.left = QtW.QWidget()
        main_lay = QtW.QFormLayout()
        self.left.setLayout(main_lay)

        def render_function_result( name , value):
            new_label = QtW.QLabel(str(name))
            new_value = QtW.QLabel(str(round(value , ColumnDescriptor.digit_rounding)))
            main_lay.addRow(new_label , new_value)

        def add_space():
            main_lay.addRow(QtW.QLabel("") , QtW.QLabel(""))

        col = self.dataframe[self.column_name]

        render_function_result("Average" , col.mean())
        render_function_result("Median" , col.median())
        render_function_result("Variance" , col.var())

        add_space()
        render_function_result("Max" , col.max())
        render_function_result("Min" , col.min())
        add_space()
        render_function_result("75th Quantile" , col.quantile(0.75))
        render_function_result("50th Quantile" , col.quantile(0.50))
        render_function_result("25th Quantile" , col.quantile(0.25))


        self.main_layout.addWidget(self.left)


    def render_right(self):
        """
        renders right side of the GUI components
        """
        col = self.dataframe[self.column_name]
        fig, axs = plt.subplots(figsize=(4 ,4))
        axs.hist(col)
        axs.set_ylabel("Frequency")
        axs.set_xlabel(f"{self.column_name} values")

        self.chart = FigureCanvasQTAgg(fig)
        # get length of other one
        height = self.left.height()
        self.chart.setMaximumHeight(height)
        self.main_layout.addWidget(self.chart)
        
