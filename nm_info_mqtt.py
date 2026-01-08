#!/usr/bin/env python3
import asyncio
import json
import paho.mqtt.client as mqtt
from nm_info import (
    scan_wifi_networks,
    list_wifi_networks,
    get_wired_network_info,
    get_wireless_network_info,
    filter_network_list,
    # The following functions can be implemented similarly if needed
    # create_new_wifi_connection,
    # delete_wifi_connection,
    # activate_wifi_connection,
    # deactivate_wifi_connection,
    # list_all_connections
)

class NetworkManagerMQTT:
    def __init__(self, broker_host='localhost', broker_port=1883, topic_prefix='nm/'):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic_prefix = topic_prefix
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.loop = None  # Will be set in main block

    def start(self):
        self.client.connect(self.broker_host, self.broker_port, 60)
        self.client.loop_start()
        self.client.subscribe(f"{self.topic_prefix}#")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"Connected to MQTT broker with result code {rc}")
        client.subscribe(f"{self.topic_prefix}#")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        print(f"Received message on {topic}: {payload}")
        # Dispatch based on topic
        if topic == f"{self.topic_prefix}scan_wifi":
            asyncio.run_coroutine_threadsafe(self.handle_scan_wifi(payload), self.loop)
        elif topic == f"{self.topic_prefix}list_wifi":
            asyncio.run_coroutine_threadsafe(self.handle_list_wifi(payload), self.loop)
        elif topic == f"{self.topic_prefix}wired_info":
            asyncio.run_coroutine_threadsafe(self.handle_wired_info(payload), self.loop)
        elif topic == f"{self.topic_prefix}wireless_info":
            asyncio.run_coroutine_threadsafe(self.handle_wireless_info(payload), self.loop)
        # Add more topic handlers as needed

    async def handle_scan_wifi(self, payload):
        interface = payload if payload else None
        self.publish(f"{self.topic_prefix}scan_wifi_resp", json.dumps({"status": "scan requested"}))
        print("Scanning for WiFi networks...")
        networks = await scan_wifi_networks(interface)
        print(f"Found {len(networks)} networks")
        filtered_networks = await filter_network_list(networks, unique_ssids=True, best_signal=True, show_hidden=False)
        print(f"Filtered to {len(filtered_networks)} unique networks")
        self.publish(
            f"{self.topic_prefix}scan_wifi_resp",
            json.dumps({
            "status": "scan complete",
            "networks_found": len(networks),
            "unique_networks": len(filtered_networks)   
            })
        )
        self.publish_networks(filtered_networks)

    async def handle_list_wifi(self, payload):
        print("Handling list_wifi")
        interface = payload if payload else None
        networks = await list_wifi_networks(interface)
        self.publish_networks(networks)


    async def handle_wired_info(self, payload):
        print("Handling wired_info")
        interface = payload if payload else None
        print(f"Getting wired info for interface: {interface}")
        info = await get_wired_network_info(interface)
        print(f"Wired info: {info}")
        self.publish(f"{self.topic_prefix}wired_info_resp", json.dumps(info))

    async def handle_wireless_info(self, payload):
        print("Handling wireless_info")
        interface = payload if payload else None
        info = await get_wireless_network_info(interface)
        self.publish(f"{self.topic_prefix}wireless_info_resp", json.dumps(info))

    def publish(self, topic, message):
        self.client.publish(topic, message)

    def publish_networks(self, networks):
        for network in networks:
            self.publish(f"{self.topic_prefix}list_wifi_resp", json.dumps(network))
        

# Example usage
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    nm_mqtt = NetworkManagerMQTT(broker_host='localhost', broker_port=1883)
    nm_mqtt.loop = loop
    try:
        nm_mqtt.start()
        loop.run_forever()
    except KeyboardInterrupt:
        nm_mqtt.stop()
        loop.stop()
