import sys
import csv
import gi
import inspect

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


STACKING_AMOUNT = 3
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

        # adding linear libary
        self.add_submodule(
            class_to_wrap=ColumnBlock , 
            color='green' ,
            list_of_things=self.column_names,
            name_of_section= 'Data Blocks' 
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
            color='purple' ,
            list_of_things=get_public_methods(sklearn.preprocessing),
            name_of_section= 'Data Preprocessing' 
        )
        self.add_submodule(
            class_to_wrap=ModelBlock , 
            color='blue' ,
            list_of_things=get_public_methods(sklearn.tree),
            name_of_section= 'Decision Tree Models' 
        )

        # save as self
        self.set_child(self.main_box)

    def add_submodule(self, class_to_wrap , color , list_of_things,name_of_section):
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
        linear_model_list = list_of_things
        for k in range(0 , len(linear_model_list)):
            curr = class_to_wrap(linear_model_list[k] , color)
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
            if isinstance(value, ModelBlock):
                print("dropped into the library")
                print(_ctrl)
                model_holder = value.get_parent().get_parent()
                pipeline_obj = value.get_parent().get_parent().get_parent().get_parent()
                # remove model_holder
                model_holder.get_parent().remove(model_holder)

class ColumnBlock(Gtk.Box):
    """
    Represents a draggable column block that can go into the x and y values section
    """
    def __init__(self, column_name , color, **kargs):
        super().__init__(**kargs)
        self.column_name = column_name
        add_style(self, 'data-block')
        self.append(Gtk.Label(label=self.column_name))
        drag_controller = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
        drag_controller.connect("prepare", self.on_drag_prepare)
        drag_controller.connect("drag-begin", self.on_drag_begin)
        self.add_controller(drag_controller)

    def on_drag_prepare(self, _ctrl, _x, _y):
        item = Gdk.ContentProvider.new_for_value(self)
        string = Gdk.ContentProvider.new_for_value(self.column_name)
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


class ModelBlock(Gtk.Box):
    """
    This represents one draggable "block" that we can drag and drop from one section of the GUI to 
    another section of the GUI. 
    """
    def __init__(self, sklearn_model_function_call , color,  **kargs):
        super().__init__(**kargs)
        self.sklearn_model_function_call = sklearn_model_function_call
        
        # getting all possible input metrics for this function and default values
        # make a grid of possible ones
        self.parameters_box = Gtk.Grid()

        # also wrap this in a scrollable
        scrollable_view = Gtk.ScrolledWindow(hexpand=True)
        scrollable_view.set_min_content_height(250)
        scrollable_view.set_child(self.parameters_box)

        # loop over the possible input arguments
        possible_args = inspect.signature(sklearn_model_function_call)
        x = 0
        for param_name, param in possible_args.parameters.items():
            curr_label = Gtk.Label(label=param_name)
            curr_entry = Gtk.Entry()
            curr_entry.set_text(str(param.default))
            # add an object to the grid
            self.parameters_box.attach(curr_label , 0 , x , 1, 1)
            self.parameters_box.attach(curr_entry , 1 , x , 1, 1)
            x += 1
        self.x = x
        # assemble blocks
        sub_body = Gtk.Expander(label=sklearn_model_function_call.__name__)
        sub_body.set_child(scrollable_view)
        self.append(sub_body)
        drag_controller = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
        drag_controller.connect("prepare", self.on_drag_prepare)
        drag_controller.connect("drag-begin", self.on_drag_begin)
        self.add_controller(drag_controller)
        add_style(self , f"block-{color}")
        self.block_color = color

    def copy(thing_to_be_copied):
        

    def on_drag_prepare(self, _ctrl, _x, _y):
        item = Gdk.ContentProvider.new_for_value(self)
        string = Gdk.ContentProvider.new_for_value(self.sklearn_model_function_call)
        return Gdk.ContentProvider.new_union([item, string])

    def on_drag_begin(self, ctrl, _drag):
        icon = Gtk.WidgetPaintable.new(self)
        ctrl.set_icon(icon, 0, 0)

    def on_drag_end(self, drag_source, drag, success):
        # The drag operation is complete.
        # Check if the move was successful and perform cleanup.
        if success and drag.get_selected_action() == Gdk.DragAction.MOVE:
            # The widget was successfully dropped, so we can remove it from its source.
            self.source_box.remove(self.drag_widget)
            print("Widget removed from source container.")

    




       
