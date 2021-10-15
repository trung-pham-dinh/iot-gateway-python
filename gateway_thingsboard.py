# https://iot.stackexchange.com/questions/4167/how-to-send-data-to-thingsboard-using-mqtt-in-python
# https://bytesofgigabytes.com/thingsboard/sending-data-to-thingsboard-using-python/

import time
import paho.mqtt.client as mqttclient
import serial.tools.list_ports
import json
print("Paho MQTT")

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "6MzKNRVTuiXDr5CcQ13E"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'LED': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['LED'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        pass


def  connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


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
    global lat, lon
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    #print(splitData)
    if splitData[1] == "iot-lat":
        str_int = splitData[2][0:2]
        str_flt = splitData[2][2:]
        res = float(str_int) + float(str_flt) / 60
        lat = str(res)
        print("lat: ", lat)
    if splitData[1] == "iot-lon":
        str_int = splitData[2][0:3]
        str_flt = splitData[2][3:]
        res = float(str_int) + float(str_flt) / 60
        lon = str(res)
        print("lon: ", lon)



mess = ""
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



client = mqttclient.Client("TrungGateway")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()


client.on_subscribe = subscribed
client.on_message = recv_message


temp = 30
humi = 50
lat = 0
lon = 0
counter = 0
ser = serial.Serial(port=getPort(), baudrate=115200)
while True:
    readSerial();
    counter +=1
    if(counter >=10):
        counter = 0
        collect_data = {'temperature': temp, 'humidity': humi, 'lat':lat, 'lon':lon}
        temp += 1
        humi += 1
        client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)

    time.sleep(1)

