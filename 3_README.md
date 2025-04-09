# MQTT-Controlled Stepper Motor and LED System

## Overview
This project uses MQTT messaging to control a stepper motor and LED via a Crickit HAT. A publisher sends motor control commands, and a subscriber listens for specific messages to trigger motor movement and LED blinking.

## System Components
- **Hardware**: Crickit HAT, stepper motor on motor ports, LED on SIGNAL1 pin.
- **Software**: 
  - `pub.py`: Publishes MQTT messages with motor commands.
  - `sub.py`: Subscribes to MQTT messages, controls motor and LED based on specific conditions.
- **Broker**: Public HiveMQ broker (`broker.hivemq.com:1883`).
- **Topic**: `"pythontest/motor/control"`.

## Messaging Logic
The system uses JSON-formatted MQTT messages to communicate motor control parameters. The subscriber only acts on messages meeting strict conditions.

### Message Format
Messages contain:
- `steps`: Integer (number of motor steps).
- `speed`: Float (delay between steps in seconds).
- `direction`: String ("FORWARD" or "BACKWARD").
- `command`: String (specific action command).
- `timestamp`: String (ISO format, optional).

Example:
```json
{
    "steps": 75,
    "speed": 0.005,
    "direction": "FORWARD",
    "command": "RUN_MOTOR",
    "timestamp": "2025-04-09T12:00:00.000000"
}
```

### Triggering Conditions
The subscriber (`sub.py`) triggers the motor and LED only when:
- All required fields (`steps`, `speed`, `direction`, `command`) are present.
- `command` is `"RUN_MOTOR"`.
- `direction` is `"FORWARD"` (case-insensitive).
- `steps` is between 50 and 100 (inclusive).
- `speed` is between 0.001 and 0.009 seconds (inclusive).

**Code Snippet (Trigger Check in `sub.py`)**:
```python
if (all(k in payload for k in ["steps", "speed", "direction", "command"]) and
    payload["command"] == "RUN_MOTOR" and
    payload["direction"].upper() == "FORWARD" and
    50 <= int(payload["steps"]) <= 100 and
    0.001 <= float(payload["speed"]) <= 0.009):
    # Motor and LED activation logic here
```

### Publisher Behavior
The publisher (`pub.py`) sends messages every 2 seconds with a 50% chance of meeting the trigger conditions:
- **Triggering Case**: Uses `steps: 50-100`, `speed: 0.001-0.009`, `direction: "FORWARD"`, `command: "RUN_MOTOR"`.
- **Non-Triggering Case**: Uses broader ranges or different values (e.g., `steps: 10-200`, `direction: "BACKWARD"`, `command: "STOP"`).

**Code Snippet (Message Generation in `pub.py`)**:
```python
should_trigger = random.choice([True, False])
if should_trigger:
    steps = random.randint(50, 100)
    speed = round(random.uniform(0.001, 0.009), 3)
    direction = "FORWARD"
    command = "RUN_MOTOR"
else:
    steps = random.randint(10, 200)
    speed = round(random.uniform(0.001, 0.02), 3)
    direction = random.choice(["FORWARD", "BACKWARD"])
    command = random.choice(["RUN_MOTOR", "STOP", "PAUSE"])
```

## Motor Control and LED Integration
- **Motor**: When triggered, moves the exact number of `steps` at the specified `speed` in the "FORWARD" direction.
- **LED**: 
  - Blinks during motor movement (on/off every 5 steps).
  - Blinks 3 times after completion, with rate based on `speed`.

**Code Snippet (Motor and LED Control in `sub.py`)**:
```python
def run_motor(steps, direction, delay):
    motor_dir = stepper.FORWARD  # Always FORWARD due to trigger condition
    for i in range(steps):
        STEP_MOTOR.onestep(direction=motor_dir)
        crickit.seesaw.digital_write(LED_PIN, (i % 10 < 5))  # Blink during movement
        time.sleep(delay)
    crickit.seesaw.digital_write(LED_PIN, False)

# After motor runs
for _ in range(3):
    blink_led(speed)  # Completion blinks
```

## Console Feedback
When conditions are met, the console provides detailed confirmation:
```
*** CONDITIONS MET ***
Specific range specifications satisfied:
- Steps: 75 (between 50 and 100)
- Speed: 0.005 (between 0.001 and 0.009)
- Direction: FORWARD (FORWARD)
- Command: RUN_MOTOR (RUN_MOTOR)
Triggering motor and LED now...
Activating motor: 75 steps, 0.005 delay, FORWARD
```

Non-matching messages print:
```
Message received but no action taken - conditions not met
```

## Running the System
1. Ensure hardware is connected (Crickit HAT, motor, LED).
2. Install dependencies: `pip install -r requirements.txt`.
3. Run `pub.py` on one terminal.
4. Run `sub.py` on the hardware device.
5. Stop with `Ctrl+C`.

## Dependencies (requirements.txt)
```
paho-mqtt
adafruit-circuitpython-crickit
adafruit-circuitpython-motor
```

## Conclusion Notes on Logic
- The system is event-driven, relying on MQTT messages to trigger actions.
- Trigger conditions are strict, ensuring precise control over motor and LED behavior.

---

## References
- **[Grok AI](https://grok.com/)**: Grok AI supported me in refining my edited Week 2 code (pub.py & sub.py) provided by Matt and bringing my logic to life while incorporating the stepper motor code I developed in last week's class.

---

📚 **Author of Notebook:** Michael Dankwah Agyeman-Prempeh [MEng. DTI '25]```