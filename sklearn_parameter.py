import sys
import csv
import gi
import inspect
import os

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject

import sklearn
from abc import ABC, abstractmethod




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
        # patch it not appending the delimiters
        if isinstance(param_value , str):
            new_param_value = '\'' + str(param_value) +'\''
            self.curr_entry.set_text(new_param_value)
        else:
            self.curr_entry.set_text(str(param_value))
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
    """
        Non-marker, this still returns zero, meaning no_verbose, but not displayed to user screen.
    """
    def __init__(self , param_name , param_value):
        super().__init__()
        self.curr_label = Gtk.Box()
        self.curr_entry = Gtk.Box()
        self.param_name = param_name
    def get_left_side(self):
        return self.curr_label
    def get_right_side(self):
        return self.curr_entry
    def get_value(self):
        return 0
    def get_param_name(self):
        return self.param_name

class NJobsParameter(SklearnParameterPair):
    """
        This removes said label, but whenever available, locks the n_jobs to number of cpu cores - 2
    """
    num_cpus = os.cpu_count() - 2 if (os.cpu_count() > 2)  else 1
    def __init__(self , param_name , param_value):
        super().__init__()
        self.curr_label = Gtk.Box()
        self.curr_entry = Gtk.Box()
        self.param_name = param_name
    def get_left_side(self):
        return self.curr_label
    def get_right_side(self):
        return self.curr_entry
    def get_value(self):
        return NJobsParameter.num_cpus
    def get_param_name(self):
        return self.param_name




class SklearnParameterFactory():

    """
    A list of special cases, of parameter name to special case.
    """
    special_cases = {
        "verbose" : VerboseModifier,
        "n_jobs" : NJobsParameter,
    }

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
        print("Thing : " , type(param_default_value))
        print("New FACTORY" ,type(param_default_value.default))
        if param_name in SklearnParameterFactory.special_cases:
            return SklearnParameterFactory.special_cases[param_name](param_name , param_default_value.default)
        elif isinstance(param_default_value.default , bool):
            return TogglePair(param_name , param_default_value.default)
        else:
            return TextEntryPair(param_name , param_default_value.default)
