# subscriber.py
import paho.mqtt.client as mqtt
import time
import json
from adafruit_crickit import crickit
from adafruit_motor import stepper

# Stepper motor and LED setup
STEP_MOTOR = crickit.stepper_motor
LED_PIN = crickit.SIGNAL1
MIN_INTERSTEP_DELAY = 0.002  # Note: Using your specified range (0.001-0.009) instead
MAX_INTERSTEP_DELAY = 0.02

# Initialize LED pin as output
crickit.seesaw.pin_mode(LED_PIN, crickit.seesaw.OUTPUT)

def blink_led(delay):
    blink_rate = (delay - 0.001) / (0.009 - 0.001)  # Adjusted for new range
    blink_rate = 1 - blink_rate
    led_on_time = 0.05 + (blink_rate * 0.2)
    led_off_time = 0.05 + ((1-blink_rate) * 0.5)
    
    crickit.seesaw.digital_write(LED_PIN, True)
    time.sleep(led_on_time)
    crickit.seesaw.digital_write(LED_PIN, False)
    time.sleep(led_off_time)

def run_motor(steps, direction, delay):
    dir_map = {"FORWARD": stepper.FORWARD, "BACKWARD": stepper.BACKWARD}
    motor_dir = dir_map.get(direction, stepper.FORWARD)
    
    for i in range(steps):
        STEP_MOTOR.onestep(direction=motor_dir)
        crickit.seesaw.digital_write(LED_PIN, (i % 10 < 5))
        time.sleep(delay)
    crickit.seesaw.digital_write(LED_PIN, False)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to broker")
        client.subscribe("pythontest/motor/control")
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received message on topic {msg.topic}: {payload}")
        
        # Check for specific conditions to trigger motor and LED
        # *** THIS IS THE SPECIFIC MESSAGE CHECK LINE ***
        if (all(k in payload for k in ["steps", "speed", "direction", "command"]) and
            payload["command"] == "RUN_MOTOR" and
            payload["direction"].upper() == "FORWARD" and
            50 <= int(payload["steps"]) <= 100 and
            0.001 <= float(payload["speed"]) <= 0.009):
            
            # Print confirmation of conditions being met before triggering
            print("*** CONDITIONS MET ***")
            print("Specific range specifications satisfied:")
            print(f"- Steps: {payload['steps']} (between 50 and 100)")
            print(f"- Speed: {payload['speed']} (between 0.001 and 0.009)")
            print(f"- Direction: {payload['direction'].upper()} (FORWARD)")
            print(f"- Command: {payload['command']} (RUN_MOTOR)")
            print("Triggering motor and LED now...")
            
            steps = int(payload["steps"])
            speed = float(payload["speed"])
            direction = payload["direction"].upper()
            
            print(f"Activating motor: {steps} steps, {speed} delay, {direction}")
            run_motor(steps, direction, speed)
            for _ in range(3):
                blink_led(speed)
        else:
            print("Message received but no action taken - conditions not met")
                
    except Exception as e:
        print(f"Error processing message: {e}")

# Create subscriber client
subscriber = mqtt.Client()
subscriber.on_connect = on_connect
subscriber.on_message = on_message

# Connect to public broker
print("Connecting to broker...")
subscriber.connect("broker.hivemq.com", 1883, 60)

# Start the subscriber loop
subscriber.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping subscriber...")
    crickit.seesaw.digital_write(LED_PIN, False)
    subscriber.loop_stop()
    subscriber.disconnect()