# Author: Josh Huang
# main script that runs upon pi turn on

from datetime import datetime
import time
from imu import IMU
from servo0 import Servo0
from servo1 import Servo1
from camera import Camera
from radioParser import RadioParser
import math

debug = True
vars = {}
if debug:
    vars = dict(launch_accel=11, landing_delta_accel=0.1, landing_wait_time=5)
else:
    vars = dict(launch_accel=20, landing_delta_accel=0.1, landing_wait_time=120)

#region initialize components
imu = IMU()
s0 = Servo0()
s1 = Servo1()
# TODO initialize DC motor class
radioParser = RadioParser()
cam = Camera()
#endregion
    
def main():
    #region phase1 on pad
    a = 0.99
    x,y,z = imu.getAccel()
    prev_mag = magnitude(x,y,z)
    while True:
        x,y,z = imu.getAccel()
        mag = magnitude(x,y,z)
        mag = prev_mag*a + mag*(1-a)

        if (mag > vars['launch_accel']):
            print("Launch")
            break
            
        prev_mag = mag
        time.sleep(.01)
    #endregion
        
    #region phase2 launched/detect land
    x,y,z = imu.getAccel()
    prev_mag = magnitude(x,y,z)
    land_time = 0
    while True:
        x,y,z = imu.getAccel()
        mag = magnitude(x,y,z)
        mag = mag*a + prev_mag*(1-a)
        
        if (abs(mag - prev_mag) < vars['landing_delta_accel']):
            if (land_time == 0):
                land_time = datetime.now()
            if (datetime.now() - land_time).total_seconds() > vars['landing_wait_time']:
                print("Landed")
                break
        else:
            land_time = 0
        
        prev_mag = mag
        time.sleep(.05)
        #regionend
        
    #region phase3 deploy
    theta_DC,theta_0 = imu.GetAdjustments()
    print(theta_DC, theta_0)
    # TODO: use DC class to make adjustments based on imu
    s0.rotate(theta_0)
    #endregion
    
    #region camera commands
    while True:
        commands = radioParser.parser()
        if commands:
            # print(commands[0])
            for cmd in commands[0]:
                if (cmd == "A1"): # Turn camera 60º to the right
                    s1.rotate(60)
                elif (cmd == "B2"): #Turn camera 60º to the left
                    s1.rotate(-60)
                elif (cmd == "C3"): # Take picture
                    cam.capture("PDF")
                elif (cmd == "D4"): # Change camera mode from color to grayscale
                    pass
                elif (cmd == "E5"): # Change camera mode back from grayscale to color 
                    pass
                elif (cmd == "F6"): # Rotate image 180º (upside down).
                    pass
                elif (cmd == "G7"): # Special effects filter (Apply any filter or image distortion you want and state what filter or distortion was used)
                    pass
                elif (cmd == "H8"): # Remove all filters.
                    pass
        
        time.sleep(5)
            
    
    

    #endregion
    
    #???: ability to re-adjust payload if IMU detects payload has shifted?

def magnitude(x,y,z):
    return math.sqrt(x*x + y*y + z*z)

if __name__ == "__main__":
    main()