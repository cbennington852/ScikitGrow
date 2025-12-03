import json
import sys
import csv
import traceback
import gi
import inspect
import utility

gi.require_version("Gtk", "4.0")
import block_libary
from gi.repository import GLib, Gtk, Gio, Gdk, GObject
import sklearn



class DataframeViewer(Gtk.ScrolledWindow):

    def __init__(self , main_dataframe , **kargs):
        super().__init__(**kargs)
        self.set_size_request(300, 300)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.main_dataframe = main_dataframe

        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        csv_viewer_box = Gtk.Box()
        # read csv
        # retrieve the pandas dataframe
        # add the top header
        # add all of the dataframe rows.
        # may have to make a conversion map
        column_types = []
        for col in self.main_dataframe.columns:
            tmp = GObject.type_from_name("gchararray")
            print(tmp)
            column_types.append(tmp)

        liststore = Gtk.ListStore(*column_types)

        limit = 60
        for index, row in self.main_dataframe.iterrows():
            row = [str(point) for point in row]
            liststore.append(list(row))
            limit -= 1
            if limit <= 0:
                break

        # Create a TreeView and link it to the model
        treeview = Gtk.TreeView(model=liststore)

        # Create a column for each dataframe header
        for i, col_name in enumerate(self.main_dataframe.columns):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_name, renderer, text=i)
            treeview.append_column(column)

        # Add the TreeView (not the ListStore!) to the container
        csv_viewer_box.append(treeview)
        self.set_child(csv_viewer_box)
        utility.add_style(self, "csv-reader ")
