import json
import sys
import csv
import traceback
import gi
import inspect

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
        self.box.set_halign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)

        self.box.append(Gtk.Label(label=f"  +  "))
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
    
    def json_parameters(self , curr_block):
        """Creates a json representation of the parameters than can be put into 
        this specific sklearn object. 

        Args:
            curr_block (): _description_

        Returns:
            _type_: _description_
        """
        map_of_parameters = {}
        print("type...." , type(curr_block))
        print(' model: ' , curr_block.sklearn_model_function_call)
        map_of_parameters = {}
        for curr_pair in curr_block.parameter_list:
            # looping thru out list oEf parameters.
            para_name = curr_pair.get_param_name()
            para_value = curr_pair.get_value()
            map_of_parameters[para_name] = para_value
        return map_of_parameters
    
    def to_json(self):
        print('holding thing:' , self.model_block)
        if isinstance(self.model_block , block_libary.ModelBlock) or isinstance(self.model_block , block_libary.PreProcessingBlock):
            curr_model = self.json_parameters(self.model_block)
            return {
                "sklearn_model_name" : self.model_block.sklearn_model_function_call.__name__,
                "sklearn_model": self.model_block.sklearn_model_function_call.__module__ + "." + self.model_block.sklearn_model_function_call.__name__,
                "color" : self.model_block.color,
                "model_parameters" : curr_model,
            }
        elif isinstance(self.model_block , block_libary.ColumnBlock):
            return {
                "column" : self.model_block.data_held
            }
        else:
            print("NOT SEEN CHANGE DROPPABLE HOLDER")


    def contains_draggable(self):
        return self.model_block != None

    def on_drop(self, _ctrl, value, _x, _y):
        # clear the background.
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
    _references_to_all_objects = []
    style = 'style'
    droppable_this_holds = 'droppable_this_holds'
    only_one_entry = 'only_one_entry'
    entries = 'entries'
    unique_serialization_name = 'unique_serialization_name'


    def __init__(self, unique_serialization_name , style, droppable_this_holds, only_one_entry = False, **kargs):
        super().__init__(**kargs)
        first_entry = DroppableHolder(style , droppable_this_holds , self)
        self.append(first_entry)
        self.unique_serialization_name = unique_serialization_name
        self.droppable_this_holds = droppable_this_holds
        self.style = style
        self.only_one_entry = only_one_entry
        ListDroppableHolder._references_to_all_objects.append(self)

    def get_only_one_entry(self):
        return self.only_one_entry
    
    def load_state_from_json(json_data):
        """
        A function to load the current state from json. 
        """
        # loop thru all the references in each object, if we hit a serial with 
        # it's name, we will then fill in the information. 
        for list_droppable_holder in ListDroppableHolder._references_to_all_objects:
            # find serial within the json context. 
            for json_list_droppable_holder in json_data:
                if list_droppable_holder.unique_serialization_name == json_list_droppable_holder['unique_serialization_name']:
                    print(json.dumps(json_list_droppable_holder , indent=2))
                    # we now have the specific list_droppable_holder and the json tangent.
                    # 1. Delete all children in list droppable holders.
                    for child in list_droppable_holder:
                        list_droppable_holder.remove(child)

                    # 2. Loop thru json section, and call each block_libary 
                    #    draggable, to "re-serialize" this section.
                    # 2.1 Make the block_libary object using the render_from_json()
                    entries = json_list_droppable_holder['entries']
                    for entry in entries:
                        print("New Entry" , entry)
                        print("Uniuqw" , json_list_droppable_holder['unique_serialization_name'])
                        if entry: # check to make sure not none
                            new_draggable = list_droppable_holder.droppable_this_holds.get_gtk_object_from_json(entry)
                            # make new droppable holder ... then add the new _draggable
                            new_droppable_holder = DroppableHolder(
                                style=list_droppable_holder.style,
                                thing_to_hold=list_droppable_holder.droppable_this_holds,
                                parent=list_droppable_holder
                            )
                            new_droppable_holder.model_block = new_draggable
                            new_droppable_holder.box.append(new_draggable)
                            # oh also, add a new empty droppable holder.

                            for child in new_droppable_holder.box:
                                new_droppable_holder.box.remove(child)
                            
                            list_droppable_holder.append(new_droppable_holder)
                            print("Hello from json serializer" , list_droppable_holder.droppable_this_holds)
                    empty_droppable_holder = DroppableHolder(
                                style=list_droppable_holder.style,
                                thing_to_hold=list_droppable_holder.droppable_this_holds,
                                parent=list_droppable_holder
                            )
                    if (json_list_droppable_holder['unique_serialization_name'] != 'y_values'):
                        list_droppable_holder.append(empty_droppable_holder)
                    # if y empty
                    if (json_list_droppable_holder['unique_serialization_name'] == 'y_values') and list_droppable_holder == []:
                        list_droppable_holder.append(empty_droppable_holder)

                    
                    


    def get_all_json_data():
        """Class level function to get all of the droppable holders.

        Returns:
            _type_: _description_
        """
        res = []
        for droppable_holder in ListDroppableHolder._references_to_all_objects:
            res.append(droppable_holder.to_json())
        return res

    def to_json(self):
        lst_entries = []
        for unknown in self:
            print(unknown)
            lst_entries.append(unknown.to_json())
        return {
            ListDroppableHolder.unique_serialization_name : self.unique_serialization_name,
            ListDroppableHolder.style: self.style,
            ListDroppableHolder.droppable_this_holds: self.droppable_this_holds.__name__,
            ListDroppableHolder.only_one_entry : self.only_one_entry,
            ListDroppableHolder.entries : lst_entries
        }

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
        #print("Current json serialization...")
        #print(json.dumps(ListDroppableHolder.get_all_json_data(), indent=4))
        list_model_holders = list(self)
        if self.only_one_entry :
            return
        else:
            count  = 0
            for x in range(0 , len(list_model_holders)):
                child = list_model_holders[x]
                if not child.contains_draggable():
                    count += 1
            if count == 0:
                self.append(DroppableHolder(self.style, self.droppable_this_holds, self ))


