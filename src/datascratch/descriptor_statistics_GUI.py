from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag , QIcon
import traceback
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

        def handle_column(col ):
            try:
                # check to see if in converted cols.
                if self.engine_results.is_column_in_list_converted_columns(col):
                    new_col = ClassificationDescriptor(
                        dataframe=self.dataframe,
                        column_name=col,
                        engine_results=self.engine_results
                    )
                    self.cols.append(new_col)
                    self.main_lay.addWidget(new_col)
                else:
                    new_col = ContinuousDescriptor(
                        column_name=col , 
                        dataframe=self.dataframe,
                        )
                    self.cols.append(new_col)
                    self.main_lay.addWidget(new_col)
            except Exception as e:
                print("==============ERROR===============")
                print(f"Column : {col} on descriptor")
                traceback.print_exception(e)
                print(str(e))


        for col in engine_results.x_cols:
            handle_column(col)
        handle_column(self.engine_results.y_col[0])

        self.setWidget(self.main)


class GeneralDescriptor(QtW.QGroupBox):
    digit_rounding = 5

    def __init__(self , dataframe : pd.DataFrame , column_name : str, **kwargs):
        """
        An abstract subclass which renders each individual column data information, this gives general stats,
        as well as a bar chart to show data skew.s

        Two sections L | R
            L ... shows Statistics
                - min
                - max
            R ... shows bar graph

        """
        super().__init__(**kwargs)
        self.dataframe = dataframe
        self.setTitle(column_name)
        self.column_name = column_name
        self.main_layout = QtW.QHBoxLayout()
        self.setLayout(self.main_layout)
        self.render_left()
        self.render_right()
    def plot_chart(self, fig):
        self.chart = FigureCanvasQTAgg(fig)
        height = 0
        if hasattr(self , 'left'):
            height = self.left.height()
        else:
            height = 500
        self.chart.setMaximumHeight(height)
        self.main_layout.addWidget(self.chart)
    def render_left(self):
        return QtW.QWidget()
    def render_right(self):
        return QtW.QWidget()
        


class ClassificationDescriptor(GeneralDescriptor):
    def __init__(self, dataframe, column_name, engine_results : EngineResults, **kwargs):
        self.engine_results = engine_results
        # Find the column converter
        self.col_conv = engine_results.get_converted_column(column_name)
        # Counting occurrence of each class.
        self.sizes_occurrence = []
        value_counts = dataframe[column_name].value_counts()
        for class_encoded in range(0 , len(self.col_conv.code_map)):
            # get occurrence.
            curr_count = value_counts[class_encoded]
            self.sizes_occurrence.append(curr_count)
        super().__init__(dataframe, column_name, **kwargs)
        

    def render_left(self):
        """
        renders left side of the GUI components
        """
        self.left = QtW.QWidget()
        main_lay = QtW.QFormLayout()
        self.left.setLayout(main_lay)

        def render_function_result( name , value):
            new_label = QtW.QLabel(str(name))
            new_value = QtW.QLabel(str(value))
            main_lay.addRow(new_label , new_value)

        def add_space():
            main_lay.addRow(QtW.QLabel("") , QtW.QLabel(""))

        col = self.dataframe[self.column_name]

        render_function_result("Count of all columns" , col.count())
        render_function_result("Num of Unique" , len(col.unique()))
        add_space()
        # maybe a scrollable window with all of the counts?
        list_values = []
        for x in range(0 , len(self.col_conv.code_map)):
            name = self.col_conv.code_map[x]
            count = self.sizes_occurrence[x]
            list_values.append(f"{name} ... {count}")
        tiny_scroller = QtW.QScrollArea()
        tiny_scroll_win = QtW.QListView()
        tiny_scroll_win.setModel(QtCore.QStringListModel(list_values))
        tiny_scroller.setWidget(tiny_scroll_win)
        tiny_scroller.setMaximumHeight(self.height())
        main_lay.addRow("Occurrence counts" , tiny_scroller)
        self.main_layout.addWidget(self.left)

    def render_right(self):
        fig, axs = plt.subplots(figsize=(4 ,4))
        axs.pie(self.sizes_occurrence, labels=self.col_conv.code_map, autopct='%1.1f%%', startangle=90) 
        self.plot_chart(fig)


class ContinuousDescriptor(GeneralDescriptor):

    def render_left(self):
        """
        renders left side of the GUI components
        """
        self.left = QtW.QWidget()
        main_lay = QtW.QFormLayout()
        self.left.setLayout(main_lay)

        def render_function_result( name , value):
            new_label = QtW.QLabel(str(name))
            new_value = QtW.QLabel(str(round(value , GeneralDescriptor.digit_rounding)))
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
        self.plot_chart(fig)
        
        
