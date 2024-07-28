import os
import json
import zipfile
import time
import requests
import schedule
from datetime import datetime
import docker
import threading
import paho.mqtt.client as mqtt
from collections import defaultdict
from threading import Timer

# Configuration - Update these values with your own settings
config = {
    "mqtt_broker": "YOUR_MQTT_BROKER_IP",
    "mqtt_port": 1883,
    "mqtt_user": "YOUR_MQTT_USERNAME",
    "mqtt_password": "YOUR_MQTT_PASSWORD",
    "zigbee2mqtt_topic": "zigbee2mqtt/#",
    "backup_dir": "/path/to/your/backup/directory",
    "cloud_dir": "your_remote_cloud_directory",
    "discord_webhook_url": "your_discord_webhook_url",
    "notification_interval": 300,  # Time between notifications in seconds
    "uptime_threshold": 300,  # Uptime threshold for zigbee2mqtt restart in seconds
    "offline_device_threshold": 10,  # Number of offline devices to trigger restart
    "check_interval": 10,  # Interval for checking container status in seconds
    "backup_time": "01:45"  # Time for daily backup
}

# Docker client
client = docker.from_env()

# Global state dictionary
device_states = {}
offline_devices_initial = set()
notification_queue = defaultdict(list)

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(config["zigbee2mqtt_topic"])

def on_message(client, userdata, msg):
    global device_states
    topic = msg.topic
    try:
        payload = json.loads(msg.payload)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON message: {e}")
        return

    if 'state' in payload:
        print(f"Received message: {payload}")
        device_states[topic] = payload['state']
        if topic in offline_devices_initial:
            offline_devices_initial.remove(topic)
            notification_queue['online'].append(topic)
        if payload['state'] == 'offline':
            notification_queue['offline'].append(topic)
        check_device_status()

def check_device_status():
    offline_devices = sum(1 for state in device_states.values() if state == 'offline')
    print(f"Offline devices count: {offline_devices}")
    if offline_devices > config["offline_device_threshold"]:
        if check_zigbee2mqtt_uptime():
            urgent_notification_and_restart_services(offline_devices)

def send_discord_notification(message, urgent=False):
    print(f"Sending Discord notification: {message}")
    if urgent:
        data = {'content': f'```diff\n- {message}\n```'}
    else:
        data = {'content': message}
    response = requests.post(config["discord_webhook_url"], json=data)
    return response.status_code == 204

def check_zigbee2mqtt_uptime():
    container = client.containers.get('zigbee2mqtt')
    started_at = datetime.strptime(container.attrs['State']['StartedAt'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
    uptime = time.time() - started_at.timestamp()
    return uptime > config["uptime_threshold"]

def urgent_notification_and_restart_services(offline_devices):
    send_discord_notification(f"Urgent: {offline_devices} devices are offline! Restarting services.", urgent=True)
    client.containers.get('mosquitto').restart()
    client.containers.get('zigbee2mqtt').restart()
    send_discord_notification("Services restarted: mosquitto, zigbee2mqtt", urgent=True)

def backup_and_upload():
    # Create a zip file
    timestamp = datetime.now().strftime('%d%m%Y_%H-%M-%S')
    backup_file = f'zigbee2mqtt_backup_{timestamp}.zip'
    backup_path = os.path.join('/tmp', backup_file)

    with zipfile.ZipFile(backup_path, 'w') as zipf:
        for root, _, files in os.walk(config["backup_dir"]):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                           os.path.join(config["backup_dir"], '..')))

    # Upload to cloud
    upload_success = os.system(f'rclone copy {backup_path} {config["cloud_dir"]}') == 0

    # Send Discord notification
    message = f'Backup created and uploaded: {upload_success}'
    send_discord_notification(message)

    # Clean up the local backup file
    os.remove(backup_path)

    return upload_success

def initial_check_and_backup():
    # Perform initial backup and upload
    backup_and_upload()

def process_notifications():
    global notification_queue
    if notification_queue:
        online_devices = notification_queue['online']
        offline_devices = notification_queue['offline']

        if online_devices:
            online_message = "```diff\n+ Devices online:\n" + "\n".join(online_devices) + "\n```"
            send_discord_notification(online_message)

        if offline_devices:
            offline_message = "```diff\n- Devices offline:\n" + "\n".join(offline_devices) + "\n```"
            send_discord_notification(offline_message)

        notification_queue = defaultdict(list)

    Timer(config["notification_interval"], process_notifications).start()

def monitor_containers():
    while True:
        for container_name in ['mosquitto', 'zigbee2mqtt']:
            try:
                container = client.containers.get(container_name)
                if container.status != 'running':
                    send_discord_notification(f"Container {container_name} is not running!", urgent=True)
            except Exception as e:
                send_discord_notification(f"Error checking container {container_name}: {str(e)}", urgent=True)
        time.sleep(config["check_interval"])

def main():
    # Perform initial check and backup
    initial_c
