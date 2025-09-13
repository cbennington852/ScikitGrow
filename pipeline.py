import sys
import csv
import traceback
import gi

gi.require_version("Gtk", "4.0")
import block_libary
from gi.repository import GLib, Gtk, Gio, Gdk, GObject
import sklearn




class DroppableHolder(Gtk.Box ):
    """A GTK object that "holds" the custom GTK model block. 

    Args:
        Gtk (_type_): _description_
    """
    def __init__(self, style, thing_to_hold,  parent = None, **kargs):
        """Make thing

        Args:
            style (str): the string containing the name of the style.
            thing_to_hold (_type_): The thing that the model holder contains. 
            parent (_type_, optional): _description_. Defaults to None.
        """
        super().__init__(**kargs)
        self.thing_to_hold = thing_to_hold
        self.parent = parent
        block_libary.add_style(self , style)
        self.box = Gtk.Box()
        self.box.append(Gtk.Label(label=f"drop {thing_to_hold.__name__} here!"))
        self.append(self.box)

        drop_controller = Gtk.DropTarget.new(
            type=GObject.TYPE_NONE, actions=Gdk.DragAction.MOVE
        )
        drop_controller.set_gtypes([thing_to_hold])
        drop_controller.connect("drop", self.on_drop)
        self.add_controller(drop_controller)
        self.model_block = None

    def get_thing(self):
        return self.model_block

    def contains_draggable(self):
        return self.model_block != None

    def on_drop(self, _ctrl, value, _x, _y):
        if isinstance(value, self.thing_to_hold):
            for child in self.box:
                self.box.remove(child)
            new_block = self.thing_to_hold.copy(value) 
            # TODO: add a copy method that returns a copy of said object.
            self.box.append(new_block)
            self.model_block = new_block
            try:
                self.parent.consider_changing_num_holders(value)
            except Exception:
                print(traceback.format_exc())
                print("do nothing")
        else:
            print(f"some kinda bug? {value}")


class ListDroppableHolder(Gtk.Box):
    """A class to hold multiple droppable holders, and manage them. 
    """
    def __init__(self, style, droppable_this_holds, only_one_entry = False, **kargs):
        super().__init__(**kargs)
        first_entry = DroppableHolder(style , droppable_this_holds , self)
        self.append(first_entry)
        self.droppable_this_holds = droppable_this_holds
        self.style = style
        self.only_one_entry = only_one_entry

    def get_only_one_entry(self):
        return self.only_one_entry

    def get_all_values(self):
        res = []
        for child in self:
            print(child)
            if child.contains_draggable():
                res.append(child.get_thing().get_value())
        return res
    def get_all_gtk_objects(self):
        res = []
        for child in self:
            res.append(child.get_thing())
        return res

    def consider_changing_num_holders(self , value):
        list_model_holders = list(self)
        if self.only_one_entry :
            return
        else:
            count  = 0
            for x in range(0 , len(list_model_holders)):
                child = list_model_holders[x]
                print(child)
                if not child.contains_draggable():
                    count += 1
            if count == 0:
                self.append(DroppableHolder(self.style, self.droppable_this_holds, self ))


class SklearnPipeline(Gtk.Box):
    """Should return and actual sklearn pipeline, and if there are issues, this should return some kinda
    error message, so that error message can be checked. This could be done through a try and catch block.

    pipeline expands to allow for more draggables when one is added.

    This contains two "parts" one of which is the data section, and the other of which is the pipeline section. 

    We should also use entry completion to help user put in correct stuff! 

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
        self.x_values_entry = ListDroppableHolder(
            'data-pipeline',
            block_libary.ColumnBlock
        )
        # make a y_value, with completions
        y_value_label = Gtk.Label(label='Y-values')
        self.y_values_entry = ListDroppableHolder(
            'data-pipeline',
            block_libary.ColumnBlock,
            only_one_entry=True
        )
        # build the data section
        box_data.attach(x_value_label , 0 , 0 ,1 ,1)
        box_data.attach(self.x_values_entry, 1, 0, 1,1)
        box_data.attach(y_value_label , 0, 1,1,1)
        box_data.attach(self.y_values_entry , 1 ,1 ,1 , 1)
        

        #============================================
        # pipeline section box
        #============================================

        self.box_pipeline = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_pipeline.append(Gtk.Label(label="Pre-processing"))
        self.box_pipeline.append(Gtk.Label(label="Sklearn Models"))
        # upon adding more to this section, it should add another box.
        # for now tho, let's have it be a button? 
        self.pipeline = ListDroppableHolder(
            'data-pipeline',
            block_libary.ModelBlock,
            orientation=Gtk.Orientation.VERTICAL
        )
        self.box_pipeline.append(self.pipeline)
        # append important stuff
        self.append(Gtk.Label(label="X and Y axis"))
        self.append(box_data)
        self.append(self.box_pipeline)

    def get_x_values(self):
        return self.x_values_entry.get_all_values()
    
    def get_y_value(self):
        return self.y_values_entry.get_all_values()


    def get_sklearn_pipeline(self ):
        """
        Returns the full sklearn pipeline object, using the input / stuff from the user. 

        returns an untrained pipeline 
        """
        # create a list of the models going into the pipeline
        model_list = []
        # loop thru each model and add them to the pipeline 
        x = 0
        for outer_child in self.pipeline:
            # Get the current model if there is one here
            if outer_child.model_block != None:
                print(outer_child.model_block)
                curr_model = SklearnPipeline.parse_current_model(outer_child)
                new_entry_in_model_list = (f"{x}{curr_model.__class__.__name__}")
                model_list.append((new_entry_in_model_list , curr_model))
            x += 1
        untrained_pipeline = sklearn.pipeline.Pipeline(model_list)
        return untrained_pipeline
        

    def parse_current_model(outer_child):
        # now we have all of the DroppableHolder objects
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