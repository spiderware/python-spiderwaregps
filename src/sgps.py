#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is part of spiderwareGPS.
#    
#    pygEDA is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    spiderwareGPS is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with spiderwareGPS.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright 2012 Markus Hutzler, spiderware gmbh

import usb.core
import usb.util
import sys
import gpxpy
import gpxpy.gpx

import sgps.decoder
import sgps.frames

def mirror_byte(i):
    ret = 0x00
    
    for x in xrange(8):
        if i&1<<x:
            ret|=(1<<(7-x))
    return ret
    
def mirror_word(i):
    ret = 0x00
    
    for x in xrange(32):
        if i&1<<x:
            ret|=(1<<(31-x))
    return ret


class WorldLogUSB():
    def __init__(self):
        pass
        self.data_buffer = []
        self.ctrl_buffer = []
        
        
    def find(self):
        self.devices = usb.core.find(find_all=True, idVendor=0x2544, idProduct=0x0001)
        return len(self.devices)
        
    def write(self,data):
        if not self.ep_OUT:
            return 0
        self.ep_OUT.write(data)
        return 1
        
        
    def read(self,size):
        if not self.ep_IN:
            return None
        return self.ep_IN.read(size,10).tolist()
        
    def open_device(self,device=0):
        d = self.devices[device]
        d.set_configuration()
        conf = d.get_active_configuration()
        i = conf[(0,0)]
        self.ep_IN = conf[(0, 0)][1]
        self.ep_OUT = conf[(0, 0)][0]
    
    def get_memory_state(self):
        self.write([0x01])
        d = self.read(4)
        ret = d[3]*0x1000000+d[2]*0x10000+d[1]*0x100+d[0]
        return ret
    
    def get_memory(self,start,len):
        self.write([0x03,(start>>24)&0xff,(start>>16)&0xff,(start>>8)&0xff,start&0xff,len])
        return self.read(len)
        
    
    def erase_memory(self):
        self.write([0x04])
        return
    
    def get_battery_status(self):
        self.write([0x05])
        d = self.read(4)
        vbat = float(d[1]*0x100+d[0])*78.125/1000000.0
        charge = float(d[3]*0x100+d[2])/256.0
        print vbat
        return (vbat,charge)
    
    def get_unique_id(self):
        self.write([0x06])
        d = self.read(8)
        print d
        return d
    
    
    def get_device_info(self):
        self.write([0x07])
        d = self.read(8)
        print d
        return d
        
    
    def get_device_state(self):
        self.write([0x02])
        d = self.read(4)
        ret = d[3]*0x1000000+d[2]*0x10000+d[1]*0x100+d[0]
        return ret
         

def binary_string(data,size):
    ret = ''
    for i in xrange(size):
        if data&1:
            ret+='1'
        else:
            ret += '0'
        data = data >> 1
    return ret[::-1]

def print_help():
    print "possible commands:"
    print "\tconvert"
    print "\terase"
    print "\tinfo"

def print_flags(flags):
    if flags & (1<<2):
        print "FLAG_FRAM"
    if flags & (1<<3):
        print "FLAG_DATA"
    if flags & (1<<4):
        print "FLAG_BMA250"
    if flags & (1<<5):
        print "FLAG_SST25WF080"
    if flags & (1<<6):
        print "FLAG_RTC"
    if flags & (1<<7):
        print "FLAG_ACTIVE"
    if flags & (1<<8):
        print "FLAG_MOTION"
    if flags & (1<<9):
        print "FLAG_BT"
    if flags & (1<<10):
        print "FLAG_MODE"
    if flags & (1<<11):
        print "FLAG_STANDBY"
    if flags & (1<<12):
        print "FLAG_GPS_BUFFER_0"
    if flags & (1<<13):
        print "FLAG_GPS_BUFFER_1"
    if flags & (1<<14):
        print "FLAG_GPS_BINARY"
    if flags & (1<<15):
        print "FLAG_GPS_BUSY"
    if flags & (1<<16):
        print "FLAG_GPS_ON"
    if flags & (1<<17):
        print "FLAG_GPS_PTF_ACK"
    if flags & (1<<18):
        print "FLAG_GPS_NAV_OK"
    if flags & (1<<19):
        print "F_OFF"
    if flags & (1<<20):
        print "F_SLEEP"
    if flags & (1<<21):
        print "F_LOW_POWER"
    

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    
def get_raw(filename=None):
    if filename:
        data = []
        fh = open(filename,'rb')
        for byte in fh.read():
            data.append(ord(byte))
        fh.close()
        return data
    data = []
    current = 0
    mem = d.get_memory_state()
    while current < mem:
        data += d.get_memory(current,100)
        current += 100
    return data

