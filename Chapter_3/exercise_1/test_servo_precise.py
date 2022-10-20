from gpiozero import AngularServo
import time

s = AngularServo(17, min_angle=0, max_angle=180)

try:
    for i in range(180):
        s.angle = i
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Program stopped")