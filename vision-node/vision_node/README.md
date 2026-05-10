# 👁️ Vision Node: Real-Time Edge Occupancy Detector

This repository folder contains the code for the **Vision Node**, the eyes of the Parkinator system. Built to run inside the **Arduino App Lab**, this script processes real-time video feeds using edge AI to detect available parking spots and reports them back to the Central Brain via MQTT.

## 🌟 Overview

Instead of sending heavy video streams to a central server, the Vision Node processes frames locally. It utilizes a custom-trained object detection model to identify empty parking spaces (represented in our PoC by orange circles).

To maximize energy efficiency, the Vision Node operates on a **Demand-Driven** architecture: it listens for commands from the Central Brain and only begins actively reporting data when a user is actively looking for parking in its designated area.

## ⚙️ How It Works

1. **Local Object Detection:** The script uses the `VideoObjectDetection` brick from the Arduino App Lab, configured with a confidence threshold (`0.4`) and a debounce timer (`1.5s`) to prevent flickering data.
2. **State Toggling:** It subscribes to an MQTT topic (e.g., `smoothoperators/parkinator/rocboronat`). When the Central Brain requests data, the node wakes up.
3. **Data Broadcasting:** Every time empty spots are detected, it counts the total number of free spaces and publishes this integer to the Brain's listening topic (`smoothoperators/brain/rocboronat`).
4. **Bandwidth Optimization:** A small delay (`time.sleep(5)`) is implemented to prevent spamming the MQTT broker while still providing near-real-time updates to the driver.

## 🛠️ Configuration

Before running the node, you must configure the MQTT topics to match the node's physical location. Update the following variables at the top of the script:

```python
# The MQTT Broker (Public HiveMQ for the MVP)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

# The topic this node LISTENS to for Sleep/Wake commands
MQTT_TOPIC = "smoothoperators/parkinator/[YOUR_NODE_ID]" 

# The topic this node PUBLISHES spot counts to
BRAIN_TOPIC = "smoothoperators/brain/[YOUR_NODE_ID]"

```

*(Make sure `[YOUR_NODE_ID]` perfectly matches the ID registered in the Central Brain's `node_registry`, e.g., `rocboronat`).*

## 🚀 Running the Node

1. Open the **Arduino App Lab**.
2. Create a new App and add the **Video Object Detection** brick.
3. Configure the brick with your trained Edge Impulse model (which detects the empty spot markers).
4. Paste this Python script into the `main.py` file.
5. Ensure your camera is properly positioned over your parking setup.
6. Click **Run**.

Once started, the node will connect to the HiveMQ broker and wait quietly. You will see `✅ Sensor Node Connected to HiveMQ!` in the console. As soon as a user requests parking in this area via Telegram, the node will toggle active and begin publishing the live spot count.
