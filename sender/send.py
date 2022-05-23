import serial
import click
import time
import json
from afproto import *

TRANSMIT_PORT_NAME = '/dev/tty.usbserial-14410' # ls /dev/tty.*
BAUDRATE = 115200
BUFFER_SIZE = 2147483647 # decrease if buffer overflows
TRANSMIT_DELAY = 1.0 # increase if buffer overflows

@click.command()
@click.option('--name', prompt='Name of file to send', help='Name of file to send.')
def send_file(name):
    port = serial.Serial(TRANSMIT_PORT_NAME, baudrate=BAUDRATE, parity=serial.PARITY_ODD)
    file = open(name, 'r')
    msg = file.read()
    file.close()
    data_dict = {"filename":name, "filedata":msg}
    data_json = json.dumps(data_dict)
    msg = afproto_frame_data(data_json).encode()
    for i in range(0, len(msg), BUFFER_SIZE):
        port.write(msg[i:min(i+BUFFER_SIZE, len(msg))])
        time.sleep(TRANSMIT_DELAY)
    port.close()

if __name__ == '__main__':
    send_file()