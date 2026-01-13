from src.main import MainMenu , MainWindow , SaveFile , SaveFileException
import pandas as pd
from src.draggable import Draggable , DraggableColumn
import sklearn
import pickle
from src.save_file import SaveFile
from PyQt5.QtTest import QTest
import time
import os.path
from src.descriptor_statistics_GUI import DescriptorStatisticsGUI
from pytestqt import qtbot

df = pd.read_csv("resources/random_data.csv")

def setup_test_environment_one():
    """
    A simple enviorment where there is one default pipeline, with only one model.
    """
    window = MainWindow(df)
    
    # setup up the pipeline
    pm = window.pipeline_mother
    curr_pipeline = pm.pipelines[0]
    curr_cols_sub = pm.columns_subwindow

    # Make a draggable linear_regressor
    drag_lin = Draggable(
        "LinearRegression",
        sklearn.linear_model.LinearRegression,
        Draggable.BUBBLE,
        "#000000"
    )

    drag_col_x = DraggableColumn(
        'Example Chemical 1'
    )
    drag_col_y = DraggableColumn(
        'Example Chemical 2'
    )

    # Add it
    curr_pipeline.model_pipe.my_layout.addWidget(drag_lin)
    curr_cols_sub.x_columns.my_layout.addWidget(drag_col_x)
    curr_cols_sub.y_columns.my_layout.addWidget(drag_col_y)
    return window




def setup_test_environment_two():
    """
    A simple enviorment where there are multiple pipelines. 
    This allows us to check and ensure that these work on multi 
    pipeline projects.
    """
    window = MainWindow(df)

    # setup up the pipeline
    pm = window.pipeline_mother
    curr_pipeline = pm.pipelines[0]
    curr_cols_sub = pm.columns_subwindow

    # Make a draggable linear_regressor
    drag_lin = Draggable(
        "LinearRegression",
        sklearn.linear_model.LinearRegression,
        Draggable.BUBBLE,
        "#000000"
    )

    drag_lin_2 = Draggable(
        "LinearRegression",
        sklearn.linear_model.Ridge,
        Draggable.BUBBLE,
        "#000000"
    )
    # Alter one of the parameters to verify the parameters are being saved
    print("these are parameters"  ,drag_lin_2.data.parameters)
    new_para = []
    for name , value in drag_lin_2.data.parameters:
        if name == 'alpha':
            new_para.append(('alpha' , 69.0))
        else:
            new_para.append((name , value))
    drag_lin_2.data.parameters = new_para

    # make a new pipeline.
    pm.add_pipeline()


    drag_col_x = DraggableColumn(
        'Example Chemical 1'
    )
    drag_col_y = DraggableColumn(
        'Example Chemical 2'
    )

    # Add it
    curr_pipeline.model_pipe.my_layout.addWidget(drag_lin)
    pm.pipelines[1].model_pipe.my_layout.addWidget(drag_lin_2)
    curr_cols_sub.x_columns.my_layout.addWidget(drag_col_x)
    curr_cols_sub.y_columns.my_layout.addWidget(drag_col_y)
    return window


def setup_generator_environment(window ):
    """Setup test envorment 2 and return engine results, once trained. 

    Returns:
        _type_: _description_
    """
    start_time = time.time()
    max_time = 3
    def check_time():
        return time.time() - start_time < max_time
    
    window.pipeline_mother.columns_subwindow.train_models.click()
    while (not hasattr(window.plotter , 'worker')) and check_time():
        time.sleep(0.01)
    while not hasattr(window.plotter.worker, 'engine_results') and check_time():
        time.sleep(0.01)
    # Setting a timer due to absurd internal PyQt libary error
    # The even thread is messed up for some reason only while testing.
    return window.plotter.worker.engine_results

def test_save_single_column(qtbot):
    window = setup_test_environment_one()
    qtbot.addWidget(window)
    file_name = 'data_test.pkl'
    window.save_function(file_name=file_name , no_popup=True)
    with open(file_name, 'rb') as file:
        loaded_data : SaveFile = pickle.load(file)
        assert loaded_data.columns_data.x_cols == ['Example Chemical 1']
        assert loaded_data.columns_data.y_cols == ['Example Chemical 2']
    window.close()

def test_loading_columns(qtbot):
    window = setup_test_environment_one()
    qtbot.addWidget(window)
    file_name = 'data_test.pkl'
    window.save_function(file_name=file_name , no_popup=True)
    saved_window = MainWindow.open_on_saved_file(file_name)

    # Now make sure the the window has all of the nessicary things
    assert saved_window.pipeline_mother.x_columns.get_cols_as_string_list() == ['Example Chemical 1']

def test_loading_models(qtbot):
    window = setup_test_environment_one()
    qtbot.addWidget(window)
    file_name = 'data_test.pkl'
    window.save_function(file_name=file_name , no_popup=True)
    saved_window = MainWindow.open_on_saved_file(file_name)


    assert saved_window.pipeline_mother.pipelines[0].model_pipe.get_data()[0].sklearn_function == sklearn.linear_model.LinearRegression

def test_others_empty(qtbot):
    window = setup_test_environment_one()
    qtbot.addWidget(window)

    file_name = 'data_test.pkl'
    window.save_function(file_name=file_name , no_popup=True)

    assert len(window.pipeline_mother.pipelines[0].validator.get_data()) == 0


def test_saving_and_loading_multiple_pipelines(qtbot):
    window = setup_test_environment_two()
    qtbot.addWidget(window)

    file_name = 'data_test.pkl'
    window.save_function(file_name=file_name , no_popup=True)
    saved_window = MainWindow.open_on_saved_file(file_name)
    assert saved_window.pipeline_mother.pipelines[1].model_pipe.get_data()[0].sklearn_function == sklearn.linear_model.Ridge


def test_saving_and_loading_altered_parameters(qtbot):
    window = setup_test_environment_two()
    qtbot.addWidget(window)

    file_name = 'data_test.pkl'
    window.save_function(file_name=file_name , no_popup=True)
    saved_window = MainWindow.open_on_saved_file(file_name)
    params = saved_window.pipeline_mother.pipelines[1].model_pipe.get_data()[0].parameters
    for name , value in params:
        if name == 'alpha':
            assert value == 69.0
            return
    assert False


def test_file_creation(qtbot):
    window = setup_test_environment_two()
    qtbot.addWidget(window)

    file_name = 'test_7.pkl'
    window.save_function(file_name=file_name , no_popup=True)
    time.sleep(0.2)
    assert os.path.isfile(file_name)

def test_wrong_file_type(qtbot):
    try:
        saved_window = MainWindow.open_on_saved_file("run.sh")
    except Exception:
        assert True


def test_running_predictor(qtbot):
    # check to see that the prredictor does not crash and returns an engine result
    window = setup_test_environment_two()
    qtbot.addWidget(window)

    if setup_generator_environment(window) is not None:
        assert True
    else:
        assert False

