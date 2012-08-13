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

import datetime
import time

system_flags = ['error',
                'start up',
                'stand by',
                'wake up',
                'break begins',
                'break ends',
                'gps on',
                'gps off',
                'battery low',
                'charging begins',
                'charging ends',
                'wall power on',
                'wall power off',
                'changed profile',
                'waypoint',
                'accelerometer off',
                'accelerometer on',
                'new track begins','18','19','20','21','22','23','','','','','','','','',
                ]


#TODO: this is not an elegant way to do it. Make it better! 
def array2uint32(a):
    return a[0]*0x1000000 + a[1]*0x10000 + a[2]*0x100 + a[3] 

#TODO: this is not an elegant way to do it. Make it better! 
def array2uint24(a):
    return a[0]*0x10000 + a[1]*0x100 + a[2]  
    
#TODO: this is not an elegant way to do it. Make it better! 
def array2uint16(a):
    return a[0]*0x100 + a[1]
    
    
def gpstime2datetime(weeks,tow):
    return datetime.datetime(1980,1,6) + datetime.timedelta(weeks=weeks,seconds=tow)


class SGPSObject(object):
    timestamp = 0
    escaped = False
    pass

    def gps_data(self):
        return None
    

class Time(SGPSObject):
    frame_id = 0x01
    tow = 0  # time of week in seconds
    week = 0  # week number since 1980-01-06
    
    
    def __init__(self, data):
        self.week = array2uint16(data[0:2])
        self.tow = array2uint24(data[2:5])
        self.timestamp = gpstime2datetime(self.week,self.tow)
        
    def description(self):
        return '<Time %s>'%self.timestamp
        
    def get_timestamp(self,offset=0):
        return self.timestamp + datetime.timedelta(seconds=offset)
        
class Position(SGPSObject):
    frame_id = 0x02
    offset = 0  # time since last timeframe (in seconds)
    lat = 0.0
    lon = 0.0
    alt = 0
    v_error = 0
    h_error = 0
    flags = 0
    data = []
    timestamp = None
    
    def __init__(self, data, time):
        self.data = data
        self.offset  = array2uint16(data[0:2]) 
        if time:  
            self.timestamp = time.get_timestamp(self.offset)
        
        self.lat = array2uint32(data[2:6])   
        self.lon = array2uint32(data[6:10]) 
        self.alt = array2uint16(data[10:12])    
        self.h_error = data[12]   
        self.v_error = data[13]
        self.flags =   data[14]
        
        if(self.lat & 0x80000000):
            self.lat = -0x100000000 + self.lat
        if(self.lon & 0x80000000):
            self.lon = -0x100000000 + self.lon
        if(self.alt & 0x8000):
            self.alt = -0x10000 + self.alt
    
    
    def description(self):
        s = '<%s (+%ds)\t'%(self.timestamp, self.offset)
        s += 'Position'
        return s+' lat=%f lon=%f (+/- %dm) alt=%dm (+/- %dm) escaped: %s>'%(float(self.lat)/10000000,float(self.lon)/10000000,self.h_error,self.alt,self.v_error,str(self.escaped))
    
    def kml(self, max_error=100000):
        #TODO: Better error handling needed
        if self.h_error < max_error and self.lat and self.lon:
            return '%f,%f,%d ' % (float(self.lon)/10000000,float(self.lat)/10000000,self.alt)
        return ''
    def gps_data(self):
        return {"timestamp":self.timestamp,"latitude":float(self.lat)/10000000,"longitude":float(self.lon)/10000000,"elevation":self.alt,"horizontal_error":self.h_error,"vertical_error":self.v_error}
    
        
class System(SGPSObject):
    frame_id = 0x03
    msg = 0
    rfu = 0
    offset = 0
    
    def __init__(self, data, time_frame=0):
        self.offset  = array2uint16(data[0:2]) 
        if time_frame:
            self.timestamp = time_frame.get_timestamp(self.offset)
        self.msg = data[2]   
        self.rfu = data[3]
        
    def description(self):
        s = '<%s (+%ds)\t'%(self.timestamp, self.offset)
        s += 'System msg="%s", refu=%d, escaped: %s>'%(system_flags[self.msg],self.rfu,str(self.escaped))
        return s
    
class Unknown(SGPSObject):
    frame_id = 0xff
    data = []
    rfu = 0
    
    def __init__(self, data):
        self.data = data 
        
    def description(self):
        s = '<Unknown  '+str(len(self.data))+'\t'+str(self.escaped)+'\t'
        for x in self.data:
            s += ' %.2x' % x
        s += '>'
        return s




    
