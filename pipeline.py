import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
import block_libary
from gi.repository import GLib, Gtk, Gio, Gdk, GObject
import sklearn




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
    def __init__(self, columns , **kargs):
        super().__init__(**kargs)
        self.columns = columns
        self.set_orientation(Gtk.Orientation.VERTICAL)

        #============================================
        # data section box
        #============================================
        box_data = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        block_libary.add_style(box_data , 'data-pipeline')
        # add text fields for the data section, each one being a x-value or y-value
        x_value_label = Gtk.Label(label="X-values")
        # making a thing with autocompletion
        self.x_values_entry = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL) 
        first_entry = Gtk.Entry()
        first_entry.connect('changed' , self.consider_adding_new_box)
        self.add_search_completion_thingy(first_entry)
        self.x_values_entry.append(first_entry)
        # make a y_value, with completions
        y_value_label = Gtk.Label(label='Y-values')
        self.y_values_entry = Gtk.Entry()
        self.add_search_completion_thingy(self.y_values_entry)
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

    def get_x_values(self):
        res = []
        for child in self.x_values_entry:
            if child.get_text() in self.columns:
                res.append(child.get_text())
        return res
    
    def get_y_value(self):
        return [self.y_values_entry.get_text()]


    def consider_adding_new_box(self, value):
        # Check to see if value in the set of column names
        num_empty = 0
        for child in self.x_values_entry:
            print(child , child.get_text())
            if child.get_text() == '':
                num_empty += 1
                if num_empty == 2:
                    child.get_parent().remove(child)
                    num_empty -= 1 
            # if so add a new column
        if num_empty == 0:
            first_entry = Gtk.Entry()
            first_entry.connect('changed' , self.consider_adding_new_box)
            self.add_search_completion_thingy(first_entry)
            self.x_values_entry.append(first_entry)
        # Check to see if we have two empty columns, if so delete one. 

    def add_search_completion_thingy(self, specific_entry):
        list_store = Gtk.ListStore(str)
        for item in self.columns:
            list_store.append([item])
            completion = Gtk.EntryCompletion()
        completion.set_model(list_store)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        specific_entry.set_completion(completion)

    def add_more_models(self , widget):
        self.box_pipeline.append(ModelHolder(self))

    def get_sklearn_pipeline(self ):
        """
        Returns the full sklearn pipeline object, using the input / stuff from the user. 

        returns an untrained pipeline 
        """
        # create a list of the models going into the pipeline
        model_list = []
        # loop thru each model and add them to the pipeline 
        x = 0
        for outer_child in self.box_pipeline:
            # Get the current model if there is one here
            if isinstance(outer_child , ModelHolder) and outer_child.model_block != None:
                curr_model = SklearnPipeline.parse_current_model(outer_child)
                new_entry_in_model_list = (f"{curr_model.__class__.__name__}__{x}")
                model_list.append(new_entry_in_model_list)
            x += 1
        untrained_pipeline = sklearn.pipeline.Pipeline(model_list)
        return untrained_pipeline
        

    def parse_current_model(outer_child):
        # now we have all of the ModelHolder objects
        map_of_parameters = {}
        curr_block = outer_child.model_block
        print(' mid: ' , outer_child.model_block)
        print(' model: ' , curr_block.sklearn_model_function_call)
        for k in range(0 , curr_block.x):
            parameter = curr_block.parameters_box.get_child_at(0 , k).get_text()
            para_value = SklearnPipeline.handle_parameter_input(curr_block.parameters_box.get_child_at(1 , k).get_text())
            # NOTE:
                # eval allows for arbitrary code execution, this is acceptable, because the purpose
                # of this program is to compile software gui components into real python code.
            print('     label: ', parameter)
            print('     value: ', para_value)
            print('     type : ', type(para_value))
            map_of_parameters[parameter] = para_value
        print(map_of_parameters)
        # now time to assemble this specific model. 
        assembled_model = curr_block.sklearn_model_function_call(**map_of_parameters)
        print(assembled_model)
        return assembled_model


    def handle_parameter_input(input):
        """
        # WARNING:
            eval allows for arbitrary code execution, this is acceptable, because the purpose
            of this program is to compile software gui components into real python code.
              
            * FINAL : use of eval()
                - this executes it as python code
        """
        try:
            return eval(input)
        except NameError:
            return str(input)