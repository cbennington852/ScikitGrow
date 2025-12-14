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
            sklearn_pipeline=linear_pipe_2,
            validator=None
        )
    ]
)

plt.show()


# Regression 2d
    # Visual
        # Add another line to the graph
    # Accuracy
        # Add multiple accuracy charts
# Regression 3d
    # Visual 
        # just add another surface to the graph
    # Accuracy 
        # Add multiple accuracy charts

# Classification 2d
    # Visual
        # just add another line to graph? 
    # Accuracy 
        # Add another bar to accuracy bar plot.

# Classification 3d
    # Visual
        # simply have multiple plots w decision lines.
    # Accuracy
        # Add another bar to accuracy bar plot.
        