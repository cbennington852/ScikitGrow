#!/usr/bin/env python

import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject


import standard_box
import sklearn_proccesses
import block_libary
import pipeline
import pandas as pd
import numpy as np
import sys
import sklearn
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt




class Main_GUI(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.example.MyGtkApplication",
            flags=Gio.ApplicationFlags.HANDLES_OPEN
        )

        self.css_file_path = "./styles.css"
        self.block_library_var = block_libary.BlockLibary()
        self.main_dataframe = pd.DataFrame()
        GLib.set_application_name("SciKitLearn GUI")

    def create_window(self, file):
        
        self.main_dataframe = self.process_input_file(file)
        self.pipeline_box = pipeline.SklearnPipeline(self.main_dataframe.columns.tolist()) 
         # the main window
        window = Gtk.ApplicationWindow(application=self, title="Sklearn GUI software")
        window.set_default_size(1200, 900)

        # left side
        left_box = Gtk.Paned(
            orientation=Gtk.Orientation.VERTICAL,
        )
        self.add_style(left_box , 'back-area')
        # right side
        right_box = Gtk.Paned(
            orientation=Gtk.Orientation.VERTICAL,
        )
        self.add_style(right_box , 'back-area')

        # The main box
        main_box = Gtk.Paned (
            orientation=Gtk.Orientation.HORIZONTAL,
        )
        self.add_style(main_box , 'back-area')

        # chart stuff
        chart_box = self.render_graph()
        right_box.set_start_child(chart_box)

        # block library stuff
        block_library = self.render_block_library()
        right_box.set_end_child(block_library)
    
        # The csv viewer
        csv_veiwer_box = self.render_csv()
        left_box.set_start_child(csv_veiwer_box )

        # pipeline 
        pipeline_main_box = self.render_pipeline()
        left_box.set_end_child(pipeline_main_box )

        # adding left and right boxes
        main_box.set_start_child(left_box)
        main_box.set_end_child(right_box)
        # adding main box
        window.set_child(main_box)
        window.set_titlebar(self.render_top_bar())
        self.load_css_file()
        window.present()

    def do_activate(self):
        print("No no veery bad")

    def do_open(self, files: list[Gio.File], n_files,  hint: str):
        for file in files:
            self.create_window(file.get_path())

    def render_csv(self):
        top_control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        control_button = Gtk.Button(label="Edit CSV")
        top_control_box.append(control_button)


        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(300,300)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)


        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        csv_viewer_box = Gtk.Box()
        # read csv
        # retrieve the pandas dataframe
        # add the top header 
        # add all of the dataframe rows.
        # may have to make a conversion map
        column_types = []
        for col in self.main_dataframe.columns:
            tmp = GObject.type_from_name('gchararray')
            print(tmp)
            column_types.append(tmp)

        liststore = Gtk.ListStore(*column_types)

        limit = 200
        for index, row in self.main_dataframe.iterrows():
            row = [str(point) for point in row] 
            liststore.append(list(row))
            limit -= 1
            if limit <= 0:
                break

         # Create a TreeView and link it to the model
        treeview = Gtk.TreeView(model=liststore)

        # Create a column for each dataframe header
        for i, col_name in enumerate(self.main_dataframe.columns):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_name, renderer, text=i)
            treeview.append_column(column)

        # Add the TreeView (not the ListStore!) to the container
        csv_viewer_box.append(treeview)
        scrolled_window.set_child(csv_viewer_box)
        self.add_style(scrolled_window , 'csv-reader ')

        main_box = standard_box.StdBox(
            header_box=top_control_box,
            body_box=scrolled_window
        )
        return main_box


    def process_input_file(self, filepath):
        excel_extensions = ['.xls','.xlsx','.xlsm','.xlsb','.ods','.odt']
        filepath = filepath
        print(filepath)
        # is a csv
        if '.csv' in filepath:
            main_dataframe = pd.read_csv(filepath)
            return main_dataframe
        # is excel
        for possible_extension in excel_extensions:
            if possible_extension in filepath:
                main_dataframe = pd.read_excel(filepath)
                return main_dataframe
        # is json
        if '.json' in filepath:
            main_dataframe = pd.read_json(filepath)
            return main_dataframe
        if '.parquet' in filepath:
            main_dataframe = pd.read_parquet(filepath)
            return main_dataframe
        # filetype not supported
        print("""
            File Type not supported, try:
            .csv
            .json
            .parquet
            .xls
            .xlsx
            .xlsm
            .xlsb
            .ods.odt
        """)
        sys.exit(1)


    def load_css_file(self):
            with open(self.css_file_path) as f:
                # Load CSS
                css = f.read()
                css_provider = Gtk.CssProvider()
                css_provider.load_from_data(css)

                # Apply CSS to display
                Gtk.StyleContext.add_provider_for_display(
                    Gdk.Display.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )


    def add_style(self, gui_thing , class_name):
        gui_thing.get_style_context().add_class(class_name)


    def train_model(self):
        """
            trains the model
        """
        # parse and get the untrained pipeline
        curr_pipeline = self.pipeline_box.get_sklearn_pipeline()

        # use pandas to load the .csv as a dataframe
        print(self.main_dataframe)

        # get the x and y values 
        x_cols = self.pipeline_box.get_x_values()
        y_cols = self.pipeline_box.get_y_value()
        x = self.main_dataframe[x_cols]
        y = self.main_dataframe[y_cols]
        print(x)
        print(y)
        
        # if it is a one - one we should refect that in x-y valyes
        print(curr_pipeline)
        curr_pipeline.fit(x , y)

        y_pred = curr_pipeline.predict(x)

        # we could have a sections for regression and Classification
        # get the last step on pipeline to see which it is 
        # maybe later we make it automatic but user can specify
        last_step_name , last_step_model = curr_pipeline.steps[-1]
        # if is classifier 
        if sklearn.base.is_classifier(last_step_model):
            # render a classifier graph. 
            print("Not there yet")
        elif sklearn.base.is_regressor(last_step_model):
            # must be regression
            # Only one x value ... horizontal scatter plot
            if len(x.columns) == 1:
                self.plot_single_regression(x , y , y_pred , x_cols , y_cols)
            else:
                print("gooning")
            
            
        else:
            raise ValueError("Ending result is neither a classifier or regressor. ")
        # making the graph / chart

    def plot_single_regression(self, x , y , y_pred , x_cols, y_cols):
        print("gooning ... x cols == 1 and regression")
        fig, ax = plt.subplots()
        ax.scatter(x , y , color='red' , label=f"Dataset")
        ax.plot(x , y_pred , color='blue' , label='AI predictions')
        ax.set_title(f"{x_cols[0]} and {y_cols[0]}")
        ax.set_xlabel(f"{x_cols[0]}")
        ax.set_ylabel(f"{y_cols[0]}")
        ax.legend(loc='upper left')

        for child in self.main_canvas:
            child.get_parent().remove(child)
        
        self.main_canvas.append(FigureCanvas(fig))  # a Gtk.DrawingArea
        self.main_canvas.set_size_request(500, 500)



    def plot_chart(self, widget):
        print("Not there yet")
        model = self.train_model()
        print(model)

    def render_pipeline(self):

        # make top control buttons
        top_control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        control_button = Gtk.Button(label="Run Sklearn! ▶️")
        control_button.connect("clicked", self.plot_chart)
        self.add_style(control_button , 'control-button')
        top_control_box.append(control_button)

        # create a standard box
        main_box = standard_box.StdBox(
            header_box=top_control_box,
            body_box=self.pipeline_box
        )

        return main_box


    def render_top_bar(self):
        header_bar = Gtk.HeaderBar.new()
        header_bar.set_show_title_buttons(True)
        return header_bar

    def render_block_library(self):
        # make a search bar
        search_bar = Gtk.SearchEntry()
        search_bar.set_placeholder_text("Search for blocks...")
        search_bar.connect("search-changed", self.searching_block_library)

        main_box = standard_box.StdBox(
            header_box=search_bar,
            body_box=self.block_library_var
        )

        return main_box

    def searching_block_library(self, search_entry):
        search_entry = search_entry.get_text().lower()
        for children in self.block_library_var.main_box:
            if isinstance(children , Gtk.Label):
                if len(search_entry) < 2:
                    children.set_visible(True)
                else:
                    children.set_visible(False)
            elif isinstance(children , Gtk.Grid):
                for grid_child in children:
                    curr_func_name = grid_child.sklearn_model_function_call.__name__.lower()
                    if search_entry in curr_func_name:
                        grid_child.set_visible(True)
                    else:
                        grid_child.set_visible(False)



    def render_graph(self):
        self.main_canvas = Gtk.Box()
        self.main_canvas.set_size_request(500, 500)
        canvas = FigureCanvas()  # a Gtk.DrawingArea
        self.main_canvas.append(canvas)
        return self.main_canvas




app = Main_GUI()
exit_status = app.run(sys.argv)
sys.exit(exit_status)