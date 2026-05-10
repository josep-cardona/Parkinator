import paho.mqtt.client as mqtt
from arduino.app_utils import App
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
import time
import random

# --- CONFIGURATION ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smoothoperators/parkinator/rocboronat" 
BRAIN_TOPIC = "smoothoperators/brain/rocboronat"

video_detector = VideoObjectDetection(confidence=0.4, debounce_sec=1.5)
Active = False
Empty = 8

def on_all_detections(detections: dict):
    global Empty
    Empty = 0
    for key, values in detections.items():
        for value in values:
            Empty += 1
    print(f"Empty spots detected: {Empty}")
    client.publish(BRAIN_TOPIC, f"{Empty}")
    time.sleep(5)


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Sensor Node Connected to HiveMQ!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Connection failed: {rc}")

def on_message(client, userdata, msg):
    global Active
    
    payload = msg.payload.decode("utf-8").upper()
    print(f"📩 MQTT Received: {payload}")
     
    Active = not Active
    
    client.publish(BRAIN_TOPIC, f"{Empty}")
    
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    client = mqtt.Client()

video_detector.on_detect_all(on_all_detections)

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

App.run() 

