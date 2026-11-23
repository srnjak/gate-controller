import RPi.GPIO as GPIO
import time

# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Define the list of pin numbers to read
pins_to_read = [17, 27, 22]

# Loop over each pin to set it up as an input with a pull-up resistor
for pin_number in pins_to_read:
    GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Wait a little
time.sleep(0.1)

# Loop over each pin again to read its value and print it
for pin_number in pins_to_read:
    input_value = GPIO.input(pin_number)
    print(f"Read value from pin {pin_number}: {input_value}")

# Clean up GPIO to reset pin configurations
GPIO.cleanup()
