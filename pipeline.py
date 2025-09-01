import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
import block_libary
from gi.repository import GLib, Gtk, Gio, Gdk, GObject




class TargetView(Gtk.Box):
    def __init__(self, **kargs):
        super().__init__(**kargs)

        self.box = Gtk.Box()
        self.box.append(Gtk.Label(label="Hello drop here!"))
        self.append(self.box)

        drop_controller = Gtk.DropTarget.new(
            type=GObject.TYPE_NONE, actions=Gdk.DragAction.COPY
        )
        drop_controller.set_gtypes([block_libary.ModelBlock])
        drop_controller.connect("drop", self.on_drop)
        self.add_controller(drop_controller)

    def on_drop(self, _ctrl, value, _x, _y):
        if isinstance(value, block_libary.ModelBlock):
            for child in self.box:
                self.box.remove(child)
            self.box.append(block_libary.ModelBlock(
                sklearn_model_function_call=value.sklearn_model_function_call,
                color=value.block_color
            ))
        else:
            print(f"some kinda bug? {value}")



class SklearnPipeline(Gtk.Box):
    """Should return and actual sklearn pipeline, and if there are issues, this should return some kinda
    error message, so that error message can be checked. This could be done through a try and catch block.

    pipeline expands to allow for more draggables when one is added.

    This contains two "parts" one of which is the data section, and the other of which is the pipeline section. 

    We should also use entry compleetion to help user put in correct stuff! 

    Args:
        Gtk (_type_): _description_
    """
    def __init__(self, **kargs):
        super().__init__(**kargs)

        self.set_orientation(Gtk.Orientation.VERTICAL)

        #============================================
        # data section box
        #============================================
        box_data = Gtk.Box()
        # add text fields for the data section, each one being a x-value or y-value
        x_value_label = Gtk.Label(label="X-values")
        self.x_values_entry = Gtk.Entry()
        y_value_label = Gtk.Label(label='Y-values')
        self.y_values_entry = Gtk.Entry()
        # build the data section
        box_data.append(x_value_label)
        box_data.append(self.x_values_entry)
        box_data.append(y_value_label)
        box_data.append(self.y_values_entry)


        #============================================
        # pipeline section box
        #============================================

        self.box_pipeline = Gtk.Box()

        # upon adding more to this section, it should add another box.
        # for now tho, let's have it be a button? 
        self.box_pipeline.append(TargetView())
        #button to add more
        button_add_more = Gtk.Button(label='+')
        button_add_more.connect('clicked' , self.add_more_models)
        
        
        # append things
        self.box_pipeline.append(button_add_more)
        

        # append important stuff
        self.append(box_data)
        self.append(self.box_pipeline)

    def add_more_models(self , widget):
        self.box_pipeline.prepend(TargetView())

