import sys
import csv
import gi
import traceback

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject

class GUIHeader(Gtk.Box):
    """The code / boiler plate for a "box" with a header of buttons. 
    This applies to every box that contains something. 

    Args:
        Gtk (_type_): _description_
    """
    def __init__(self, header_box , body_box, **kargs):
        super().__init__(**kargs)