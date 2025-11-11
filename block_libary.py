import sys
import csv
import gi
import inspect
import sklearn_parameter
import utility
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject
import sklearn.model_selection as skms

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

class NoValidator():
    def __init__(self):
        return None

STACKING_AMOUNT = 2
class BlockLibary(Gtk.ScrolledWindow):
    """
    This is the "library" of available functions from sklearn that we can use in this package for this project. 
    """
    def __init__(self, column_names , **kargs):
        super().__init__(**kargs)

        # adding styles
        self.column_names = column_names
        add_style(self , 'block-library')
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        #
        #
        #
        drop_controller= Gtk.DropTarget.new(
            type=GObject.TYPE_NONE, actions=Gdk.DragAction.MOVE
        )
        drop_controller.set_gtypes([ModelBlock , ColumnBlock])
        drop_controller.connect("drop", self.remove_block)
        self.main_box.add_controller(drop_controller)
        #
        #
        #
        self.main_box.set_hexpand(True)
        self.main_box.set_vexpand(True)
        add_style(self.main_box , 'block-library')

        self.add_submodule(
            class_to_wrap=ColumnBlock , 
            color='green' ,
            list_of_things=self.column_names,
            name_of_section= 'Data Blocks' 
        )
        self.add_submodule(
            class_to_wrap=PreProcessingBlock, 
            color='purple' ,
            list_of_things=get_public_methods(sklearn.preprocessing),
            name_of_section= 'Data Preprocessing' 
        )
        self.add_submodule(
            class_to_wrap=ModelBlock , 
            color='green' ,
            list_of_things=get_public_methods(sklearn.linear_model),
            name_of_section= 'Linear Models' 
        )
        self.add_submodule(
            class_to_wrap=ModelBlock , 
            color='orange' ,
            list_of_things=get_public_methods(sklearn.neural_network),
            name_of_section= 'Deep Neural Networks' 
        )
        self.add_submodule(
            class_to_wrap=ModelBlock , 
            color='blue' ,
            list_of_things=get_public_methods(sklearn.tree),
            name_of_section= 'Decision Tree Models' 
        )

        self.add_submodule(
            class_to_wrap=ModelBlock , 
            color='pink' ,
            list_of_things=get_public_methods(sklearn.ensemble),
            name_of_section= 'Decision Tree Models' 
        )

        self.add_submodule(
            class_to_wrap=ValidatorBlock , 
            color='validator' ,
            list_of_things=[
                skms.KFold,
                skms.LeaveOneOut,
                skms.StratifiedKFold,
                No_Validator
            ],
            name_of_section= 'Validators' 
        )

        # save as self
        self.set_child(self.main_box)

    def add_submodule(self, class_to_wrap , color , list_of_things, name_of_section , ):
        """Adds a sklearn submodule to the class. 

        Args:
            submodule (sklearn.submodule): sklearn submodule to be parsed.
            color (str): string color that points to a css class in the css file.
        """
        #setup grid
        main_box = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)
        # for all of the models in linear_model add them
        # remove the abstract classes
        new_list_of_things = []
        for potential_class in list_of_things:
            if not inspect.isabstract(potential_class):
                new_list_of_things.append(potential_class)
        # adding the classes as model blocks
        for k in range(0 , len(new_list_of_things)):
            curr = class_to_wrap(new_list_of_things[k] , color)
            y = k // STACKING_AMOUNT
            x = k % STACKING_AMOUNT
            # apply a style that is a certain color
            main_box.attach(curr , x , y , 1 , 1)
        # add label
        label_thing = Gtk.Label(label=name_of_section)
        add_style(label_thing , 'block-label')
        self.main_box.append(label_thing)
        self.main_box.append(main_box)


    def remove_block(self, _ctrl, value, _x, _y):
        print("dropped into the library")
        print(_ctrl)
        model_holder = value.get_parent().get_parent()
        print(model_holder)
        if model_holder.get_parent().get_only_one_entry() == False:
            model_holder.get_parent().remove(model_holder)

class DraggableBlock(Gtk.Box):
    """
    Parent class that defines a draggable box, something to make drag and drop easier 
    in the future. 
    """
    def __init__(self, data_held , color, display_name , **kargs):
        super().__init__(**kargs)
        self.data_held = data_held
        self.color = color
        add_style(self, 'data-block')
        self.append(Gtk.Label(label=display_name))
        drag_controller = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
        drag_controller.connect("prepare", self.on_drag_prepare)
        drag_controller.connect("drag-begin", self.on_drag_begin)
        self.add_controller(drag_controller)
    
    def get_value(self):
        return self.data_held
    
    def get_gtk_object_from_json(json_data):
        """
        Creates an object of this class from json
        """
        raise ValueError("Not written yet. block_libary")
    
    def to_json(self):
        return {
            'type' : self.__class__.__name__,
            'data_held' : self.get_value(),
        }
    
    def copy(thing_to_be_copied):
        return DraggableBlock(
            column_name=thing_to_be_copied.data_held,
            color=thing_to_be_copied.color
        )

    def on_drag_prepare(self, _ctrl, _x, _y):
        item = Gdk.ContentProvider.new_for_value(self)
        string = Gdk.ContentProvider.new_for_value(self.data_held)
        return Gdk.ContentProvider.new_union([item, string])

    def on_drag_begin(self, ctrl, _drag):
        icon = Gtk.WidgetPaintable.new(self)
        ctrl.set_icon(icon, 0, 0)

    def on_drag_end(self, drag_source, drag, success):
        print('source: ',drag_source, ' drag:' , drag, ' success:' , success)
        # Check if the move was successful and perform cleanup.
        if success and drag.get_selected_action() == Gdk.DragAction.MOVE:
            # The widget was successfully dropped, so we can remove it from its source.
            self.source_box.remove(self.drag_widget)


