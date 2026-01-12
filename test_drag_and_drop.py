import sklearn_engine
import pandas as pd
from main import MainMenu , MainWindow , SaveFile , SaveFileException

import sklearn
import sklearn_engine
import time
import pandas as pd
import sklearn
import seaborn as sns
from sklearn_engine import Pipeline , EngineResults
import sklearn.model_selection as val
from PyQt5 import QtCore, QtTest

df = pd.read_csv("resources/random_data.csv")


def simulate_drag_and_drop(qtbot , source_widget , target_widget):
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



def test_library_to_pipeline(qtbot):
    window = MainWindow(df)
    qtbot.addWidget(window)
    # gather random draggable
    window.libary.setCurrentIndex(0)
    regressor_section = window.libary.lin_reg
    random_regressor = regressor_section.my_layout.itemAt(0).widget()
    # gather pipeline to drag to.
    pm = window.pipeline_mother
    curr_pipeline = pm.pipelines[0]
    curr_cols_sub = pm.columns_subwindow
    target_models = curr_pipeline.model_pipe

    simulate_drag_and_drop(
        qtbot=qtbot,
        source_widget=random_regressor,
        target_widget=target_models
    )

    print("Draggable? " , random_regressor , type(random_regressor))
    print(target_models.my_layout.count() , type(target_models)  ,target_models.get_pipeline_objects())
    if len(target_models.get_pipeline_objects()) != 0:
        assert True
    else: 
        assert False

