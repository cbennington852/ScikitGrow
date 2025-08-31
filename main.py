import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject


import viewclasses


css_file_path = "./styles.css"

def load_css_file():
        with open(css_file_path) as f:
            # Load CSS
            css = f.read()
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(css)

            # Apply CSS to display
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
def read_csv_data(filepath):
    data = []
    with open(filepath, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data.append(row)
    return data

def add_style(gui_thing , class_name):
    gui_thing.get_style_context().add_class(class_name)

def render_csv():
    scrolled_window = Gtk.ScrolledWindow()
    

    scrolled_window.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
    csv_viewer_box = Gtk.Box()
    csv_viewer_box.get_style_context().add_class("bordered-box")
    # read csv
    csv_data = read_csv_data("./customers-100.csv")
    liststore = Gtk.ListStore(*([str] * len(csv_data[0])))

    for line in csv_data:
        liststore.append(line)

   # Create a TreeView and link it to the model
    treeview = Gtk.TreeView(model=liststore)

    # Create a column for each CSV header
    for i, column_title in enumerate(csv_data[0]):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, renderer, text=i)
        treeview.append_column(column)

    # Add the TreeView (not the ListStore!) to the container
    csv_viewer_box.append(treeview)
    scrolled_window.set_child(csv_viewer_box)
    scrolled_window.set_max_content_height(300)
    scrolled_window.set_max_content_width(300)
    return scrolled_window


def render_pipeline():
    main_box = Gtk.Box()
    flow_box = Gtk.FlowBox()
    views_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    views_box.props.vexpand = True
    flow_box.props.selection_mode = Gtk.SelectionMode.NONE
    flow_box.append(viewclasses.SourceFlowBoxChild("Item 1", "image-missing"))
    flow_box.append(viewclasses.SourceFlowBoxChild("Item 2", "help-about"))
    flow_box.append(viewclasses.SourceFlowBoxChild("Item 3", "edit-copy"))
    views_box.append(viewclasses.TargetView(vexpand=True))
    main_box.append(flow_box)
    main_box.append(views_box)
    return main_box


def render_top_bar():
    header_bar = Gtk.HeaderBar.new()
    header_bar.set_show_title_buttons(True)
    return header_bar



class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.MyGtkApplication")
        GLib.set_application_name("SciKitLearn GUI")

    def do_activate(self):
        # the main window
        window = Gtk.ApplicationWindow(application=self, title="Hello World")
        window.set_default_size(600, 600)

        # left side
        left_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
        )
        # right side
        right_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
        )
        add_style(right_box, "chart")

        # The main box
        main_box = Gtk.Box (
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
        )

    
        # The csv viewer
        csv_veiwer_box = render_csv()
        add_style(csv_veiwer_box , "csv-viewer")
        csv_veiwer_box.set_size_request(300,300)
        left_box.append(csv_veiwer_box)

        # pipeline 
        pipeline_box = render_pipeline()
        left_box.append(pipeline_box)

        # chart stuff
        chart_box = Gtk.Box()
        add_style(chart_box , 'chart')
        left_box.append(chart_box)

        # end of loop stuff
        main_box.append(left_box)
        main_box.append(right_box)
        window.set_child(main_box)
        window.set_titlebar(render_top_bar())
        load_css_file()
        window.present()





app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)