import random
import time
import sys
from Adafruit_IO import MQTTClient

AIO_FEED_ID = ["iot-led", "iot-temp"]
AIO_USERNAME = "phamdinhtrung"
AIO_KEY = "aio_DNZB93UIb5X0iR6vDhD8EIteXdxd"


def connected(client):
    print("Ket noi thanh cong...")
    for feed in AIO_FEED_ID:
        client.subscribe(feed)


def subscribe(client , userdata, mid, granted_qos):
    print("Subscribe thanh cong...")


def disconnected(client):
    print("Ngat ket noi...")
    sys.exit (1)


feedPub = {"iot-temp": [0, 0.0, True], "iot-led": [0, 0.0, True]}
#                        value,time,success

def message(client, feed_id, payload):
    if not feedPub[feed_id][2]:
        print("Publish successfully!")
        feedPub[feed_id][2] = True
    else:
        print("Nhan du lieu: " + payload)


def checkPublish():
    for feed in AIO_FEED_ID:
        if feedPub[feed][2] == False and time.time() - feedPub[feed][1] > 1000:
            print("Send again!")
            feedPub[feed][2] = True
            publish(feed, feedPub[feed][0])


def publish(feed, value):
    global feedPub
    if feedPub[feed][2]:
        client.publish(feed, value)
        feedPub[feed][1] = time.time()
        feedPub[feed][0] = value
        feedPub[feed][2] = False






client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

while True:
    value = random.randint(0, 100)
    print("Publish:", value)

    checkPublish()
    publish("iot-temp", value)

    time.sleep(10)