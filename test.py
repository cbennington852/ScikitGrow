import gi
import cairo
import math

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


class PlotApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.points = []
        self.phase = 0
        self.max_points = 200

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self, title="Rapidly Updating Plot")
        
        # 1. Create a DrawingArea widget
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_draw_func(self.on_draw)
        
        window.set_child(drawing_area)
        window.set_default_size(600, 400)
        window.present()

        # 3. Use GLib.timeout_add to trigger updates every 20ms
        GLib.timeout_add(1, self.update_plot, drawing_area)

    def update_plot(self, drawing_area):
        """Generates new data and queues a redraw."""
        # Append a new point to the data list
        self.phase += 0.1
        new_y = (math.sin(self.phase) * 0.45) + 0.5
        self.points.append(new_y)

        # Keep the list size limited for a smooth scrolling effect
        if len(self.points) > self.max_points:
            self.points.pop(0)

        # 4. Queue a redraw of the DrawingArea
        drawing_area.queue_draw()
        
        # Return True to continue the timer
        return True

    def on_draw(self, drawing_area, cr, width, height):
        """
        2. Custom draw function using Cairo to plot the data.
        This function is called by GTK whenever the DrawingArea needs to be redrawn.
        """
        # Clear the background
        cr.set_source_rgb(0.05, 0.05, 0.1)
        cr.paint()

        # Set line properties
        cr.set_source_rgb(0.4, 0.8, 0.6)  # Light green color
        cr.set_line_width(2)

        # Get the scaling factor for x and y axes
        x_scale = width / (self.max_points - 1)
        
        # Check if there's any data to plot
        if not self.points:
            return
            
        # Move to the starting position
        cr.move_to(0, height * (1 - self.points[0]))

        # Plot the line
        for i, y_value in enumerate(self.points):
            x = i * x_scale
            y = height * (1 - y_value)
            cr.line_to(x, y)

        cr.stroke()


if __name__ == "__main__":
    app = PlotApp(application_id="com.example.RapidPlot")
    app.run(None)
