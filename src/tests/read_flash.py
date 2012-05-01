13
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


#! /usr/bin/env python
"""\
    Scan for serial ports. Linux specific variant that also includes USB/Serial
    adapters.
    
    Part of pySerial (http://pyserial.sf.net)
    (C) 2009 <cliechti@gmx.net>
    """

import sys
import os
import serial
import glob

def scan():
    """scan for available ports. return a list of device names."""
    return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + glob.glob('/dev/tty.*')


def scan_win():
    """scan for available ports. return a list of tuples (num, name)"""
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.portstr))
            s.close()   # explicit close cause of delayed GC in java
        except serial.SerialException:
            pass
    print available
    return available



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



def read_bin(debug=False):
    s.write('mg\n') # memory get command
    s.flushInput()
    escape = False
    data_in = True
    data = []
    frame = []
    time_on = 0
    time_off = 0
    time_n = 0
    cycle_cnt = 0
    c = ' '
    bin = open('data.bin','w');
    
    x = 0
    byte = 0
    while data_in:
        byte = s.read(2)
        if debug:
            sys.stdout.write(byte)
        try:
            byte = int(byte,16)
        except:
            print byte    
            break
        bin.write(chr(byte))
        x+=1
        
        if byte == 0x7e and escape:
            frame.append(byte)
            escape = False
            #print 'escape 0x7e'
    
        elif byte == 0x7e:
            # start escape
            escape = True
               
        elif byte == 0x7f and escape:
            # escape FF
            frame.append(0xFF)   
            escape = False 
            #print 'escape 0xFF'
    
        elif escape:
            #print new frame
            if not frame == []:
                data.append(frame)
            frame = [byte]
            escape = False
            
        else:
            if byte == 0xff:
                data_in = False
                data.append(frame)
            else:
                #print hex(byte)
                frame.append(byte)
        
    bin.close()



if __name__=='__main__':
    port_selected = False
    
    while not port_selected:
        print "Found ports:"
        ind = 1
        if os.name == 'nt':
            devlist = scan_win()
        else:
            devlist = scan()
        for name in devlist:
            print ind, name
            ind+=1
        sys.stdout.write('choose port [1..%i]: '%(ind-1))
        answer = sys.stdin.readline()
        
        try:
            answer = int(answer.strip())
        except ValueError:
            print 'Please enter a correct value!'
        try:
            port = devlist[answer-1]
            port_selected = True
        except IndexError:
            print 'Please enter a correct value!'
    print 'selected port:', port

    # if windows
    if os.name == 'nt':
        s = serial.Serial(port[0],115200,timeout=1)

    # if linux
    else:
        s = serial.Serial(port,115200,timeout=1)


    if s:
        print 'port opend.',
    while not answer == 'q':    
        print 'What do you want to do?'
        print 'rb: read data and save as binary'
        print 'rbd: read data and save as binary (debug mode)'
        print 'mem: get current memory status'
        print 'erase: get current memory status'
        print 'kml: save data as kml-file'
        print 'q: exit program'
        sys.stdout.write('> ')
        answer = sys.stdin.readline()
        answer = answer.strip()
    
        if answer == 'mem':
            s.write('mp\n')
            s.flushInput()
            d = ''
            c = ''
            while not c == '\n':
                c = s.read(1)
                d += c
            status = int(d[:8],16)
            print status/1024,'kByte, (',float(status)/(1024*1024)*100,'%)'
                
        if answer == 'rbd':
            print 'reading...',
            read_bin(debug=True)

        if answer == 'rb':
            print 'reading...',
            read_bin()
            print 'DONE. (saved as data.bin)'
            """
            s.flush()
            s.write('mg\n')
            while 1:
                sys.stdout.write( s.read(1) )
            """
            
        if answer == 'erase':
            print 'erasing...',
            s.write('me\n')
            print 'DONE.'
            
    # done
    s.close()
    print 'bye bye'
        
exit (0)



    
#print data



exit(0)

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
            if len(frame) == 6:
                week = array2uint16(frame[1:3])
                system_tow = array2uint32([0,frame[3],frame[4],frame[5]])
            else:
                print 'bat time frame' 
        elif frame[0] == 0x02:
            if len(frame) == 16:
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
            else:
                print 'frame 0x02 corrupt!!!'
    
        elif len(frame) >= 5 and frame[0] == 0x03:
            
            tow = system_tow + array2uint16(frame[1:3])   
            s = tow
            day = s/86400
            h = (s-(day*86400))/3600
            m = (s-(day*86400)-(h*3600))/60
            s = s-(day*86400)-(h*3600)-(m*60)
            stat = frame[3]
            
            for i in xrange(len(frame[3:])/2): 
                stat = frame[3+i*2]
                rfu = frame[3+i*2+1]
                if stat == 0x00:
                    stat = 'ERROR'
                elif stat == 0x01:
                    stat = 'START UP'
                    print '-----------------------------------'
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
                    time_off += rfu;
                elif stat == 0x07:
                    stat = 'GPS OFF'
                    time_on += rfu;
                    cycle_cnt += 1;
                elif stat == 0x08:
                    stat = 'BATTERY LOW'
                    rfu = rfu*24
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
                    rfu = rfu*24
                    
                else:
                    stat = 'unknown state! '+'0x%02x'%stat
                
                ob.write('%02d:%02d:%02d,%d,%s\n'%(h,m,s,rfu, stat))
                print '%d| %02d:%02d:%02d : %s (%d)'%(f_cnt,h,m,s,stat,rfu)
            
            
        else:
            print 'unknown:',frame, len(frame)    

if cycle_cnt and time_on and time_off:
    print '----------------------- REPORT: --------------------------'
    print 'GPS on:',time_on,'\tGPS off:',time_off,'\tcurrent:',float(1*time_off+35*time_on)/(time_on+time_off),'mA'#((float(time_off)*.1+float(time_on)*40.0))/time,'mA,',float(time)/60,'min'
    print '----------------------------------------------------------'

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