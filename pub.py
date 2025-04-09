# publisher.py
import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to broker")
    else:
        print(f"Connection failed with code {rc}")

# Create publisher client
publisher = mqtt.Client()
publisher.on_connect = on_connect

# Connect to public broker
print("Connecting to broker...")
publisher.connect("broker.hivemq.com", 1883, 60)
publisher.loop_start()

try:
    while True:
        # Randomly decide if this message will trigger the subscriber (50% chance)
        should_trigger = random.choice([True, False])
        
        if should_trigger:
            # Generate values that WILL trigger the subscriber
            steps = random.randint(50, 100)  # Steps between 50-100
            speed = round(random.uniform(0.001, 0.009), 3)  # Speed between 0.001-0.009
            direction = "FORWARD"
            command = "RUN_MOTOR"
        else:
            # Generate values that WON'T trigger (outside the range or different command/direction)
            steps = random.randint(10, 200)  # Wider range, might be outside 50-100
            speed = round(random.uniform(0.001, 0.02), 3)  # Wider range, might be outside 0.001-0.009
            direction = random.choice(["FORWARD", "BACKWARD"])
            command = random.choice(["RUN_MOTOR", "STOP", "PAUSE"])  # Might not be RUN_MOTOR
        
        # Create motor control message
        motor_command = {
            "steps": steps,
            "speed": speed,
            "direction": direction,
            "command": command,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publish to topic
        topic = "pythontest/motor/control"
        
        publisher.publish(
            topic,
            json.dumps(motor_command),
            qos=1
        )
        print(f"Published to {topic}: {motor_command}")
        
        time.sleep(2)  # Publish every 2 seconds
        
except KeyboardInterrupt:
    print("Stopping publisher...")
    publisher.loop_stop()
    publisher.disconnect()