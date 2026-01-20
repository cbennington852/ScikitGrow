import pandas as pd
import sklearn
import src.datascratch.sklearn_engine as sklearn_engine
import pandas as pd
import sklearn
import seaborn as sns
from src.datascratch.sklearn_engine import Pipeline , EngineResults
import sklearn.model_selection as val


dataframe = pd.read_csv("resources/random_data.csv")

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
        pipeline_x_values=['sepal_width'],
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


def test_predictions_2d_reg():
    res : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
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
    res_value = res.predict([5.0 , 5.0])
    print(res_value)
    assert round(res_value[res.trained_models[0]] , 3) == round(40.43950829 , 3)

def test_predictions_1d_reg():
    res : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
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
    res_value = res.predict([5.0])
    print("Res Value"  ,res_value)
    assert round(res_value[res.trained_models[0]] , 3) == round(38.422 , 3)

def test_predictions_1d_reg():
    res : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=classifier_dataframe,
        pipeline_x_values=['sepal_width' , 'species'  ],
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
    res_value = res.predict([5.0 , 'setosa'])
    print("Res Value"  ,res_value)
    assert res_value[res.trained_models[0]] == 'setosa'

def test_metrics():
    res : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
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
    assert len(res.trained_models[0].model_results.relevant_statistical_results) != 0


def test_metrics_2d():
    res : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=dataframe,
        pipeline_x_values=['Example Chemical 2' ,  'Example Chemical 3'],
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
    assert len(res.trained_models[0].model_results.relevant_statistical_results) != 0

def test_metrics_classification():
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
    assert len(res.trained_models[0].model_results.relevant_statistical_results) != 0

def test_plot_no_model():
    res : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=classifier_dataframe,
        pipeline_x_values=['sepal_width' , 'petal_length'],
        pipeline_y_value=['species'],
        curr_pipelines=[
            
        ]
    )
    assert res.visual_plot

def test_plot_no_model():
    res  : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=classifier_dataframe,
        pipeline_x_values=['sepal_width' , 'petal_length'],
        pipeline_y_value=['species'],
        curr_pipelines=[
            
        ]
    )
    assert res.visual_plot

def test_plot_no_model_scatter():
    res  : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=classifier_dataframe,
        pipeline_x_values=['sepal_width' ],
        pipeline_y_value=['species'],
        curr_pipelines=[
            
        ]
    )
    assert res.visual_plot

def test_validators_with_regression():
    res : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=dataframe,
        pipeline_x_values=['Example Chemical 2' ,  'Example Chemical 3'],
        pipeline_y_value=['Example Chemical 1'],
        curr_pipelines=[
            Pipeline(
                sklearn_pipeline=linear_pipe,
                validator=val.KFold(n_splits=2),
            ),
            Pipeline(
                sklearn_pipeline=tree_pipe_1,
                validator=val.KFold(n_splits=2)
            )
        ]
    )
    assert len(res.trained_models[0].model_results.relevant_statistical_results) != 0

def test_validators_with_classification():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
            main_dataframe=classifier_dataframe,
            pipeline_x_values=['sepal_width' , 'petal_length'],
            pipeline_y_value=['species'],
            curr_pipelines=[
                Pipeline(
                    sklearn_pipeline=classifier_pipe,
                    validator=val.KFold(n_splits=2)
                ),
                Pipeline(
                    sklearn_pipeline=classifier_pipe_2,
                    validator=val.KFold(n_splits=2)
                )
            ]
        )
    assert len(res.trained_models[0].model_results.relevant_statistical_results) != 0

def test_classification_3_cols():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
            main_dataframe=classifier_dataframe,
            pipeline_x_values=['sepal_width' , 'petal_length' , 'sepal_length'],
            pipeline_y_value=['species'],
            curr_pipelines=[
                Pipeline(
                    sklearn_pipeline=classifier_pipe,
                    validator=val.KFold(n_splits=2)
                ),
                Pipeline(
                    sklearn_pipeline=classifier_pipe_2,
                    validator=val.KFold(n_splits=2)
                )
            ]
        )
    assert len(res.trained_models[0].model_results.relevant_statistical_results) != 0

