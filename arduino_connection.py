import configparser
import serial
import time
import pandas as pd

class ArduinoConnection:
    def __init__(self, config:configparser) -> None:
        self.serial_port = config.get("connection", "serial_port")
        self.baude_rate = config.getint("connection", "baud_rate")
        self.serial_connection = None

        self.connected = False
        self.start_time = None

        self.number_sensors = config.getint("sensors", "number_sensors")
        self.pins = config.get("sensors", "pins").split(",")

        self.data = {}
        for sensor_id in range(self.number_sensors):
            self.data[sensor_id] = pd.DataFrame(columns=["timestamp", "gsr-value", "hr-value"])


        assert type(self.serial_port) == str
        assert type(self.baude_rate) == int
        assert (type(self.number_sensors) == int) & (self.number_sensors > 0)
        assert (type(self.pins) == list) & (len(self.pins) > 0)

    def connect(self) -> bool:
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baude_rate)
            self.wait_message("ready")
            self.sent_to_arduino(f"NumSensors,{self.number_sensors}")
            self.sent_to_arduino(f"Pins,{','.join(self.pins)}")
            self.connected = True
        except Exception:
            return False
        return True
    
    def start_measurement(self) -> None:
        if self.connected:
            self.sent_to_arduino("start")

    def stop_measurement(self) -> None:
        if self.connected:
            self.sent_to_arduino("stop")
    
    def wait_message(self, message_query) -> str:
        message = ""
        start = time.perf_counter()
        while message.find(message_query):
            while self.serial_connection.inWaiting() == 0:
                if time.perf_counter()-start > 5:
                    raise TimeoutError("Make sure the arduino is running the correct code!")
            message = self.recieve_from_arduino()
        return message
    
    def sent_to_arduino(self, message:str) -> None:
        self.serial_connection.write(bytes(f"<{message}>", 'utf-8'))

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
    
    def collect(self) -> None:
        message = self.wait_message("Sensor")
        if self.start_time is None:
            self.start_time = time.perf_counter()
        _, sensor_id, value = message.split(",")
        sensor_id = int(sensor_id)
        value = int(value)
        hr = ((1024+(2*value))*10000)/((512-value)+0.00001)
        row = {"timestamp": time.perf_counter()-self.start_time, "gsr-value": value, "hr-value": hr}
        
        self.data[sensor_id].loc[len(self.data[sensor_id])] = row

    def save(self, sensor_id, file) -> None:
        if file.split(".")[-1] == "csv":
            self.data[sensor_id].dropna().to_csv(file)
        elif file.split(".")[-1] == "xlsx":
            self.data[sensor_id].dropna().to_excel(file)

    def reset(self) -> None:
        self.stop_measurement()
        self.start_time = None
        for sensor_id in range(self.number_sensors):
            self.data[sensor_id] = pd.DataFrame(columns=["timestamp", "gsr-value", "hr-value"])

    def close(self) -> None:
        if self.serial_connection is not None:
            self.sent_to_arduino("exit")
            self.serial_connection.close()
            self.serial_connection = None
            self.connected = False


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        arduino_connection = ArduinoConnection(config)

        arduino_connection.connect()

        arduino_connection.start_measurement()

        start = time.perf_counter()
        while time.perf_counter() - start < 15:
            print(arduino_connection.recieve_from_arduino())

        arduino_connection.stop_measurement()
        start = time.perf_counter()
        while time.perf_counter() - start < 2:
            print(arduino_connection.recieve_from_arduino())
    except KeyboardInterrupt:
        pass

    arduino_connection.close()

    
