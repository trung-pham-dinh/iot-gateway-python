import serial.tools.list_ports
import time
import sys
from Adafruit_IO import MQTTClient


AIO_FEED_ID = ["iot-led", "iot-pump", "iot-temp"]
AIO_USERNAME = "phamdinhtrung"
AIO_KEY = "aio_DNZB93UIb5X0iR6vDhD8EIteXdxd"


def connected(client):
    print("Ket noi thanh cong...")
    for feed in AIO_FEED_ID:  # subcribe to all feeds
        client.subscribe(feed)


def subscribe(client , userdata , mid , granted_qos):
    print("Subcribe thanh cong...")


def disconnected(client):
    print("Ngat ket noi...")
    sys.exit (1)


def message(client, feed_id, payload):
    if not feedPub[feed_id][2]:  # if we get the response of which feed we send to, means succesfully publish
        print("Publish successfully!")
        feedPub[feed_id][2] = True
    else:
        print("Nhan du lieu tu " + str(feed_id) + ": " + payload)  # get the response from a feed we didnt send to before
        ser.write(("!0:"+feed_id+":"+str(payload)+"#").encode())  # dataframe to send to arduino: !0:iot-temp:30#


#


feedPub = {"iot-temp": [0, 0.0, True], "iot-led": [0, 0.0, True], "iot-pump": [0, 0.0, True]}
#              value,time capture since publish, success publish?


def publish(feed, value):
    global feedPub
    if feedPub[feed][2]:
        client.publish(feed, value)
        feedPub[feed][1] = time.time()
        feedPub[feed][0] = value
        feedPub[feed][2] = False # set the flag, the flag will turn true if receive a respond on time


def checkPublish():
    for feed in AIO_FEED_ID:
        if feedPub[feed][2] is False and time.time() - feedPub[feed][1] > 2:  # resend after 2 second without response
            print("Send again!")
            feedPub[feed][2] = True
            publish(feed, feedPub[feed][0])


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()


def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        print(strPort)
        # "USB Serial"
        if "USB Serial" in strPort:
            splitPort = strPort.split(" ")
            commPort = splitPort[0]
    return commPort


ser = serial.Serial(port="COM3", baudrate=115200)


mess = ""


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    if splitData[1] == "iot-temp":
        print("Temperature: " + splitData[2] + ". Ready to publish to iot-temp...")
        publish("iot-temp", splitData[2])


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
    checkPublish()
    readSerial()
    time.sleep(1)
