import paho.mqtt.client as mqtt
import time
import json

def gen_token(source):
    ts = time.localtime()
    token = ''
    tsi = 0
    for c in source:
        token = f"{token}{ord(c)}{ts[tsi]}"
        tsi = tsi + 1
        if tsi > 4:
            tsi = 0
    return token


client = mqtt.Client()

client.connect('192.168.2.200')
topic = 'serial_bridge'

message = {
    'source': 'web1',
    'token': gen_token('web1'),
    'payload':'another test'
}

client.publish(topic, json.dumps(message))
