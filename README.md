# Human Resistance Measurement with GSR Sensor

Welcome to the Human Resistance Measurement project, designed to make the utilization of cost-effective GSR (Galvanic Skin Response) sensors effortless for individuals with little to no programming experience. This project is tailored to be user-friendly and compatible with Arduino or Arduino-compatible boards. While it is primarily developed with the [Grove - GSR sensor](https://www.seeedstudio.com/Grove-GSR-sensor-p-1614.html) and the [Seeeduino V4.3](https://www.seeedstudio.com/Seeeduino-V4-2-p-2517.html), it can be adapted to work with similar sensors or Arduino boards. More details about the board and sensors used and how they can be wired can be found on https://wiki.seeedstudio.com/Grove-GSR_Sensor/.

## Getting Started

To begin using this project, follow these simple steps:

1. **Upload the Arduino Sketch:**
   - Use the [Arduino IDE](https://www.arduino.cc/en/software) to upload the Arduino sketch located in the `/GSR-Sensor/GSR-Sensor.ino` directory.

2. **Run the Application:**
   - If you're on a Windows machine, you can run the provided executable.
   - For other platforms or if you prefer manual execution, follow the instructions below:

     - Set up a Python 3.12 environment on your computer.
     - Install the necessary requirements specified in the project.

3. **Configure the Program:**
   - The program can be customized to your specific needs by editing the [config file](/config.ini).
   - In the `config.ini` file, configure the following settings:
     - **Serial Port:** Identify and specify the correct serial port of your Arduino device. On Windows, you can find this information in the Device Manager under "Ports (COM & LPT)." Right-click on your device, choose "Properties," and look for the port in the brackets in the name at the top.
     - **Baud Rate:** Set the baud rate to match the one you've configured for your Arduino device. This information can usually be found as the first value in the "Port Settings" tab of the same "Properties" window of your Arduino in the Device Manager.
     - **Number of Sensors** Set the amount of sensors you're intending to use.
     - **Pins** Provide the pins the Sensors are connected to. **Important!** On the [Grove Base Shield](https://www.seeedstudio.com/Base-Shield-V2.html) the naming on the connectors does not correspond directly to the pins they are connected to. E.g. the A0 port is wired to the pins A0 and A1 while the A1 port is wired to the pins A2 and A3. The Grove - GSR sensor only uses the first pin of each port so pin A0 should be selected for a sensor connected to port A0 and pin A2 for a sensor connected to port A1.

Now you're ready to measure human resistance using the GSR sensor with ease! If you encounter any issues or have questions, feel free to reach out for assistance.

Enjoy your journey into the world of GSR sensors, even with limited programming experience.

