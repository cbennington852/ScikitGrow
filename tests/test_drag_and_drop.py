import src.datascratch.sklearn_engine
import pandas as pd
from src.datascratch.main import MainMenu , MainWindow , SaveFile , SaveFileException
import sklearn
import time
import pandas as pd
import sklearn
import seaborn as sns
from src.datascratch.sklearn_engine import Pipeline , EngineResults
from src.datascratch.draggable import Draggable
from PyQt5.QtGui import QDropEvent, QDrag
from PyQt5.QtCore import Qt, QMimeData, QEvent

import sklearn.model_selection as val
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtTest
import pytest

df = pd.read_csv("resources/random_data.csv")


def simulate_drag_and_drop(qtbot , source_widget , target_widget):
    # IMPORTANT : Testing drag and drop using qtbot is broken....
    # https://github.com/pytest-dev/pytest-qt/issues/260
    source_center = source_widget.rect().center()
    target_center = target_widget.rect().center()

    # Simulate mouse press on the source
    qtbot.mousePress(source_widget, QtCore.Qt.LeftButton, pos=source_center)

    # Simulate moving the mouse to the target
    # You might need to call processEvents() in between moves for complex apps
    qtbot.mouseMove(source_widget, pos=QtCore.QPoint(20, 20)) 
    # Move to the final target location
    qtbot.mouseMove(target_widget, pos=QtCore.QPoint(10, 10))


    # # Simulate mouse release to drop
    qtbot.mouseRelease(target_widget, QtCore.Qt.LeftButton, pos=target_center)


class FakeDropEvent():
    # Simulates a drop event, because the base infrastructure from PyQt is broken.
    # Source
        # https://github.com/pytest-dev/pytest-qt/issues/260
        # https://forum.qt.io/topic/135108/testing-drag-drop/5

    def __init__(self , source , pos):
        self._source = source
        self._pos = pos

    def source(self):
        return self._source
    
    def pos(self):
        return self._pos
    
    def accept(self):
        pass

    def ignore(self):
        pass

    def simulate_fake_drop(self , target_drop):
        # also draggable repaits
        self._source.paintEvent(self)
        # enter event
        target_drop.dragEnterEvent(self)
        # Called from drag enter
        target_drop.paintEvent(self)
        # Drag enter 
        target_drop.dropEvent(self)


def test_library_model_to_pipeline(qtbot):
    window = MainWindow(df)
    qtbot.addWidget(window)

    window.libary.setCurrentIndex(0)
    regressor_section = window.libary.lin_reg
    random_draggable = regressor_section.my_layout.itemAt(0).widget()

    # gather pipeline to drag to.
    pm = window.pipeline_mother
    curr_pipeline = pm.pipelines[0]
    curr_cols_sub = pm.columns_subwindow
    target_drop = curr_pipeline.model_pipe

    fake_drop = FakeDropEvent(
        random_draggable,
        QtCore.QPoint(0,0)
    )

    fake_drop.simulate_fake_drop(target_drop)
    
    assert len(target_drop.get_pipeline_objects()) != 0

def test_library_preprocessor_to_pipeline(qtbot):
    window = MainWindow(df)
    qtbot.addWidget(window)

    window.libary.setCurrentIndex(0)
    regressor_section = window.libary.pre_sub_module
    random_draggable = regressor_section.my_layout.itemAt(0).widget()

    # gather pipeline to drag to.
    pm = window.pipeline_mother
    curr_pipeline = pm.pipelines[0]
    curr_cols_sub = pm.columns_subwindow
    target_drop = curr_pipeline.preproccessor_pipe

    fake_drop = FakeDropEvent(
        random_draggable,
        QtCore.QPoint(0,0)
    )

    fake_drop.simulate_fake_drop(target_drop)
    
    assert len(target_drop.get_pipeline_objects()) != 0

def test_library_validator_to_pipeline(qtbot):
    window = MainWindow(df)
    qtbot.addWidget(window)

    window.libary.setCurrentIndex(0)
    regressor_section = window.libary.vali_submodule
    random_draggable = regressor_section.my_layout.itemAt(0).widget()

    # gather pipeline to drag to.
    pm = window.pipeline_mother
    curr_pipeline = pm.pipelines[0]
    curr_cols_sub = pm.columns_subwindow
    target_drop = curr_pipeline.validator

    fake_drop = FakeDropEvent(
        random_draggable,
        QtCore.QPoint(0,0)
    )

    fake_drop.simulate_fake_drop(target_drop)
    
    assert len(target_drop.get_pipeline_objects()) != 0

def test_library_to_columns_to_pipeline(qtbot):
    window = MainWindow(df)
    qtbot.addWidget(window)

    window.libary.setCurrentIndex(0)
    regressor_section = window.libary.columns_tab.widget()
    random_draggable = regressor_section.my_layout.itemAt(0).widget()

    # gather pipeline to drag to.
    pm = window.pipeline_mother
    curr_pipeline = pm.pipelines[0]
    curr_cols_sub = pm.columns_subwindow
    target_drop = curr_cols_sub.x_columns

    fake_drop = FakeDropEvent(
        random_draggable,
        QtCore.QPoint(0,0)
    )

    fake_drop.simulate_fake_drop(target_drop)
    
    assert target_drop.get_num_cols() != 0

def test_main_menu_loads(qtbot):
    window = MainMenu()
    qtbot.addWidget(window)
    assert window

