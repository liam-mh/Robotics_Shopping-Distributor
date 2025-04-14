# -------------------------------------------------------------------
# 	Project:      Robotics Task 2: Shopping Distributor
#	  Author:       Liam Hammond C1022456 
#                 Guy Nicklin C1009267
#	  Created:      01/04/2025
# -------------------------------------------------------------------

# Imports
# -------------------------------------------------------------------
from vex import *

# Robot Configuration
# -------------------------------------------------------------------
brain          = Brain()
brain_inertial = Inertial()
paddle_2       = Motor(Ports.PORT1)
paddle_1       = Motor(Ports.PORT2) 
belt           = Motor(Ports.PORT3, True)
ai_vision      = AiVision(Ports.PORT4, AiVision.ALL_TAGS)
pusher         = Motor(Ports.PORT5)
pusher.set_velocity(30, PERCENT)
wait(100, MSEC) # ensure init

# Constants
# -------------------------------------------------------------------
items = [
    {"id": 1, "name": "Milk",           "price": 1.99, "temp": "fridge"},
    {"id": 5, "name": "Cheese",         "price": 3.59, "temp": "fridge"},
    {"id": 4, "name": "Chicken Breast", "price": 6.49, "temp": "fridge"},

    {"id": 9, "name": "Frozen Peas",    "price": 1.89, "temp": "frozen"},
    {"id": 2, "name": "Frozen Pizza",   "price": 1.99, "temp": "frozen"},
    {"id": 6, "name": "Ice Cream",      "price": 4.49, "temp": "frozen"},

    {"id": 7, "name": "Eggs",           "price": 2.99, "temp": "dry"},
    {"id": 8, "name": "Beans",          "price": 0.39, "temp": "dry"},
    {"id": 3, "name": "Rice",           "price": 1.99, "temp": "dry"},

    {"id": 29, "name": "Checkout"},
]

shop = []

# Motor Functions
# -------------------------------------------------------------------
def use_paddle(inputMotor, length) :
    # Controls a motor to simulate a paddle movement.
    # Args:
    #     inputMotor: The motor object to control.
    #     length: The duration in milliseconds to hold the paddle at the extended position.
    motor = inputMotor
    motor.set_position(0, DEGREES)
    motor.spin_to_position(70, DEGREES)
    wait(length, MSEC)  
    motor.spin_to_position(0, DEGREES)
    wait(2000, MSEC)  
    motor.stop()

def drive_belt() :
    # Controls a motor to turn the drive belt.
    belt.set_velocity(30, PERCENT)
    while True:
        belt.spin(FORWARD)
        wait(100, MSEC)

def push_item() :
    # Controls a motor to move an item from the initial platform onto the drive belt.
    motor = pusher
    motor.set_position(0, DEGREES)
    motor.spin_to_position(-160, DEGREES)
    wait(1000, MSEC)  
    motor.spin_to_position(0, DEGREES)
    wait(2000, MSEC)  
    motor.stop()

# Helper Functions
# -------------------------------------------------------------------
def ai_cam() :
    # Uses the ai camera to detect labels.
    # Returns:
    #     int | None.
    ai_objects = ai_vision.take_snapshot(AiVision.ALL_TAGS)
    length = str(len(ai_objects))
    if len(ai_objects) > 0:
        tag = ai_objects[0].id
        if tag is not None:
            return tag
    return None

def get_item_from_id(scan_id) :
    # Checks the items array for matching item.
    # Args:
    #     scan_id: int
    # Returns:
    #     item{} | None.
    for item in items:
        if scan_id == item["id"]: 
            return item 
    return None

# Printer Functions
# -------------------------------------------------------------------
def print_item(item) :
    # Prints the item content to the screen.
    # Args:
    #    item: item{}
    brain.screen.clear_screen()  
    brain.screen.set_cursor(1, 1)
    brain.screen.print(item["id"])
    brain.screen.next_row()
    brain.screen.print(item["name"])
    brain.screen.next_row()
    brain.screen.print(item["price"])
    brain.screen.next_row()
    brain.screen.print(item["temp"])
    brain.screen.next_row()

def print_shop() :
    # Prints total price of the shop array.
    total = 0
    for item in shop :
        total = total + item["price"]
    brain.screen.clear_screen()  
    brain.screen.set_cursor(1, 1)
    brain.screen.print('total: ', total)


# Main Run File
# -------------------------------------------------------------------
# Start the drive belt on thread
belt_thread = Thread(drive_belt) 
while True:

    # Scan present barcodes
    scan_id = None
    scan_id = ai_cam()

    # Checkout edge case
    if scan_id is 29 : 
        brain.play_sound(SoundType.TADA)
        belt.set_velocity(0, PERCENT) 
        print_shop()
        wait(5000, MSEC) 
        break

    # Present item edge case
    elif scan_id is not None:

        brain.play_note(1, 4, 200, 50)
        matched_item = get_item_from_id(scan_id)
        
        # Valid item edge case
        if matched_item :
            
            print_item(matched_item)
            shop.append(matched_item)
            wait(1000, MSEC) 

            # Move valid item onto the conveyor belt
            pusher_thread = Thread(push_item)

            # Sort item dependent on temperature edge case
            # Direct item to fridge
            if matched_item["temp"] == "fridge" :
                paddle_thread = Thread(use_paddle(paddle_2, 3000))
                paddle_thread.stop()

            # Direct item to freezer
            elif matched_item["temp"] == "frozen" :
                paddle_thread = Thread(use_paddle(paddle_1, 1800))
                paddle_thread.stop()

            # Direct item to dry store
            else :
                wait(3000, MSEC)

            pusher_thread.stop()
        
        # Error handle invalid barcode
        else :
            brain.screen.clear_screen()  
            brain.screen.set_cursor(1, 1)
            brain.screen.print('Unrecognised item')
            brain.screen.next_row()
            brain.screen.print('please remove')
            brain.play_sound(SoundType.POWER_DOWN)
            wait(2000, MSEC)