import tkinter as tk
from tkinter import dnd

class DraggableLabel(tk.Label):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self.on_start_drag)

    def on_start_drag(self, event):
        dnd.dnd_start(self, event)

    def dnd_end(self, event , _):
        pass

class DropTargetFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(bg="lightblue")

    def dnd_enter(self, source, event):
        self.config(bg="lightgreen")  # Visual feedback for entering

    def dnd_leave(self, source, event):
        self.config(bg="lightblue")   # Revert color on leaving

    def dnd_motion(self, source, event):
        pass # Can update visuals based on motion if needed

    

    def dnd_commit(self, source, event):
        print(f"Dropped {source.cget('text')} on target!")
        source.master = self # Reparent the widget to the new frame
        source.pack() # Or use .place() or .grid() to position it

root = tk.Tk()

draggable_label = DraggableLabel(root, text="Drag Me!", bg="yellow")
draggable_label.pack(pady=20)

drop_frame = DropTargetFrame(root, width=200, height=100)
drop_frame.pack(pady=20)

root.mainloop()