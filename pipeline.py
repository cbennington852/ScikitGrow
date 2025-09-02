import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
import block_libary
from gi.repository import GLib, Gtk, Gio, Gdk, GObject



class ModelHolder(Gtk.Box):
    def __init__(self, parent = None, **kargs):
        super().__init__(**kargs)

        self.parent = parent

        block_libary.add_style(self , 'pipeline-model-holder')

        self.box = Gtk.Box()
        self.box.append(Gtk.Label(label="drop models here!"))
        self.append(self.box)

        drop_controller = Gtk.DropTarget.new(
            type=GObject.TYPE_NONE, actions=Gdk.DragAction.COPY
        )
        drop_controller.set_gtypes([block_libary.ModelBlock])
        drop_controller.connect("drop", self.on_drop)
        self.add_controller(drop_controller)
        self.model_block = None

    def on_drop(self, _ctrl, value, _x, _y):
        if isinstance(value, block_libary.ModelBlock):
            for child in self.box:
                self.box.remove(child)
            new_block = block_libary.ModelBlock(
                sklearn_model_function_call=value.sklearn_model_function_call,
                color=value.block_color
            )
            self.box.append(new_block)
            self.parent.add_more_models(None)
            self.model_block = new_block
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
        box_data = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        block_libary.add_style(box_data , 'data-pipeline')
        # add text fields for the data section, each one being a x-value or y-value
        x_value_label = Gtk.Label(label="X-values")
        self.x_values_entry = Gtk.Entry()
        y_value_label = Gtk.Label(label='Y-values')
        self.y_values_entry = Gtk.Entry()
        # build the data section
        box_data.attach(x_value_label , 0 , 0 ,1 ,1)
        box_data.attach(self.x_values_entry, 1, 0, 1,1)
        box_data.attach(y_value_label , 0, 1,1,1)
        box_data.attach(self.y_values_entry , 1 ,1 ,1 , 1)


        #============================================
        # pipeline section box
        #============================================

        self.box_pipeline = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_pipeline.append(Gtk.Label(label="Sklearn Models"))
        # upon adding more to this section, it should add another box.
        # for now tho, let's have it be a button? 
        self.box_pipeline.append(ModelHolder(self))
        # append important stuff
        self.append(box_data)
        self.append(self.box_pipeline)


    def add_more_models(self , widget):
        self.box_pipeline.append(ModelHolder(self))

    def get_sklearn_pipeline(self , widget):
        """
        Returns the full sklearn pipeline object, using the input / stuff from the user. 
        """

        # loop thru each model and add them to the pipeline 
        print(self.box_pipeline)
        for outer_child in self.box_pipeline:
            # all of the guis
            print('outer: ',outer_child)
            if isinstance(outer_child , ModelHolder) and outer_child.model_block != None:
                # now we have all of the ModelHolder objects
                curr_block = outer_child.model_block
                print(' mid: ' , outer_child.model_block)
                print(' mid: ' , curr_block.sklearn_model_function_call)
                for k in range(0 , curr_block.x):
                    print('     label: ',curr_block.parameters_box.get_child_at(0 , k).get_text())
                    print('     value: ',curr_block.parameters_box.get_child_at(1 , k).get_text())


            # if there is data that we can't proccess, leave the option out.

        # train the pipline on the data
        print("x: " , self.x_values_entry.get_text())
        print("y: " , self.y_values_entry.get_text())
