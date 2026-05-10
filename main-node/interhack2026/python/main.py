# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
# SPDX-License-Identifier: MPL-2.0

import time
import math
from arduino.app_bricks.telegram_bot import TelegramBot, Sender, Message
from arduino.app_bricks.cloud_llm import CloudLLM, CloudModel
from arduino.app_utils import App
import paho.mqtt.client as mqtt

# --- 1. GLOBAL DATABASES ---
node_registry = {
    "rocboronat": {
        "street": "Roc Boronat",
        "lat": 41.403770, "lon": 2.193262,
        "busyness": 5, 
        "subscribed_users": set() # Keeps track of who is watching this node
    },
    "sagradafamilia": {
        "street": "Basílica de la Sagrada Família",
        "lat": 41.40388072632617, "lon": 2.1743116478002236,
        "busyness": 9, 
        "subscribed_users": set()
    }
}

latest_node_data = {} 
users_db = {}

# --- 2. MQTT CONFIGURATION ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_SUB = "smoothoperators/brain/#"
MQTT_TOPIC_SEND = "smoothoperators/parkinator" 

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ Connected to MQTT! Listening to: {MQTT_TOPIC_SUB}")
    client.subscribe(MQTT_TOPIC_SUB)

def on_message(client, userdata, msg):
    topic_parts = msg.topic.split("/")
    payload = msg.payload.decode("utf-8")
    
    if len(topic_parts) >= 3:
        node_id = topic_parts[2]
        if node_id in node_registry:
            old_spots = latest_node_data.get(node_id)
            latest_node_data[node_id] = payload
            
            # PUSH NOTIFICATION LOGIC
            if old_spots is not None and old_spots != payload:
                print(f"🚨 STATE CHANGE: {node_id} went from {old_spots} to {payload} spots!")
                # Notify everyone in the subscribed_users list for this node
                for chat_id in list(node_registry[node_id]["subscribed_users"]):
                    if chat_id in users_db:
                        try:
                            street = node_registry[node_id]["street"]
                            icon = "🟢" if int(payload) > 0 else "🔴"
                            users_db[chat_id]["sender_obj"].reply(f"🔔 *LIVE UPDATE* 🔔\n{icon} {street} now has {payload} spots available!")
                        except:
                            pass

try:
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    mqtt_client = mqtt.Client()
    
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start() 

# --- 3. MATH & LLM SETUP ---
bot = TelegramBot()
llm = CloudLLM(model=CloudModel.GOOGLE_GEMINI, system_prompt="You are a strict data API.")

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_coordinates_from_llm(user_text):
    prompt = f"Provide the latitude and longitude of '{user_text}' in Barcelona. Reply ONLY with numbers separated by a comma like '41.123, 2.456'."
    response = ""
    for chunk in llm.chat_stream(prompt):
        response += chunk
    try:
        parts = response.split(",")
        return float(parts[0].strip()), float(parts[1].strip())
    except:
        return None, None

def unsubscribe_user_from_all(chat_id):
    """Safely removes a user from all nodes and puts nodes to sleep if empty"""
    if chat_id in users_db:
        for node_id in users_db[chat_id]["subscribed_nodes"]:
            if chat_id in node_registry[node_id]["subscribed_users"]:
                node_registry[node_id]["subscribed_users"].remove(chat_id)
                # 🛑 SLEEP TRIGGER: List went from 1 to 0
                if len(node_registry[node_id]["subscribed_users"]) == 0:
                    print(f"💤 No users need {node_id}. Putting camera to SLEEP to save power.")
                    mqtt_client.publish(f"{MQTT_TOPIC_SEND}/{node_id}", "STOP")
        users_db[chat_id]["subscribed_nodes"] = []

def init_user(sender_obj):
    chat_id = sender_obj.chat_id
    if chat_id not in users_db:
        users_db[chat_id] = {
            "current_lat": 41.3910, 
            "current_lon": 2.1806,
            "target_name": None,
            "subscribed_nodes": [],
            "sender_obj": sender_obj 
        }
    else:
        users_db[chat_id]["sender_obj"] = sender_obj

