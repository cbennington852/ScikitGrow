import sklearn_engine
import pandas as pd
import sklearn
import sklearn_engine
import pandas as pd
import sklearn
import seaborn as sns
from sklearn_engine import Pipeline

dataframe = pd.read_csv("example_datasets/test.csv")
classifier_dataframe = sns.load_dataset('iris')

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

classifier_pipe = sklearn.pipeline.Pipeline([
    ("Linear_m" , sklearn.linear_model.RidgeClassifier())
])

classifier_pipe_2 = sklearn.pipeline.Pipeline([
    ("tree" , sklearn.tree.DecisionTreeClassifier())
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
    assert isinstance(res , sklearn_engine.EngineResults)

def test_3d_regression():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=dataframe,
        pipeline_x_values=['Example Chemical 2' , 'Example Chemical 3' ],
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
    assert isinstance(res , sklearn_engine.EngineResults)

def test_2d_classification():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=classifier_dataframe,
        pipeline_x_values=['sepal_width' ],
        pipeline_y_value=['species'],
        curr_pipelines=[
            Pipeline(
                sklearn_pipeline=classifier_pipe,
                validator=None
            ),
            Pipeline(
                sklearn_pipeline=classifier_pipe_2,
                validator=None
            )
        ]
    )
    assert isinstance(res , sklearn_engine.EngineResults)

def test_3d_classification():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=classifier_dataframe,
        pipeline_x_values=['sepal_width' , 'petal_length'],
        pipeline_y_value=['species'],
        curr_pipelines=[
            Pipeline(
                sklearn_pipeline=classifier_pipe,
                validator=None
            ),
            Pipeline(
                sklearn_pipeline=classifier_pipe_2,
                validator=None
            )
        ]
    )
    assert isinstance(res , sklearn_engine.EngineResults)