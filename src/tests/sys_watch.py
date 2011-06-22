import serial,sys, datetime

s = serial.Serial('/dev/tty.usbserial-A5UBS4UK',115200)


def msg(stat):
    if stat == "00":
        return 'ERROR'
    elif stat == "01":
        return 'START UP'
    elif stat == "02":
        return 'STAND BY'
    elif stat == "03":
        return 'WAKE UP'
    elif stat == "04":
        return 'BREAK BEGINS'
    elif stat == "05":
        return 'BREAK ENDS'
    elif stat == "06":
        return 'GPS ON'
    elif stat == "07":
        return 'GPS OFF'
    elif stat == "08":
        return 'BATTERY LOW'
    elif stat == "09":
        return 'CHARGE BEGINS'
    elif stat == "0A":
        return 'CHARGE ENDS'
    elif stat == "0B":
        return 'WALL POWER ON'
    elif stat == "0C":
        return 'WALL POWER OFF'
    elif stat == "0D":
        return 'PROFILE'
    elif stat == "0E":
        return 'WAYPOINT'
    elif stat == "0F":
        return 'ACC OFF'
    elif stat == "10":
        return 'ACC ON'
    elif stat == "11":
        return 'NEW TRACK'
    elif stat == "12":
        return 'BATT'
    else:
        return '??'

while 1:
    line = s.readline()
    if line[:5] == "SYS: ":
        for msg_pos in xrange(len(line[5:])/4):
            print datetime.datetime.now(),"SYS", msg(line[5+msg_pos*4:5+msg_pos*4+2]),line[5+msg_pos*4+2:5+msg_pos*4+4]
        
    else: 
        print datetime.datetime.now(),line.strip()