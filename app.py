import configparser
import tkinter as tk
from tkinter import Tk, messagebox, Button, filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from arduino_connection import ArduinoConnection
from utils import resource_path


class App:
    def __init__(self) -> None:
        self.window = Tk()
        self.defaultbg = self.window.cget('bg')
        self.active = True
        config = configparser.ConfigParser()
        config.read(resource_path('config.ini'))
        self.arduino_connection = ArduinoConnection(config)

        self.measurement_active = False

        self.button_connect = Button(self.window, text="Connect", command=self.connect)
        self.button_connect.pack()

        self.button_start_stop = Button(self.window, text="Start", command=self.start_stop)
        self.button_start_stop.pack()
        self.button_start_stop["state"] = "disabled"

        f = Figure(figsize=(5,5), dpi=100)

        self.canvas = FigureCanvasTkAgg(f, self.window)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, self.window)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def mainloop(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        while self.active:
            self.window.update_idletasks()
            self.window.update()
            if self.measurement_active:
                self.arduino_connection.collect()
                self.plot()

    def plot(self):
        f = Figure(figsize=(5,5), dpi=100)
        ax = f.add_subplot(111)
        for sensor_id in range(self.arduino_connection.number_sensors):
            ax.plot("timestamp", "value",data=self.arduino_connection.data[sensor_id], label=f"Sensor {sensor_id+1}")
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("GSR-Value")
        ax.legend()
        self.canvas.figure = f

        self.canvas.draw()

    def on_close(self):
        self.arduino_connection.close()
        self.active = False
        self.window.destroy()

    def connect(self):
        if self.arduino_connection.connected:
            self.arduino_connection.close()
            self.measurement_active = False
            self.button_connect.configure(background=self.defaultbg)
            return
        if self.arduino_connection.connect():
            # success
            self.button_connect.configure(background="green")
            self.button_start_stop["state"] = "normal"
        else:
            # failed
            self.button_connect.configure(background="red")
            messagebox.showerror(title="Could not connect!", 
                                 message="An Error has occured while trying to connect!\nPlease try replugging the device or check and confirm the configured port and baude rate.")

    def start_stop(self):
        if self.measurement_active:
            self.measurement_active = False
            self.arduino_connection.stop_measurement()
            self.button_start_stop.configure(text="Start")
        else:
            self.measurement_active = True
            self.arduino_connection.start_measurement()
            self.button_start_stop.configure(text="Stop")

if __name__ == "__main__":
    app = App()
    app.mainloop()