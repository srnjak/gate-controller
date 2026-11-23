import RPi.GPIO as GPIO
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description='Read GPIO pin state.')
parser.add_argument('pin_number', type=int, help='BCM pin number to read')
args = parser.parse_args()

# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Use the argument for the pin number
pin_number = args.pin_number

# Set up the specified pin as an input with a pull-up resistor
GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Read the value from the pin
input_value = GPIO.input(pin_number)

# Print the read value
print("Read value from pin", pin_number, ":", input_value)

# Clean up GPIO to reset pin configurations
GPIO.cleanup()