# --- 4. TELEGRAM HANDLERS ---
def park_cmd(sender: Sender, message: Message):
    init_user(sender)
    chat_id = sender.chat_id
    
    # If they ask for parking, clean up their old session first
    unsubscribe_user_from_all(chat_id)
    
    user_request = message.text.replace("/park", "").strip()
    if not user_request:
        sender.reply("⚠️ Usage: `/park [Address or Landmark]`")
        return

    sender.reply(f"🤖 Searching for coordinates for '{user_request}'...")
    
    target_lat, target_lon = get_coordinates_from_llm(user_request)
    if target_lat is None:
        sender.reply("❌ Could not find that location.")
        return
        
    SEARCH_RADIUS_KM = 3
    nearby_nodes = []
    
    for node_id, data in node_registry.items():
        if calculate_distance(target_lat, target_lon, data["lat"], data["lon"]) <= SEARCH_RADIUS_KM:
            nearby_nodes.append(node_id)
            
    if not nearby_nodes:
        sender.reply(f"❌ No cameras within {SEARCH_RADIUS_KM}km.")
        return
        
    users_db[chat_id]["target_name"] = user_request
    users_db[chat_id]["subscribed_nodes"] = nearby_nodes
    
    nodes_to_wait_for = []
    
    # --- WAKE UP TRIGGER ---
    for node_id in nearby_nodes:
        # If list was empty, this is the first user! WAKE THE NODE UP.
        if len(node_registry[node_id]["subscribed_users"]) == 0:
            print(f"⚡ User requested {node_id}. WAKING UP CAMERA.")
            latest_node_data[node_id] = None 
            mqtt_client.publish(f"{MQTT_TOPIC_SEND}/{node_id}", "START")
            nodes_to_wait_for.append(node_id)
            
        # Add user to the node's tracking list
        node_registry[node_id]["subscribed_users"].add(chat_id)
    
    # Only wait for data from cameras we just woke up (cached data is instant)
    if nodes_to_wait_for:
        sender.reply(f"📡 Waking up {len(nodes_to_wait_for)} sleeping camera(s)...")
        timeout = 5.0
        elapsed = 0.0
        while elapsed < timeout:
            if all(latest_node_data[n_id] is not None for n_id in nodes_to_wait_for):
                break
            time.sleep(0.5)
            elapsed += 0.5

    # (Context Building & LLM logic remains identical...)
    results_str = ""
    valid_spots_found = False
    
    for node_id in nearby_nodes:
        spots_str = latest_node_data.get(node_id)
        if spots_str and spots_str.isdigit() and int(spots_str) > 0:
            valid_spots_found = True
            d_target = calculate_distance(target_lat, target_lon, node_registry[node_id]["lat"], node_registry[node_id]["lon"])
            d_user = calculate_distance(users_db[chat_id]["current_lat"], users_db[chat_id]["current_lon"], node_registry[node_id]["lat"], node_registry[node_id]["lon"])
            results_str += f"- Location: {node_registry[node_id]['street']}\n  Free spots: {spots_str}\n  Dist to destination: {d_target:.1f} km\n  Dist from you: {d_user:.1f} km\n  Busyness (1-10): {node_registry[node_id]['busyness']}\n\n"
            
    if not valid_spots_found:
        sender.reply("⚠️ All nearby spots are full or offline.")
        return

    final_prompt = f"""
    The user wants to park near {user_request}. 
    Here is the live data from our IoT cameras:
    
    {results_str}
    
    Note on 'Busyness': A score of 10 means highly trafficked, so spots might disappear before the user arrives. A low score is a safer bet.
    
    Task: 
    Recommend up to the top 5 options. Format as a clean numbered list.
    For each option, include:
    - The street name and number of free spots.
    - A short 1-sentence reason WHY you ranked it here (weighing the distance to destination vs busyness level).
    - The Map Link.
    Keep your language friendly and concise.
    
    """    
    final_resp = ""
    for chunk in llm.chat_stream(final_prompt):
        final_resp += chunk
        
    sender.reply(final_resp)
    sender.reply("👀 *You are subscribed.* When you park, type `/cancel` to turn off the cameras and save energy!")

def cancel_cmd(sender: Sender, message: Message):
    unsubscribe_user_from_all(sender.chat_id)
    sender.reply("✅ Subscriptions cancelled. Have a great day!")

bot.add_command("park", park_cmd, "Get AI parking recommendation")
bot.add_command("cancel", cancel_cmd, "Stop live parking notifications")

print("Demand-Driven Brain Online... Press Ctrl+C to stop.")
App.run()