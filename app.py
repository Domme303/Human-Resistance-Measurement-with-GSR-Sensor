import configparser
import tkinter as tk
from tkinter import Tk, messagebox, Button, filedialog

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

    def mainloop(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        while self.active:
            self.window.update_idletasks()
            self.window.update()
            if self.measurement_active:
                self.arduino_connection.collect()

    def on_close(self):
        self.arduino_connection.close()
        self.active = False
        self.window.destroy()

    def connect(self):
        if self.arduino_connection.connected:
            self.arduino_connection.close()
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