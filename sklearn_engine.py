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


class SklearnPlotter(Gtk.Notebook):
    """A GTK notebook that contains all of the plotting info. 

        self.main_sklearn_pipe() 
        ^^^ calls the main plotting function

    Args:
        Gtk (_type_): _description_
    """
    def __init__(self , parent, **kargs):
        super().__init__(**kargs)
        # Create content for the first page
        self.parent = parent
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
        print("Before making deepcopy")
        self.og_mainframe = main_dataframe.copy(deep=True)
        print("After making deepcopy!")
        cols = pipeline_x_values + pipeline_y_value
        for col in cols:
            print(main_dataframe , main_dataframe.columns.tolist())
            print(type(col))
            # the columns are integers? or were serialized as ones.
            #  
            print("Type" , pd.api.types.is_string_dtype(main_dataframe[[str(col)]]))
            if pd.api.types.is_string_dtype(main_dataframe[col]):
                codes, uniques = pd.factorize(main_dataframe[col])
                print(codes)
                print(uniques)
                main_dataframe[col] = codes
        return main_dataframe
    
    def plot_no_model(self , main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value):
        # load x and y_values        
        self.x = main_dataframe[self.x_cols]
        self.y = main_dataframe[self.y_cols].iloc[:, 0]
        if (len(pipeline_x_values) == 1 and len(pipeline_y_value) == 1):
            # 2d scatterplot.
            fig, ax = plt.subplots()
            color_cycle = self.get_color_map()
            ax.scatter(self.x , self.y , color=color_cycle[0], label=f"Dataset")
            ax.set_title(f"{pipeline_x_values[0]} and {pipeline_y_value[0]}")
            ax.set_xlabel(f"{pipeline_x_values[0]}")
            ax.set_ylabel(f"{pipeline_y_value[0]}")
            ax.legend(loc='upper left')
            return fig
        
        elif (len(pipeline_x_values) == 2 and len(pipeline_y_value) == 1):
            x = self.x
            y = self.y
            color_cycle = self.get_color_map()
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            cmap = self.get_clf_color_map()
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

    def main_sklearn_pipe(self , main_dataframe,  curr_pipeline , pipeline_x_values  , pipeline_y_value , validator,  ptr_to_button):
        """Runs the main sklearn pipeline, filtering through the different options that
          the user could have inputted into this software. 

        Args:
            main_dataframe (pd.Dataframe): main inputted dataframe
            curr_pipeline (sklearn.pipeline): sklearn_pipeline object
            pipeline_x_values ([str]): _description_
            pipeline_y_value ([str]): _description_
        """
        print("Input valdiator" , validator)
        def thread_end_tasks():
            ptr_to_button.set_sensitive(True)
            self.spinner.stop()
            self.control_box_ptr.remove(self.spinner)
            self.control_box_ptr.append(ptr_to_button)
        # on a separate thread?
        def sklearn_alternate_thread():
            try:
                main_dataframe_copy = main_dataframe.copy(deep=True)
                main_dataframe_copy = self.factorize_string_cols(main_dataframe_copy , pipeline_x_values , pipeline_y_value)
                # parse and get the untrained pipeline
                self.curr_pipeline = curr_pipeline
                self.validator = validator

                # get the x and y values 
                self.x_cols = pipeline_x_values
                self.y_cols = pipeline_y_value
                result_validation = self.validate_column_inputs(main_dataframe_copy ,curr_pipeline, pipeline_x_values , pipeline_y_value)
                if result_validation:
                    self.plot_figure_canvas(result_validation , self.plotting_page)
                    thread_end_tasks()
                    return 
                self.x = main_dataframe_copy[self.x_cols]
                self.y = main_dataframe_copy[self.y_cols].iloc[:, 0]
                self.train_model(main_dataframe_copy , curr_pipeline , pipeline_x_values , pipeline_y_value)
                figure = self.filter_pipeline()
                accuracy_plot = self.filter_accuracy_plotting(main_dataframe_copy , curr_pipeline , pipeline_x_values , pipeline_y_value)
                self.current_figure_plotted = figure
                self.current_figure_accuracy = accuracy_plot
                self.plot_figure_canvas(figure , self.plotting_page)
                self.plot_figure_canvas(accuracy_plot , self.accuracy_page)
            except Exception as e:
                traceback.print_exc()
                msg = str(e)
                if len(msg) > 80:
                    msg = msg[:80]
                
                dialog = Gtk.AlertDialog()
                dialog.set_message(f"{type(e).__name__}")
                dialog.set_detail(msg)
                dialog.set_modal(True)
                dialog.set_buttons(["OK"])
                GLib.idle_add(dialog.show)
            thread_end_tasks()

        self.control_box_ptr = ptr_to_button.get_parent()
        self.spinner = Gtk.Spinner()
        utility.add_style(self.spinner , 'spinner')
        self.spinner.start()
        self.control_box_ptr.append(self.spinner)
        ptr_to_button.set_sensitive(False)
        sklearn_thread_1 = threading.Thread(target=sklearn_alternate_thread)
        sklearn_thread_1.start()

        # plotting stuff...
        


       
        
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
            raise ValueError("Unexpected error ... Last model not regressor or classifier")
        
    def add_style( gui_thing, class_name):
        gui_thing.get_style_context().add_class(class_name)
        
    def plot_figure_canvas(self, fig , page):
        """Small helper function to plot the output from matplotlib into GTK. 

        Args:
            fig (Figure): The matplotlib figure output
            page (Gtk.Page): The pointer to the notebook page we want to plot to.
        """
        # remove prior plotting
        for child in page:
            page.remove(child)

        

        # creating overlay with the full screen button
        overlay = Gtk.Overlay()
        overlay.set_child(FigureCanvas(fig))
        full_screen_button = Gtk.Button()
        icon_path = utility.get_resource_path("full_screen.svg") 
        image = Gtk.Image.new_from_file(icon_path)
        SklearnPlotter.add_style(image , 'full_screen_button_image')
        full_screen_button.set_child(image)
        full_screen_button.set_size_request(30 , 30)
        SklearnPlotter.add_style(full_screen_button , 'trans_button')
        full_screen_button.set_halign(Gtk.Align.END)
        full_screen_button.set_valign(Gtk.Align.START)
        full_screen_button.set_margin_bottom(10)
        full_screen_button.connect("clicked" , lambda x : self.create_window(fig))
        overlay.add_overlay(full_screen_button)
        page.append(overlay)  # a Gtk.DrawingArea
        print("Done plotting ")

    
    
    # helper to start a full screen thing
    def create_window(self , fig):
        new_fig = copy.deepcopy(fig)
        new_window = Gtk.ApplicationWindow(application=self.parent)
        new_window.set_title("")
        new_window.set_default_size(1500, 1000)
        new_window.set_child(FigureCanvas(new_fig))
        new_window.show()


    def validate_column_inputs(self, main_dataframe, curr_pipeline, pipeline_x_values , pipeline_y_value):
        lst_cols = main_dataframe.columns
        # If model empty do empty plot
        if len(self.curr_pipeline.steps) == 0:
            return self.plot_no_model(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value)

        # If user added a pre-processor but not a model do an empty plot.
        last_step_name , last_step_model = self.curr_pipeline.steps[-1]
        if not (sklearn.base.is_classifier(last_step_model) or sklearn.base.is_regressor(last_step_model)):
            return self.plot_no_model(main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value)
        # if user has an duplicate column
        if len(set(pipeline_x_values)) < len(pipeline_x_values):
            pipeline_x_values = list(set(pipeline_x_values))
            self.x_cols = pipeline_x_values

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

        Returns: 
            Tuple(trained_model)
        """
        # later here we will get and fit the training validation thing the user wants. 
        print("X vals" , self.x)
        print("Y Vals" , self.y)
        print("Validator ...." , self.validator)
        self.curr_pipeline.fit(self.x , self.y)
        if (self.validator != []) and (not isinstance(self.validator[0][1] , block_libary.NoValidator)):
            self.y_preds = SklearnPlotter.k_fold_general_threads(
                model=self.curr_pipeline,
                kf=self.validator[0][1],
                X=self.x,
                y=self.y
            )
        else:
            self.curr_pipeline.fit(self.x , self.y)
            self.y_preds = self.curr_pipeline.predict(self.x)

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
        last_step_name , last_step_model = self.curr_pipeline.steps[-1]
        # if is classifier 
        if sklearn.base.is_classifier(last_step_model):
            # render a classifier graph. 
            if len(self.x.columns) == 1:
                return self.plot_classifier_1d(self.x , self.y , self.y_preds , self.curr_pipeline , self.x_cols , self.y_cols)
            elif len(self.x.columns) == 2:
                return self.plot_classifier_2d(self.x , self.y , self.y_preds , self.curr_pipeline , self.x_cols , self.y_cols)
            else:
                return self.plot_classifier_n_plus(self.x , self.y , self.y_preds , self.curr_pipeline , self.x_cols , self.y_cols)

        elif sklearn.base.is_regressor(last_step_model):
            # render a regressor graph
            if len(self.x.columns) == 1:
                return self.plot_single_regression(self.x , self.y , self.y_preds , self.x_cols , self.y_cols)
            elif len(self.x.columns) == 2:
                return self.plot_3d_regressor(self.x , self.y, self.curr_pipeline, self.x_cols , self.y_cols)
            else:
                return self.plot_n_plus_regressor(self.x , self.y, self.curr_pipeline, self.x_cols , self.y_cols)
                
        else:
            raise ValueError("Ending result is neither a classifier or regressor. ")
        # making the graph / chart


    #=============================================================
    # sections of graphing
    #=============================================================

    def classifier_accuracy_plot(self, main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value):
        fig, ax = plt.subplots()
        accuracy = sklearn.metrics.accuracy_score(self.y, self.y_preds)
        ax.bar(['Accuracy'], [accuracy], color='skyblue')

        # Add text label and formatting
        ax.set_ylim(0, 1)
        ax.set_ylabel('Accuracy')
        ax.set_title('Model Accuracy')
        ax.text(0, accuracy / 2, f"{accuracy:.2%}", ha='center', va='center', fontsize=12, color='black')

        # Return the figure
        return fig

    def regressor_accuracy_plot(self, main_dataframe , curr_pipeline , pipeline_x_values , pipeline_y_value):

        rmse = sklearn.metrics.mean_squared_error(self.y, self.y_preds)

        fig, ax = plt.subplots()
        ax.scatter(self.y, self.y_preds, alpha=0.6, color='teal', edgecolor='k', label='Predicted Points')
        ax.plot([self.y.min(), self.y.max()], [self.y.min(), self.y.max()], 'r--', lw=2, label='Ideal Fit (y = x)')
        ax.set_xlabel("Actual Values")
        ax.set_ylabel("Predicted Values")
        ax.legend()
        ax.grid(True)
        # adding other stuff
        textstr = (
            f"\nPredicted vs. Actual Values"
            f"\nRMSE                : {rmse}" + 
            f"\nExplained Variance  : {sklearn.metrics.explained_variance_score(self.y, self.y_preds):.2f}" + 
            f"\nr2                  : {sklearn.metrics.r2_score(self.y, self.y_preds):.2f}"
        )
        ax.set_title(textstr)
        print("accuracy")
        return fig
    
    def plot_n_plus_regressor(self , x , y , model ,  x_cols , y_cols):
        fig, ax = plt.subplots()

        ax.text(x=0.5 , y=0.5, s="Your plot is in the 4th dimension, the accuracy graph still works, " \
                "however, the \"plot\"graph will onl show the first three dimensions", transform=ax[0].transAxes,
                horizontalalignment='center', verticalalignment='center',)
        return fig

    def plot_3d_regressor(self , x , y , model ,  x_cols , y_cols):
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

        # Step 4: Predict y values over the grid
        y_pred = y_pred.reshape(x1_grid.shape)

        # Step 5: Plotting
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plot surface
        cmap = self.get_clf_color_map()
        ax.plot_surface(x1_grid, x2_grid, y_pred,  alpha=0.7)

        # Plot actual data points
        ax.scatter(x.iloc[:, 0], x.iloc[:, 1], y, c=color_cycle[1], edgecolor='k')

        # Labels
        ax.set_xlabel(f"{x_cols[0]}")
        ax.set_ylabel(f"{x_cols[1]}")
        ax.set_position([0.05, 0.05, 0.9, 0.9]) 
        ax.set_zlabel(f"{y_cols[0]}")
        ax.set_title(f"3D Surface for {y_cols[0]}")
        return fig

    def plot_classifier_n_plus(self, x , y, y_pred, clf, x_cols , y_cols ):
        pass

    def plot_classifier_1d(self, X , y, y_pred, clf, x_cols , y_cols ):
        max_margin = 0.5
        x_min, x_max = X.min() - max_margin, X.max() + max_margin
        y_enc = sklearn.preprocessing.LabelEncoder().fit_transform(y)
        x_plot = np.linspace(x_min, x_max, 1000).reshape(-1, 1)
        y_preds = clf.predict(x_plot)
        fig, ax = plt.subplots()
        n_classes = len(np.unique(y_enc))
        cmap = ListedColormap(self.get_clf_color_map().colors[:n_classes])
        ax.scatter(X, y, c=y_enc, cmap=cmap,
                    edgecolor='k', marker='o', s=50, label=f'')

        # Plot the hard predicted class line (The step function)
        ax.plot(x_plot[:, 0], y_preds, label='Hard Predicted Class (0 or 1)',
                color='blue', linewidth=3)

        switch_index = np.argmax(y_preds)
        decision_boundary_x = x_plot[switch_index, 0]

        ax.axvline(x=decision_boundary_x, color='red', linestyle='--',
                    label=f'Decision Boundary (x={decision_boundary_x:.2f})')

        # Set labels and title
        classes = np.unique(self.og_mainframe[y_cols])
        classes_color_encoding = np.unique(y_enc)
        ax.set_title(f'Classifier for {y_cols[0]}')
        ax.set_xlabel(f'{x_cols[0]}')
        ax.set_ylabel(f'{y_cols[0]}')
        ax.legend(loc='upper left')
        ax.grid(True, axis='x', linestyle='--', alpha=0.6)
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
        classes = np.unique(self.og_mainframe[y_cols])
        classes_color_encoding = np.unique(y_enc)
        print(self.og_mainframe[y_cols])
        for x in range(0 , len(classes)):
            class_val = classes_color_encoding[x]
            handles.append(
                ax.plot([], [], marker='o', linestyle='', color=cmap(class_val),
                        label=f'Class {classes[x]}', markeredgecolor='k')
            )
        ax.legend(loc='upper left')
        return fig

    def plot_single_regression(self, x , y , y_pred , x_cols, y_cols):
        fig, ax = plt.subplots()
        color_cycle = self.get_color_map()
        ax.scatter(x , y , color=color_cycle[0], label=f"Dataset")
        ax.plot(x , y_pred ,  color=color_cycle[1] , label='AI predictions')
        ax.set_title(f"{x_cols[0]} and {y_cols[0]}")
        ax.set_xlabel(f"{x_cols[0]}")
        ax.set_ylabel(f"{y_cols[0]}")
        ax.legend(loc='upper left')
        return fig
