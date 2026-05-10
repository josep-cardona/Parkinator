# 🧠 The "Brain" Node: Intelligence Bridge & Telegram Coordinator

This folder contains the central orchestrator of the smart parking system. Written in Python for the **Arduino App Lab**, this script acts as the nervous system connecting the physical Edge AI cameras, the Cloud LLM, and the end-user via Telegram.

## 🌟 Key Features

* **Demand-Driven Edge Computing:** To save power and bandwidth, this brain actively manages the edge nodes. It sends `START` commands via MQTT to wake up cameras only when a user requests parking in that area, and `STOP` commands to put them back to sleep when the user types `/cancel`.
* **LLM-Powered Geocoding & Reasoning:** Uses a Cloud LLM (Google Gemini) to instantly convert natural language locations (e.g., "Sagrada Familia") into coordinates, calculate proximity, and weigh live availability against historical "busyness" to recommend the safest bet.
* **Live Push Notifications:** Users are "subscribed" to the cameras they are navigating towards. If a spot is taken while the user is driving, the Brain instantly pushes a Telegram alert via MQTT state-change detection.

## 🛠️ Prerequisites

This script is designed to run within the **Arduino App Lab** using the built-in bricks, but requires the following external setups:

1. **Telegram Bot Token:** Obtained from [@BotFather](https://t.me/botfather) on Telegram.
2. **MQTT Broker:** Currently configured to use the public `broker.hivemq.com` for the hackathon prototype.
3. **Arduino Bricks Configuration:**
* `Telegram Bot` brick configured with your token.
* `Cloud LLM` brick configured with Google Gemini access.



*(If running locally outside the App Lab, you will need the `paho-mqtt` Python library).*

## ⚙️ Configuration & Node Registry

### 1. Adding New Cameras

The system uses a hardcoded `node_registry` for the MVP. To add a new camera node to the network, edit the dictionary at the top of the script:

```python
node_registry = {
    "your_camera_id": {
        "street": "Name of the Street",
        "lat": 41.00000, "lon": 2.00000, # Geographic coordinates
        "busyness": 5,                   # Heuristic (1 = quiet, 10 = chaotic)
        "subscribed_users": set()        # Leave empty!
    }
}

```

*Note: The `your_camera_id` must exactly match the MQTT topic ID the edge camera is publishing to.*

### 2. MQTT Topics

The Brain communicates with the edge nodes over specific topics:

* **Listens on:** `smoothoperators/brain/#` (Receives live spot counts from cameras).
* **Publishes to:** `smoothoperators/parkinator/{node_id}` (Sends `START`/`STOP` power commands).

## 💬 Usage & Telegram Commands

Once the script is running, open your Telegram Bot and use the following commands:

* `/park [Location/Landmark]`
* *Example:* `/park Roc Boronat`
* *Action:* The LLM finds the coordinates, searches for cameras within a 1km radius, wakes them up via MQTT, waits for their live feed, and generates a ranked list of recommendations.


* `/cancel`
* *Action:* Unsubscribes the user from all live updates. If a camera suddenly has 0 active watchers, the Brain sends an MQTT `STOP` command to power down the camera's vision processing.