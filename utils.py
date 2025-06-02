import RPi.GPIO as GPIO
import pygame

GPIO.setmode(GPIO.BCM)

PIN_CLK = 18
PIN_DO  = 16
PIN_DI  = 20
PIN_CS  = 24
# set up the SPI interface pins
GPIO.setup(PIN_DI,  GPIO.OUT)
GPIO.setup(PIN_DO,  GPIO.IN)
GPIO.setup(PIN_CLK, GPIO.OUT)
GPIO.setup(PIN_CS,  GPIO.OUT)

# read SPI data from ADC8032


BUTTON_PINS = {
    "up": 26,
    "down": 19,
    "left": 13,
    "right": 6,
    "select": 5,
    "reset": 21


}

for pin in BUTTON_PINS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BUTTON_COOLDOWN = 200  # milliseconds
PLATFORMER_COOLDOWN = 20
last_pressed = {key: 0 for key in BUTTON_PINS}
def get_ADC(channel):
	# 1. CS LOW.
        GPIO.output(PIN_CS, True)      # clear last transmission
        GPIO.output(PIN_CS, False)     # bring CS low

	# 2. Start clock
        GPIO.output(PIN_CLK, False)  # start clock low

	# 3. Input MUX address
        for i in [1,1,channel]: # start bit + mux assignment
                 if (i == 1):
                         GPIO.output(PIN_DI, True)
                 else:
                         GPIO.output(PIN_DI, False)

                 GPIO.output(PIN_CLK, True)
                 GPIO.output(PIN_CLK, False)

        # 4. read 8 ADC bits
        ad = 0
        for i in range(8):
                GPIO.output(PIN_CLK, True)
                GPIO.output(PIN_CLK, False)
                ad <<= 1 # shift bit
                if (GPIO.input(PIN_DO)):
                        ad |= 0x1 # set first bit

        # 5. reset
        GPIO.output(PIN_CS, True)

        return ad

def read_gpio_input():
    return {name: not GPIO.input(pin) for name, pin in BUTTON_PINS.items()}

def button_pressed(name):
    current_time = pygame.time.get_ticks()
    if read_gpio_input()[name] and current_time - last_pressed[name] > BUTTON_COOLDOWN:
        last_pressed[name] = current_time
        return True
    return False

def platformer_pressed(name):
    current_time = pygame.time.get_ticks()
    if read_gpio_input()[name] and current_time - last_pressed[name] > PLATFORMER_COOLDOWN:
        last_pressed[name] = current_time
        return True
    return False
