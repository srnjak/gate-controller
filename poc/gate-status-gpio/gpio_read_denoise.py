import RPi.GPIO as GPIO
import argparse
from collections import Counter

def read_gpio_with_filter(pin_number, samples=1000, delay=0.01):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    readings = [GPIO.input(pin_number) for _ in range(samples)]
    GPIO.cleanup()
    most_common = Counter(readings).most_common(1)[0][0]
    return most_common

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read GPIO pin state with filtering.')
    parser.add_argument('pin_number', type=int, help='BCM pin number to read')
    args = parser.parse_args()

    # Read the value from the pin with some filtering
    input_value = read_gpio_with_filter(args.pin_number)
    print(f"Filtered read value from pin {args.pin_number}: {input_value}")
