import sys
import csv
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk, Gio, Gdk, GObject


import viewclasses
import standard_box
import sklearn_proccesses


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
    # make top control buttons
    top_control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    control_button = Gtk.Button(label="Edit CSV")
    top_control_box.append(control_button)


    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_size_request(300,300)
    scrolled_window.set_hexpand(True)
    scrolled_window.set_vexpand(True)


    scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    csv_viewer_box = Gtk.Box()
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
    add_style(scrolled_window , 'csv-reader ')

    main_box = standard_box.StdBox(
        header_box=top_control_box,
        body_box=scrolled_window
    )
    return main_box


def render_pipeline():
    # make top control buttons
    top_control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    control_button = Gtk.Button(label="Add Pipeline")
    top_control_box.append(control_button)

    # drag and drop demo
    flow_box = Gtk.FlowBox()
    views_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    views_box.props.vexpand = True
    flow_box.props.selection_mode = Gtk.SelectionMode.NONE
    flow_box.append(viewclasses.SourceFlowBoxChild("Item 1", "image-missing"))
    flow_box.append(viewclasses.SourceFlowBoxChild("Item 2", "help-about"))
    flow_box.append(viewclasses.SourceFlowBoxChild("Item 3", "edit-copy"))
    views_box.append(viewclasses.TargetView(vexpand=True))
    drop_demo = Gtk.Box()
    drop_demo.append(views_box)
    drop_demo.append(flow_box)
    
    # create a standard box
    main_box = standard_box.StdBox(
        header_box=top_control_box,
        body_box=drop_demo
    )

    return main_box


def render_top_bar():
    header_bar = Gtk.HeaderBar.new()
    header_bar.set_show_title_buttons(True)
    return header_bar

def render_block_library():
    main_box = standard_box.StdBox(
        header_box=Gtk.Box(),
        body_box=Gtk.Box()
    )

    return main_box

def render_graph():
    main_box = sklearn_proccesses.PlottingBox()
    return main_box



class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.MyGtkApplication")
        GLib.set_application_name("SciKitLearn GUI")

    def do_activate(self):
        # the main window
        window = Gtk.ApplicationWindow(application=self, title="Hello World")
        window.set_default_size(1200, 900)

        # left side
        left_box = Gtk.Paned(
            orientation=Gtk.Orientation.VERTICAL,
        )
        # right side
        right_box = Gtk.Paned(
            orientation=Gtk.Orientation.VERTICAL,
        )

        # The main box
        main_box = Gtk.Paned (
            orientation=Gtk.Orientation.HORIZONTAL,
        )


        # chart stuff
        chart_box = render_graph()
        right_box.set_start_child(chart_box)

        # block library stuff
        block_library = render_block_library()
        right_box.set_end_child(block_library)
    
        # The csv viewer
        csv_veiwer_box = render_csv()
        left_box.set_start_child(csv_veiwer_box )

        # pipeline 
        pipeline_box = render_pipeline()
        left_box.set_end_child(pipeline_box )

        # adding left and right boxes
        main_box.set_start_child(left_box)
        main_box.set_end_child(right_box)
        # adding main box
        window.set_child(main_box)
        window.set_titlebar(render_top_bar())
        load_css_file()
        window.present()





app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)