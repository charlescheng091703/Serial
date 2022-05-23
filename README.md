SERIAL DRIVER DOCUMENTATION

Author: Charles Cheng

INSTALLATION

For the sender, 

> conda create -y --name Serial python
> conda activate Serial
> conda install pyserial
> conda install click 

For the receiver,

> conda create -y --name Serial python
> conda activate Serial
> conda install pyserial

SELECTING THE PORT

On Windows, 

> mode

On Mac,
> ls /dev/tty.*
Copy the port name over to TRANSMIT_PORT_NAME and RECEIVE_PORT_NAME.

EXECUTION

send.py takes in one command line argument, the name of the file to send. For example,
> python send.py --name small.txt 

receive.py takes no arguments. The code runs in an infinite while loop. To run,
> python receive.py

To halt, 
> Ctrl + c
