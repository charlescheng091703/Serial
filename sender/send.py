import serial
import click
import time
import json
from zfec.easyfec import Encoder
import random

TRANSMIT_PORT_NAME = '/dev/tty.usbserial-14420' # ls /dev/tty.*
BAUDRATE = 230400  
BUFFER_SIZE = 2147483647 # decrease if buffer overflows
TRANSMIT_DELAY = 1 # increase if buffer overflows
NUM_TOTAL_BLOCKS = 25
NUM_RECONSTR_BLOCKS = 20 # NUM_TOTAL_BLOCKS - NUM_RECONSTR_BLOCKS = number of check blocks

def file_to_json(filename):
    file = open(filename, 'r')
    msg = file.read()
    file.close()
    data_dict = {"filename":filename, "filedata":msg}
    data_json = json.dumps(data_dict)
    return data_json.encode()

@click.command()
@click.option('--name', prompt='Name of file to send', help='Name of file to send.')
def send_file(name):
    with serial.Serial(TRANSMIT_PORT_NAME, baudrate=BAUDRATE, parity=serial.PARITY_ODD) as port:
        msg = file_to_json(name)
        enc = Encoder(NUM_RECONSTR_BLOCKS, NUM_TOTAL_BLOCKS)
        stream = enc.encode(msg)
        packet_constrs = random.sample(list(enumerate(stream)), NUM_RECONSTR_BLOCKS)

        buffer_out = b''
        for constr in packet_constrs:
            buffer_out += f"{constr[0]:03}".encode() + constr[1]

        for i in range(0, len(buffer_out), BUFFER_SIZE):
            port.write(buffer_out[i:min(i+BUFFER_SIZE, len(buffer_out))])
            time.sleep(TRANSMIT_DELAY)

if __name__ == '__main__':
    send_file()