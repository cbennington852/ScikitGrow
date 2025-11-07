import json
import sys
import csv
import traceback
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject


import standard_box
import sklearn_proccesses
import block_libary
import os
import pipeline
import pandas as pd
import numpy as np
import sys
import sklearn
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib as mpl
from gi.repository import Gtk, GdkPixbuf
import pickle
import seaborn as sns
import joblib
from TopMenu import TopMenuButton

class SplashScreen():
    css_file_path = "./splash.css"
    splash_screen_text = """Welcome to SciKit Grow!\nThis is still a work in progress, so some features will not work as intended. Import dataset works on the following datatypes : .csv .json .parquet .xls .xlsx .xlsm .xlsb"""
    """
        Code to render a splash screen before they open up a actual application. 
    """
    def render_splash_screen(self, parent_application):
        self.window = Gtk.ApplicationWindow(application=parent_application)

        display = Gdk.Display.get_default()
        theme = Gtk.IconTheme.get_for_display(display)

        # Add your resource path to the icon theme
        theme.add_resource_path("/com/charlesbennington/scikitgrow/app/icon")
        icon_path = "Mini_Logo_SciKit_Grow"
        self.window.set_icon_name(icon_path)

        # load the icon
        self.parent = parent_application
        self.window.set_title("Dataframe")
        self.window.set_default_size(1000, 800)

        # setting the child panel
        self.load_css_file()
        self.window.set_child(self.get_splash_screen_panel())
        self.window.show()

    def get_example_dataset_panel(self):
        example_panel = Gtk.FlowBox(orientation=Gtk.Orientation.VERTICAL)
        self.start_example('diamonds')
        return example_panel
    
    def start_example(self , example_name):
        example_dataset = sns.load_dataset(example_name)
        self.parent.create_window(example_dataset)
        self.window.destroy()

    def load_image_from_file(file_name):
        """
            Returns a model, might change later
        """
        icon_path = SplashScreen.get_resource_path(file_name) 
        return Gtk.Image.new_from_file(icon_path)
    
    def get_splash_screen_panel(self):
        main_panel = Gtk.Grid(
            hexpand=True,
            vexpand=True
        )
        self.add_style(main_panel , "mainpanel")
        
        # To clarify this is a new project from an already dataset. 
        example_project_btn = Gtk.Button(
            label="new project",
            hexpand=True,
            vexpand=True
        )
        self.add_style(example_project_btn , 'buttons')
        example_project_btn.connect('clicked' , lambda x: self.start_example('diamonds'))
        example_project_btn.set_child(SplashScreen.load_image_from_file("Example_dataset.svg"))
        
        # loads an example dataset into existence.
        # Likely from pandas 
        import_project_btn = Gtk.Button(
            label="Project from example",
            hexpand=True,
            vexpand=True
        )
        import_project_btn.set_child(SplashScreen.load_image_from_file("Import_data.svg"))
        self.add_style(import_project_btn , 'buttons')
        import_project_btn.connect("clicked" , lambda x: self.open_file_dialog(self.window))
        main_title_pic = Gtk.Picture.new_for_resource("/com/charlesbennington/scikitgrow/app/icon/48x48/apps/Full_logo_SciKit_Grow.svg")
        main_title_pic.set_size_request(200 , 200)

        main_panel.attach(main_title_pic , 
            column=0,
            row=0,
            width=2,
            height=1,)
        main_panel.attach(
            Gtk.Label(
                label=SplashScreen.splash_screen_text,
                wrap=True
            ),
            column=0,
            row=1,
            width=2,
            height=1,
        )
        main_panel.attach(example_project_btn, column=0, row=2 , width=1, height=1)
        main_panel.attach(import_project_btn, column=1, row=2 ,width=1, height=1)
        return main_panel

    def on_open_response(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                print(f"Selected file: {file.get_path()}")
                # now we want to run the main thingy
                self.parent.create_window(file.get_path())
                self.window.destroy()
        except GLib.Error as e:
            print(f"Error opening file: {e.message}")


    def open_file_dialog(self, parent_window):
        dialog = Gtk.FileDialog.new()
        filter = Gtk.FileFilter()
        filter.set_name("Datasets")
        filter.add_pattern("*.sckl")
        filter.add_pattern("*.csv")
        filter.add_pattern("*.parquet")
        filter.add_pattern("*.xls")
        filter.add_pattern("*.xlsx")
        filter.add_pattern("*.xlsm")
        filter.add_pattern("*.xlsb")
        filter.add_pattern("*.ods")
        filter.add_pattern("*.odt")
        dialog.set_default_filter(filter)
        dialog.set_title("Open File")
        dialog.open(parent_window, None, self.on_open_response)

    def get_resource_path(rel_path):
        dir_of_py_file = os.path.dirname(__file__)
        rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
        abs_path_to_resource = os.path.abspath(rel_path_to_resource)
        return abs_path_to_resource

    def add_style(self, gui_thing, class_name):
        gui_thing.get_style_context().add_class(class_name)

    def load_css_file(self):
        with open(SplashScreen.css_file_path) as f:
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