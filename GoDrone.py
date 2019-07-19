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
newChannels = [1024] * 16
timeSent = 0
def updateData():
    # Update joystick data
    dataFromClient, address = server_socket.recvfrom(256)
    print(list(dataFromClient))
    global timeSent
    global newChannels
    timeSent = time.time()
    cmd = ""
    for i in range(0,4):
        cmd += chr(dataFromClient[i])
    if(cmd == "SBUS"):
        checksum1 = 0
        for byte in dataFromClient:
            checksum1 = checksum1 ^ byte
        checksum1 = checksum1 & 0xFE
        checksum2 = (~checksum1) & 0xFE
        if(checksum1 == dataFromClient[36] and checksum2 == dataFromClient[37]):
            channels = dataFromClient[4:36]
            chan = []
            for i in range(0,len(channels),2):
                LSB = channels[i]
                MSB = channels[i+1] << 8
                num = int(LSB + MSB)

                #if(i == 4):
                #     print(height)

                chan.append(num)
            channels = chan
            #print(self.channels)
            for i in range(len(channels)):
                update_channel(i, channels[i])
            time.sleep(0.02)
            print(newChannels)
            # print(self.height)
            ser.write(create_SBUS(newChannels))
            newChannels = [1024] * 16
            
def bit_not(n, numbits=8):
    return (1 << numbits) - 1 - n


def create_SBUS(chan):
    data = bytearray(25)

    data[0] = 0x0f  # start byte

    current_byte = 1
    available_bits = 8

    for ch in chan:
        ch &= 0x7ff
        remaining_bits = 11
        while remaining_bits:
            mask = bit_not(0xffff >> available_bits << available_bits, 16)
            enc = (ch & mask) << (8 - available_bits)
            data[current_byte] |= enc

            encoded_bits = 0
            if remaining_bits < available_bits:
                encoded_bits = remaining_bits
            else:
                encoded_bits = available_bits

            remaining_bits -= encoded_bits
            available_bits -= encoded_bits
            ch >>= encoded_bits

            if available_bits == 0:
                current_byte += 1
                available_bits = 8

    data[23] = 0
    data[24] = 0
    return data

def set_channel(chan, data):
    newChannels[chan] = data & 0x07ff

def update_channel(chan, value):
    set_channel(chan, mapData(value))

def mapData(n):
    return int((819 * ((n - 1500) / 500)) + 992)

while True:
    updateData()
