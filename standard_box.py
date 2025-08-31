
import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject

def add_style(gui_thing , class_name):
    gui_thing.get_style_context().add_class(class_name)

class StdBox(Gtk.Box):
    def __init__(self, header_box , body_box, **kargs):
        super().__init__(**kargs)
        # make the main frame
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        add_style(main_box , 'frame')

        # make top control buttons
        add_style(header_box , 'header-box')
        for child in header_box:
            add_style(child, 'header-button')
        main_box.append(header_box)

        main_box.append(header_box)
        main_box.append(body_box)
        self.append(main_box)



    
