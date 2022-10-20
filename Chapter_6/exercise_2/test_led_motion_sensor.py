import RPi.GPIO as GPIO
import time
import threading

class MotionSensor:

    def __init__(self, pin = 12):

        self.pin = pin
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def is_activated(self):

        res = False
        if GPIO.input(self.pin) == GPIO.HIGH:
            res = True
        return res

class Blinker:

    def __init__(self, pin = 16):
        self.is_active = False
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def blink(self, speed = 0.25, duration = 5):

        if not self.is_active:
            self.is_active = True
            print("LED active")
            thread = threading.Thread(target=self.control_led, args=(speed, duration,))
            thread.start()
         
    def control_led(self, speed = 0.25, duration = 5):

        start_time = time.time()

        while (time.time() - start_time) < duration:
            GPIO.output(self.pin, True)
            time.sleep(speed)
            GPIO.output(self.pin, False)
            time.sleep(speed)
        self.is_active = False    

if __name__ == '__main__':

    blinker = Blinker()
    motion_sensor = MotionSensor()

    while True:
        try:
            if motion_sensor.is_activated():
                blinker.blink(1, 5)
        except KeyboardInterrupt:
            GPIO.cleanup()
            break