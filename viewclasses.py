
import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
import block_libary
from gi.repository import GLib, Gtk, Gio, Gdk, GObject


class SourceFlowBoxChild(Gtk.FlowBoxChild):
    def __init__(self, name, icon_name):
        super().__init__()

        self.name = name
        self.icon_name = icon_name

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(box)

        icon = Gtk.Image(icon_name=self.icon_name)
        label = Gtk.Label(label=self.name)

        box.append(icon)
        box.append(label)

        drag_controller = Gtk.DragSource()
        drag_controller.connect("prepare", self.on_drag_prepare)
        drag_controller.connect("drag-begin", self.on_drag_begin)
        self.add_controller(drag_controller)

    def on_drag_prepare(self, _ctrl, _x, _y):
        item = Gdk.ContentProvider.new_for_value(self)
        string = Gdk.ContentProvider.new_for_value(self.name)
        return Gdk.ContentProvider.new_union([item, string])

    def on_drag_begin(self, ctrl, _drag):
        icon = Gtk.WidgetPaintable.new(self)
        ctrl.set_icon(icon, 0, 0)


class TargetView(Gtk.Box):
    def __init__(self, **kargs):
        super().__init__(**kargs)

        self.box = Gtk.Box()
        self.box.append(Gtk.Label(label="Hello drop here!"))
        self.append(self.box)

        drop_controller = Gtk.DropTarget.new(
            type=GObject.TYPE_NONE, actions=Gdk.DragAction.COPY
        )
        drop_controller.set_gtypes([block_libary.ModelBlock])
        drop_controller.connect("drop", self.on_drop)
        self.add_controller(drop_controller)

    def on_drop(self, _ctrl, value, _x, _y):
        if isinstance(value, block_libary.ModelBlock):
            for child in self.box:
                self.box.remove(child)
            self.box.append(block_libary.ModelBlock(
                sklearn_model_function_call=value.sklearn_model_function_call,
                color=value.block_color
            ))
        else:
            print(f"some kinda bug? {value}")

        print(self)