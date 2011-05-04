import serial,sys

s = serial.Serial('/dev/tty.usbserial-A5004Gk9',115200)

s.write(sys.argv[1]+'\n')
while 1:
    sys.stdout.write(s.read(1))
    sys.stdout.flush()