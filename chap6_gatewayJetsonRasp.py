import serial.tools.list_ports
import random
import time
import sys
from Adafruit_IO import MQTTClient


AIO_FEED_ID = "iot-led"
AIO_USERNAME = "phamdinhtrung"
AIO_KEY = "aio_DNZB93UIb5X0iR6vDhD8EIteXdxd"


def connected(client):
    print("Ket noi thanh cong...")
    client.subscribe(AIO_FEED_ID)


def subscribe(client , userdata , mid , granted_qos):
    print("Subcribe thanh cong...")


def disconnected(client):
    print("Ngat ket noi...")
    sys.exit (1)


def message(client, feed_id, payload):
    print("Nhan du lieu: " + payload)
    ser.write((str(payload) + "#").encode())


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

"""
def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        print("port: " + strPort)
        if '/dev/ttyACM0' in strPort:
            commPort = '/dev/ttyACM0'
    return commPort
"""

ser = serial.Serial('/dev/ttyACM0', baudrate=115200)
# run: dmesg | grep tty, to see available usb port
# remember to run this command on cmd to get the permission: sudo chmod a+rw /dev/ttyACM0


mess = ""

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    if splitData[1] == "TEMP":
        client.publish("iot-temp", splitData[2])


def readSerial():
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        global mess # global keyword: to change a mess variable(global var)
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            #print("start,end,len: " + str(start) + " " + str(end) + " " + str(len(mess)))
            processData(mess[start:end + 1])
            if end == len(mess):
                mess = ""
            else:
                mess = mess[end+1:]  # appending the next data frame


while True:
    readSerial()
    time.sleep(1)
