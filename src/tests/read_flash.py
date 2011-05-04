
# THIS SCRIPT IS NOT FOR PUBLIC USE, IT TESTS THE CURRENT VERSION OF GPS HARDWARE (NOT RELEASED YET)
# TODO:
# - seperate read and file generation process in classes
# - exception handling
# - lots of other things

#Copyright (C) 2011  Markus Hutzler, spiderware gmbh switzerland
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# markus dot hutzler at spiderware dot ch


import serial,sys


def f2sf(f):
    return f
    if f > 214.7483647:
        return -f+214.7483647
    else:
        return f
        
def array2uint32(a):
    return a[0]*0x1000000 + a[1]*0x10000 + a[2]*0x100 + a[3] 
    
def array2uint16(a):
    return a[0]*0x100 + a[1]

s = serial.Serial('/dev/tty.usbserial-A5004Gk9',115200,timeout=1)
#('/dev/tty.usbserial-A5004Gk9',115200)



s.write('mg\n') # memory get command
escape = False
data_in = True
data = []
frame = []
time_on = 0
time_off = 0
time_n = 0
c = ' '
bin = open('data.bin','w');

while not c == '|':
    c = s.read(1)
x = 0
while data_in:
    try:
        byte = int(s.read(2),16)
    except:
        print byte    
        break
    bin.write(chr(byte))
    x+=1
    
    if byte == 0x7e and escape:
        frame.append(byte)
        escape = False
        print 'escape 0x7e'

    elif byte == 0x7e:
        # start escape
        escape = True
           
    elif byte == 0x7e and escape:
        # escape FF
        frame.append(0xFF)   
        escape = False 
        print 'escape 0xFF'

    elif escape:
        #print new frame
        if not frame == []:
            data.append(frame)
        frame = [byte]
        escape = False
        
    else:
        if byte == 0xff:
            data_in = False
        else:
            #print hex(byte)
            frame.append(byte)
    
bin.close()
    
#print data

print 'len:',len(data)
ob = open('bat.csv','wb')
f_cnt = 0
tow_n = 0

week = 0
system_tow = 0

calculated = []
for frame in data:
    #print frame
    if len(frame) > 0:
        #print 'DATA:',frame, 'LEN:', len(frame) 
        # time frame
        if frame[0] == 0x01:
            week = array2uint16(frame[1:3])
            system_tow = array2uint32([0,frame[3],frame[4],frame[5]])
        
        elif frame[0] == 0x02:
            #print frame
            
            
            f_cnt+=1
            
            
            tow = system_tow + array2uint16(frame[1:3])   
            
            lat = array2uint32(frame[3:7])   
            lon = array2uint32(frame[7:11]) 
            alt = array2uint16(frame[11:13])    
            h_error = frame[13]   
            #print h_error 
            v_error = frame[14]
            flags =   frame[15]
            #print h
            if lat > 0x7fffffff:
                lat = -0x7fffffff+lat 
            if lon > 0x7fffffff:
                lon = -0x7fffffff+lon 
            if alt > 0x7fffffff:
                alt = -0x7fffffff+alt 
            if lat/10000000 < 47.0:
                print 'error?'
            s = tow
            day = s/86400
            h = (s-(day*86400))/3600
            m = (s-(day*86400)-(h*3600))/60
            s = s-(day*86400)-(h*3600)-(m*60)
            
            print '%d| %02d:%02d:%02d : pos: %.7f,%.7f\talt: %d\th:%d\tv:%d\tflags:%02x'%(f_cnt,h,m,s,f2sf(float(lat)/10000000),f2sf(float(lon)/10000000),alt,h_error,v_error,flags)
            calculated.append([week,tow,f2sf(float(lat)/10000000),f2sf(float(lon)/10000000),alt])
    
        elif len(frame) == 5 and frame[0] == 0x03:
            
            tow = system_tow + array2uint16(frame[1:3])   
            s = tow
            day = s/86400
            h = (s-(day*86400))/3600
            m = (s-(day*86400)-(h*3600))/60
            s = s-(day*86400)-(h*3600)-(m*60)
            stat = frame[3]
            
                        
            if stat == 0x00:
                stat = 'ERROR'
            elif stat == 0x01:
                stat = 'START UP'
            elif stat == 0x02:
                stat = 'STAND BY'
            elif stat == 0x03:
                stat = 'WAKE UP'
            elif stat == 0x04:
                stat = 'BREAK BEGINS'
            elif stat == 0x05:
                stat = 'BREAK ENDS'
            elif stat == 0x06:
                stat = 'GPS ON'
            elif stat == 0x07:
                stat = 'GPS OFF'
            elif stat == 0x08:
                stat = 'BATTERY LOW'
            elif stat == 0x09:
                stat = 'CHARGE BEGINS'
            elif stat == 0x0A:
                stat = 'CHARGE ENDS'
            elif stat == 0x0B:
                stat = 'WALL POWER ON'
            elif stat == 0x0C:
                stat = 'WALL POWER OFF'
            elif stat == 0x0D:
                stat = 'PROFILE'
            elif stat == 0x0E:
                stat = 'WAYPOINT'
            elif stat == 0x0F:
                stat = 'ACC OFF'
            elif stat == 0x10:
                stat = 'ACC ON'
            elif stat == 0x11:
                stat = 'NEW TRACK'
            elif stat == 0x12:
                stat = 'BATT'
                
            else:
                stat = 'unknown state! '+'0x%02x'%stat
            
            vbat = frame[4] * 24
            ob.write('%02d:%02d:%02d,%d,%s\n'%(h,m,s,vbat, stat))
            print '%d| %02d:%02d:%02d : Battery: %d\t%s'%(f_cnt,h,m,s,vbat, stat)
            
            
        else:
            print 'unknown:',frame, len(frame)    

time = time_on+time_off
#print 'on:',time_on,'off:',time_off,((float(time_off)*.1+float(time_on)*40.0))/time,'mA,',float(time)/60,'min'
ob.close()        

header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>test.kmz</name>
	<description><![CDATA[<h3></h3><b><i></i></b><br><p></p><br><p></p>]]></description>
	<Style id="line">
		<LineStyle>
			<color>7f0000ff</color>
			<width>4</width>
		</LineStyle>
	</Style>
	<Placemark>
		<styleUrl>#line</styleUrl>
		<LineString>
			<coordinates>
"""

footer = """
				</coordinates>
		</LineString>
	</Placemark>
	<Folder>
		<name>Geolives</name>
		<ScreenOverlay>
			<name>Geolives</name>
			<Icon>
				<href>http://www.geolives.ch/flash/logobig.gif</href>
			</Icon>
			<overlayXY x="0" y="-1" xunits="fraction" yunits="fraction"/>
			<screenXY x="0.01" y="0.02" xunits="fraction" yunits="fraction"/>
			<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>
			<size x="0" y="0" xunits="fraction" yunits="fraction"/>
		</ScreenOverlay>
	</Folder>
</Document>
</kml>

"""
o = open('out.kml','w')
o.write(header)

for l in calculated:
    o.write('%.8f,%.8f,0 '%(l[3],l[2]))
    


o.write(footer)
o.close()