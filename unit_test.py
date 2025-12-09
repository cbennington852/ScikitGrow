import sklearn_engine
import pandas as pd
import sklearn

dataframe = pd.read_csv("example_datasets/test.csv")

linear_pipe = sklearn.pipeline.Pipeline([
    ("Linear_m" , sklearn.linear_model.LinearRegression())
])

def test_2d_regression():
    sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=dataframe,
        curr_pipeline=linear_pipe,
        pipeline_x_values=['Example Chemical 2' , 'Example Chemical 3' ],
        pipeline_y_value=['Example Chemical 1'],
        validator=[]
    )
    assert True