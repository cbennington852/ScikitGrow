import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject

import sklearn

def add_style(gui_thing , class_name):
    gui_thing.get_style_context().add_class(class_name)

def get_public_methods(library):
    """
    returns the methods for that library that are all models. 
    """
    res = []
    for function in dir(library):
        if function[0] != '_' and function[0].isupper():
            res.append(getattr(library , function))
    return res


def add_sklearn_submodule(passed_box, submodule , color):
    #setup grid
    main_box = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
    main_box.set_hexpand(True)
    main_box.set_vexpand(True)
    # for all of the models in linear_model add them
    linear_model_list = get_public_methods(submodule)
    for k in range(0 , len(linear_model_list)):
        curr = ModelBlock(linear_model_list[k] , color)
        y = k // STACKING_AMOUNT
        x = k % STACKING_AMOUNT
        # apply a style that is a certain color
        main_box.attach(curr , x , y , 1 , 1)
    # add label
    label_thing = Gtk.Label(label=submodule.__name__)
    add_style(label_thing , 'block-label')
    passed_box.append(label_thing)
    passed_box.append(main_box)


STACKING_AMOUNT = 3
class BlockLibary(Gtk.ScrolledWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs)

        # adding styles
        add_style(self , 'block-library')
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)
        add_style(main_box , 'block-library')

        # adding linear libary
        add_sklearn_submodule(main_box , sklearn.linear_model , 'green')
        add_sklearn_submodule(main_box , sklearn.ensemble , 'purple')
        add_sklearn_submodule(main_box , sklearn.neural_network , 'orange')
        add_sklearn_submodule(main_box , sklearn.tree , 'blue')


        # save as self
        self.main_box = main_box
        self.set_child(main_box)
   

class ModelBlock(Gtk.Box):
    def __init__(self, sklearn_model_function_call , color,  **kargs):
        super().__init__(**kargs)
        self.sklearn_model_function_call = sklearn_model_function_call
        self.append(Gtk.Label(label=sklearn_model_function_call.__name__))
        drag_controller = Gtk.DragSource()
        drag_controller.connect("prepare", self.on_drag_prepare)
        drag_controller.connect("drag-begin", self.on_drag_begin)
        self.add_controller(drag_controller)
        add_style(self , f"block-{color}")
        self.block_color = color


    def on_drag_prepare(self, _ctrl, _x, _y):
        item = Gdk.ContentProvider.new_for_value(self)
        string = Gdk.ContentProvider.new_for_value(self.sklearn_model_function_call)
        return Gdk.ContentProvider.new_union([item, string])

    def on_drag_begin(self, ctrl, _drag):
        icon = Gtk.WidgetPaintable.new(self)
        ctrl.set_icon(icon, 0, 0)




       
