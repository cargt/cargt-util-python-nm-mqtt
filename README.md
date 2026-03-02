# Getting Started

Install required packages

```pip install -r requirements.txt```

Run the MQTT client

```python ./nm_info_mqtt.py```

You can query device info from the broker using another client (i.e. MQTT Explorer).

# Command Topics
Topic prefix is ```nm/```.

The client will subscribe to all ```nm/``` topics, but will only respond to the following:

# ```device_info```
```nm/device_info```: The payload should be one of the following:
1. ```all```: report information for all interfaces
2. ```ethernet```: report information for ethernet interfaces
3. ```wifi```: report information for wifi interfaces

The response to the ```nm/device_info``` request will come in the topic ```nm/device_info_resp```.


This is an example of the payload in the ```nm/device/info_resp``` message for all interfaces:
```
eth0 [34:5C:40:03:65:24]
     10.64.164.89/16
eth1 [34:5C:40:03:65:25]
mlan0 [00:50:43:02:FE:01]
     192.168.1.180/24
uap0 [F6:3B:6C:70:E6:BC]
wfd0 [76:18:1E:19:6B:19]
```

See Readme-mqttTopicsAndFunctionality.md for full documentation.
