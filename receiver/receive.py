import serial
import time
import json
from afproto import *

RECEIVE_PORT_NAME = 'COM3' # mode
BAUDRATE = 115200
RECEIVE_DELAY = 1e-4 # rate at which serial buffer is being copied to local memory
STATE = "IDLE" # IDLE when no data is being transmitted
               # ACTIVE when data is being transmitted
BUFFER_SIZE = 2147483647

def write_file(data):
    data_dict = json.loads(data)
    with open(data_dict["filename"], 'w', encoding='utf-8') as file:
        file.write(data_dict["filedata"])
    return data_dict["filename"] # returns filename

def receive_data():
    global STATE
    buffer = ''
    with serial.Serial(RECEIVE_PORT_NAME, baudrate=BAUDRATE, parity=serial.PARITY_ODD) as port:
        port.set_buffer_size(rx_size=BUFFER_SIZE, tx_size=BUFFER_SIZE)
        while True:
            if port.inWaiting():
                if STATE == "IDLE":
                    start_time = time.time()
                    STATE = "ACTIVE"
                try:
                    buffer += port.read(port.inWaiting()).decode()
                except serial.SerialException:
                    print("Serial port transmit/receive error detected.")
            elif STATE == "ACTIVE":
                frame_data, _ = afproto_get_data(buffer)
                if frame_data != None:
                    filename = write_file(frame_data)
                    elapsed_time = time.time() - start_time
                    print("%s received in %.3f s" % (filename, elapsed_time))
                    buffer = ''
                    STATE = "IDLE"
            time.sleep(RECEIVE_DELAY)

if __name__ == '__main__':
    receive_data()