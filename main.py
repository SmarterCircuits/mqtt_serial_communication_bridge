import network
from umqtt.simple import MQTTClient
from comms import Comms
import json
import time
import _thread

# Set the SSID and passphrase of the wifi network
ssid = ''
password = ''

# Set the IP address of the MQTT broker
mqtt_server = '192.168.2.200'

# Set the allowed sources the bridge accepts messages from
allowed_sources = ['web1']

def on_message(t, msg):
    json_str = msg.decode('utf-8')
    data = json.loads(json_str)
    if data['source'] not in allowed_sources:
        return
    token = gen_token(data['source'])
    if token != data['token']:
        return
    comms.send(data['payload'])
    
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

def mqtt_loop():
    while True:
        # Blocking wait for message
        mqtt_client.wait_msg()

def serial_loop():
    while True:
        try:
            message = comms.read()
            if message is not None:
                mqtt_client.publish('command', message)
        except:
            #serial state can be weird after power drops, this is a sledgehammer to prevent that from interupting startup
            pass
        time.sleep(0.2)
    
mqtt_client = None
comms = None

if __name__ == "__main__":
    print("Local time is：%s" %str(time.localtime()))
    print("connecting to wifi...")
    # Connect to the Wi-Fi network
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(ssid, password)
    # Wait for the connection to be established
    while not sta_if.isconnected():
        pass
    
    print("connected to wifi. connecting to MQTT broker...")
    
    mqtt_client = MQTTClient("mqtt_serial_bridge", mqtt_server)
    mqtt_client.set_callback(on_message)
    mqtt_client.connect()
    mqtt_client.subscribe(b"serial_bridge")
    
    print("connected to MQTT broker. initializing serial communications...")
    
    comms = Comms()
    
    print("Serial communications initialized. Starting threads.")
    
    _thread.start_new_thread(mqtt_loop, ())
    serial_loop()
    