class SklearnPipeline(Gtk.ScrolledWindow):
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
        self.set_hexpand(True)
        self.set_size_request(300, 300)
        self.set_vexpand(True)
        self.main = Gtk.Box()
        self.main.set_orientation(Gtk.Orientation.VERTICAL)

        #============================================
        # data section box
        #============================================
        box_data = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        block_libary.add_style(box_data , 'data-pipeline')
        # add text fields for the data section, each one being a x-value or y-value
        x_value_label = Gtk.Label(label="X-values")
        # making a thing with autocompletion
        self.x_values_entry = ListDroppableHolder(
            unique_serialization_name='x_values',
            style='data-pipeline',
            droppable_this_holds=block_libary.ColumnBlock
        )
        # make a y_value, with completions
        y_value_label = Gtk.Label(label='Y-values')
        self.y_values_entry = ListDroppableHolder(
            unique_serialization_name='y_values',
            style='data-pipeline',
            droppable_this_holds=block_libary.ColumnBlock,
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
        self.preprocessing = ListDroppableHolder(
            unique_serialization_name='preproccessor',
            style='data-pipeline',
            droppable_this_holds=block_libary.PreProcessingBlock,
            orientation=Gtk.Orientation.VERTICAL
        )
        self.box_pipeline.append(self.preprocessing)
        self.box_pipeline.append(Gtk.Label(label="Sklearn Models"))
        # upon adding more to this section, it should add another box.
        # for now tho, let's have it be a button? 
        self.pipeline = ListDroppableHolder(
            unique_serialization_name='sklearn_model',
            style='data-pipeline',
            droppable_this_holds=block_libary.ModelBlock,
            orientation=Gtk.Orientation.VERTICAL
        )
        self.box_pipeline.append(self.pipeline)
        # append important stuff
        self.main.append(Gtk.Label(label="X and Y axis"))
        self.main.append(box_data)
        self.main.append(self.box_pipeline)
        self.set_child(self.main)

    def get_x_values(self):
        return self.x_values_entry.get_all_values()
    
    def get_y_value(self):
        return self.y_values_entry.get_all_values()


    def get_sklearn_pipeline(self):
        """
        Returns the full sklearn pipeline object, using the input / stuff from the user. 

        returns an untrained pipeline 
        """
        # create a list of the models going into the pipeline
        model_list = []
        def parse_sklearn_model_holder_list(pointer_to_list_model_holder):
            x = 0
            for outer_child in pointer_to_list_model_holder:
                # Get the current model if there is one here
                if outer_child.model_block != None:
                    print("Parameter list" , outer_child.model_block.parameter_list)
                    list_of_parameters = outer_child.model_block.parameter_list
                    map_of_parameters = {}
                    
                    # looping thru out list oEf parameters.
                    for curr_pair in list_of_parameters:
                        para_name = curr_pair.get_param_name()
                        para_value = curr_pair.get_value()
                        map_of_parameters[para_name] = para_value

                    # assembling the current model
                    new_entry_in_model_list = (f"{x}_{outer_child.model_block.__class__.__name__}_{outer_child.model_block.sklearn_model_function_call}")
                    assembled_model = outer_child.model_block.sklearn_model_function_call(**map_of_parameters)
                    model_list.append((new_entry_in_model_list , assembled_model))
                x += 1
                
        parse_sklearn_model_holder_list(self.preprocessing)
        parse_sklearn_model_holder_list(self.pipeline)

        print("UNTRAINED PIEPLEINE")
        print(model_list)
        untrained_pipeline = sklearn.pipeline.Pipeline(model_list)
        return untrained_pipeline
    

        
    """
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
    """


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