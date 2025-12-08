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
import sklearn_engine

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
    def __init__(self , parent, ptr_to_button, **kargs):
        super().__init__(**kargs)
        # Create content for the plotting page
        self.parent = parent
        self.plotting_page = Gtk.Box()
        plotting_page_label = Gtk.Label(label="Plot")
        self.append_page(self.plotting_page, plotting_page_label)

        # Create content for the accuracy page
        self.accuracy_page = Gtk.Box()
        accuracy_page_label = Gtk.Label(label="Accuracy")
        self.append_page(self.accuracy_page, accuracy_page_label)

        # Create content for the prediction page
        self.prediction_page = Gtk.Box()
        prediction_label = Gtk.Label(label="Predict")
        self.append_page(self.prediction_page, prediction_label)

        self.ptr_to_button = ptr_to_button

     # helper to start a full screen thing
    def create_window(self , fig):
        new_fig = copy.deepcopy(fig)
        new_window = Gtk.ApplicationWindow(application=self.parent)
        new_window.set_title("")
        new_window.set_default_size(1500, 1000)
        new_window.set_child(FigureCanvas(new_fig))
        new_window.show()

    def run_engine(self , main_dataframe , pipeline_x_values , pipeline_y_value , curr_pipeline , validator ):
        def internal_run_engine():
            try:
                sklearn_results = sklearn_engine.SklearnEngine.main_sklearn_pipe(
                    main_dataframe=main_dataframe,
                    pipeline_x_values=pipeline_x_values,
                    pipeline_y_value=pipeline_y_value,
                    curr_pipeline=curr_pipeline,
                    validator=validator
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
                GLib.idle_add(dialog.show)
            self.thread_end_tasks()

        self.control_box_ptr = self.ptr_to_button.get_parent()
        self.spinner = Gtk.Spinner()
        utility.add_style(self.spinner , 'spinner')
        self.spinner.start()
        self.control_box_ptr.append(self.spinner)
        self.ptr_to_button.set_sensitive(False)
        sklearn_thread_1 = threading.Thread(target=internal_run_engine)
        sklearn_thread_1.start()

        raise ValueError("Not working yet")
    
    def thread_end_tasks(self):
            self.ptr_to_button.set_sensitive(True)
            self.spinner.stop()
            self.control_box_ptr.remove(self.spinner)
            self.control_box_ptr.append(self.ptr_to_button)

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
        utility.add_style(image , 'full_screen_button_image')
        full_screen_button.set_child(image)
        full_screen_button.set_size_request(30 , 30)
        utility.add_style(full_screen_button , 'trans_button')
        full_screen_button.set_halign(Gtk.Align.END)
        full_screen_button.set_valign(Gtk.Align.START)
        full_screen_button.set_margin_bottom(10)
        full_screen_button.connect("clicked" , lambda x : self.create_window(fig))
        overlay.add_overlay(full_screen_button)
        page.append(overlay)  # a Gtk.DrawingArea
        print("Done plotting ")