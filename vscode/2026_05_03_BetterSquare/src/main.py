# ------------------------------------------
# 
# 	Project:
#	Author:
#	Created: 04/12/2026
#	Configuration:
# 
# ------------------------------------------

# Library imports
from vex import *
from math import pi
import time

# Begin project code
brain = Brain()

'''
This is how we declare what motors we have (we will use m1 and m2 for the left side and m3/m4 for the right side)
We looked at the arrow on the motor to determine which way is forward, however we need to do this in reverse because
we are using external gear, so:
- Motors on left side need to spin backwards to get the robot to move FORWARD
- Motors on right side need to spin forwards to get the robot to move FORWARD
Also for a RIGHT turn (we talked about PIVOT turns vs. SWING turns):
- Wheels on the left side of robot spin forwards
- Wheels on the right side of robot spin backwards

We found the VEX documentation here: https://api.vex.com/v5/home/python/index.html

For motors the relevant section is here: https://api.vex.com/v5/home/python/Motion/motor_and_motor_group.html#motor

There are the arguments for the Motor constructor: Motor(port, gears, reverse). For our green cartridges we need to
use GearSetting.RATIO_18_1

MotorGroup is just a convenient way of putting our motors into a list to make code smaller
'''

# left motors
m1 = Motor(Ports.PORT1, GearSetting.RATIO_18_1, True)
m2 = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
lm = MotorGroup(m1, m2)
# right motors
m3 = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
m4 = Motor(Ports.PORT4, GearSetting.RATIO_18_1, False)
rm = MotorGroup(m3, m4)

INCH_TO_MM = 25.4

wheelTravel = 4 * pi * INCH_TO_MM # mm
trackWidth = 242 # MM
wheelBase = 10 * INCH_TO_MM # MM
units = MM
externalGearRatio = 60/60 # 60T on motor, 60T on wheel

'''
05-03-2026 SUMMARY
------------------

What we focused on today was firstly to make the robot move faster. When we did this we saw that turns got really "wobbly".
To understand why, we tried to use the gyro (inertial sensor) directly using a simple check to see if the robot has reached
90 degrees, e.g.

while g.heading(DEGREES) < 90:
    dt.turn(RIGHT)

We saw that this did not work, because heading starts off reading about 359 degrees. Instead we use g.rotation(), ie:

while g.rotation(DEGREES) < 90:
    dt.turn(RIGHT)

This made the robot turn, but it was going too fast to stop in time. To fix this we observed that we want to slow the robot
down as it gets close to 90degrees, so doing something like:

target_heading = 90
current_heading = g.rotation(DEGREES)
while current_heading < 90:
    turn_speed = target_heading - current_heading
    left_motors.spin(FORWARD, turn_speed, PERCENT)
    right_motors.spin(REVERSE, turn_speed, PERCENT)
    wait(10, MSEC)
    current_heading = g.rotation(DEGREES)

This was still a bit too fast so we slowed it down using a factor of 0.5, ie

turn_speed = 0.5 * (target_heading - current_heading)

We rewrote this using more standard terms:

heading_error = target_heading - current_heading
turn_gain = 0.5
turn_speed = turn_gain * heading_error

This is just a straight line equation: Y = A.X + B (B is zero in this case) and means that the motor speed is PROPORTIONAL to the error

We looked at the error threshold, which is how close we want to get to the desired angle (e.g. 0.5degrees to 1.0 degrees). This
can be done using abs() as follows:

target_heading = 90
heading_error = target_heading - g.rotation(DEGREES)
turn_gain = 0.5
while abs(heading_error) > 0.5: # keep going while error is greater than 0.5degrees (either + or -)
    turn_speed = turn_gain * heading_error
    left_motors.spin(FORWARD, turn_speed, PERCENT)
    right_motors.spin(REVERSE, turn_speed, PERCENT)
    wait(10, MSEC)
    heading_error = target_heading - g.rotation(DEGREES)

In SmartDrive, the two new functions we need are:
dt.set_turn_constant() # GAIN
dt.set_turn_threshold() # FINAL ERROR or THRESHOLD

Finally to the robot to turn exactly 360 degrees, we observed that when turning 10 times the robot was off by about 10degrees,
so we need to multiply our inertial sensor readings by 361/360 (ie one extra degree for every 360 degrees turned). This was
done by using a simple inheritance of VEX's Inertial class.
'''

# We want to fix how the inertial sensors returns headings and rotations. The only thing we need to change is the rotation() function!
# We use a simple inheritance class, MyInertial(), to do this where only rotation() is changed - everything else stays the same
class MyInertial(Inertial):
    def rotation(self, units):
        return super().rotation(units) * 361 / 360

g = MyInertial(Ports.PORT5)
dt = SmartDrive(lm, rm, g, wheelTravel, trackWidth, wheelBase, units, externalGearRatio)

# This code runs during the 3, 2, 1 countdown
def pre_autonomous():
    # actions to do when the program starts
    brain.screen.clear_screen()
    brain.screen.print("pre auton code")
    wait(100, MSEC)

    # For an inertial sensor to work, robot must be still on the field when the program starts
    g.calibrate()
    
    wait(2, SECONDS)

    print("pre auton done - robot is ready!")

def turn_example_code():
    proportional_gain = 0.5
    error_threshold = 1.0
    target_heading = 90
    current_heading = g.rotation(DEGREES)
    heading_error = target_heading - current_heading
    while abs(heading_error) > error_threshold:
        speed = proportional_gain * heading_error
        lm.spin(FORWARD, speed, PERCENT)
        rm.spin(REVERSE, speed, PERCENT)
        wait(10, MSEC)
        current_heading = g.rotation(DEGREES)
        heading_error = target_heading - current_heading

    dt.stop(BRAKE)

def check_gyro():
    dt.turn_for(RIGHT, 10 * 360, DEGREES) # spin 10 times

def drive_a_square():
    dt.drive_for(FORWARD, 1200, MM, wait=True)
    dt.turn_for(RIGHT, 90, DEGREES, wait=True)
    # leg2
    dt.drive_for(FORWARD, 1200, MM, wait=True)
    dt.turn_for(RIGHT, 90, DEGREES, wait=True)
    # leg3
    dt.drive_for(FORWARD, 1200, MM, wait=True)
    dt.turn_for(RIGHT, 90, DEGREES, wait=True)
    # leg4
    dt.drive_for(FORWARD, 1200, MM, wait=True)
    dt.turn_for(RIGHT, 90, DEGREES, wait=True)

def autonomous():
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    # place automonous code here
    # leg1
    # Notice we wait for each command to finish before going on to the next
    # We could set wait=False if we want to run an intake or something in the middle of a drive command
    dt.set_drive_velocity(67, PERCENT)
    dt.set_turn_velocity(67, PERCENT)
    dt.set_turn_constant(0.7) # Vex's term for proportional gain (Kp)
    dt.set_turn_threshold(0.5)
    # dt.set_timeout(10, SECONDS)

    what_to_do = 1
    if what_to_do == 1:
        drive_a_square()
    if what_to_do == 2:
        turn_example_code()
    if what_to_do == 3:
        check_gyro()

def user_control():
    brain.screen.clear_screen()
    # place driver control in this while loop
    while True:
        wait(20, MSEC)

# create competition instance
comp = Competition(user_control, autonomous)
pre_autonomous()
