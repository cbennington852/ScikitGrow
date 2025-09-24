import tkinter as tk
import tkinter as ttk
import dataframe_viewer


####################################################
#               APP CONSTANTS
####################################################
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
PATH_TO_ICON = 'my_icon.png'
WINDOW_TITLE = "My Tkinter Window"

####################################################
#               MAIN GUI
####################################################
class MainGUI():
    def __init__(self):
        # Create the main window
        self.root = tk.Tk()

        # Set window properties
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # setting main window
        icon_image = tk.PhotoImage(file=PATH_TO_ICON)
        self.root.iconphoto(True, icon_image)

        # Start the main event loop
        self.render_main_view()
        self.root.mainloop()

    def render_main_view(self):
        self.main_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_window.pack(fill=tk.BOTH, expand=True)

        # Create two frames for the panes
        right_frame = ttk.PanedWindow(self.main_window,orient=tk.VERTICAL, width=200, height=200, relief=tk.SUNKEN, borderwidth=2)
        left_frame = ttk.PanedWindow(self.main_window, orient=tk.VERTICAL, width=200, height=200, relief=tk.SUNKEN, borderwidth=2)
        
        # create the frames 
        top_left_frame = ttk.Frame(left_frame, width=200, height=200, relief=tk.SUNKEN, borderwidth=2)
        bottom_left_frame = ttk.Frame(left_frame, width=200, height=200, relief=tk.SUNKEN, borderwidth=2)
        top_right_frame = ttk.Frame(right_frame, width=200, height=200, relief=tk.SUNKEN, borderwidth=2)
        bottom_right_frame = ttk.Frame(right_frame, width=200, height=200, relief=tk.SUNKEN, borderwidth=2)

        # create each view
        self.dataframe_view = dataframe_viewer.DataframeView(master=top_left_frame)

        # render each window
        self.dataframe_view.pack()

        # Add the frames to the PanedWindow
        self.main_window.add(left_frame) 
        self.main_window.add(right_frame)
        right_frame.add(top_right_frame)
        right_frame.add(bottom_right_frame)
        left_frame.add(top_left_frame)
        left_frame.add(bottom_left_frame)

     




                

app = MainGUI()