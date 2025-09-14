import sys
import csv
import gi
import traceback
from matplotlib.colors import ListedColormap
import seaborn

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject
from cycler import cycler


import matplotlib

matplotlib.use("GTK4Agg")  # Or 'GTK3Agg' for GTK3
import matplotlib.pyplot as plt

from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure
import sklearn
import pandas as pd
import numpy as np


class SklearnPlotter(Gtk.Notebook):
    """A GTK notebook that contains all of the plotting info. 

        self.main_sklearn_pipe() 
        ^^^ calls the main plotting function

    Args:
        Gtk (_type_): _description_
    """
    def __init__(self , **kargs):
        super().__init__(**kargs)
        # Create content for the first page
        self.plotting_page = Gtk.Box()
        plotting_page_label = Gtk.Label(label="Plot")
        self.append_page(self.plotting_page, plotting_page_label)

        # Create content for the second page
        self.accuracy_page = Gtk.Box()
        accuracy_page_label = Gtk.Label(label="Accuracy")
        self.append_page(self.accuracy_page, accuracy_page_label)

    def factorize_string_cols(self, main_dataframe , pipeline_x_values , pipeline_y_value):
        """Takes all of the string like columns and serializes them, with each unique 
        value getting a new serial number

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_
        """
        # returns as new main dataframe. 
        self.og_mainframe = main_dataframe.copy(deep=True)
        cols = pipeline_x_values + pipeline_y_value
        for col in cols:
            if pd.api.types.is_string_dtype(main_dataframe[col]):
                # uses # Use factorize() to serialize the 'products' column
                codes, uniques = pd.factorize(main_dataframe[col])
                print(codes)
                print(uniques)
                main_dataframe[col] = codes
        return main_dataframe

    def main_sklearn_pipe(self , main_dataframe,  curr_pipeline , pipeline_x_values  , pipeline_y_value):
        """Runs the main sklearn pipeline, filtering through the different options that
          the user could have inputted into this software. 

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            curr_pipeline (sklearn.pipeline): sklearn_pipeline object
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_
        """
    
        main_dataframe = self.factorize_string_cols(main_dataframe , pipeline_x_values , pipeline_y_value)
        # plotting the normal regular plotting chart
        self.train_model(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value)
        figure = self.filter_pipeline()
        self.plot_figure_canvas(figure , self.plotting_page)
        # plotting the accuracy chart
        print("HI")
        accuracy_plot = self.filter_accuracy_plotting(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value)
        self.plot_figure_canvas(accuracy_plot , self.accuracy_page)
       
        
    def filter_accuracy_plotting(self, main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value):
        """
        ACCURACY ONLY 
        Filters the dataset based on the pipeline, trying to see specifically what type
        of input the user wants to get back out at them. 

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            curr_pipeline (sklearn.pipeline): sklearn_pipeline object
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_

        Raises:
            ValueError: Not a regressor or classifier

        Returns:
            Figure: the figure containing the chart to be plotted. 
        """
        print(curr_pipeline , "sfdsd")
        
        last_step_name , last_step_model = curr_pipeline.steps[-1]
        # if is classifier 
        if sklearn.base.is_classifier(last_step_model):
            return self.classifier_accuracy_plot(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value)
        elif sklearn.base.is_regressor(last_step_model):
            return self.regressor_accuracy_plot(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value)
        else:
            raise ValueError("The last step must be a regressor or a classifier ")

        
    def plot_figure_canvas(self, fig , page):
        """Small helper function to plot the output from matplotlib into GTK. 

        Args:
            fig (Figure): The matplotlib figure output
            page (Gtk.Page): The pointer to the notebook page we want to plot to.
        """
        for child in page:
            page.remove(child)
        page.append(FigureCanvas(fig))  # a Gtk.DrawingArea
        print("Done plotting ")

    def validate_column_inputs(self, main_dataframe, pipeline_x_values , pipeline_y_value):
        lst_cols = main_dataframe.columns
        for x_col in pipeline_x_values:
            if x_col not in lst_cols:
                raise ValueError(f"Error: {x_col} is not in the dataset")
        for y_col in pipeline_y_value:
            if y_col not in lst_cols:
                raise ValueError(f"Error: {y_col} is not in the dataset")

    def train_model(self , main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value):
        """
        Trains the model using the main dataframe and pipeline_x_values. This is also
        where we will see what type of test train split the user has implemented into 
        their pipeline.

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            curr_pipeline (sklearn.pipeline): sklearn_pipeline object
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_
        """
        # parse and get the untrained pipeline
        self.curr_pipeline = curr_pipeline

        # get the x and y values 
        self.x_cols = pipeline_x_values
        self.y_cols = pipeline_y_value
        self.validate_column_inputs(main_dataframe , pipeline_x_values , pipeline_y_value)
        self.x = main_dataframe[self.x_cols]
        self.y = main_dataframe[self.y_cols].iloc[:, 0]
        
        # later here we will get and fit the training validation thing the user wants. 
        self.curr_pipeline.fit(self.x , self.y)

    def get_color_map(self):
        return plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    def get_clf_color_map(self):
        return matplotlib.colors.ListedColormap(self.get_color_map())

    def filter_pipeline(self):
        """
        PLOTTING ONLY 
        Filters the dataset based on the pipeline, trying to see specifically what type
        of input the user wants to get back out at them. 

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            curr_pipeline (sklearn.pipeline): sklearn_pipeline object
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_

        Raises:
            ValueError: Not a regressor or classifier

        Returns:
            Figure: the figure containing the chart to be plotted. 
        """
        y_pred = self.curr_pipeline.predict(self.x)
        last_step_name , last_step_model = self.curr_pipeline.steps[-1]
        # if is classifier 
        if sklearn.base.is_classifier(last_step_model):
            # render a classifier graph. 
            if len(self.x.columns) == 1:
                return self.plot_classifier_1d(self.x , self.y , y_pred , self.curr_pipeline , self.x_cols , self.y_cols)
            elif len(self.x.columns) == 2:
                return self.plot_classifier_2d(self.x , self.y , y_pred , self.curr_pipeline , self.x_cols , self.y_cols)
            else:
                return self.plot_classifier_n_plus(self.x , self.y , y_pred , self.curr_pipeline , self.x_cols , self.y_cols)

        elif sklearn.base.is_regressor(last_step_model):
            # render a regressor graph
            if len(self.x.columns) == 1:
                return self.plot_single_regression(self.x , self.y , y_pred , self.x_cols , self.y_cols)
            elif len(self.x.columns) == 2:
                return self.plot_2d_regressor(self.x , self.y, self.curr_pipeline, self.x_cols , self.y_cols)
            else:
                return self.plot_n_plus_regressor(self.x , self.y, self.curr_pipeline, self.x_cols , self.y_cols)
                
        else:
            raise ValueError("Ending result is neither a classifier or regressor. ")
        # making the graph / chart


    #=============================================================
    # sections of graphing
    #=============================================================

    def classifier_accuracy_plot(self, main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value):
        y_pred = curr_pipeline.predict(self.x)
        fig, ax = plt.subplots()
        textstr = (
            f"Accuracy  : {sklearn.metrics.accuracy_score(self.y, y_pred)}"
        )
        props = dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.7) # Customize box style
        ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', horizontalalignment='right', bbox=props)
        return fig

    def regressor_accuracy_plot(self, main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value):
        y_pred = curr_pipeline.predict(self.x)

        rmse = sklearn.metrics.mean_squared_error(self.y, y_pred)

        fig, ax = plt.subplots()
        ax.scatter(self.y, y_pred, alpha=0.6, color='teal', edgecolor='k', label='Predicted Points')
        ax.plot([self.y.min(), self.y.max()], [self.y.min(), self.y.max()], 'r--', lw=2, label='Ideal Fit (y = x)')
        ax.set_xlabel("Actual Values")
        ax.set_ylabel("Predicted Values")
        ax.legend()
        ax.grid(True)
        # adding other stuff
        textstr = (
            f"\nPredicted vs. Actual Values"
            f"\nRMSE                : {rmse}" + 
            f"\nExplained Variance  : {sklearn.metrics.explained_variance_score(self.y, y_pred):.2f}" + 
            f"\nr2                  : {sklearn.metrics.r2_score(self.y, y_pred):.2f}"
        )
        ax.set_title(textstr)
        print("accuracy")
        return fig
    
    def plot_n_plus_regressor(self , x , y , model ,  x_cols , y_cols):
        fig, ax = plt.subplots()

        ax.text(x=0.5 , y=0.5, s="Your plot is in the 4th dimension, the accuracy graph still works, " \
                "however, the \"plot\"graph will onl show the first three dimensions", transform=axs[0].transAxes,
                horizontalalignment='center', verticalalignment='center',)
        return fig

    def plot_2d_regressor(self , x , y , model ,  x_cols , y_cols):
        # Step 3: Create grid for plotting
        x1_range = np.linspace(x.iloc[:, 0].min(), x.iloc[:, 0].max(), 50)
        x2_range = np.linspace(x.iloc[:, 1].min(), x.iloc[:, 1].max(), 50)
        x1_grid, x2_grid = np.meshgrid(x1_range, x2_range)
        color_cycle = self.get_color_map()


        # Create a DataFrame from the grid for prediction
        grid_df = pd.DataFrame({
            x_cols[0]: x1_grid.ravel(),
            x_cols[1]: x2_grid.ravel()
        })

        # Step 4: Predict y values over the grid
        y_pred = model.predict(grid_df).reshape(x1_grid.shape)

        # Step 5: Plotting
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        # Plot surface
        ax.plot_surface(x1_grid, x2_grid, y_pred, cmap='viridis', alpha=0.7)

        # Plot actual data points
        ax.scatter(x.iloc[:, 0], x.iloc[:, 1], y, c=color_cycle[0], edgecolor='k')

        # Labels
        ax.set_xlabel(f"{x_cols[0]}")
        ax.set_ylabel(f"{x_cols[1]}")
        ax.set_zlabel(f"{y_cols[0]}")
        ax.set_title(f"3D Surface for {y_cols[0]}")
        return fig

    def plot_classifier_n_plus(self, x , y, y_pred, clf, x_cols , y_cols ):
        pass

    def plot_classifier_1d(self, x , y, y_pred, clf, x_cols , y_cols ):
        x_min, x_max = x.min() - 1, x.max() + 1
        X = x

        if X.ndim == 1:
            X = X.reshape(-1, 1)

        fig, ax = plt.subplots(figsize=(8, 4))

        # Generate test inputs
        x_min, x_max = X.min() - 1, X.max() + 1
        x_test = np.linspace(x_min, x_max, 400).reshape(-1, 1)

        if hasattr(clf, "predict_proba"):
            y_proba = clf.predict_proba(x_test)
            n_classes = y_proba.shape[1]
            for class_idx in range(n_classes):
                ax.plot(x_test, y_proba[:, class_idx],
                        label=f"P(class {class_idx})")
            ax.set_ylabel("Probability")
            ax.set_title(f"Classifier: {clf.__class__.__name__}")
        elif hasattr(clf, "decision_function"):
            decision = clf.decision_function(x_test)
            if decision.ndim == 1:  # binary classification
                ax.plot(x_test, decision, label="Decision function")
            else:  # multiclass
                for i in range(decision.shape[1]):
                    ax.plot(x_test, decision[:, i], label=f"Score class {i}")
            ax.set_ylabel("Decision score")
            ax.set_title(f"Classifier: {clf.__class__.__name__}")
        else:
            raise ValueError("Classifier must implement predict_proba or decision_function")

        # Plot training points
        for class_val in np.unique(y):
            ax.scatter(X[y == class_val], np.full_like(X[y == class_val], class_val),
                    label=f"Class {class_val}", alpha=0.6)

        return fig

    def plot_classifier_2d(self, x , y, y_pred, clf, x_cols , y_cols ):
        y_enc = sklearn.preprocessing.LabelEncoder().fit_transform(y)
        # Plot the decision boundary
        fig, ax = plt.subplots()
        n_classes = len(np.unique(y_enc))
        #cmap = self.get_clf_color_map()
        cmap = ListedColormap(self.get_clf_color_map().colors[:n_classes])
        sklearn.inspection.DecisionBoundaryDisplay.from_estimator(
            clf,
            x,
            response_method="predict",
            cmap=cmap,
            ax=ax
        )

        # Plot the data points
        ax.scatter(x.iloc[:, 0], x.iloc[:, 1], cmap=cmap,  c=y_enc, edgecolors='k')
        ax.set_title(f"Classifier for {y_cols[0]}")
        ax.set_xlabel(f"{x_cols[0]}")
        ax.set_ylabel(f"{x_cols[1]}")
        handles = []
        classes = np.unique(y_enc)
        print(self.og_mainframe[y_cols])
        for class_val in classes:
            handles.append(
                ax.plot([], [], marker='o', linestyle='', color=cmap(class_val),
                        label=f'Class {class_val}', markeredgecolor='k')
            )
        ax.legend(loc='upper left')
        return fig

    def plot_single_regression(self, x , y , y_pred , x_cols, y_cols):
        print("gooning ... x cols == 1 and regression")
        fig, ax = plt.subplots()
        color_cycle = self.get_color_map()
        ax.scatter(x , y , color=color_cycle[0], label=f"Dataset")
        ax.plot(x , y_pred ,  color=color_cycle[1] , label='AI predictions')
        ax.set_title(f"{x_cols[0]} and {y_cols[0]}")
        ax.set_xlabel(f"{x_cols[0]}")
        ax.set_ylabel(f"{y_cols[0]}")
        ax.legend(loc='upper left')
        return fig
