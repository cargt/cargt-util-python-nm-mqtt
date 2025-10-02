#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
networkmanager mqtt subscriber
"""
import paho.mqtt.client as paho

import sdbus

from sdbus_block.networkmanager import (
    NetworkDeviceGeneric,
    NetworkDeviceWireless,
    NetworkDeviceWired,
    NetworkManager,
    IPv4Config,
)

from sdbus_block.networkmanager.enums import DeviceType

def on_message(mosq, obj, msg):
    # print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
    print("%s: %s" % (msg.topic, msg.payload))
    response_topic = ""
    response_payload = ""
    
    sdbus.set_default_bus(sdbus.sd_bus_open_system())
    network_manager = NetworkManager()

    if(msg.topic == "nm_cli/device_info"):
        all_devices = {path: NetworkDeviceGeneric(path) for path in network_manager.devices}
        decoded_msg_payload = msg.payload.decode('utf-8')

        if (decoded_msg_payload == "ethernet") or (decoded_msg_payload == "all"):
            response_topic = "nm_cli/device_info_resp"
            ethernet_devices = [
                NetworkDeviceWired(path)
                for path, device in all_devices.items()
                if device.device_type == DeviceType.ETHERNET
            ]

            for device in ethernet_devices:
                print(device.interface, ' [', device.hw_address, ']', )
                response_payload += device.interface + ' [' + device.hw_address + ']' + '\r\n'
                device_ip4_conf_path = device.ip4_config
                ip4_conf = IPv4Config(device_ip4_conf_path)
                for address_data in ip4_conf.address_data:
                    if device_ip4_conf_path == '/':
                        # This is how NetworkManager indicates there is no ip config
                        # for the interface
                        continue
                    else:
                        ip4_conf = IPv4Config(device_ip4_conf_path)
                        for address_data in ip4_conf.address_data:
                            print('     ', address_data['address'][1], '/', str(address_data['prefix'][1]), '\r\n')
                            response_payload += '     ' + address_data['address'][1] + '/' + str(address_data['prefix'][1]) + '\r\n'

    
        if (decoded_msg_payload == "wifi") or (decoded_msg_payload == "all"):
            response_topic = "nm_cli/device_info_resp"
            wifi_devices = [
                NetworkDeviceWireless(path)
                for path, device in all_devices.items()
                if device.device_type == DeviceType.WIFI
            ]

            for device in wifi_devices:
                print(device.interface, ' [', device.hw_address, ']', )
                response_payload += device.interface + ' [' + device.hw_address + ']' + '\r\n'
                device_ip4_conf_path = device.ip4_config
                ip4_conf = IPv4Config(device_ip4_conf_path)
                for address_data in ip4_conf.address_data:
                    if device_ip4_conf_path == '/':
                        # This is how NetworkManager indicates there is no ip config
                        # for the interface
                        continue
                    else:
                        ip4_conf = IPv4Config(device_ip4_conf_path)
                        for address_data in ip4_conf.address_data:
                            print('     ', address_data['address'][1], '/', str(address_data['prefix'][1]), '\r\n') 
                            response_payload += '     ' + address_data['address'][1] + '/' + str(address_data['prefix'][1]) + '\r\n'

    
    if (response_topic != "") and (response_payload != ""):
        mosq.publish(response_topic, response_payload, 0)

def on_publish(mosq, obj, mid):
    pass

if __name__ == '__main__':
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    #client.tls_set('root.ca', certfile='c1.crt', keyfile='c1.key')
    client.connect("127.0.0.1", 1883, 60)

    client.subscribe("nm_cli/#", 0)

    while client.loop() == 0:
        pass

# vi: set fileencoding=utf-8 :