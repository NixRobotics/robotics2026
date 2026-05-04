# ------------------------------------------
# 
# 	Project:      VEXcode Project
#	Author:       VEX
#	Created:
#	Description:  VEXcode V5 Python Project
# 
# ------------------------------------------

# Library imports
from vex import *

# Begin project code

brain = Brain()

wait(100, MSEC)

brain.screen.draw_image_from_file("pic.png", 240, 0)

'''
First Example:
- Keep track of motor speeds using just global and local variables
- Gets very messy as we add more motors
'''

# These are global scope variables
motor1_speed = 0
motor2_speed = 0
# motor3_speed, motor4_speed, etc. - Too Much Typing!!!

def update_motor1_speed(new_speed):
    # Any variables here will the local scope. To tell python we want the global varaibles we use the "global" keyword
    global motor1_speed
    motor1_speed = new_speed

def print_motor1_speed():
    # global motor1_speed - note that this is not needed here as we are only reading the variable
    print("motor1 speed is", motor1_speed)

def update_motor2_speed(new_speed):
    # Any variables here will the local scope. To tell python we want the global varaibles we use the "global" keyword
    global motor2_speed
    motor2_speed = new_speed

def print_motor2_speed():
    global motor2_speed # note that this is strictly not needed here as we are only reading the variable not writing to it
    print("motor2 speed is", motor2_speed)

print("---- EXAMPLE 1 RUNNING ----")

print_motor1_speed()
update_motor1_speed(20)
print_motor1_speed()

print_motor2_speed()
update_motor2_speed(15)
print_motor2_speed()

'''
Second Example:
- We use a python List instead
'''

motor_speeds = [0, 0, 0, 0, 0, 0] # this is a list with 6 items that will all be set to zero
motor_temperatures = [0] * 6 # this is a shorthand way of doing the same thing

# Note to access items in the list, the first item is '0' not '1', ie
motor2_speed = motor_speeds[1] # this is second motor in the list, not the first one
motor6_speed = motor_speeds[-1] # last one in python, ie 6th motor

# Now we only need to write one function for update and print
def update_motor_speed(new_speed, motor_number):
    global motor_speeds # again use global so we get the right motor_speeds
    motor_speeds[motor_number] = new_speed

def print_motor_speed(motor_number):
    # global not needed here as we only want the read
    print("current motor speed = ", motor_speeds[motor_number], "for motor", motor_number)

print("---- EXAMPLE 2 RUNNING ----")

# Now to update each motor we can use a for loop - len() tells us how many items there are in a list
print("length of list", len(motor_speeds))
for motor_number in range(len(motor_speeds)): # motor_number will be from 0 - 5 (ie 0, 1, 2, 3, 4, 5)
    print("updating motor number", motor_number + 1)
    print_motor_speed(motor_number)
    update_motor_speed(30, motor_number)
    print_motor_speed(motor_number)

'''
Third Example:
- So far we use a lot of messy variables and code spread out over the program
- We can use a class instead to group everything together
- Note that everything uses 'self' now - this is a new "class scope" (vs. local or global scope)
'''

class MyMotor:
    def __init__(self): # __init__ is a way of telling python to set our default values, ie for speed, temperature etc.
        # default speed
        self.speed = 0
        self.gear_ratio = 1
        self.temperature = 20 # degrees C

    def update_speed(self, new_speed):
        self.speed = new_speed

    def update_temperature(self, new_temp):
        self.temperature = new_temp

    def print_speed(self):
        print("current motor speed = ", self.speed)

    def print_gear_ratio(self):
        print("gear ratio = ", self.gear_ratio)

print("---- EXAMPLE 3 RUNNING ----")

# Now we can create a list of motors
motors = [MyMotor(), MyMotor(), MyMotor(), MyMotor(), MyMotor(), MyMotor()]
for motor_number in range(len(motors)): # motor_number will be from 0 - 5 (ie 0, 1, 2, 3, 4, 5)
    print("updating motor number", motor_number + 1)
    motors[motor_number].print_speed()
    motors[motor_number].update_speed(30)
    motors[motor_number].print_speed()

'''
Fourth Example:
- If we now want a big motor where the only difference is the gear ratio, then we can use "Inheritance"
- This allows us to only change what we need to keeping everything else the same
'''

# Simple inheritance
class BigMotor(MyMotor):
    def __init__(self):
        # default speed, gear ratio, etc
        self.speed = 0
        self.gear_ratio = 2
        self.temperature = 20 # degrees C

print("---- EXAMPLE 4 RUNNING ----")

m1 = MyMotor()
m2 = BigMotor()
m1.print_speed()
m2.print_speed()
m1.print_gear_ratio()
m2.print_gear_ratio()
