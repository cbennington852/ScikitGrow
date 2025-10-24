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
from main import Main_GUI

class SplashScreen():
    """
        Code to render a splash screen before they open up a actual application. 
    """
    def render_splash_screen(parent_application):
        window = Gtk.ApplicationWindow(application=parent_application)
        window.set_title("Dataframe")
        window.set_default_size(400, 300)
        main_panel = Gtk.Box()

        

        # setting the child panel
        window.set_child(main_panel)
        window.show()