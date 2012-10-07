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

import sgps.frames
import datetime

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
                    
                    
                    
                    
                    
