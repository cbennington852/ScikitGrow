from main import MainMenu , MainWindow
import pandas as pd
from draggable import Draggable , DraggableColumn
import sklearn
import pickle
from save_file import SaveFile
from PyQt5.QtTest import QTest

df = pd.read_csv("example_datasets/test.csv")

# TEST 1 : build an environment that is testable.
def setup_test_environment_one():
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

def test_save_single_model():
    window = setup_test_environment_one()
    file_name = 'data_test.pkl'
    window.save_button_pressed(file_name=file_name , no_popup=True)
    # Simulate a key press.
    with open(file_name, 'rb') as file:
        loaded_data = pickle.load(file)
        assert len(loaded_data.pipelines_data) == 1 # check only one pipeline
        assert len(loaded_data.pipelines_data[0].model_pipeline) == 1 # check pipeline has only one model
        assert loaded_data.pipelines_data[0].model_pipeline[0].sklearn_function == sklearn.linear_model.LinearRegression
    window.close()

def test_save_single_column():
    window = setup_test_environment_one()
    file_name = 'data_test.pkl'
    window.save_button_pressed(file_name=file_name , no_popup=True)
    with open(file_name, 'rb') as file:
        loaded_data : SaveFile = pickle.load(file)
        assert loaded_data.columns_data.x_cols == ['Example Chemical 1']
        assert loaded_data.columns_data.y_cols == ['Example Chemical 2']
    window.close()

def test_loading_columns():
    window = setup_test_environment_one()
    file_name = 'data_test.pkl'
    window.save_button_pressed(file_name=file_name , no_popup=True)

    # Now make sure the the window has all of the nessicary things
    assert window.pipeline_mother.x_columns.get_cols_as_string_list() == ['Example Chemical 1']

def test_loading_columns():
    window = setup_test_environment_one()
    file_name = 'data_test.pkl'
    window.save_button_pressed(file_name=file_name , no_popup=True)

    # Now make sure the the window has all of the nessicary things
    assert window.pipeline_mother.x_columns.get_cols_as_string_list() == ['Example Chemical 1']

def test_loading_models():
    window = setup_test_environment_one()
    file_name = 'data_test.pkl'
    window.save_button_pressed(file_name=file_name , no_popup=True)
    
    assert window.pipeline_mother.pipelines[0].model_pipe.get_data()[0].sklearn_function == sklearn.linear_model.LinearRegression



# now think of ways to test loading.

