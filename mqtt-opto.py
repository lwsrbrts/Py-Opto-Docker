#!/usr/bin/env python3
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import os

# Set up some variables for use.
CLIENT = os.environ['CLIENT_NAME']
BROKER = os.environ['MQTT_BROKER']
OPTO_PIN = int(os.environ['OPTO_PIN'])  # 7 on SIDE, 4 on FRONT
MQTT_USER = os.environ['MQTT_USER']
MQTT_PASS = os.environ['MQTT_PASS']

# The topic default
TOPIC = "garage/" + CLIENT


# Use broadcom pin numbers
GPIO.setmode(GPIO.BCM)
GPIO.setup(OPTO_PIN, GPIO.IN)

# Connect to the MQTT broker
client = mqtt.Client(CLIENT)
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.connect(BROKER, 1883, 60)
client.loop_start()

# The state of the PIR when we start.
# This is used to keep track of the sensor so we can ignore false callbacks from
# the add_event_detect.
if GPIO.input(OPTO_PIN) == 1:
    state = False
else:
    state = True

# define a function to handle the state transitions
def motion_detection(pin):

    global state

    # Motion was detected if pin is 0 (LOW)
    if GPIO.input(OPTO_PIN) == 1:
        if state == False:
            print ("False request for OFF")
            #pass
        else:
            print(time.strftime('%X') + ": Publishing OFF message for " + CLIENT)
            data = client.publish(TOPIC, '{"state":"off"}', 1, True)
            print(time.strftime('%X') + ": Waiting for publish ack...")
            data.wait_for_publish()
            print(time.strftime('%X') + ": Received publish ack. Awaiting next event...")
            state = False
    else:
        if state == False:
            print(time.strftime('%X') + ": Publishing ON message for " + CLIENT)
            data = client.publish(TOPIC, '{"state":"on"}', 1, True)
            print(time.strftime('%X') + ": Waiting for publish ack...")
            data.wait_for_publish()
            print(time.strftime('%X') + ": Received publish ack. Awaiting next event...")
            state = True
        else:
            print("False request for ON")
            #pass

# Start up
motion_detection(OPTO_PIN)

# Add an event to the PIN (we monitor it). Add bouncetime to reduce multiple callbacks.
GPIO.add_event_detect(OPTO_PIN, GPIO.BOTH, callback=motion_detection, bouncetime=20)

# Enter the processing loop, except when an interrupt/exception occurs.
try:
    while True:
        pass
except:
    print("Quitting by request or exception.")
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()