def read_file(file):
    # read data from file
    ret = []
    print 'reading file:',file
    try:
        fh = open(file,'rb')
        for byte in fh.read():
            ret.append( ord(byte))
    except IOError:
        print 'file',file,'does not exist'
        exit(1)
    return ret

def read_device(info=False):
    ret = []
    # read data from USB
    print 'reading data from USB device'
    d = WorldLogUSB()
    d.find()
    try:
        d.open_device()
    except IndexError:
        print 'Device not found'
        exit(1)
        
    mem = d.get_memory_state()
    if info:
        print 'MEM  : %.02f'%(float(mem)/1024),'kByte'
        print 'FLAGS:',binary_string(d.get_device_state(),32)
        print_flags(d.get_device_state())
        vbat, charge = d.get_battery_status()
        print 'BATTERY: %.02fV, %.02f%%'%(vbat, charge)
        d.get_unique_id()
        d.get_device_info()
    sys.stdout.write('         |')
    sys.stdout.write( ' '*100)
    sys.stdout.write( '|\n')
    sys.stdout.write('READING: |')
    sys.stdout.flush()
    current = 0
    mem = d.get_memory_state()
    pc = mem/100
    current_pc = 0
    printed_pc = 0
    while current < mem:
        ret += d.get_memory(current,100)
        current += 100
        current_pc = current / pc
        #print current_pc, printed_pc
        if current_pc > printed_pc:
            for i in xrange(current_pc-printed_pc):
                sys.stdout.write('#')
                sys.stdout.flush()
            printed_pc = current_pc
    print '|'
    return ret
    
    