class ColumnBlock(DraggableBlock):
    """
    Represents a draggable column block that can go into the x and y values section
    """
    def __init__(self, column_name , color, **kargs):
        super().__init__(
            data_held = column_name,
            color = color,  # not used.... deprecated 
            display_name = column_name, 
            **kargs
        )
    def get_gtk_object_from_json(json_data):
        print("my_json_data" , json_data)
        return ColumnBlock(
            column_name=json_data['column'],
            color='blue'
        )
    def copy(thing_to_be_copied):
        return ColumnBlock(
            column_name=thing_to_be_copied.data_held,
            color=thing_to_be_copied.color
        )
    



class ModelBlock(DraggableBlock):
    """
    This represents one draggable "block" that we can drag and drop from one section of the GUI to 
    another section of the GUI. 
    """
    def __init__(self, sklearn_model_function_call , color,  **kargs):
        super().__init__(
            data_held=sklearn_model_function_call,
            color=color,
            display_name="",
            **kargs
        )
        self.sklearn_model_function_call = sklearn_model_function_call
        
        # getting all possible input metrics for this function and default values
        # make a grid of possible ones
        self.parameters_box = Gtk.Grid()

        # also wrap this in a scrollable
        scrollable_view = Gtk.ScrolledWindow(hexpand=True)
        scrollable_view.set_min_content_height(250)
        scrollable_view.set_child(self.parameters_box)

        # loop over the possible input arguments
        
        self.process_args(sklearn_model_function_call)
        # assemble blocks
        sub_body = Gtk.Popover()
        sub_body.set_child(scrollable_view)
        scrollable_view.set_size_request(400 , 200)
        menu_button = Gtk.MenuButton(label=sklearn_model_function_call.__name__ , popover=sub_body)
        menu_button.get_style_context().add_class("block-dropdown-button")
        self.append(menu_button)

        drag_controller = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
        drag_controller.connect("prepare", self.on_drag_prepare)
        drag_controller.connect("drag-begin", self.on_drag_begin)
        self.add_controller(drag_controller)
        add_style(self , f"block-{color}")
        self.block_color = color

    def get_value(self):
        return self.sklearn_model_function_call.__name__
    
    def process_args(self , sklearn_model_function_call ):
        """This here defines each specific "parameter_name" to "entry"
            mapping in the block. 
        Args:
            sklearn_model_function_call (_type_): _description_
        """
        possible_args = inspect.signature(sklearn_model_function_call).parameters.items()
        print(possible_args)
        x = 0
        self.parameter_list = []
        for param_name, param in possible_args:
            # curr_label = Gtk.Label(label=param_name)
            # curr_entry = Gtk.Entry()
            # curr_entry.set_text(str(param.default))
            curr = sklearn_parameter.SklearnParameterFactory.get(
                param,
                param_name,
                sklearn_model_function_call
            )
            # add the box to list for later use
            self.parameter_list.append(curr)
            self.parameters_box.attach(curr.get_left_side() , 0 , x , 1, 1)
            self.parameters_box.attach(curr.get_right_side() , 1 , x , 1, 1)
            x += 1
        self.x = x
    
    
    def get_gtk_object_from_json(json_data):
        """
        inherited ... makes a gtk object from the json serialization 
        """
        print(json_data)
        # 1. Make a new ModelBlock.
            # The labels should be auto initialized...
        print(globals())
        new_model_block = ModelBlock(
            # below uses eval.
                # NOTE: security vulnerability .. eval used
                # using eval to get this as a class. 
            sklearn_model_function_call=eval(json_data['sklearn_model']),
            color= json_data['color'],# should be fixed later ... this needs to be passed
        )
        print(new_model_block)
        # 2. Loop thru and fill in the values from json
        for child in new_model_block.parameters_box:
            new_model_block.parameters_box.remove(child)
        x = 0
        new_model_block.parameter_list = []
        for param_name, param in json_data['model_parameters'].items():
            # curr_label = Gtk.Label(label=param_name)
            # curr_entry = Gtk.Entry()
            # curr_entry.set_text(str(param.default))
            # NOTE: param needs to have of the <class 'inspect.Parameter'> class
            param_as_inspect_param = inspect.Parameter(
                name=param_name,
                default=param,
                annotation=inspect.Parameter.empty,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD
            )
            curr = sklearn_parameter.SklearnParameterFactory.get(
                param_as_inspect_param,
                param_name,
                new_model_block.sklearn_model_function_call
            )
            # add the box to list for later use
            new_model_block.parameter_list.append(curr)
            new_model_block.parameters_box.attach(curr.get_left_side() , 0 , x , 1, 1)
            new_model_block.parameters_box.attach(curr.get_right_side() , 1 , x , 1, 1)
            x += 1
        new_model_block.x = x
    
        return new_model_block



    def copy(thing_to_be_copied):
        return ModelBlock(
            thing_to_be_copied.sklearn_model_function_call,
            color=thing_to_be_copied.block_color
        )

class PreProcessingBlock(ModelBlock):
       def __init__(self, sklearn_model_function_call , color,  **kargs):
        super().__init__(
            sklearn_model_function_call=sklearn_model_function_call,
            color=color,
            **kargs
        )
        def get_gtk_object_from_json(json_data):
            super().get_gtk_object_from_json(json_data)

class ValidatorBlock(ModelBlock):
    def __init__(self, sklearn_model_function_call , color,  **kargs):
        super().__init__(
            sklearn_model_function_call=sklearn_model_function_call,
            color=color,
            **kargs
        )