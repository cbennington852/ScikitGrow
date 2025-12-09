import sys
import csv
import gi
import traceback
from matplotlib.colors import ListedColormap
import seaborn
import threading
from splash_screen import SplashScreen
import utility
import block_libary
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject
from cycler import cycler
import matplotlib
import copy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure
import sklearn
import pandas as pd
import numpy as np
from abc import ABC , abstractmethod

class ModelTrainingResults():
    """
    Small class to hold the results from training the model.
    """
    def __init__(self , y_predictions , trained_model):
        self.y_predictions = y_predictions
        self.trained_model = trained_model

class EngineResults():
    """
    Small class to hold the results from the engine.
    """
    def __init__(self, visual_plot , accuracy_plot):
        self.visual_plot = visual_plot
        self.accuracy_plot = accuracy_plot


MESH_ALPHA=0.7
        

class SklearnEngine():

    def factorize_string_cols(main_dataframe , pipeline_x_values , pipeline_y_value):
        """Takes all of the string like columns and serializes them, with each unique 
        value getting a new serial number

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_
        """
        cols = pipeline_x_values + pipeline_y_value
        for col in cols:
            if pd.api.types.is_string_dtype(main_dataframe[col]):
                codes, uniques = pd.factorize(main_dataframe[col])
                print(codes)
                print(uniques)
                main_dataframe[col] = codes
        return main_dataframe
    
    def plot_no_model(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value):
        # load x and y_values        
        x = main_dataframe[pipeline_x_values]
        y = main_dataframe[pipeline_y_value].iloc[:, 0]
        if (len(pipeline_x_values) == 1 and len(pipeline_y_value) == 1):
            # 2d scatterplot.
            fig, ax = plt.subplots()
            color_cycle = SklearnEngine.get_color_map()
            ax.scatter(x , y , color=color_cycle[0], label=f"Dataset")
            ax.set_title(f"{pipeline_x_values[0]} and {pipeline_y_value[0]}")
            ax.set_xlabel(f"{pipeline_x_values[0]}")
            ax.set_ylabel(f"{pipeline_y_value[0]}")
            ax.legend(loc='upper left')
            return fig
        
        elif (len(pipeline_x_values) == 2 and len(pipeline_y_value) == 1):
            color_cycle = SklearnEngine.get_color_map()
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            cmap = SklearnEngine.get_clf_color_map()
            ax.scatter(x.iloc[:, 0], x.iloc[:, 1], y, c=color_cycle[1], edgecolor='k')
            ax.set_xlabel(f"{pipeline_x_values[0]}")
            ax.set_ylabel(f"{pipeline_x_values[1]}")
            ax.set_position([0.05, 0.05, 0.9, 0.9]) 
            ax.set_zlabel(f"{pipeline_y_value[0]}")
            ax.set_title(f"3D Surface for {pipeline_y_value[0]}")
            return fig
        else:
            fig, ax = plt.subplots()
            return fig

    def main_sklearn_pipe(main_dataframe,  curr_pipeline , pipeline_x_values  , pipeline_y_value , validator) -> EngineResults:
        """Runs the main sklearn pipeline, filtering through the different options that
          the user could have inputted into this software. 

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            curr_pipeline (sklearn.pipeline): sklearn_pipeline object
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_
        """
        #raise ValueError("NOTE : Need to refactor this, decouple the sklearn stuff from the GUI stuff")        

        # make a copy of the dataframe
        main_dataframe_copy = main_dataframe.copy(deep=True)
        # If user wants a string, try to factorize.
        main_dataframe_copy = SklearnEngine.factorize_string_cols(main_dataframe_copy , pipeline_x_values , pipeline_y_value)
        # Preform basic validation on the inputs
        result_validation = SklearnEngine.validate_column_inputs(main_dataframe_copy ,curr_pipeline, pipeline_x_values , pipeline_y_value)

        if result_validation:
            return result_validation
        
        # Gather the x and y data
        x = main_dataframe_copy[pipeline_x_values]
        y = main_dataframe_copy[pipeline_y_value].iloc[:, 0]

        # Train the model
        model_training_results = SklearnEngine.train_model(
            main_dataframe=main_dataframe_copy, 
            curr_pipeline=curr_pipeline, 
            x=x,
            y=y,
            validator=validator
        )

        last_step_name , last_step_model = curr_pipeline.steps[-1]

        if sklearn.base.is_classifier(last_step_model):
            return SklearnEngine.ClassificationPlotterFilter.main_filter(
                main_dataframe ,
                curr_pipeline , 
                pipeline_x_values , 
                pipeline_y_value ,
                x , 
                y , 
                model_training_results.trained_model,
                model_training_results.y_predictions
            )
        elif sklearn.base.is_regressor(last_step_model):
            return SklearnEngine.RegressionPlotterFilter.main_filter(
                main_dataframe ,
                curr_pipeline , 
                pipeline_x_values , 
                pipeline_y_value ,
                x , 
                y , 
                model_training_results.trained_model,
                model_training_results.y_predictions
            )
        else:
            raise ValueError("Sci-kit Engine Internal Error ... Not a recognized model type.")
        

    def validate_column_inputs(main_dataframe, curr_pipeline, pipeline_x_values , pipeline_y_value):
        lst_cols = main_dataframe.columns
        # If model empty do empty plot
        if len(curr_pipeline.steps) == 0:
            return EngineResults(
                visual_plot=SklearnEngine.plot_no_model(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value),
                accuracy_plot=None
            )

        # If user added a pre-processor but not a model do an empty plot.
        last_step_name , last_step_model = curr_pipeline.steps[-1]
        if not (sklearn.base.is_classifier(last_step_model) or sklearn.base.is_regressor(last_step_model)):
            return EngineResults(
                visual_plot=SklearnEngine.plot_no_model(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value),
                accuracy_plot=None
            )
       
        # check to make sure cols are from this dataset.
        for x_col in pipeline_x_values:
            if x_col not in lst_cols:
                raise ValueError(f"Error: {x_col} is not in the dataset")
        for y_col in pipeline_y_value:
            if y_col not in lst_cols:
                raise ValueError(f"Error: {y_col} is not in the dataset")

    def k_fold_general_threads(model , kf , X , y):
        print("Staring Validator training!!!")
        def train_indexes(train_index , test_index):
            """
            The thing that we call each time in he k_fold
            """
            model_clone = sklearn.clone(model)
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            model_clone.fit(X_train , y_train)
            curr_y_preds = model_clone.predict(X_test)
            final_y[test_index] = curr_y_preds.flatten()

        # the final array
        final_y = np.empty(len(y))
        # k fold thing 
        threads = []
        for fold, (train_index, test_index) in enumerate(kf.split(X, y)):
            curr_thread = threading.Thread(target=train_indexes , kwargs={
                "train_index" : train_index,
                "test_index" : test_index
            })
            threads.append(curr_thread)
            curr_thread.start()
        for thread in threads:
            thread.join()
        return final_y 

    def train_model( main_dataframe , curr_pipeline , x , y , validator) -> ModelTrainingResults:
        """
        Trains the model using the main dataframe and pipeline_x_values. This is also
        where we will see what type of test train split the user has implemented into 
        their pipeline.

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            curr_pipeline (sklearn.pipeline): sklearn_pipeline object
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_

        Returns: 
            Trained Model
        """
        # Train the mode        
        curr_pipeline.fit(x , y)
        # Apply the user specified validator
        if (validator != []) and (not isinstance(validator[0][1] , block_libary.NoValidator)):
            y_preds = SklearnEngine.k_fold_general_threads(
                model=curr_pipeline,
                kf=validator[0][1],
                X=x,
                y=y
            )
        else:
            y_preds = curr_pipeline.predict(x)

        # Return 
        return ModelTrainingResults(
            y_predictions=y_preds,
            trained_model=curr_pipeline
        )
    
    def get_color_map():
        return plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    def get_clf_color_map():
        return matplotlib.colors.ListedColormap(SklearnEngine.get_color_map())
    
    # We have two classes, one for classifier and the other for plotting.
    # Plotter Filter
    # Classifier Plotter Filter
    # Regression Plotter Filter

    def get_scatter_alpha_value(number_data_points , minimum_alpha_value=0.1 , factor=3000):
        """Calculates the alpha value based on the number of data points in a dataset
        """
        first_part = (-1 * ((number_data_points ** 2) / factor)) + 100
        return max(first_part / 100 , minimum_alpha_value)

    class PlotterFilter(ABC):
        @abstractmethod
        def main_filter(
            main_dataframe ,
            curr_pipeline , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
            trained_model,
            y_predictions
        ) -> EngineResults:
            pass


    class ClassificationPlotterFilter(PlotterFilter):
        def main_filter(
            main_dataframe ,
            curr_pipeline , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
            trained_model,
            y_predictions
        ) -> EngineResults:
            visual_plot = None
            accuracy_plot = SklearnEngine.ClassificationPlotterFilter.accuracy_plot(
                main_dataframe ,
                curr_pipeline , 
                pipeline_x_values , 
                pipeline_y_value ,
                x , 
                y , 
                trained_model,
                y_predictions
            )
            if len(x.columns) == 1:
                visual_plot = SklearnEngine.ClassificationPlotterFilter.plot_1d(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                )
            elif len(x.columns) == 2:
                visual_plot = SklearnEngine.ClassificationPlotterFilter.plot_2d(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                )
            elif len(x.columns) == 3:
                visual_plot =  SklearnEngine.ClassificationPlotterFilter.plot_3(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                )
            else:
                visual_plot =  SklearnEngine.ClassificationPlotterFilter.plot_3_plus(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                )
            return EngineResults(
                visual_plot=visual_plot,
                accuracy_plot=accuracy_plot
            )
            
        def accuracy_plot(
            main_dataframe ,
            curr_pipeline , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
            trained_model,
            y_predictions
        ):
            fig, ax = plt.subplots()
            accuracy = sklearn.metrics.accuracy_score(y, y_predictions)
            ax.bar(['Accuracy'], [accuracy])
            ax.set_ylim(0, 1)
            ax.set_ylabel('Accuracy')
            ax.set_title('Model Accuracy')
            ax.text(0, accuracy / 2, f"{accuracy:.2%}", ha='center', va='center', fontsize=12)
            return fig
            
        def plot_1d(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                ):
            max_margin = 0.5
            x_min, x_max = x.min() - max_margin, x.max() + max_margin
            y_enc = sklearn.preprocessing.LabelEncoder().fit_transform(y)
            x_plot = np.linspace(x_min, x_max, 1000).reshape(-1, 1)
            y_preds = trained_model.predict(x_plot)
            fig, ax = plt.subplots()
            n_classes = len(np.unique(y_enc))
            cmap = ListedColormap(SklearnEngine.get_clf_color_map().colors[:n_classes])
            ax.scatter(X, y, c=y_enc, cmap=cmap,
                        edgecolor='k', marker='o', s=50, label=f'')
            ax.plot(x_plot[:, 0], y_preds, label='Hard Predicted Class (0 or 1)',
                    color='blue', linewidth=3)
            switch_index = np.argmax(y_preds)
            decision_boundary_x = x_plot[switch_index, 0]
            ax.axvline(x=decision_boundary_x, color='red', linestyle='--',
                        label=f'Decision Boundary (x={decision_boundary_x:.2f})')
            ax.set_title(f'Classifier for {pipeline_y_value[0]}')
            ax.set_xlabel(f'{pipeline_y_value[0]}')
            ax.set_ylabel(f'{pipeline_y_value[0]}')
            ax.legend(loc='upper left')
            ax.grid(True, axis='x', linestyle='--', alpha=0.6)
            return fig
        
        def plot_2d(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                ):
            y_enc = sklearn.preprocessing.LabelEncoder().fit_transform(y)
            # Plot the decision boundary
            fig, ax = plt.subplots()
            n_classes = len(np.unique(y_enc))
            cmap = ListedColormap(SklearnEngine.get_clf_color_map().colors[:n_classes])
            sklearn.inspection.DecisionBoundaryDisplay.from_estimator(
                trained_model,
                x,
                response_method="predict",
                cmap=cmap,
                ax=ax
            )

            # Plot the data points
            ax.scatter(x.iloc[:, 0], x.iloc[:, 1], cmap=cmap,  c=y_enc, edgecolors='k')
            ax.set_title(f"Classifier for {pipeline_y_value[0]}")
            ax.set_xlabel(f"{pipeline_x_values[0]}")
            ax.set_ylabel(f"{pipeline_x_values[1]}")
            handles = []
            classes = np.unique(main_dataframe[pipeline_y_value])
            classes_color_encoding = np.unique(y_enc)
            for x in range(0 , len(classes)):
                class_val = classes_color_encoding[x]
                handles.append(
                    ax.plot([], [], marker='o', linestyle='', color=cmap(class_val),
                            label=f'Class {classes[x]}', markeredgecolor='k')
                )
            ax.legend(loc='upper left')
            return fig
        
        def plot_3(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                ):
            raise ValueError("TODO : Write a 3 dimensional classification visualization")
        #https://www.researchgate.net/figure/3-Dimensional-surface-plot-of-classification-accuracy-against-spread-and-pattern-numbers_fig1_273402360
        # shows how to do this.

        def plot_4_plus(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                ):
           fig, ax = plt.subplots()
           return fig



    class RegressionPlotterFilter(PlotterFilter):
        def main_filter(
            main_dataframe ,
            curr_pipeline , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
            trained_model,
            y_predictions
        ) -> EngineResults:
            accuracy_plot = SklearnEngine.RegressionPlotterFilter.accuracy(main_dataframe ,
                curr_pipeline , 
                pipeline_x_values , 
                pipeline_y_value ,
                x , 
                y , 
                trained_model,
                y_predictions
            )
            visual_plot = None
            if len(x.columns) == 1:
                visual_plot = SklearnEngine.RegressionPlotterFilter.plot_1d(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                )
            elif len(x.columns) == 2:
                visual_plot = SklearnEngine.RegressionPlotterFilter.plot_2d(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                )
            elif len(x.columns) == 3:
                visual_plot =  SklearnEngine.RegressionPlotterFilter.plot_3d(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                )
            else:
                visual_plot =  SklearnEngine.RegressionPlotterFilter.plot_4_plus(
                    main_dataframe ,
                    curr_pipeline , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                    trained_model,
                    y_predictions
                )
            return EngineResults(
                visual_plot=visual_plot,
                accuracy_plot=accuracy_plot
            )


        def plot_1d(
            main_dataframe ,
            curr_pipeline , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
            trained_model,
            y_predictions
        ):
            fig, ax = plt.subplots()
            color_cycle = SklearnEngine.get_color_map()
            ax.scatter(x , y , color=color_cycle[0], label=f"Dataset", alpha=SklearnEngine.get_scatter_alpha_value(len(x)))
            ax.plot(x , y_predictions ,  color=color_cycle[1] , label='Model predictions')
            ax.set_title(f"{pipeline_x_values[0]} and {pipeline_y_value[0]}")
            ax.set_xlabel(f"{pipeline_x_values[0]}")
            ax.set_ylabel(f"{pipeline_y_value[0]}")
            ax.legend(loc='upper left')
            return fig
        
        def plot_2d(
            main_dataframe ,
            curr_pipeline , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
            trained_model,
            y_predictions
        ):
            # Step 3: Create grid for plotting
            x1_range = np.linspace(x.iloc[:, 0].min(), x.iloc[:, 0].max(), 50)
            x2_range = np.linspace(x.iloc[:, 1].min(), x.iloc[:, 1].max(), 50)
            x1_grid, x2_grid = np.meshgrid(x1_range, x2_range)
            color_cycle = SklearnEngine.get_color_map()

            # Create a DataFrame from the grid for prediction
            grid_df = pd.DataFrame({
                pipeline_x_values[0]: x1_grid.ravel(),
                pipeline_x_values[1]: x2_grid.ravel()
            })

            # Step 4: Predict y values over the grid
            y_pred = trained_model.predict(grid_df).reshape(x1_grid.shape)


            # Step 5: Plotting
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            # Plot surface
            cmap = SklearnEngine.get_clf_color_map()
            ax.plot_surface(x1_grid, x2_grid, y_pred,  alpha=MESH_ALPHA)

            # Plot actual data points
            ax.scatter(x.iloc[:, 0], x.iloc[:, 1], y, c=color_cycle[1], edgecolor='k')

            # Labels
            ax.set_xlabel(f"{pipeline_x_values[0]}")
            ax.set_ylabel(f"{pipeline_x_values[1]}")
            #ax.set_position([0.05, 0.05, 0.9, 0.9]) 
            ax.set_zlabel(f"{pipeline_y_value[0]}")
            ax.set_title(f"3D Surface for {pipeline_y_value[0]}")
            return fig
            
        def plot_3d(
            main_dataframe ,
            curr_pipeline , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
            trained_model,
            y_predictions
        ):
            raise ValueError("Not implemented")



        
        def plot_4d_plus(
            main_dataframe ,
            curr_pipeline , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
            trained_model,
            y_predictions
        ):
            fig, ax = plt.subplots()
            return fig



        def accuracy(
            main_dataframe ,
            curr_pipeline , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
            trained_model,
            y_predictions
        ):
            fig, ax = plt.subplots()
            ax.scatter(y, y_predictions, alpha=SklearnEngine.get_scatter_alpha_value(len(x)), edgecolor='k', label='Predicted Points')
            ax.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Prefect Prediction')
            ax.set_xlabel("Actual Values")
            ax.set_ylabel("Predicted Values")
            ax.legend()
            ax.grid(True)
            textstr = (
                f"\nPredicted vs. Actual Values"
                f"\nRMSE                : {sklearn.metrics.mean_squared_error(y, y_predictions):.2f}" + 
                f"\nExplained Variance  : {sklearn.metrics.explained_variance_score(y, y_predictions):.2f}" + 
                f"\nr2                  : {sklearn.metrics.r2_score(y, y_predictions):.2f}"
            )
            ax.set_title(textstr)
            return fig
    
       
    
  




