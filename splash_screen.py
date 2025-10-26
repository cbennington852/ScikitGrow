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
import pickle
import joblib
from TopMenu import TopMenuButton

class SplashScreen():
    css_file_path = "./splash.css"
    splash_screen_text = """Welcome to SciKit Grow!\nThis is still a work in progress, so some features will not work as intended. Import dataset works on the following datatypes : .csv .json .parquet .xls .xlsx .xlsm .xlsb"""
    """
        Code to render a splash screen before they open up a actual application. 
    """
    def render_splash_screen(self, parent_application):
        window = Gtk.ApplicationWindow(application=parent_application)
        self.parent = parent_application
        window.set_title("Dataframe")
        window.set_default_size(1000, 800)
        main_panel = Gtk.Grid(
            hexpand=True,
            vexpand=True
        )
        self.add_style(main_panel , "mainpanel")
        
        text_buffer = Gtk.TextBuffer.new()
        text_buffer.set_text("This is some initial text in the Gtk.TextView.\n"
                                  "You can edit this text.\n"
                                  "It supports multiple lines and text wrapping.")

        # Create a Gtk.TextView and associate it with the buffer
        text_view = Gtk.TextView.new_with_buffer(text_buffer)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD) 



        # To clarify this is a new project from an already dataset. 
        example_project_btn = Gtk.Button(
            label="new project",
            hexpand=True,
            vexpand=True
        )
        self.add_style(example_project_btn , 'buttons')
        icon_path = SplashScreen.get_resource_path("Example_dataset.svg") 
        image = Gtk.Image.new_from_file(icon_path)
        example_project_btn.set_child(image)
        
        # loads an example dataset into existence.
        # Likely from pandas 
        import_project_btn = Gtk.Button(
            label="Project from example",
            hexpand=True,
            vexpand=True
        )
        icon_path = SplashScreen.get_resource_path("Import_data.svg") 
        image = Gtk.Image.new_from_file(icon_path)
        import_project_btn.set_child(image)
        self.add_style(import_project_btn , 'buttons')
        import_project_btn.connect("clicked" , lambda x: self.open_file_dialog(window))


        main_panel.attach(
            Gtk.Label(
                label=SplashScreen.splash_screen_text,
                wrap=True
            ),
            column=0,
            row=0,
            width=2,
            height=1,
        )
        main_panel.attach(example_project_btn, column=0, row=1 , width=1, height=1)
        main_panel.attach(import_project_btn, column=1, row=1 ,width=1, height=1)

        # setting the child panel
        self.load_css_file()
        window.set_child(main_panel)
        window.show()

    def on_open_response(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                print(f"Selected file: {file.get_path()}")
                # now we want to run the main thingy
                self.parent.create_window(file.get_path())

        except GLib.Error as e:
            print(f"Error opening file: {e.message}")


    def open_file_dialog(self, parent_window):
        dialog = Gtk.FileDialog.new()
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