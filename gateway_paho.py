# https://io.adafruit.com/api/docs/mqtt.html#adafruit-io-mqtt-api
# http://www.steves-internet-guide.com/into-mqtt-python-client/

import sys
import paho.mqtt.client as paho
import random
import time

feedPath = "phamdinhtrung/feeds/"
topic = ["iot-led", "iot-pump", "iot-temp"]


def on_connect(client, userdata, flags, rc):  # http://www.steves-internet-guide.com/client-connections-python-mqtt/
    if rc == 0:
        print("connected OK Returned code =", rc)
        print("subcribe(result, mid): ", client.subscribe(topic=feedPath+topic[0], qos=0))
    else:
        print("Bad connection Returned code = ", rc)


def on_log(client, userdata, level, buf):  # every sending or receiving action will call this function (publish, subcribe, keep alive,...)
    print("on_log: ", buf)


def on_subscribe(client, userdata, mid, granted_qos):
    print("on_subscribe: mid value = ", mid)


def on_message(client, userdata, message):
    # print("on_message:  payload=", str(message.payload.decode("utf-8")), ", topic=", message.topic, ", retained=", message.retain)
    # if message.retain == 1:
    #     print("This is a retained message")
    feed_id = message.topic.split("/")[2]
    payload = message.payload.decode("utf-8")
    print("Receive value ", payload, " from feed ", feed_id)


def on_publish(client, userdata, mid):  # http://www.steves-internet-guide.com/publishing-messages-mqtt-client/
    print("on_publish(mid): ", mid)


broker = "io.adafruit.com"
port = 1883
username = "phamdinhtrung"
password = "aio_DNZB93UIb5X0iR6vDhD8EIteXdxd"


client = paho.Client("PC")
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_publish = on_publish
client.on_message = on_message
client.on_log = on_log


client.username_pw_set(username, password)
client.connect(broker, port=1883, keepalive= 20) # keepalive: http://www.steves-internet-guide.com/mqtt-keep-alive-by-example/
client.loop_start()


while True:
    client.publish("phamdinhtrung/feeds/iot-temp", random.randint(0, 100), qos=1)
    time.sleep(5)
