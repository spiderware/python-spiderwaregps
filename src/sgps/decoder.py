#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    This file is part of the worldLog project.
#    
#    python-worldLog-scripts is free software: you can redistribute it and/or modify
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
#    along with python-worldLog-scripts.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright 2012 Markus Hutzler, spiderware gmbh

__author__ = "Markus Hutzler, spiderware gmbh"
__copyright__ = "Copyright 2012, spiderware gmbh"
__credits__ = ["Markus Hutzler", "Stefan Foulis", "David Gunzinger"]
__license__ = "GPL"
__version__ = "0.2"
__maintainer__ = "Markus Hutzler"
__status__ = "Beta"

import sgps.frames
import datetime
import pois

class Decoder(object):

    def __init__(self):
        self.data = []
        self.current_time = None
        
    def generate_object(self,f):
        if f[0] == 0x01 and len(f) == 6:
            self.current_time = sgps.frames.Time(f,None)
            return self.current_time
        elif f[0] == 0x02 and len(f) == 16:
            return sgps.frames.Position(f,self.current_time)
        elif f[0] == 0x03 and len(f) == 5:
            return sgps.frames.System(f,self.current_time)
        else:
            return sgps.frames.Unknown(f,self.current_time)

    def objects(self,filter=[]):
        # only for testing, this tool is not made for POIs and optimazions
        ret = []
        break_start = None
        break_end = None
        in_break = False
        # add POIs to object list
        for obj in self.data:
            if obj.__class__.__name__ == "Position":
                if ('POI' in filter or 'TrackStart' in filter) and in_break:
                    in_break = False
                    if break_end.timestamp() and break_start.timestamp():
                        time = break_end.timestamp() - break_start.timestamp()
                        if time.total_seconds() > 2*60 and 'POI' in filter:
                            ret.append(sgps.frames.POI(current_position.location,break_start.timestamp(),"Break %s"%time,'','break',symbol='Picnic Area'))
                        if time.total_seconds() > 10*60*60 and 'TrackStart' in filter:
                            ret.append(sgps.frames.TrackStart(current_position.location,break_end.timestamp()))
                current_position = obj
                if 'Position' in filter:
                    ret.append(obj)
                
            if obj.__class__.__name__ == "System":
                if 'System' in filter:
                    ret.append(obj)
                
                if 'POI' in filter or 'TrackStart' in filter:
                    if obj.msg == 4 and not in_break: #Break beginns
                        break_start = obj
                        in_break = True
                    elif obj.msg == 5: # Break ends
                        break_end = obj
                        
                    elif obj.msg == 14 and 'POI' in filter: # waypoint
                        #def __init__(self, location, timestamp, name, description, type):
                        ret.append(sgps.frames.POI(current_position.location,obj.timestamp(),"Waypoint %d"%obj.rfu,'','std_waypoint'))
        return ret
                
                    
           
    def decode(self,raw):
        # binary data to frame objects
        byte = 0
        escape = 0
        frame = []
        escaped = False
        for byte in raw:
            if byte == 0x7e and escape:
                frame.append(byte)
                escape = False
                escaped = True
                #print 'escape 0x7e'
        
            elif byte == 0x7e:
                # start escape
                escape = True
                   
            elif byte == 0x7f and escape:
                # escape FF
                frame.append(0xFF)   
                escape = False 
                escaped = True
                #print 'escape 0xFF'
        
            elif escape:
                #print new frame
                if len(frame) > 0:
                    obj = self.generate_object(frame)
                    obj.escaped = escaped
                    escaped = False
                    self.data.append(obj)
                    
                frame = [byte]
                escape = False
                
            else:
                if byte == 0xff:
                    if len(frame) > 0:
                        self.data.append(self.generate_object(frame))
                    frame = []
                else:
                    #print hex(byte)
                    frame.append(byte)
                    
                    
                    
                    
                    
