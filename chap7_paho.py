"""
Paho
Checking error, publish again in 2s, publish again for 3 times
"""
import serial.tools.list_ports
import sys
import paho.mqtt.client as paho
import time

broker = "io.adafruit.com"
port = 1883
username = "phamdinhtrung"
password = "aio_DNZB93UIb5X0iR6vDhD8EIteXdxd"

feedPath = "phamdinhtrung/feeds/"
feeds = ["iot-led", "iot-pump", "iot-temp", "iot-humid"]

# Serial function **************************************************************************************************
mess = ""


def getPort():
    ports = serial.tools.list_ports.comports()
    n_port = len(ports)
    comport = "None"
    for i in range(0, n_port):
        port = ports[i]
        strport = str(port)
        print(strport)
        # "USB Serial"
        if "Arduino Uno" in strport:
            splitport = strport.split(" ")
            comport = splitport[0]
    return comport


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    #print(splitData)
    if splitData[1] == "iot-temp" or splitData[1] == "iot-humid":
        print("Receive ", splitData, " from Arduino gateway. Ready to publish...")
        publish(splitData[1], splitData[2])


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


# Publish and check error *******************************************************************************************
class FeedInfo:
    def __init__(self):
        self.time = 0.0  # time when publish
        self.isPublishing = False  # ready to publish
        self.count = 0  # number of time we republish

        self.queue = []

    def init(self):
        self.time = time.time()
        self.isPublishing = True
        self.count = 0

    def resetForSendAgain(self):
        self.time = time.time()
        self.count = self.count + 1

# create pubInfo to store infomation of publishing
pubInfo = {}
for feed in feeds:
    pubInfo[feed] = FeedInfo()


def publish(feed, value):
    pubInfo[feed].queue.append(value)



def checkPublish():
    for feed in feeds:  # frequently check publishing status of each feed
        feedInfo = pubInfo[feed]
        if not feedInfo.isPublishing and len(feedInfo.queue) > 0:  # if this feed is not publishing and have data in queue
            print("Start sending value: ", feedInfo.queue[0], "to feed ", feed)
            feedInfo.init()
            client.publish(feedPath + feed, feedInfo.queue[0])

        elif feedInfo.isPublishing:  # if this feed is currently trying to publish
            if feedInfo.count < 3:
                if time.time() - feedInfo.time > 3:  # send again after 2s without response
                    print("Sending again value: ", feedInfo.queue[0], "of feed ", feed, ". Time(s): ", feedInfo.count)
                    feedInfo.resetForSendAgain()
                    client.publish(feedPath + feed, feedInfo.queue[0])  # send again
            else:  # stop sending again after 3 times
                print("Stop sending again value: ", feedInfo.queue[0], "of feed ", feed)
                feedInfo.queue.pop(0)
                feedInfo.isPublishing = False


# Callback function **************************************************************************************************
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connect successfully to server...")
        for feed in feeds:
            client.subscribe(topic=feedPath+feed)
    else:
        print("Bad connection")
        sys.exit(1)


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribe successfully to feed...")


def on_message(client, userdata, message):
    feed_id = message.topic.split("/")[2]
    payload = message.payload.decode("utf-8")
    if pubInfo[feed_id].isPublishing:  # if we get the response from feed which is trying to publishing
        print("Publish successfully value: ", payload, " to feed ", feed_id)
        pubInfo[feed_id].isPublishing = False
        pubInfo[feed_id].queue.pop(0)
    else:
        print("Receive value ", payload, " from feed ", feed_id)
        ser.write(("!0:"+feed_id+":"+str(payload)+"#").encode())  # dataframe to send to arduino: !0:iot-temp:30#


def on_disconnect(client):
    print("Disconnect...")
    sys.exit (1)


# Setup callback function and client object ***************************************************************************
client = paho.Client("LAPTOP")
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_disconnect = on_disconnect


# Setup connection to server *******************************************************************************************
client.username_pw_set(username, password)
client.connect(broker, port=port, keepalive=20)
client.loop_start()


# Setup COM for Arduino *********************************************************************************************
ser = serial.Serial(port=getPort(), baudrate=115200)
print("Connect successfully to Arduino...")

while True:
    checkPublish()
    readSerial()