import socket
import time
import serial
from threading import Thread
port = "/dev/ttyAMA0"
baudRate = 100000

ser = serial.Serial(port=port, baudrate=baudRate, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_TWO)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 6666))
print ("UDPServer Waiting for client on port 6666")
channels = []
timeSent = 0
def updateData():
    while True:
        dataFromClient, address = server_socket.recvfrom(256)
        global timeSent
        timeSent = time.time()
        cmd = ""
        global channels
        global send
        for i in range(0,4):
            cmd += chr(dataFromClient[i])
        if(cmd == "SBUS"):
            send = True
            checksum1 = 0
            for byte in dataFromClient:
                checksum1 = checksum1 ^ byte
            checksum1 = checksum1 & 0xFE
            checksum2 = (~checksum1) & 0xFE
            if(checksum1 == dataFromClient[30] and checksum2 == dataFromClient[29]):
                channels = dataFromClient[4:29]
        elif(cmd == "BEAT"):
            print("BEAT")
def sendSBUSData():
    while True:
        global channels
        global timeSent
        if (time.time() - timeSent < 1):
            time.sleep(0.05)
            ser.write(channels)
        else:
            None

t1 = Thread(target = updateData)
t2 = Thread(target = sendSBUSData)

t1.start()
t2.start()
