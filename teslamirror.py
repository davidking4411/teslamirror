from gpiozero import Button, LED,MotionSensor
from gpiozero.pins.pigpio import PiGPIOFactory
import datetime as dt
import time
import yaml
import os
from SmartMirrorLaptop.teslajason import teslajason

def write_data():
    v.wake_up()
    time.sleep(2)
    data = v.data_request('charge_state')
    yamldata = dict(
        battery_level = data['battery_level'],
	battery_range = int(data['battery_range']),
	cabin_temp = int(v.data_request('climate_state')['inside_temp']*9/5+32),
        string = ''
    )
    print(yamldata)

    with open('SmartMirrorLaptop/data.yml', 'w') as outfile:
        yaml.dump(yamldata, outfile, default_flow_style=False)

    return yamldata

def write_string(string):
    yamldata['string'] = string

    with open('SmartMirrorLaptop/data.yml', 'w') as outfile:
        yaml.dump(yamldata, outfile, default_flow_style=False)

def start_conditioning():
    print('Conditioning vehicle')
    v.wake_up()
    v.command('auto_conditioning_start')

def open_garagedoor():
    # uses gpiozero's remote gpio module
    try:
        factory = PiGPIOFactory(host='')
        door = LED(12,pin_factory=factory)
        door.on()
        time.sleep(.2)
        door.off()
    except:
        print('Garage door not connected')
    write_string('Garagedoor opened')
    time.sleep(10)
    write_string('')

c = teslajason.Connection( access_token = '') # an easy way to get your token is at http://eviecar.io/falcon/teslaweb/?q=generate_token_html
v = c.vehicles[0]
motsense = MotionSensor(4) # motion sensor
motsense.threshold = .8
button = Button(26) # physical button on right
button2 = Button(5) # physical button 2 on left
display = LED(12) # display driver opticoupler
displaycount = 0 # initialize motion sensor timer
displayon = True # is the display starting on?
try:
    yamldata = write_data() # to initialize yamldata dictionary
except:
    time.sleep(4)
    yamldata = write_data()

while True:
    if button.is_pressed: # button on right
        print("Button 1 is pressed")
        buttoncount = 0
        while button.is_pressed:
            print('Button 1 being pressed',buttoncount)
            buttoncount+=1
            time.sleep(.1)
        if buttoncount > 10:
            #button1 held down
            print('Fetching data from vehicle')
            write_string('Fetching data from vehicle')
            try:
                yamldata = write_data()
            except:
                time.sleep(5)
                yamldata = write_data()
        else:
		#open blinds

    if button2.is_pressed: # button on left
        print("Button 2 is pressed")
        buttoncount2 = 0
        while button2.is_pressed:
            print('Button 2 being pressed',buttoncount2)
            buttoncount2+=1
            time.sleep(.1)
        if buttoncount2 > 10:
            print('button2 held')
            write_string('Preconditioning Ted')
            try:
                start_conditioning()
            except:
                print('Retrying conditioning')
                time.sleep(5)
                start_conditioning()
            time.sleep(5)
            write_string('')
        else:
            print('Button2 not held. Opening garagedoor')
            write_string('Opening garagedoor')
            #open_garagedoor()
            time.sleep(5)
            write_string('')

    if motsense.is_active: # turn on display
        print("motion detected")
        displaycount = 0 #reset counter start
        if not displayon: # turn on if it didn't start on
            display.on()
            time.sleep(.3)
            display.off()
            displayon = True
    elif displaycount == 5*60*5: # turn off display
        display.on()
        time.sleep(.3)
        display.off()
        displayon = False
        displaycount+=1
    else:
        print("Nothing detected")
        displaycount += 1
    #update yaml at specific time
    if dt.datetime.now().hour == 8 and dt.datetime.now().minute == 35 and dt.datetime.now().second < 1:
        try:
            yamldata = write_data()
        except:
            print('First API attempt failed. Trying again...')
            time.sleep(10)
            yamldata = write_data()
            time.sleep(2)
    print (dt.datetime.now())
    time.sleep(.2)
    print('displaycount',displaycount)