last_on = None
last_off = None
on_time = 0
off_time = 0
color = bcolors.ENDC
if __name__ == "__main__":
    # command line:
    # [] command source destination
    # examples:
    # sgps.py read usb data.json
    # sgps.py read data.bib data.json
    # sgps.py erase
    raw_data = []
    if len(sys.argv) < 2:
        print "no command given"
        print_help()
    cmd = sys.argv[1]
    
    if cmd == 'info':
        pass
        exit(0)
    if cmd == 'convert':
        if len(sys.argv) < 3:
            print "no source given"
            exit(1)
        # reading data
        if sys.argv[2] in ['USB','usb']:
            raw_data = read_device(True)
        else:
            raw_data = read_file(sys.argv[2])
            pass
        # at this point raw_data contains readed data from file or USB
        decoder = sgps.decoder.Decoder()
        decoder.decode(raw_data)
        
        if len(sys.argv) == 3:
            # print data on terminal
            print 'converting to terminal output'
            #print raw_data
            for item in decoder.data:
                if item.__class__.__name__ == 'System':
                    if item.debug_level() <= 1:
                        print item
                else:
                    print item
            pass
        elif sys.argv[3][-5:] == '.json':
            print 'converting to JSON'
            file = open(sys.argv[3],'w')
            for item in decoder.data:
                file.write(item.json())
            file.close()
            print 'JSON file: "%s" created'%sys.argv[3]

        elif sys.argv[3][-4:] == '.bin':
            # write file to disk (BIN format)
            print 'saving as BIN'
        elif sys.argv[3][-4:] == '.kml':
            # write file to disk (KML format)
            print 'converting to KML'
        elif sys.argv[3][-4:] == '.gpx':
            print 'converting to GPX'
            # write file to disk (GPX format)
            # Creating a new file:
            # --------------------
            
            gpx = gpxpy.gpx.GPX()
    
            # Create first track in our GPX:
            gpx_track = gpxpy.gpx.GPXTrack()
            gpx.tracks.append(gpx_track)
    
            # Create first segment in our GPX track:
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
            gpx_track.segments.append(gpx_segment)
            last_known_position = None
            for frame in decoder.data:
                if frame.__class__.__name__ == "Position":
                    last_known_position = frame
                    gpx_segment.points.append(frame.gpx_element())
                if frame.__class__.__name__ == "System" and last_known_position:
                    gpx_segment.points.append(frame.gpx_element(last_known_position))
    
            with open(sys.argv[3], 'w') as f:
                read_data = f.write(gpx.to_xml())
                f.closed
                
            print 'GPX file: "%s" created'%sys.argv[3]
        else:
            print "unknown output format:",  sys.argv[3]
            exit(1) 
        exit(0)
        
    if cmd == "erase":
        pass
        exit(0)
    print "unknown command:", sys.argv[1]
    print_help()
    exit(1)
    
    file = None
    if '--file' in sys.argv:
        try:
            file = sys.argv[sys.argv.index('--file')+1]
            cmd = sys.argv[sys.argv.index('--file')+2]
        except IndexError:
            print 'unknown arguments'
            #print_help()
            exit(1)
        
    if '--usb' in sys.argv:
        try:
            cmd = sys.argv[sys.argv.index('--usb')+1]
        except IndexError:
            print 'command missing'
            print_help()
            exit(1)
            
        d = WorldLogUSB()
        d.find()
        d.open_device()
        mem = d.get_memory_state()
        
        data = []
        
        print 'MEM  : %.02f'%(float(mem)/1024),'kByte'
        print 'FLAGS:',binary_string(d.get_device_state(),32)
        print_flags(d.get_device_state())
        vbat, charge = d.get_battery_status()
        print 'BATTERY: %.02fV, %.02f%%'%(vbat, charge)
        d.get_unique_id()
        d.get_device_info()
    
    if cmd == 'info' and not file:
        pass
    elif cmd == 'erase' and not file:
        d.erase_memory()
        print 'erasing memory...'
        print 'MEM  : %.02f'%(float(d.get_memory_state())/1024),'kByte'

    elif cmd == 'save_raw' and not file:
        data = get_raw(file)
        
    elif cmd == 'save_gpx':
        data = get_raw(file)
        print data
    
        decoder = sgps.decoder.Decoder()
        decoder.decode(data)
        # Creating a new file:
        # --------------------
        
        gpx = gpxpy.gpx.GPX()

        # Create first track in our GPX:
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        # Create first segment in our GPX track:
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        
        for frame in decoder.data:
            print frame
            gps_data = frame.gps_data()
            if(gps_data != None):
                gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(latitude=gps_data["latitude"], longitude=gps_data["longitude"], elevation=gps_data["elevation"],time=gps_data["timestamp"],horizontal_dilution=gps_data["horizontal_error"],vertical_dilution=gps_data["vertical_error"]))

        with open('out.gpx', 'w') as f:
            read_data = f.write(gpx.to_xml())
            f.closed
        
    elif cmd == 'read':
        data = get_raw(file)
    
        decoder = sgps.decoder.Decoder()
        decoder.decode(data)
        for frame in decoder.data:
            if frame.frame_id == 0x01:
                color = bcolors.OKBLUE
            elif frame.frame_id == 0x03:
                if frame.msg == 4:
                    color = bcolors.OKGREEN
                if frame.msg == 5:
                    color = bcolors.WARNING
                if frame.msg == 6:  # gps on
                    last_on = frame.timestamp
                    if last_on and last_off:
                        off_time += (last_on - last_off).total_seconds()
                if frame.msg == 7: # gps off
                    last_off = frame.timestamp
                    if last_on and last_off:
                        on_time += (last_off - last_on).total_seconds()
                        print (last_off - last_on).total_seconds()
                    
            print color+frame.description()+bcolors.ENDC,
            if on_time and off_time:
                pc = float(on_time)/(float(on_time)+float(off_time))
                ma = pc*30+(1-pc)*0.12
                print  '\t\tON: '+str(on_time)+'\tOFF: '+str(off_time)+'\t'+str(pc*100)+'%'+'\t'+str(ma)+'mA'
            else:
                print
            color = bcolors.ENDC
    else:
        print "unknown command:", sys.argv[1]
        print_help()
