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
    print "\tread"
    print "\terase"

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
    
last_on = None
last_off = None
on_time = 0
off_time = 0
color = bcolors.ENDC
if __name__ == "__main__":
    d = WorldLogUSB()
    d.find()
    d.open_device()
    mem = d.get_memory_state()
    current = 0
    data = []
    print 'MEM  : %.02f'%(float(mem)/1024),'kByte'
    print 'FLAGS:',binary_string(d.get_device_state(),32)
    print_flags(d.get_device_state())
    vbat, charge = d.get_battery_status()
    print 'BATTERY: %.02fV, %.02f%%'%(vbat, charge)
    d.get_unique_id()
    d.get_device_info()
    
    if not len(sys.argv) > 1:
        print 'command missing'
        print_help()
        exit(1)
    
    if sys.argv[1] == 'erase':
        d.erase_memory()
        print 'erasing memory...'
        print 'MEM  : %.02f'%(float(d.get_memory_state())/1024),'kByte'

    elif sys.argv[1] == 'save':
        while current < mem:
            data += d.get_memory(current,100)
            current += 100; 
    
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
            gps_data = frame.gps_data()
            if(gps_data != None):
                gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(latitude=gps_data["latitude"], longitude=gps_data["longitude"], elevation=gps_data["elevation"],time=gps_data["timestamp"],horizontal_dilution=gps_data["horizontal_error"],vertical_dilution=gps_data["vertical_error"]))

        with open(sys.argv[2], 'w') as f:
            read_data = f.write(gpx.to_xml())
            f.closed
        
    elif sys.argv[1] == 'read':
        while current < mem:
            data += d.get_memory(current,100)
            current += 100; 
    
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
