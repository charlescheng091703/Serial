# Author: Charles Cheng
# Modified: 06/16/2022

import time, json
import serial
from zfec.easyfec import Decoder

# Define constants
RECEIVE_PORT_NAME = 'COM3' # mode
BAUDRATE = 230400 # must agree with that of sender
RECEIVE_DELAY = 1e-4 # rate at which serial buffer is being copied to local memory
BUFFER_SIZE = 2147483647 # decrease if buffer overflows
NUM_TOTAL_BLOCKS = 25
NUM_RECONSTR_BLOCKS = 20 # NUM_TOTAL_BLOCKS - NUM_RECONSTR_BLOCKS = number of check blocks
TIMEOUT_TIME = 2 # time to wait before end of transmission is assumed
STATE = "IDLE" # ACTIVE when data is being sent or timeout has not occurred
               # IDLE when file is being written or timeout has occurred

# Takes a json-formatted dictionary containing filename and file contents
# and writes a new file 
def write_file(data):
    data_dict = json.loads(data)
    with open(data_dict["filename"], 'w', encoding='utf-8') as file:
        file.write(data_dict["filedata"])
    print(data_dict["filename"]+" successfully transmitted.")
    return data_dict["filename"] # returns filename

# Performs zfec decoding
# If successful, it writes the file with the received data
# Otherwise, it prints an error statement 
def reconstruct_and_write(buffer):
    dec = Decoder(NUM_RECONSTR_BLOCKS, NUM_TOTAL_BLOCKS)
    block_size = int(len(buffer)/NUM_RECONSTR_BLOCKS)
    blocks = [] # list of package contents
    blocknums = [] # list of block indices
    try:
        for i in range(NUM_RECONSTR_BLOCKS):
            # First three digits are block number, the rest of bytes are package content
            blocknums.append(int(buffer[block_size*i:block_size*i+3].decode()))
            blocks.append(buffer[block_size*i+3:block_size*(i+1)])
        decoded = dec.decode(blocks, sharenums=blocknums, padlen=0).decode().rstrip('\0')
        filename = write_file(decoded)
    except:
        print("Invalid transmission received. Unable to process.")

def receive_data():
    global STATE
    buffer = b''
    timeout = time.time()
    with serial.Serial(RECEIVE_PORT_NAME, baudrate=BAUDRATE, parity=serial.PARITY_ODD) as port:
        port.set_buffer_size(rx_size=BUFFER_SIZE, tx_size=BUFFER_SIZE)
        while True: # runs infinitely; Ctrl + C to quit
            # Implementation of state machine 
            if STATE == "ACTIVE":
                if port.inWaiting():
                    timeout = time.time()
                    buffer += port.read(port.inWaiting())
                    time.sleep(RECEIVE_DELAY)
                elif time.time() - timeout > TIMEOUT_TIME:
                    STATE = "IDLE"
            elif STATE == "IDLE":
                buffer_length = len(buffer)
                if buffer_length != 0:
                    reconstruct_and_write(buffer)
                    buffer = b''
                elif port.inWaiting():
                    STATE = "ACTIVE"

if __name__ == '__main__':
    receive_data()