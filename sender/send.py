# Author: Charles Cheng
# Modified: 06/16/2022

import time, json, random
import serial
import click
from zfec.easyfec import Encoder

# Define constants
TRANSMIT_PORT_NAME = '/dev/tty.usbserial-14420' # ls /dev/tty.*
BAUDRATE = 230400 # must agree with that of receiver 
BUFFER_SIZE = 2147483647 # decrease if buffer overflows
TRANSMIT_DELAY = 1 # increase if buffer overflows
NUM_TOTAL_BLOCKS = 25
NUM_RECONSTR_BLOCKS = 20 # NUM_TOTAL_BLOCKS - NUM_RECONSTR_BLOCKS = number of check blocks

# Converts file to json format: filename (metadata) and file contents stored
# Returns (unicode) encoded dictionary
def file_to_json(filename):
    file = open(filename, 'r')
    msg = file.read()
    file.close()
    data_dict = {"filename":filename, "filedata":msg}
    data_json = json.dumps(data_dict)
    return data_json.encode()

# Performs zfec encoding 
# For more information about encoding parameterization,
# visit https://pypi.org/project/zfec/ 
def zfec_encode(data):
    enc = Encoder(NUM_RECONSTR_BLOCKS, NUM_TOTAL_BLOCKS)
    stream = enc.encode(data)
    # Randomly chooses which NUM_RECONSTR_BLOCKS packages to send
    packet_constrs = random.sample(list(enumerate(stream)), NUM_RECONSTR_BLOCKS)

    buffer_out = b''
    for constr in packet_constrs:
        # Each package/block starts with 3 digits denoting the block number (metadata)
        # followed by the contents of the package
        buffer_out += f"{constr[0]:03}".encode() + constr[1]
    return buffer_out

@click.command()
@click.option('--name', prompt='Name of file to send', help='Name of file to send.')
def send_file(name):
    with serial.Serial(TRANSMIT_PORT_NAME, baudrate=BAUDRATE, parity=serial.PARITY_ODD) as port:
        msg = file_to_json(name)
        buffer_out = zfec_encode(msg)

        # Ensures maximum size of data sent out at once is equal to BUFFER_SIZE
        for i in range(0, len(buffer_out), BUFFER_SIZE):
            port.write(buffer_out[i:min(i+BUFFER_SIZE, len(buffer_out))])
            time.sleep(TRANSMIT_DELAY)

if __name__ == '__main__':
    send_file()