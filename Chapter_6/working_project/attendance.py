import time
import serial
import adafruit_fingerprint
import pandas as pd 
import sys

from datetime import datetime
from gpio_helper import Blinker, MotionSensor

def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""

    print("Waiting for image...")
    start_time = time.time()
    while finger.get_image() != adafruit_fingerprint.OK:
        if time.time() - start_time > 2:
            return False            
    
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True

def main():
 
    while True:

        while not motion_sensor.is_activated():
            time.sleep(0.05)

        print('Motion detected.')
        tries = 0
        user_input = False
        finger_found = True

        while not get_fingerprint():
            time.sleep(.05)
            tries += 1
            print("Num of tries: ", tries)
            if tries >= 5:
                print("No finger detected")
                blinker.blink(0.1, 3)
                finger_found = False
                break

        if finger_found:      
            date = time.asctime(time.localtime(time.time()))
            id = finger.finger_id            

            dict = {'id': [id], 'datetime': [date]}
            print("Saving data: ", dict)
            blinker.blink(1, 3)    
            df = pd.DataFrame(dict)
            df.to_csv('attendance.csv', mode = 'a', header = False, index=False)
 
if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Usage: {} led_pin sensor_pin, e.g. python3 attendance.py 17 27'.format(sys.argv[0]))
        sys.exit(1)    

    blinker = Blinker(int(sys.argv[1]))
    motion_sensor = MotionSensor(int(sys.argv[2]))
    uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)   

    main()
