import time
import serial
import adafruit_fingerprint
import time
import pandas as pd 
from datetime import datetime

uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
dates = []

def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True

def get_num(max_number):
    """Use input() to get a valid number from 0 to the maximum size
    of the library. Retry till success!"""
    i = -1
    while (i > max_number - 1) or (i < 0):
        try:
            i = int(input("Enter ID # from 0-{}: ".format(max_number - 1)))
        except ValueError:
            pass
    return i

dates = []
ids = []

try:
    while get_fingerprint():
        time.sleep(.05)

    dates.append(time.asctime(time.localtime(time.time())))
    ids.append(finger.finger_id)
    print(dates, ids)
    dict = {'id': ids, 'datetime': dates}
    df = pd.DataFrame(dict)
    df.to_csv('file1.csv')
except KeyboardInterrupt:        
    
    df.to_csv('file1.csv')

