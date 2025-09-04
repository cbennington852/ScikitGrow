import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject


import matplotlib
matplotlib.use('GTK4Agg') # Or 'GTK3Agg' for GTK3
import matplotlib.pyplot as plt

from matplotlib.backends.backend_gtk4agg import \
    FigureCanvasGTK4Agg as FigureCanvas
from matplotlib.figure import Figure

class PlottingBox(Gtk.Box):
    def __init__(self, **kargs):
        super().__init__(**kargs)

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6])
        self.canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
        self.canvas.set_size_request(500, 500)
        self.append(self.canvas)

