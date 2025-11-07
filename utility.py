import os
import sys
import csv
import gi
import inspect
import sklearn_parameter
import utility
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject

import sklearn

def load_image_from_file(file_name):
        """
            Returns a model, might change later
        """
        icon_path = get_resource_path(file_name) 
        return Gtk.Image.new_from_file(icon_path)

def get_resource_path(rel_path):
    dir_of_py_file = os.path.dirname(__file__)
    rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
    abs_path_to_resource = os.path.abspath(rel_path_to_resource)
    return abs_path_to_resource