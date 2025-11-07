#!/usr/bin/env python

import json
import sys
import csv
import traceback
import gi
import threading

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
import matplotlib as mpl
import pickle
import joblib
from splash_screen import SplashScreen
from TopMenu import TopMenuButton


class Main_GUI(Gtk.Application):
    def __init__(self):

        RESOURCE_FILE = "resources.gresource"

        

        def load_resources():
            try:
                # Load the binary resource bundle
                resource = Gio.Resource.load(RESOURCE_FILE)
                # Register the resource globally
                Gio.resources_register(resource)
                print(f"Resources from {RESOURCE_FILE} loaded and registered.")
            except Exception as e:
                print(f"Error loading resources: {e}")
        load_resources()

        # Get your default icon theme for the display
        
        super().__init__(
            application_id="com.charlesbennington.scikitgrow",
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        
        self.css_file_path = "./styles.css"
        GLib.set_application_name("SciKitLearn GUI")

    def render_main_box_from_dataframe(self, ignore_pipeline=False):
        # left side
        self.left_box = Gtk.Paned(
            orientation=Gtk.Orientation.VERTICAL,
        )
        self.add_style(self.left_box, "back-area")
        # right side
        self.right_box = Gtk.Paned(
            orientation=Gtk.Orientation.VERTICAL,
        )
        self.add_style(self.right_box, "back-area")

        # The main box
        self.main_box = Gtk.Paned(
            orientation=Gtk.Orientation.HORIZONTAL,
        )
        self.add_style(self.main_box, "back-area")

        # chart stuff
        chart_box = self.render_graph()

        # block library stuff
        self.block_library = self.render_block_library()

        # pipeline
        self.dataframe_main_box = (
            self.render_pandas_dataframe()
        )  # self.render_pipeline()

        self.right_box.set_end_child(self.dataframe_main_box)
        self.right_box.set_start_child(chart_box)
        if ignore_pipeline == False:
            self.left_box.set_start_child(self.render_pipeline())
        self.left_box.set_end_child(self.block_library)

        # adding left and right boxes
        self.main_box.set_start_child(self.left_box)
        self.main_box.set_end_child(self.right_box)
        return self.main_box

    def create_window(self, file):
        self.main_dataframe = self.process_input_file(file)
        

        # the main window
        self.window = Gtk.ApplicationWindow(
            application=self, title=f"{self.filepath}"
        )
        icon_path = "Mini_Logo_SciKit_Grow"
        self.window.set_icon_name(icon_path)

        self.window.set_default_size(1200, 900)

        self.render_main_box_from_dataframe()

        # adding main box
        self.window.set_child(self.main_box)
        self.window.set_titlebar(self.render_top_bar())
        self.load_css_file()
        self.window.present()

    def do_activate(self):
        """
        This function is called upon the user when the user calls this app
        not on a .csv or tangential file type.
        """
        splash_screen = SplashScreen()
        splash_screen.render_splash_screen(self)

    def do_open(self, files: list[Gio.File], n_files, hint: str):
        for file in files:
            self.create_window(file.get_path())

    def create_dataframe_window(self, _):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("Dataframe")
        window.set_default_size(400, 300)
        window.set_child(self.render_pandas_dataframe())
        window.show()

    def render_pandas_dataframe(
        self,
    ):

        top_control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(300, 300)
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
            tmp = GObject.type_from_name("gchararray")
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
        self.add_style(scrolled_window, "csv-reader ")

        main_box = standard_box.StdBox(
            header_box=top_control_box, body_box=scrolled_window
        )
        return main_box

    def process_input_file(self, filepath):
        if (isinstance(filepath , pd.DataFrame)):
            self.main_dataframe = filepath
            self.pipeline_box = pipeline.SklearnPipeline(
                self.main_dataframe.columns.tolist()
            )
            self.filepath = ''
            return self.main_dataframe
        self.filepath = filepath
        excel_extensions = [".xls", ".xlsx", ".xlsm", ".xlsb", ".ods", ".odt"]
        print(filepath)
        # is a csv
        if ".sckl" in filepath:
            with open(filepath, "r") as f:
                json_data = json.load(f)
                # 1. set the current dataframe to be the new dataframe from the file_handle
                self.main_dataframe = pd.read_json(json_data["main_dataframe"])
                # below prevents it from invorectly serializing them as no-strings
                    # example: name 98 ---> serizes as int named collumn
                self.main_dataframe.columns = self.main_dataframe.columns.map(str)
                # 2. load the app context, and have the program "restore" it's state.
                current_app_context = json_data["current_app_context"]
            self.pipeline_box = pipeline.SklearnPipeline(
                self.main_dataframe.columns.tolist()
            )
            pipeline.ListDroppableHolder.load_state_from_json(current_app_context)

            return self.main_dataframe
        if ".csv" in filepath:
            self.main_dataframe = pd.read_csv(filepath)
            self.pipeline_box = pipeline.SklearnPipeline(
                self.main_dataframe.columns.tolist()
            )
            return self.main_dataframe
        # is excel
        for possible_extension in excel_extensions:
            if possible_extension in filepath:
                self.main_dataframe = pd.read_excel(filepath)
                self.pipeline_box = pipeline.SklearnPipeline(
                    self.main_dataframe.columns.tolist()
                )
                return self.main_dataframe
        # is json
        if ".json" in filepath:
            self.main_dataframe = pd.read_json(filepath)
            self.pipeline_box = pipeline.SklearnPipeline(
                self.main_dataframe.columns.tolist()
            )
            return self.main_dataframe
        if ".parquet" in filepath:
            self.main_dataframe = pd.read_parquet(filepath)
            self.pipeline_box = pipeline.SklearnPipeline(
                self.main_dataframe.columns.tolist()
            )
            return self.main_dataframe
        # filetype not supported
        print(
            """
            File Type not supported, try:
            .csv
            .json
            .parquet
            .xls
            .xlsx
            .xlsm
            .xlsb
            .ods.odt
        """
        )
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
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def add_style(self, gui_thing, class_name):
        gui_thing.get_style_context().add_class(class_name)

    def higher_order_wrapper_main_sklearn_pipeline_no_error(self, _):
        try:
            self.main_canvas.main_sklearn_pipe(
                main_dataframe=self.main_dataframe,
                curr_pipeline=self.pipeline_box.get_sklearn_pipeline(),
                pipeline_x_values=self.pipeline_box.get_x_values(),
                pipeline_y_value=self.pipeline_box.get_y_value(),
                ptr_to_button=self.control_button
            )
        except Exception as e:
            traceback.print_exc()
            msg = str(e)
            print(msg)

    def higher_order_wrapper_main_sklearn_pipeline(self, button):
        try:
            self.main_canvas.main_sklearn_pipe(
                main_dataframe=self.main_dataframe,
                curr_pipeline=self.pipeline_box.get_sklearn_pipeline(),
                pipeline_x_values=self.pipeline_box.get_x_values(),
                pipeline_y_value=self.pipeline_box.get_y_value(),
                ptr_to_button=self.control_button
            )
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
            dialog.show()

    def render_pipeline(self):

        # make top control buttons
        top_control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.control_button = Gtk.Button(label="Train Model")
        
        self.control_button.connect(
            "clicked", self.higher_order_wrapper_main_sklearn_pipeline
        )
        thing_box = Gtk.FlowBox(orientation=Gtk.Orientation.VERTICAL)
        thing_box.append(SplashScreen.load_image_from_file("green_arrow.svg"))
        thing_box.append(Gtk.Label(label="Train Model"))
        self.control_button.set_child(thing_box)
        self.add_style(self.control_button, "control-button")
        top_control_box.append(self.control_button)

        # create a standard box
        main_box = standard_box.StdBox(
            header_box=top_control_box, body_box=self.pipeline_box
        )

        return main_box

    def open_button_pressed(self, button):
        splash_screen = SplashScreen()
        splash_screen.render_splash_screen(self)

    def save_as_button_pressed(self, button):
        dialog = Gtk.FileDialog(
            title="Save File"       
        )
        file_filter = Gtk.FileFilter()
        file_filter.set_name("Project File")
        dialog.set_initial_name("my_project.sckl")
        file_filter.add_pattern("*.sckl")
        dialog.set_default_filter(file_filter)
        dialog.save(self.window, None, self.on_save_as_button_pressed)

    def dump_app_data_to_json(self , path_file):
        json_current_app_context = pipeline.ListDroppableHolder.get_all_json_data()
        json_main_dataframe = self.main_dataframe.copy(deep=True).to_json(
            orient="records"
        )
        with open(path_file, "w") as f:
                json.dump(
                    {
                        "current_app_context": json_current_app_context,
                        "main_dataframe": json_main_dataframe,
                    },
                    f,
                    indent=4,
                )
        
    def save_button_pressed(self , button):
        if str(self.filepath).count(".sckl") == 1:
            self.dump_app_data_to_json(self.filepath)
        else:
            self.save_as_button_pressed(None)

    def on_save_as_button_pressed(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            if not file:
                print("Did not select a file")
                return 
            self.dump_app_data_to_json(file.get_path())
        except GLib.Error as e:
            print(f"Error opening file: {e.message}")

        

    def render_top_bar(self):
        header_bar = Gtk.HeaderBar.new()
        header_bar.set_show_title_buttons(True)

        # File Menu button
        file_menu = TopMenuButton("File")
        file_menu.add_function("Open", self.open_button_pressed)
        file_menu.add_function("Save", self.save_button_pressed)
        file_menu.add_function("Save As", self.save_as_button_pressed)

        graph_menu = TopMenuButton("Graph Settings")
        graph_menu.add_function("Graph theme", self.select_graph_theme_popup)
        graph_menu.add_function("Export Accuracy chart", self.export_accuracy_chart_to_file)
        graph_menu.add_function("Export Plot chart", self.export_chart_to_file)

        # add the dataframe viewer
        show_df_button = Gtk.Button(label="Show Dataframe")
        show_df_button.connect("clicked", self.create_dataframe_window)

        header_bar.pack_start(file_menu)
        header_bar.pack_start(graph_menu)

        return header_bar
    
    def export_chart_to_file(self , button ):
        print(self.main_canvas.current_figure_plotted)
        print(self.main_canvas.current_figure_accuracy)
        print(button)
        which_export = "accuracy"
        dialog = Gtk.FileDialog(
            title="Save File"       
        )
        file_filter = Gtk.FileFilter()
        file_filter.set_name(f"Export {which_export}")
        dialog.set_initial_name("chart.png")
        file_filter.add_pattern("*.png")
        file_filter.add_pattern("*.jpg")
        file_filter.add_pattern("*.svg")
        dialog.set_default_filter(file_filter)
        def save_image( dialog, result):
            try:
                file = dialog.save_finish(result)
                if not file:
                    print("Did not select a file")
                    return 
                self.main_canvas.current_figure_plotted.savefig(file.get_path())
            except GLib.Error as e:
                print(f"Error savinf file image: {e.message}")
        dialog.save(self.window, None, save_image)

    def export_accuracy_chart_to_file(self , button ):
        print(self.main_canvas.current_figure_plotted)
        print(self.main_canvas.current_figure_accuracy)
        print(button)
        which_export = "Plot"
        dialog = Gtk.FileDialog(
            title="Save File"       
        )
        file_filter = Gtk.FileFilter()
        file_filter.set_name(f"Export {which_export}")
        dialog.set_initial_name("chart.png")
        file_filter.add_pattern("*.png")
        file_filter.add_pattern("*.jpg")
        file_filter.add_pattern("*.svg")
        dialog.set_default_filter(file_filter)
        def save_image( dialog, result):
            try:
                file = dialog.save_finish(result)
                if not file:
                    print("Did not select a file")
                    return 
                self.main_canvas.current_figure_accuracy.savefig(file.get_path())
            except GLib.Error as e:
                print(f"Error savinf file image: {e.message}")
        dialog.save(self.window, None, save_image)

    def theme_selected(self, button, new_theme):
        mpl.rcParams.update(mpl.rcParamsDefault)
        plt.style.use(new_theme)
        try:
            self.higher_order_wrapper_main_sklearn_pipeline_no_error(None)
        except:
            print("Not ready yet ... hehe")

    def select_graph_theme_popup(self, _):
        main_box_small = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        plt.style.use("dark_background")
        print(plt.style.available)
        # make all of the radio buttons
        available_styles = plt.style.available
        # make the first radio button
        radio1 = Gtk.CheckButton(label=available_styles[0])
        radio1.connect("toggled", self.theme_selected, available_styles[0])
        main_box_small.append(radio1)
        for x in range(1, len(available_styles)):
            radio_curr = Gtk.CheckButton(label=available_styles[x])
            radio_curr.connect("toggled", self.theme_selected, available_styles[x])
            main_box_small.append(radio_curr)
            radio_curr.set_group(radio1)

        window_small = Gtk.ApplicationWindow(application=self)
        window_small.set_title("Graph ColorScheme")
        window_small.set_default_size(400, 300)
        window_small.set_child(main_box_small)
        window_small.show()

    def render_block_library(self):
        # make a search bar
        search_bar = Gtk.SearchEntry()
        search_bar.set_placeholder_text("Search for blocks...")
        self.block_library_var = block_libary.BlockLibary(self.main_dataframe.columns)
        search_bar.connect("search-changed", self.searching_block_library)

        main_box = standard_box.StdBox(
            header_box=search_bar, body_box=self.block_library_var
        )

        return main_box

    def searching_block_library(self, search_entry):
        search_entry = search_entry.get_text().lower()
        for children in self.block_library_var.main_box:
            if isinstance(children, Gtk.Label):
                if len(search_entry) < 2:
                    children.set_visible(True)
                else:
                    children.set_visible(False)
            elif isinstance(children, Gtk.Grid):
                for grid_child in children:
                    curr_func_name = grid_child.get_value().lower()
                    print(curr_func_name, search_entry, search_entry in curr_func_name)
                    if search_entry in curr_func_name:
                        grid_child.set_visible(True)
                    else:
                        grid_child.set_visible(False)

    def render_graph(self):
        self.main_canvas = sklearn_proccesses.SklearnPlotter(self)
        self.main_canvas.set_size_request(500, 500)
        return self.main_canvas


app = Main_GUI()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
