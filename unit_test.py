import sklearn_engine
import pandas as pd
import sklearn
import sklearn_engine
import pandas as pd
import matplotlib.pyplot as plt
import sklearn
from sklearn_engine import Pipeline

dataframe = pd.read_csv("example_datasets/test.csv")

linear_pipe = sklearn.pipeline.Pipeline([
    ("Linear_m" , sklearn.linear_model.LinearRegression())
])

linear_pipe_2 = sklearn.pipeline.Pipeline([
    ("Linear_m" , sklearn.linear_model.Lasso())
])

tree_pipe_1 =  sklearn.pipeline.Pipeline([
    ("tree_m" , sklearn.tree.DecisionTreeRegressor(
        max_depth=100
    ))
])
def test_2d_regression():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=dataframe,
        pipeline_x_values=['Example Chemical 2'  ],
        pipeline_y_value=['Example Chemical 1'],
        curr_pipelines=[
            Pipeline(
                sklearn_pipeline=linear_pipe,
                validator=None
            ),
            Pipeline(
                sklearn_pipeline=tree_pipe_1,
                validator=None
            )
        ]
    )
    assert True