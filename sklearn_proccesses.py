import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject


import matplotlib

matplotlib.use("GTK4Agg")  # Or 'GTK3Agg' for GTK3
import matplotlib.pyplot as plt

from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure
import sklearn
import pandas as pd
import numpy as np


class SklearnPlotter(Gtk.Box):
    def __init__(self , **kargs):
        super().__init__(**kargs)

    def main_sklearn_pipe(self , main_dataframe,  curr_pipeline , pipeline_x_values  , pipeline_y_value):
        try:
            self.train_model(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value)
            figure = self.filter_pipeline()
            print(figure)
            self.plot_figure_canvas(figure)
        except Exception as e:
            msg = str(e)
            if len(msg) > 80:
                msg = msg[:80]
            dialog = Gtk.AlertDialog()
            dialog.set_message(f"{type(e).__name__}")
            dialog.set_detail(msg)
            dialog.set_modal(True)
            dialog.set_buttons(["OK"])
            dialog.show()
        
        
        
    def plot_figure_canvas(self, fig):
        for child in self:
            child.get_parent().remove(child)
        self.append(FigureCanvas(fig))  # a Gtk.DrawingArea
        self.set_size_request(600, 600)
        print("Done plotting ")

    def train_model(self , main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value):
        """
            trains the model
        """
        # parse and get the untrained pipeline
        self.curr_pipeline = curr_pipeline

        # get the x and y values 
        self.x_cols = pipeline_x_values
        self.y_cols = pipeline_y_value
        print(self.x_cols)
        print(self.y_cols)
        self.x = main_dataframe[self.x_cols]
        self.y = main_dataframe[self.y_cols].iloc[:, 0]
        
        # if it is a one - one we should refect that in x-y valyes
        self.curr_pipeline.fit(self.x , self.y)

    def filter_pipeline(self):
        y_pred = self.curr_pipeline.predict(self.x)
        last_step_name , last_step_model = self.curr_pipeline.steps[-1]
        # if is classifier 
        if sklearn.base.is_classifier(last_step_model):
            # render a classifier graph. 
            return self.plot_classifier(self.x , self.y , y_pred , self.curr_pipeline , self.x_cols , self.y_cols)
        elif sklearn.base.is_regressor(last_step_model):
            # render a regressor graph
            if len(self.x.columns) == 1:
                return self.plot_single_regression(self.x , self.y , y_pred , self.x_cols , self.y_cols)
            elif len(self.x.columns) == 2:
                return self.plot_2d_regressor(self.x , self.y, self.curr_pipeline, self.x_cols , self.y_cols)
        
        else:
            raise ValueError("Ending result is neither a classifier or regressor. ")
        # making the graph / chart


    #=============================================================
    # sections of graphing
    #=============================================================

    def plot_2d_regressor(self , x , y , model ,  x_cols , y_cols):
        # Step 3: Create grid for plotting
        x1_range = np.linspace(x.iloc[:, 0].min(), x.iloc[:, 0].max(), 50)
        x2_range = np.linspace(x.iloc[:, 1].min(), x.iloc[:, 1].max(), 50)
        x1_grid, x2_grid = np.meshgrid(x1_range, x2_range)

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
        ax.scatter(x.iloc[:, 0], x.iloc[:, 1], y, c='red', edgecolor='k')

        # Labels
        ax.set_xlabel(f"{x_cols[0]}")
        ax.set_ylabel(f"{x_cols[1]}")
        ax.set_zlabel(f"{y_cols[0]}")
        ax.set_title(f"3D Surface for {y_cols[0]}")
        return fig


    def plot_classifier(self, x , y, y_pred, clf, x_cols , y_cols ):
        # Plot the decision boundary
        fig, ax = plt.subplots()
        sklearn.inspection.DecisionBoundaryDisplay.from_estimator(
            clf,
            x,
            cmap=plt.cm.coolwarm,
            alpha=0.6,
            ax=ax
        )

        # Plot the data points
        ax.scatter(x.iloc[:, 0], x.iloc[:, 1], c=y, cmap=plt.cm.coolwarm, edgecolors='k')
        ax.set_title(f"Classifier for {y_cols[0]}")
        ax.set_xlabel(f"{x_cols[0]}")
        ax.set_ylabel(f"{x_cols[1]}")
        ax.legend(loc='upper left')
        return fig

    def plot_single_regression(self, x , y , y_pred , x_cols, y_cols):
        print("gooning ... x cols == 1 and regression")
        fig, ax = plt.subplots()
        ax.scatter(x , y , color='red' , label=f"Dataset")
        ax.plot(x , y_pred , color='blue' , label='AI predictions')
        ax.set_title(f"{x_cols[0]} and {y_cols[0]}")
        ax.set_xlabel(f"{x_cols[0]}")
        ax.set_ylabel(f"{y_cols[0]}")
        ax.legend(loc='upper left')
        return fig
