import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject

def add_style( gui_thing , class_name):
        gui_thing.get_style_context().add_class(class_name)

class TopMenuButton(Gtk.MenuButton ):
    def __init__(self, label ,  **kargs):
        super().__init__(
            **kargs
        )
        add_style(self , 'toolbar-top')
        self.set_label(label=label)

        # Create a popover to act as a menu
        self.popover = Gtk.Popover()
        self.set_popover(self.popover)

        self.menu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        add_style(self.menu_box , 'toolbar-top')
        self.popover.set_child(self.menu_box)
    
    def add_function(self, label_name, function):
        btn_quit = Gtk.Button(label=label_name)
        add_style(btn_quit , 'top-bar-button')
        btn_quit.connect("clicked", function)
        self.menu_box.append(btn_quit)

