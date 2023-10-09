import configparser
import serial
import json
import time
import tkinter

from utils import resource_path

class ArduinoConnection:
    def __init__(self, config) -> None:
        self.serial_port = config.get("connection", "serial_port")
        self.baude_rate = config.getint("connection", "baud_rate")
        self.serial_connection = None

        self.number_sensors = config.getint("sensors", "number_sensors")
        self.pins = config.get("sensors", "pins").split(",")

        assert type(self.serial_port) == str
        assert type(self.baude_rate) == int
        assert (type(self.number_sensors) == int) & (self.number_sensors > 0)
        assert (type(self.pins) == list) & (len(self.pins) > 0)

    def connect(self) -> bool:
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baude_rate)
            self.wait_ready()
            self.sent_to_arduino(f"NumSensors,{self.number_sensors}")
            self.sent_to_arduino(f"Pins,{','.join(self.pins)}")
        except serial.SerialException:
            return False
        return True
    
    def wait_ready(self):
        message = ""
        start = time.perf_counter()
        while message.find("ready"):
            while self.serial_connection.inWaiting() == 0:
                if time.perf_counter()-start > 5:
                    raise TimeoutError("Make sure the arduino is running the correct code!")
            message = self.recieve_from_arduino()
    
    def sent_to_arduino(self, data:str) -> None:
        self.serial_connection.write(bytes(f"<{data}>", 'utf-8'))

    def recieve_from_arduino(self) -> str:
        message = ""
        cursor = ""
        while cursor != "<":
            cursor = self.serial_connection.read().decode('utf-8')
        
        while cursor != ">":
            if cursor != "<":
                message += cursor
            cursor = self.serial_connection.read().decode('utf-8')
        return message

    def close(self) -> None:
        if self.serial_connection is not None:
            self.serial_connection.close()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(resource_path('config.ini'))

    try:
        arduino_connection = ArduinoConnection(config)

        a = arduino_connection.connect()

        start = time.perf_counter()
        while time.perf_counter() - start < 10:
            print(arduino_connection.recieve_from_arduino())
    except KeyboardInterrupt:
        pass

    arduino_connection.close()

    
