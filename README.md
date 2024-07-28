<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zigbee2MQTT Monitor and Backup Script</title>
</head>
<body>
    <h1>Zigbee2MQTT Monitor and Backup Script</h1>
    
    <p>This script is designed to monitor the state of Zigbee2MQTT (Z2M) devices, automate backups, and handle device connectivity issues that may occur due to interferences. It can restart services and notify you through Discord when specific conditions are met.</p>
    
    <h2>Features</h2>
    <ul>
        <li>Monitors the state of Zigbee2MQTT devices.</li>
        <li>Automates daily backups of Zigbee2MQTT data.</li>
        <li>Notifies you via Discord about device statuses (online/offline).</li>
        <li>Automatically restarts Zigbee2MQTT and Mosquitto services if a specified number of devices go offline.</li>
    </ul>
    
    <h2>Configuration</h2>
    <p>The script uses a configuration dictionary to manage its settings. You can adjust the following parameters:</p>
    <ul>
        <li><strong>mqtt_broker:</strong> The IP address of the MQTT broker.</li>
        <li><strong>mqtt_port:</strong> The port number of the MQTT broker.</li>
        <li><strong>mqtt_user:</strong> The username for MQTT authentication.</li>
        <li><strong>mqtt_password:</strong> The password for MQTT authentication.</li>
        <li><strong>zigbee2mqtt_topic:</strong> The MQTT topic to subscribe to for Zigbee2MQTT updates.</li>
        <li><strong>backup_dir:</strong> The directory where Zigbee2MQTT data is stored.</li>
        <li><strong>cloud_dir:</strong> The remote directory for storing backups.</li>
        <li><strong>discord_webhook_url:</strong> The Discord webhook URL for notifications.</li>
        <li><strong>notification_interval:</strong> Time between notifications in seconds.</li>
        <li><strong>uptime_threshold:</strong> Uptime threshold for Zigbee2MQTT restart in seconds.</li>
        <li><strong>offline_device_threshold:</strong> Number of offline devices to trigger a restart.</li>
        <li><strong>check_interval:</strong> Interval for checking container status in seconds.</li>
        <li><strong>backup_time:</strong> Time for daily backup in "HH:MM" format.</li>
    </ul>
    
    <h2>Installation</h2>
    <p>Follow these steps to set up the script:</p>
    <ol>
        <li>Create a virtual environment:</li>
        <pre><code>python3 -m venv /home/meaning/scripts/venv</code></pre>
        <li>Activate the virtual environment:</li>
        <pre><code>source /home/meaning/scripts/venv/bin/activate</code></pre>
        <li>Install the required dependencies:</li>
        <pre><code>pip install schedule requests docker paho-mqtt</code></pre>
    </ol>
    
    <h2>Running the Script</h2>
    <p>You can run the script manually or set it up as a systemd service for automatic startup:</p>
    
    <h3>Manual Run</h3>
    <pre><code>python /home/meaning/scripts/zigbee2mqtt_monitor.py</code></pre>
    
    <h3>Systemd Service</h3>
    <p>To run the script as a systemd service, create a service file:</p>
    <pre><code>sudo nano /etc/systemd/system/zigbee2mqtt_monitor.service</code></pre>
    <p>Add the following configuration:</p>
    <pre><code>[Unit]
Description=Zigbee2MQTT Monitor Service
After=network.target

[Service]
User=root
WorkingDirectory=/home/meaning/scripts
ExecStart=/home/meaning/scripts/venv/bin/python /home/meaning/scripts/zigbee2mqtt_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
</code></pre>
    <p>Reload systemd, enable, and start the service:</p>
    <pre><code>sudo systemctl daemon-reload
sudo systemctl enable zigbee2mqtt_monitor.service
sudo systemctl start zigbee2mqtt_monitor.service
sudo systemctl status zigbee2mqtt_monitor.service</code></pre>
    
    <h2>Usage</h2>
    <p>Once the script is running, it will automatically monitor your Zigbee2MQTT devices, perform backups, and send notifications based on the configuration settings. If a specified number of devices go offline, the script will restart the necessary services and notify you via Discord.</p>
    
    <h2>Contributing</h2>
    <p>Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request on GitHub.</p>
    
    <h2>License</h2>
    <p>This project is licensed under the MIT License. See the LICENSE file for more details.</p>
    
    <h2>Acknowledgements</h2>
    <p>Special thanks to the contributors and the community for their valuable input and support.</p>
</body>
</html>

