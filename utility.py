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

def add_style( gui_thing, class_name):
        gui_thing.get_style_context().add_class(class_name)

def load_css_file():
    css_file_path = "./styles.css"
    with open(css_file_path) as f:
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

def display_small_popup(parent , window_name, content, width=400 , height=300):
    window_small = Gtk.ApplicationWindow(application=parent)
    window_small.set_title(window_name)
    window_small.set_default_size(width, height)
    window_small.set_child(content)
    window_small.show()