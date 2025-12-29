import matplotlib
import seaborn
import threading
import matplotlib.pyplot as plt
import sklearn
import random
import pandas as pd
import numpy as np
from abc import ABC , abstractmethod
from matplotlib.colors import ListedColormap
from list_of_acceptable_sklearn_functions import SklearnAcceptableFunctions



def is_regressor(x):
    if x in SklearnAcceptableFunctions.REGRESSORS:
        return True
    else:
        return False

def classification_filter(x):
    try:
        return sklearn.base.is_classifier(x)
    except:
        return False


# Feature expansion plan ... multiple pipelines
    # SklearnEngine takes in multiple "Pipelines"
    # Each Pipeline gets a thread for training.

    # Each plotting endpoint needs to modified, and receives a list of Pipelines

class InternalEngineError(Exception):
    pass

class Pipeline():
    rand_adj = [
        "Awesome", "Beautiful", "Charming", "Delightful", "Energetic", 
        "Fantastic", "Gorgeous", "Happy", "Intelligent", "Joyful"
    ]

    """
    A small class to hold a sklearn pipeline and optionally a validator.
    """
    def __init__(self , sklearn_pipeline : sklearn.pipeline.Pipeline , name = None , validator = None ):
        self.sklearn_pipeline = sklearn_pipeline
        self.validator = validator
        self.name = name
        self.model_results : ModelTrainingResults = None
        last_step_name , last_step_model = self.sklearn_pipeline.steps[-1]
        if self.name is None:
            self.name = random.choice(Pipeline.rand_adj) + " " + last_step_model.__class__.__name__
        if sklearn.base.is_classifier(last_step_model):
            self.supervised_learning_type = SklearnEngine.CLASSIFICATION
        elif sklearn.base.is_regressor(last_step_model):
            self.supervised_learning_type = SklearnEngine.REGRESSION
        else:
            raise InternalEngineError(f"Pipeline {name} has neither a regressor or classifier. Crashing")
            

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

    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    EMPTY = "empty"

    def check_all_same_supervised_learning_type(curr_pipelines : list[Pipeline]):
        if len(curr_pipelines) == 0:
            return SklearnEngine.EMPTY
        first = curr_pipelines[0]
        for i in range(1 , len(curr_pipelines)):
            if curr_pipelines[i].supervised_learning_type != first.supervised_learning_type:
                raise InternalEngineError(
                    f"""{first.name} Has a different supervised learning type than {curr_pipelines[i].name}. 
                    {first.name} is a {first.supervised_learning_type}, whereas {curr_pipelines[i].name} is a {curr_pipelines[i].supervised_learning_type}
                    """
                )
        return first.supervised_learning_type

    def main_sklearn_pipe(main_dataframe : pd.DataFrame,  curr_pipelines : list[Pipeline] , pipeline_x_values  , pipeline_y_value ) -> EngineResults:
        """Runs the main sklearn pipeline, filtering through the different options that
          the user could have inputted into this software. 

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            curr_pipeline lst[SklearnEngine.Pipeline]: list of pipelines
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_
        """

        # make a copy of the dataframe
        try:
            main_dataframe_copy = main_dataframe.copy(deep=True)
        except Exception as e:
            raise InternalEngineError(f"Failed to deep copy the dataframe : {str(e)}")
        
        
        
        # Drop NaN
        main_dataframe_copy = main_dataframe_copy.dropna()

        #Sort the dataframe to make plots better.
        main_dataframe_copy.sort_values(by=pipeline_x_values, inplace=True)

        # verify that the pipelines are 
        supervised_learning_type = SklearnEngine.check_all_same_supervised_learning_type(curr_pipelines)

        # If user wants a string, try to factorize.
        main_dataframe_copy = SklearnEngine.factorize_string_cols(main_dataframe_copy , pipeline_x_values , pipeline_y_value)

        # Preform basic validation on the inputs
        result_validation = SklearnEngine.validate_column_inputs(main_dataframe_copy , curr_pipelines, pipeline_x_values , pipeline_y_value)

        if result_validation:
            return result_validation
        
        # Gather the x and y data
        x = main_dataframe_copy[pipeline_x_values]
        y = main_dataframe_copy[pipeline_y_value].iloc[:, 0]

        # Train the model

        SklearnEngine.train_model(
            main_dataframe=main_dataframe_copy, 
            curr_pipeline=curr_pipelines, 
            x=x,
            y=y,
        )
        

        if supervised_learning_type == SklearnEngine.CLASSIFICATION:
            return SklearnEngine.ClassificationPlotterFilter.main_filter(
                main_dataframe ,
                curr_pipelines , 
                pipeline_x_values , 
                pipeline_y_value ,
                x , 
                y , 
            )
        elif supervised_learning_type == SklearnEngine.REGRESSION:
            return SklearnEngine.RegressionPlotterFilter.main_filter(
                main_dataframe ,
                curr_pipelines , 
                pipeline_x_values , 
                pipeline_y_value ,
                x , 
                y , 
            )
        else:
            raise ValueError("Internal Engine Error : Not Regression or classification")

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

   
        

    def validate_column_inputs(main_dataframe, curr_pipelines, pipeline_x_values , pipeline_y_value):
        lst_cols = main_dataframe.columns
        # If model empty do empty plot
        if len(curr_pipelines) == 0:
            return EngineResults(
                visual_plot=SklearnEngine.plot_no_model(main_dataframe , curr_pipelines , pipeline_x_values , pipeline_y_value),
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
    

    def train_model( main_dataframe , curr_pipeline : list[Pipeline] , x , y ) -> list[ModelTrainingResults]:
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
        results = {}
        def train_single_model(curr : Pipeline):
                curr.sklearn_pipeline.fit(x , y)
                # Apply the user specified validator
                if (curr.validator is not None):
                    y_preds = SklearnEngine.k_fold_general_threads(
                        model=curr_pipeline,
                        kf=curr.validator,
                        X=x,
                        y=y
                    )
                else:
                    y_preds = curr.sklearn_pipeline.predict(x)
                results[curr] = (
                    ModelTrainingResults(
                        y_predictions=y_preds,
                        trained_model=curr.sklearn_pipeline
                    )
                )
            
                
            
        threads = []
            # Train each pipeline on an individual thread.
        for pipeline in curr_pipeline:
            try:
                train_single_model(pipeline)
            except sklearn.utils._param_validation.InvalidParameterError as e:
                raise InternalEngineError(f"Failed to train pipeline {pipeline.name} because {str(e)}")
        # Attach the results to each pipeline
        for ptr_to_pipeline , model_results in results.items():
            ptr_to_pipeline.model_results = model_results

        
    
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
            curr_pipelines , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
        ) -> EngineResults:
            pass

    class ClassificationPlotterFilter(PlotterFilter):
        def main_filter(
            main_dataframe ,
            curr_pipelines : list[Pipeline], 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
        ) -> EngineResults:
            visual_plot = None
            accuracy_plot = SklearnEngine.ClassificationPlotterFilter.accuracy_plot(
                main_dataframe ,
                curr_pipelines , 
                pipeline_x_values , 
                pipeline_y_value ,
                x , 
                y , 
            )
            if len(x.columns) == 1:
                visual_plot = SklearnEngine.ClassificationPlotterFilter.plot_1d(
                    main_dataframe ,
                    curr_pipelines , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                )
            elif len(x.columns) == 2:
                visual_plot = SklearnEngine.ClassificationPlotterFilter.plot_2d(
                    main_dataframe ,
                    curr_pipelines , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                )
            elif len(x.columns) == 3:
                visual_plot =  SklearnEngine.ClassificationPlotterFilter.plot_3(
                    main_dataframe ,
                    curr_pipelines , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                )
            else:
                visual_plot =  SklearnEngine.ClassificationPlotterFilter.plot_3_plus(
                    main_dataframe ,
                    curr_pipelines , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                )
            return EngineResults(
                visual_plot=visual_plot,
                accuracy_plot=accuracy_plot
            )
            
        def accuracy_plot(
            main_dataframe ,
            curr_pipelines :list[Pipeline] , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
        ):
            fig, ax = plt.subplots()
            results = []
            categories = []
            for i in range(0 , len(curr_pipelines)):
                y_predictions = curr_pipelines[i].model_results.y_predictions
                accuracy = sklearn.metrics.accuracy_score(y, y_predictions)
                results.append(accuracy)
                categories.append(curr_pipelines[i].name)
            bar_container = ax.bar(categories , results)
            ax.bar_label(bar_container)
            ax.set_ylim(0, 1)
            ax.set_ylabel('Accuracy')
            ax.set_title('Model Accuracy')
            return fig
            
        def plot_1d(
                    main_dataframe ,
                    curr_pipelines :list[Pipeline] , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                ):
            max_margin = 0.5
            fig, ax = plt.subplots()
            x_min, x_max = x.min() - max_margin, x.max() + max_margin
            y_enc = sklearn.preprocessing.LabelEncoder().fit_transform(y)
            x_plot = np.linspace(x_min, x_max, 1000).reshape(-1, 1)
            n_classes = len(np.unique(y_enc))
            cmap = ListedColormap(SklearnEngine.get_clf_color_map().colors[:n_classes])
            for i in range(0 , len(curr_pipelines)):
                y_preds = curr_pipelines[i].model_results.trained_model.predict(x_plot)
                ax.plot(x_plot[:, 0], y_preds, label=f'Hard Predicted Class (0 or 1) {curr_pipelines[i].name}', linewidth=3)
                switch_index = np.argmax(y_preds)
                decision_boundary_x = x_plot[switch_index, 0]
                ax.axvline(x=decision_boundary_x, linestyle='--',
                            label=f'Decision Boundary (x={decision_boundary_x:.2f})')
            ax.set_title(f'Classifier for {pipeline_y_value[0]}')
            ax.scatter(x, y, c=y_enc, cmap=cmap, edgecolor='k', marker='o', s=50, label=f'')
            ax.set_xlabel(f'{pipeline_y_value[0]}')
            ax.set_ylabel(f'{pipeline_y_value[0]}')
            fig.legend(loc='outside upper right')
            ax.grid(True, axis='x', linestyle='--', alpha=0.6)
            return fig
        
        def plot_2d(
                    main_dataframe ,
                    curr_pipelines :list[Pipeline] , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                ):
            fig, axs = plt.subplots( 1 , len(curr_pipelines) )
            if len(curr_pipelines) == 1:
                axs = [axs]
            y_enc = sklearn.preprocessing.LabelEncoder().fit_transform(y)
            # Plot the decision boundary
            n_classes = len(np.unique(y_enc))
            cmap = ListedColormap(SklearnEngine.get_clf_color_map().colors[:n_classes])
            classes = np.unique(main_dataframe[pipeline_y_value])
            classes_color_encoding = np.unique(y_enc)
            for i in range(0 , len(curr_pipelines)):
                current_ax = axs[i]
                sklearn.inspection.DecisionBoundaryDisplay.from_estimator(
                    curr_pipelines[i].model_results.trained_model,
                    x,
                    response_method="predict",
                    cmap=cmap,
                    ax=current_ax
                )
                # Plot the data points
                axs[i].scatter(x.iloc[:, 0], x.iloc[:, 1], cmap=cmap,  c=y_enc, edgecolors='k')
                axs[i].set_title(f"Classifier for {pipeline_y_value[0]} : {curr_pipelines[i].name}")
                axs[i].set_xlabel(f"{pipeline_x_values[0]}")
                axs[i].set_ylabel(f"{pipeline_x_values[1]}")
                handles = []
                for k in range(0 , len(classes)):
                    class_val = classes_color_encoding[k]
                    handles.append(
                        axs[i].plot([], [], marker='o', linestyle='', color=cmap(class_val),
                                label=f'Class {classes[k]}', markeredgecolor='k')
                    )
                axs[i].legend(loc='upper left')
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
            curr_pipelines , 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
        ) -> EngineResults:
            accuracy_plot = SklearnEngine.RegressionPlotterFilter.accuracy(
                main_dataframe ,
                curr_pipelines , 
                pipeline_x_values , 
                pipeline_y_value ,
                x , 
                y , 
            )
            visual_plot = None
            if len(x.columns) == 1:
                visual_plot = SklearnEngine.RegressionPlotterFilter.plot_1d(
                    main_dataframe ,
                    curr_pipelines , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y , 
                )
            elif len(x.columns) == 2:
                visual_plot = SklearnEngine.RegressionPlotterFilter.plot_2d(
                    main_dataframe ,
                    curr_pipelines , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y ,
                )
            elif len(x.columns) == 3:
                visual_plot =  SklearnEngine.RegressionPlotterFilter.plot_3d(
                    main_dataframe ,
                    curr_pipelines , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y ,
                )
            else:
                visual_plot =  SklearnEngine.RegressionPlotterFilter.plot_4_plus(
                    main_dataframe ,
                    curr_pipelines , 
                    pipeline_x_values , 
                    pipeline_y_value ,
                    x , 
                    y ,
                )
            return EngineResults(
                visual_plot=visual_plot,
                accuracy_plot=accuracy_plot
            )


        def plot_1d(
            main_dataframe ,
            curr_pipelines : list[Pipeline], 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
        ):
            fig, ax = plt.subplots()
            color_cycle = SklearnEngine.get_color_map()
            ax.scatter(x , y , color=color_cycle[0], label=f"Dataset", alpha=SklearnEngine.get_scatter_alpha_value(len(x)))
            for i in range(0 , len(curr_pipelines)):
                curr = curr_pipelines[i].model_results.y_predictions
                ax.plot(x , curr ,  color=color_cycle[i+1] , label=f'{curr_pipelines[i].name} predictions')
            ax.set_title(f"{pipeline_x_values[0]} and {pipeline_y_value[0]}")
            ax.set_xlabel(f"{pipeline_x_values[0]}")
            ax.set_ylabel(f"{pipeline_y_value[0]}")
            ax.legend()
            return fig
        
        def plot_2d(
            main_dataframe ,
            curr_pipelines : list[Pipeline], 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
        ):
            # Step 3: Create grid for plotting
            x1_range = np.linspace(x.iloc[:, 0].min(), x.iloc[:, 0].max(), 50)
            x2_range = np.linspace(x.iloc[:, 1].min(), x.iloc[:, 1].max(), 50)
            x1_grid, x2_grid = np.meshgrid(x1_range, x2_range)
            lst_cmaps = plt.colormaps()

            # Create a DataFrame from the grid for prediction
            grid_df = pd.DataFrame({
                pipeline_x_values[0]: x1_grid.ravel(),
                pipeline_x_values[1]: x2_grid.ravel()
            })

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            for i  in range(0 , len(curr_pipelines)):
                pipeline = curr_pipelines[i]
                y_pred = pipeline.sklearn_pipeline.predict(grid_df).reshape(x1_grid.shape)
                cmap_index = 0
                if i < len(lst_cmaps):
                    cmap_index = i

                ax.plot_surface(x1_grid, x2_grid, y_pred, alpha=MESH_ALPHA , cmap=lst_cmaps[cmap_index])

            # Plot actual data points
            ax.scatter(x.iloc[:, 0], x.iloc[:, 1], y, c=y, edgecolor='k')

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
            fig, ax = plt.subplots()
            return fig



        
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
            curr_pipelines : list[Pipeline], 
            pipeline_x_values , 
            pipeline_y_value ,
            x , 
            y , 
        ):
            fig, axs = plt.subplots( 1 , len(curr_pipelines) )
            if len(curr_pipelines) <= 1:
                axs = [axs]
            for i in range(0 , len(curr_pipelines)):
                y_predictions = curr_pipelines[i].model_results.y_predictions
                axs[i].scatter(y, y_predictions, alpha=SklearnEngine.get_scatter_alpha_value(len(x)), edgecolor='k', label='Predicted Points')
                axs[i].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Prefect Prediction')
                axs[i].set_xlabel("Actual Values")
                axs[i].set_ylabel(f"")
                axs[i].legend()
                axs[i].grid(True)
                textstr = (
                    f"\n{curr_pipelines[i].name}"
                    f"\nPredicted vs. Actual Values"
                    f"\nRMSE                : {sklearn.metrics.mean_squared_error(y, y_predictions):.2f}" + 
                    f"\nExplained Variance  : {sklearn.metrics.explained_variance_score(y, y_predictions):.2f}" + 
                    f"\nr2                  : {sklearn.metrics.r2_score(y, y_predictions):.2f}"
                )
                axs[i].set_title(textstr)
            return fig
    
       
    
  