def test_regression_3_plus():
    res : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=dataframe,
        pipeline_x_values=['Example Chemical 2' ,  'Example Chemical 3' , 'Example Chemical 4'],
        pipeline_y_value=['Example Chemical 1'],
        curr_pipelines=[
            Pipeline(
                sklearn_pipeline=linear_pipe,
                validator=val.KFold(n_splits=2),
            ),
            Pipeline(
                sklearn_pipeline=tree_pipe_1,
                validator=val.KFold(n_splits=2)
            )
        ]
    )
    assert res


def test_regression_one_model():
    res : EngineResults = sklearn_engine.SklearnEngine.main_sklearn_pipe(
        main_dataframe=dataframe,
        pipeline_x_values=['Example Chemical 2' ,  'Example Chemical 3' , 'Example Chemical 4'],
        pipeline_y_value=['Example Chemical 1'],
        curr_pipelines=[
            Pipeline(
                sklearn_pipeline=linear_pipe,
                validator=None,
            ),
        ]
    )
    assert res

def test_classification_4_cols():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
            main_dataframe=classifier_dataframe,
            pipeline_x_values=['sepal_width' , 'petal_length' , 'sepal_length'],
            pipeline_y_value=['species'],
            curr_pipelines=[
                Pipeline(
                    sklearn_pipeline=classifier_pipe,
                    validator=val.KFold(n_splits=2)
                ),
                Pipeline(
                    sklearn_pipeline=classifier_pipe_2,
                    validator=val.KFold(n_splits=2)
                )
            ]
        )
    assert res


def test_converted_cols():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
            main_dataframe=classifier_dataframe,
            pipeline_x_values=['sepal_width' , 'species'],
            pipeline_y_value=['species'],
            curr_pipelines=[
                Pipeline(
                    sklearn_pipeline=linear_pipe,
                ),
                Pipeline(
                    sklearn_pipeline=linear_pipe_2,
                )
            ]
        )
    assert res

def test_converted_cols():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
            main_dataframe=classifier_dataframe,
            pipeline_x_values=['species' , 'sepal_width'],
            pipeline_y_value=['species'],
            curr_pipelines=[
                Pipeline(
                    sklearn_pipeline=linear_pipe,
                ),
                Pipeline(
                    sklearn_pipeline=linear_pipe_2,
                )
            ]
        )
    assert res

def test_clashing_models():
    try:
        res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
                main_dataframe=classifier_dataframe,
                pipeline_x_values=['sepal_width' , 'petal_length' , 'sepal_length'],
                pipeline_y_value=['species'],
                curr_pipelines=[
                    Pipeline(
                        sklearn_pipeline=linear_pipe,
                        validator=val.KFold(n_splits=2)
                    ),
                    Pipeline(
                        sklearn_pipeline=classifier_pipe_2,
                        validator=val.KFold(n_splits=2)
                    )
                ]
            )
        assert False
    except Exception:
        assert True

def test_invalid_xcols():
    try:
        res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
                main_dataframe=classifier_dataframe,
                pipeline_x_values=['sepal_width' , 'asdasdasd' , 'sepal_length'],
                pipeline_y_value=['species'],
                curr_pipelines=[
                    Pipeline(
                        sklearn_pipeline=linear_pipe,
                    ),
                ]
            )
        assert False
    except Exception:
        assert True

def test_invalid_ycols():
    try:
        res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
                main_dataframe=classifier_dataframe,
                pipeline_x_values=['sepal_width' , 'asdasdasd' , 'sepal_length'],
                pipeline_y_value=['species'],
                curr_pipelines=[
                    Pipeline(
                        sklearn_pipeline=linear_pipe,
                    ),
                ]
            )
        assert False
    except Exception:
        assert True
    
def test_classification_5_cols():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
            main_dataframe=classifier_dataframe,
            pipeline_x_values=['sepal_width' , 'petal_length' , 'sepal_length' , 'petal_width'],
            pipeline_y_value=['species'],
            curr_pipelines=[
                Pipeline(
                    sklearn_pipeline=classifier_pipe,
                    validator=val.KFold(n_splits=2)
                ),
                Pipeline(
                    sklearn_pipeline=classifier_pipe_2,
                    validator=val.KFold(n_splits=2)
                )
            ]
        )
    assert res


def test_no_model_5_cols():
    res = sklearn_engine.SklearnEngine.main_sklearn_pipe(
            main_dataframe=classifier_dataframe,
            pipeline_x_values=['sepal_width' , 'petal_length' , 'sepal_length' , 'petal_width'],
            pipeline_y_value=['species'],
            curr_pipelines=[]
        )
    assert res