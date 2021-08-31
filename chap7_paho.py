import serial.tools.list_ports
import sys
import paho.mqtt.client as paho
import time

broker = "io.adafruit.com"
port = 1883
username = "phamdinhtrung"
password = "aio_DNZB93UIb5X0iR6vDhD8EIteXdxd"

feedPath = "phamdinhtrung/feeds/"
feeds = ["iot-led", "iot-pump", "iot-temp"]

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
    if splitData[1] == "iot-temp":
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
pubInfo = {"iot-temp": [0, 0.0, True], "iot-led": [0, 0.0, True], "iot-pump": [0, 0.0, True]}
#              value,time capture since publish, success publish?


def publish(feed, value):
    global pubInfo
    if pubInfo[feed][2]:
        client.publish(feedPath+feed, value)
        pubInfo[feed][1] = time.time()
        pubInfo[feed][0] = value
        pubInfo[feed][2] = False  # set the flag, the flag will turn true if receive a respond on time


def checkPublish():
    for feed in feeds:
        if pubInfo[feed][2] is False and time.time() - pubInfo[feed][1] > 3:  # resend after 2 second without response
            print("Publish again to ", feed, " due to failure")
            pubInfo[feed][2] = True
            publish(feed, pubInfo[feed][0])


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
    if not pubInfo[feed_id][2]:  # if we get the response of which feed we send to, means succesfully publish
        print("Publish successfully to ", feed_id)
        pubInfo[feed_id][2] = True
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
    # client.publish(feedPath+feeds[2], random.randint(0, 100), qos=0)
    checkPublish()
    readSerial()
    #time.sleep(1)

