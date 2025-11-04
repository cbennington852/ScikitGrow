import sys
import csv
import gi
import inspect

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject

import sklearn
from abc import ABC, abstractmethod


class SklearnParameterFactory():

    def get(param_default_value , param_name , sklearn_model_function_call):
        """
        Parameters:
            - param_value
            - param_name
            - sklearn_model_function_call

        From these we should determine the overall "type" of pair for this.
            Factory
            -->
            abstract class
            -->
            toggle
            number_inp
            other..
            maybe even custom overrides.

        """
        print("New FACTORY" ,type(param_default_value.default))
        if param_name == "verbose":
            return VerboseModifier(param_name , param_default_value.default)
        elif isinstance(param_default_value.default , bool):
            return TogglePair(param_name , param_default_value.default)
        else:
            return TextEntryPair(param_name , str(param_default_value.default))


class SklearnParameterPair(ABC):
    @abstractmethod
    def get_value():
        """
        Returns the "value from the Gtk objects"
        """

    @abstractmethod
    def get_left_side(self):
        """
        Returns the label
        """

    @abstractmethod
    def get_right_side(self):
        """
        Returns the right side / values
        """
    @abstractmethod
    def get_param_name(self):
        """
        name of parameter to grab
        """

class TextEntryPair(SklearnParameterPair):
    def __init__(self , param_name , param_value):
        super().__init__()
        self.curr_label = Gtk.Label(label=param_name)
        self.curr_entry = Gtk.Entry()
        self.param_name = param_name
        self.curr_entry.set_text(param_value)
    def get_left_side(self):
        return self.curr_label
    def get_right_side(self):
        return self.curr_entry
    def get_value(self):
        return eval(self.curr_entry.get_text())
    def get_param_name(self):
        return self.param_name
    
class TogglePair(SklearnParameterPair):
    def __init__(self , param_name , param_value):
        super().__init__()
        self.curr_label = Gtk.Label(label=param_name)
        self.curr_entry = Gtk.Switch()
        self.param_name = param_name
        self.curr_entry.set_active(param_value)
    def get_left_side(self):
        return self.curr_label
    def get_right_side(self):
        return self.curr_entry
    def get_value(self):
        return self.curr_entry.props.active
    def get_param_name(self):
        return self.param_name

class VerboseModifier(SklearnParameterPair):
    def __init__(self , param_name , param_value):
        super().__init__()
        self.curr_label = Gtk.Label(label=param_name)
        self.curr_entry = Gtk.Label(label="0")
        self.param_name = param_name
    def get_left_side(self):
        return self.curr_label
    def get_right_side(self):
        return self.curr_entry
    def get_value(self):
        return 0
    def get_param_name(self):
        return self.param_name



        