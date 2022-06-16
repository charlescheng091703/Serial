import serial
import time
import json
from zfec.easyfec import Decoder

RECEIVE_PORT_NAME = 'COM3' # mode
BAUDRATE = 230400
RECEIVE_DELAY = 1e-4 # rate at which serial buffer is being copied to local memory
BUFFER_SIZE = 2147483647 # decrease if buffer overflows
NUM_TOTAL_BLOCKS = 25
NUM_RECONSTR_BLOCKS = 20 # NUM_TOTAL_BLOCKS - NUM_RECONSTR_BLOCKS = number of check blocks
TIMEOUT_TIME = 15 # maximum time permitted per file transfer

def write_file(data):
    data_dict = json.loads(data)
    with open(data_dict["filename"], 'w', encoding='utf-8') as file:
        file.write(data_dict["filedata"])
    print(data_dict["filename"]+" successfully transmitted.")
    return data_dict["filename"] # returns filename

def receive_data():
    buffer = b''
    dec = Decoder(NUM_RECONSTR_BLOCKS, NUM_TOTAL_BLOCKS)
    with serial.Serial(RECEIVE_PORT_NAME, baudrate=BAUDRATE, parity=serial.PARITY_ODD) as port:
        port.set_buffer_size(rx_size=BUFFER_SIZE, tx_size=BUFFER_SIZE)
        while True:
            timeout = time.time()
            while (time.time() - timeout < TIMEOUT_TIME):
                if port.inWaiting():
                    try:
                        buffer += port.read(port.inWaiting())
                    except serial.SerialException:
                        print("Serial port transmit/receive error detected.")
                time.sleep(RECEIVE_DELAY)
            buffer_length = len(buffer)
            if buffer_length != 0:
                block_size = int(buffer_length/NUM_RECONSTR_BLOCKS)
                blocks = []
                blocknums = [] 
                try:
                    for i in range(NUM_RECONSTR_BLOCKS):
                        blocknums.append(int(buffer[block_size*i:block_size*i+3].decode()))
                        blocks.append(buffer[block_size*i+3:block_size*(i+1)])
                    decoded = dec.decode(blocks, sharenums=blocknums, padlen=0).decode().rstrip('\0')
                    filename = write_file(decoded)
                except:
                    print("Invalid transmission received. Unable to process.")
                buffer = b''
            else:
                print("Serial port timeout. No files received.")

if __name__ == '__main__':
    receive_data()