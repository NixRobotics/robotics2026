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

'''
First we started with the DriveTrain() class that VEX gives us: https://api.vex.com/v5/home/python/Drivetrain.html#id1

We mesured and calculated the various values needed by DriveTrain:
- Wheel Travel: How far the wheel moves when it goes through one rotation, which is the same as its circumference,
                or 2 * pi * radius, or pi * diameter
- Track Width: Distanace between left and right wheels
- Wheel Base: Distance from front to back wheels
- External Gear Ratio: If we use gears on the outside of the motor, what is the ratio expressed as motor_gear / wheel_gear
                       or 60/60 (1:1) for this robot

We can then create (construct) the DriveTrain as follows:

dt = DriveTrain(lm, rm, wheelTravel, trackWidth, wheelBase, units, externalGearRatio)

We coded a simple square in the autonomous() function and saw that it did not work very well
'''

INCH_TO_MM = 25.4

wheelTravel = 4 * pi * INCH_TO_MM # mm
trackWidth = 242 # MM
wheelBase = 10 * INCH_TO_MM # MM
units = MM
externalGearRatio = 60/60 # 60T on motor, 60T on wheel

# Step1: Use VEX DriveTrain - did not work!
# dt = DriveTrain(lm, rm, wheelTravel, trackWidth, wheelBase, units, externalGearRatio)

'''
Next to understand why turns did not behave very well we decided to see if we could figure out how DriveTrain works. We
created a very simple class that only has the constructor, the drive_for() and turn_for() functions

class MyDriveTrain:
    def __init__(self): # This is how you create the constructor
        pass
    def drive_for(self): # This is how you create a class member function (also known as "method"). Note all methods start with self
        pass
    def turn_for(self):
        pass # we use pass when we want to come back and add code later

Notice the use of "self" everywhere - this is what sets the scope of a variable or function to the class. Without self we would
by default be local scope (or global scope if a global variable exists with that same name)

We can then simply replace our previous DriveTrain constructor with MyDriveTrain, ie:
dt = MyDriveTrain(...)
'''

class MyDriveTrain:
    def __init__(self, lm, rm, wheelTravel, trackWidth, wheelBase, units, externalGearRatio):
        # We save all of the input arguments as class variables so we can use them later. Notice all of the new variables
        # have the class scope (self.variable_name) so can be accessed anywhere within the class
        self.lm = lm
        self.rm = rm
        self.wheelTravel = wheelTravel
        self.trackWidth = trackWidth
        self.wheelBase = wheelBase
        self.externalGearRatio = externalGearRatio

    def drive_for(self, direction, distance, units, wait):
        '''
        The motor commands take either DEGREES or TURNS but our input distance is in MM
        - To convert we observed that wheel_turns = distance / wheel_circumference
        
        Notice that wheel_turns does not use "self." - wheel_turns is a local variable only usable in drive_for()
        
        Also notice how we do not wait for the left side to stop spinning before we start the right side as we want
        motors on both sides of the robot to spin at the same time
        '''
        wheel_turns = distance / self.wheelTravel
        self.lm.spin_for(direction, wheel_turns, TURNS, wait=False)
        self.rm.spin_for(direction, wheel_turns, TURNS, wait=True)

    def turn_for(self, direction, angle, units, wait):
        '''
        Here we tried to figure out how a robot turns. We saw that for a PIVOT turn where we want to turn the robot to the
        RIGHT, we want the wheels on the left side to spin forward and the right side to spin backwards. The question is
        by how much

        We simplified the problem by assuming that the robot only has 2 wheels. For this the calculation is easy and is the
        circle traced out by the wheels. We call this circle the "turning circle" and its circumference is just:
        turning_circle_circumference = pi * track_width (trackWidth is the distance between the left and right wheels)

        Then we can use the same distance calculation as before to calculate how far the wheels must turn for a full spin
        of the robot:
        wheel_turns = turning_circle_circumference / wheel_circumference

        Finally we only want to turn for a portion of a full turn of the robot, so we take the angle (in degree)

        wheel_turns = (turning_circle_circumference / wheel_circumference) * (angle / 360) * 1.05

        This worked much better, but wasn't quite right. We tried to figure out how to use the last piece of information
        which is "wheelBase" and saw that this is impossible due to how many different types of wheels there are and changes
        in friction. We can approximate this by tuning a "fudge factor" or roughly 1.05 in this case, but this will change too
        much to be a useful way of programming our robots

        Notice that wheel_turns does not use "self." - wheel_turns is a local variable only usable in turn_for(). Therefore
        it is not the same one we used in drive_for()
        '''
        wheel_turns = (pi * self.trackWidth / self.wheelTravel) * (angle / 360) * 1.05
        self.lm.spin_for(FORWARD, wheel_turns, TURNS, wait=False)
        self.rm.spin_for(REVERSE, wheel_turns, TURNS, wait=True)

# Step 2: Use MyDriveTrain() class - worked much better, but turns are not quite correct due to impact of "wheelBase" being too
# hard to determine
# dt = MyDriveTrain(lm, rm, wheelTravel, trackWidth, wheelBase, units, externalGearRatio)

'''
After seeing how hard it was going to be to fix DriveTrain for a reliably autonomous route we wanted really an electronic
compass to get our turns to work properly. The closest thing VEX has is an Inertial Sensor which reports "heading" that can
be used to make turns more reliable (although not necessarily accurate without some work)

We tested it and it worked "ok", but turns were very slow and did not quite end up where we wanted. This is what we will work on next
'''

# Step 3: Use SmartDrive() class along with an Inertial Sensor
# sensors
g = Inertial(Ports.PORT5)
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

def autonomous():
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    # place automonous code here
    # leg1
    # Notice we wait for each command to finish before going on to the next
    # We could set wait=False if we want to run an intake or something in the middle of a drive command
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

def user_control():
    brain.screen.clear_screen()
    # place driver control in this while loop
    while True:
        wait(20, MSEC)

# create competition instance
comp = Competition(user_control, autonomous)
pre_autonomous()
