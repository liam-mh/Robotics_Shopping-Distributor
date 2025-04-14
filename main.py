from vex import *
import urandom

brain = Brain()
brain_inertial = Inertial()
paddle_2 = Motor(Ports.PORT1)
paddle_1 = Motor(Ports.PORT2) 
belt = Motor(Ports.PORT3, True)
ai_vision = AiVision(Ports.PORT4, AiVision.ALL_TAGS)
pusher = Motor(Ports.PORT5)
pusher.set_velocity(30, PERCENT)

wait(100, MSEC)

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

def use_paddle(inputMotor, length) :
    motor = inputMotor
    motor.set_position(0, DEGREES)
    motor.spin_to_position(70, DEGREES)
    wait(length, MSEC)  
    motor.spin_to_position(0, DEGREES)
    wait(2000, MSEC)  
    motor.stop()

def drive_belt() :
    belt.set_velocity(30, PERCENT)
    while True:
        belt.spin(FORWARD)
        wait(100, MSEC)

def push_item() :
    motor = pusher
    motor.set_position(0, DEGREES)
    motor.spin_to_position(-160, DEGREES)
    wait(1000, MSEC)  
    motor.spin_to_position(0, DEGREES)
    wait(2000, MSEC)  
    motor.stop()

def ai_cam() :
    ai_objects = ai_vision.take_snapshot(AiVision.ALL_TAGS)
    length = str(len(ai_objects))
    if len(ai_objects) > 0:
        tag = ai_objects[0].id
        if tag is not None:
            return tag
    return None

def get_item_from_id(scan_id) :
    for item in items:
        if scan_id == item["id"]: 
            return item 
    return None

def print_item(item) :
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
    total = 0
    for item in shop :
        total = total + item["price"]
    brain.screen.clear_screen()  
    brain.screen.set_cursor(1, 1)
    brain.screen.print('total: ', total)

shop = []
belt_thread = Thread(drive_belt)
while True:

    scan_id = None
    scan_id = ai_cam()

    if scan_id is 29 : 
        brain.play_sound(SoundType.TADA)
        belt.set_velocity(0, PERCENT) 
        print_shop()
        wait(5000, MSEC) 
        break

    elif scan_id is not None:

        brain.play_note(1, 4, 200, 50)
        matched_item = get_item_from_id(scan_id)
        
        if matched_item :
            
            print_item(matched_item)
            shop.append(matched_item)

            wait(1000, MSEC) 
            pusher_thread = Thread(push_item)

            if matched_item["temp"] == "fridge" :
                paddle_thread = Thread(use_paddle(paddle_2, 3000))
                paddle_thread.stop()

            elif matched_item["temp"] == "frozen" :
                paddle_thread = Thread(use_paddle(paddle_1, 1800))
                paddle_thread.stop()

            else :
                wait(3000, MSEC)

            pusher_thread.stop()
        
        else :
            brain.screen.clear_screen()  
            brain.screen.set_cursor(1, 1)
            brain.screen.print('Unrecognised item')
            brain.screen.next_row()
            brain.screen.print('please remove')
            brain.play_sound(SoundType.POWER_DOWN)
            wait(2000, MSEC)