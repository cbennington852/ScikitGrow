import tkinter as tk

class DraggableFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind("<ButtonPress-1>", self.on_drag_start)
        self.bind("<B1-Motion>", self.on_drag_motion)
        self.bind("<ButtonRelease-1>", self.on_drag_release)
        self._drag_data = {"x": 0, "y": 0}

    def on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.tkraise() # Bring the dragged frame to the top

    def on_drag_motion(self, event):
        x = self.winfo_x() + (event.x - self._drag_data["x"])
        y = self.winfo_y() + (event.y - self._drag_data["y"])
        self.place(x=x, y=y)

    def on_drag_release(self, event):
        # Optional: Add logic here for dropping onto specific areas
        pass

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x400")

    parent_frame = tk.Frame(root, bg="lightblue", width=300, height=300)
    parent_frame.place(x=50, y=50)

    draggable_frame = DraggableFrame(parent_frame, bg="lightgreen", width=100, height=100)
    draggable_frame.place(x=10, y=10)

    tk.Label(draggable_frame, text="Drag Me!").pack(pady=20)

    root.mainloop()