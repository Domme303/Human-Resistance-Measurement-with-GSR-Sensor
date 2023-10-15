import configparser
from tkinter import Tk, messagebox, Button, filedialog, Label
import serial
import time

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from arduino_connection import ArduinoConnection


class App:
    def __init__(self) -> None:
        self.window = Tk()
        self.window.geometry("1040x620")
        self.window.resizable(width=False, height=False)
        self.window.update()
        self.defaultbg = self.window.cget('bg')
        self.active = True
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.arduino_connection = ArduinoConnection(config)

        self.measurement_active = False

        self.unsaved_data = False

        # Define buttons and labels
        self.button_connect = Button(self.window, text="Connect", command=self.connect)
        self.button_connect.place(x=20, y=10, width=60, height=30)

        self.button_start_stop = Button(self.window, text="Start", command=self.start_stop)
        self.button_start_stop.place(x=(self.window.winfo_width()/2)-40, y=10, width=80, height=70)
        self.button_start_stop["state"] = "disabled"

        self.button_save = Button(self.window, text="Save", command=self.on_save)
        self.button_save.place(x=self.window.winfo_width()-100, y=10, width=80, height=70)
        self.button_save["state"] = "disabled"

        self.button_reset = Button(self.window, text="Reset", command=self.on_reset)
        self.button_reset.place(x=20, y=50, width=60, height=30)

        self.text = Label(self.window, text="0hz")
        self.text.place(x=(self.window.winfo_width()/2)+50, y=35)

        # Initialize Plot
        f = Figure(figsize=(10,5), dpi=100)

        self.canvas = FigureCanvasTkAgg(f, self.window)
        self.canvas.get_tk_widget().place(x=20, y=100)

    def mainloop(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        while self.active:
            try: 
                if self.measurement_active:
                    self.arduino_connection.collect()
                    self.plot()
                    self.unsaved_data = True
                    self.text.configure(text=f"{round(self.arduino_connection.data[0].shape[0]/(time.perf_counter()-self.arduino_connection.start_time), 3)}hz")
                if self.unsaved_data and not self.measurement_active:
                    self.button_save["state"] = "normal"
                else:
                    self.button_save["state"] = "disabled"
                self.window.update_idletasks()
                self.window.update()
            except serial.SerialException:
                if messagebox.askretrycancel(title="Connection Lost", message="Serial connection lost. Please make sure the device is plugged in propperly. Press 'Retry' to try to connect again."):
                    self.arduino_connection.connected = False
                    self.connect()
                self.measurement_active = False
                self.button_start_stop.configure(text="Start")

    def plot(self):
        f = Figure(figsize=(10,5), dpi=100)
        ax = f.add_subplot(111)
        for sensor_id in range(self.arduino_connection.number_sensors):
            ax.plot("timestamp", "gsr-value",data=self.arduino_connection.data[sensor_id], label=f"Sensor {sensor_id+1}")
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("GSR-Value")
        ax.legend()
        self.canvas.figure = f

        self.canvas.draw()

    def on_save(self):
        for sensor_id in range(self.arduino_connection.number_sensors):
            file = filedialog.asksaveasfilename(title=f"Save Sensor {sensor_id+1} data", defaultextension=".xlsx", filetypes=[("Exel files",".xlsx"), ("CSV files",".csv")])
            if file is None or file == "": # Check if file selection was canceled
                return
            self.arduino_connection.save(sensor_id, file)
        
        self.unsaved_data = False

    def on_reset(self):
        if self.unsaved_data:
            self.window.bell()
            continue_ = messagebox.askyesno(title="Unsaved Data", message="There is unsaved data which will be permanently deleted if proceeded. Are you sure u want to continue?")
            if not continue_:
                return False
        
        self.arduino_connection.reset()
        self.measurement_active = False
        self.unsaved_data = False
        self.button_start_stop.configure(text="Start")

        # Reset Canvas
        f = Figure(figsize=(10,5), dpi=100)
        self.canvas.figure = f
        self.canvas.draw()

        return True

    def on_close(self):
        if not self.on_reset():
            return
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