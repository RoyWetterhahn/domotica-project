import socket
import sys
from _thread import *
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
host = ''
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

lamp_pins = {
    "1": 3,
    "2": 5,
    "3": 7,
    "4": 8,
}
for lamp, pin in lamp_pins.items():
    stringlamp = str(lamp)
    stringpin = str(pin)
    print (stringlamp + "is connected to pin" + stringpin)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

lamps = {
    "1": "off",
    "2": "off",
    "3": "off",
    "4": "off"
}
try:
    s.bind((host, port))
except socket.error as e:
    print(str(e))

s.listen(5)
print('Waiting for a connection.')

def threaded_client(conn):
    print(conn)
    #conn.send(bytes('welcome type your info\n','utf-8'))
    command = ''
    while True:
        data = conn.recv(1024)
        if not data:
            break
        command = command + data.decode('utf-8')
        splitCommand = command.split()
        print("splitCommand: ", splitCommand)
        if (str(splitCommand[0])) == "lamp":
            if len(splitCommand) != 3:
                print_all (conn, "this function only accepts 3 args: item, index, state")
            else:
                controlLamp(conn, splitCommand[0], splitCommand[1], splitCommand[2])
        else:
            print_all (conn, "this function only accepts 3 args: lamp, lampnumber, state")

        #splitStringCommand = 'test'.join(splitCommand)
        conn.sendall(str.encode('Server output: '+command))
        #print (splitStringCommand)
        #conn.sendall(str.encode('split command: '+splitStringCommand))
        command = ''
        conn.close()

def print_all(conn, message):
    print("message", message)
    string_message = str(message)
    conn.sendall(str.encode("message: " + string_message))

def controlLamp(conn, cm1, cm2, cm3):
    #print (cm1, cm2, cm3)
    if cm2 not in lamps:
        print_all(conn, ("lamp", cm2, "Bestaat Niet"))
        return None
    print ("lamp", cm2, " = ", lamps[cm2])
    if cm3 == "on":
        print_all (conn, ("setting ", cm1, cm2, "on"))
        if str(lamps[cm2]) == "off":
            lamps[cm2] = "on"
            GPIO.output(lamp_pins[cm2], 1)
            print_all(conn, ("lamp", cm2, "has been turned on"))
        else:
            print_all(conn, ("lamp", cm2, "Is already on"))

    elif cm3 == "off":
        print_all (conn, ("setting", cm1, cm2, "off"))
        if str(lamps[cm2]) == "on":
            lamps[cm2] = "off"
            GPIO.output(lamp_pins[cm2], 0)
            print_all(conn, ("lamp", cm2, "has been turned off"))
        else:
            print_all(conn, ("lamp", cm2, "is already off"))

    else:
        print_all (conn, ("3rd argument lamp must be (on) or (off)"))

while True:
    conn, addr = s.accept()
    print('connected to: '+addr[0]+':'+str(addr[1]))
    start_new_thread(threaded_client,(conn,))
