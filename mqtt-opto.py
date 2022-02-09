#!/usr/bin/env python3
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import queue, time, os

# Set up some variables for use.
CLIENT = os.environ['CLIENT_NAME']
ROOT_TOPIC = os.environ['ROOT_TOPIC']
BROKER = os.environ['MQTT_BROKER']
OPTO_PIN = int(os.environ['OPTO_PIN'])  # 7 on SIDE, 4 on FRONT
MQTT_USER = os.environ['MQTT_USER']
MQTT_PASS = os.environ['MQTT_PASS']

# The topic
TOPIC = ROOT_TOPIC + "/" + CLIENT
 
# Create a queue.
q = queue.Queue(10) # Simple FIFO queue.

# Have a type of job to publish to the queue.
class Job(object):
    def __init__(self, state):
        self.state = state
        return

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
            print (time.strftime('%X') + ": False request for OFF.")
            #pass
        else:
            print(time.strftime('%X') + ": Creating OFF job for " + CLIENT)
            q.put(Job('off'))
            state = False
    else:
        if state == False:
            print(time.strftime('%X') + ": Creating ON job for " + CLIENT)
            q.put(Job('on'))
            state = True
        else:
            print (time.strftime('%X') + ": False request for ON.")
            #pass

def process_job():
    next_job = q.get(False)
    print(time.strftime('%X') + ": Publishing " + next_job.state + " message for " + CLIENT)
    data = client.publish(TOPIC, '{"state":"' + next_job.state + '"}', 1, True)
    print(time.strftime('%X') + ": Waiting for publish ack...")
    data.wait_for_publish()
    print(time.strftime('%X') + ": Received publish ack. Pausing 2 seconds...")
    q.task_done()
    time.sleep(2) # If there are multiple jobs on the queue, we pause publishing to allow HA to keep up.
    print(time.strftime('%X') + ": Done. Awaiting next event...")

# Start up
motion_detection(OPTO_PIN)

# Add an event to the PIN (we monitor it). Add bouncetime to reduce multiple callbacks.
GPIO.add_event_detect(OPTO_PIN, GPIO.BOTH, callback=motion_detection, bouncetime=20)

# Enter the processing loop, except when an interrupt/exception occurs.
try:
    while True:
        if not q.empty():
            process_job()
except:
    print("Quitting by request or exception.")
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()