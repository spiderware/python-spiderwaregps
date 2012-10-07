import datetime
import json


import gpxpy
import gpxpy.gpx

def array2uint32(a):
    return a[0]*0x1000000 + a[1]*0x10000 + a[2]*0x100 + a[3] 


def array2uint24(a):
    return a[0]*0x10000 + a[1]*0x100 + a[2] 


def array2uint16(a):
    return a[0]*0x100 + a[1]
    
    
def gpstime2datetime(weeks,tow):
    return datetime.datetime(1980,1,6) + datetime.timedelta(weeks=weeks,seconds=tow)


class SGPSObject(object):
    frame_id = 0x00
    def gps_data(self):
        return None


class Time(SGPSObject):
    frame_id = 0x01
    tow = 0
    week = 0

    def __init__(self, data, timestamp=None):
        data = data[1:]
        self.week = array2uint16(data[0:2])
        self.tow = array2uint24(data[2:5])
        self.timestamp = gpstime2datetime(self.week,self.tow)
        
        
    def __repr__(self):
        h = self.tow/60
        m = (self.tow-h*60)/3600
        s = self.tow-h*60-m*3600
        return '<%s %s>' % (self.__class__.__name__, self.timestamp)
        #return '<%s %d:%d:%d>' % (self.__class__.__name__, h,m,s)
        
    def json(self):
        d = {'type':self.__class__.__name__,
             'timestamp':self.timestamp.isoformat()
             }
        return json.dumps(d)

    def is_valid(self):
        return True

    def get_timestamp(self, offset=0):
        return self.timestamp + datetime.timedelta(seconds=offset)
        
class Position(SGPSObject):
    frame_id = 0x02

    def __init__(self, data,time):
        data = data[1:]
        self.time = time
        self.offset  = array2uint16(data[0:2])
        self.lat = array2uint32(data[2:6])
        self.lon = array2uint32(data[6:10])
        self.alt = array2uint16(data[10:12])
        self.h_error = data[12]
        self.v_error = data[13]
        self.flags =   data[14]
        if self.lat > 0x7fffffff:
            self.lat = -0x7fffffff+self.lat 
        if self.lon > 0x7fffffff:
            self.lon = -0x7fffffff+self.lon 
        if self.alt > 0x7fff:
            self.alt = -0x7fff+self.alt

    def timestamp(self):
        if self.time:
            return self.time.get_timestamp(self.offset)
        return None

    def __repr__(self):
        return '<%s %s %f / %f (+/- %dm) \t%dm (+/- %dm)>' % (
                    self.__class__.__name__,
                    self.timestamp(),
                    float(self.lat)/10000000,
                    float(self.lon)/10000000,
                    self.h_error,
                    self.alt,
                    self.v_error)

    def json(self):
        d = {'type':self.__class__.__name__,
             'lat':float(self.lat)/10000000,
             'lon':float(self.lon)/10000000,
             'alt':self.alt,
             'h_error':self.h_error,
             'v_error':self.v_error,
             'timestamp':''
             }
        if self.timestamp():
            d['timestamp'] = self.timestamp().isoformat()
        return json.dumps(d)

    def is_valid(self):
        if not self.lat or not self.lon or not self.alt:
            return False
        return True
    
    def gpx_element(self):
        return gpxpy.gpx.GPXTrackPoint(
                                       latitude=float(self.lat)/10000000, 
                                       longitude=float(self.lon)/10000000, 
                                       elevation=self.alt,
                                       time=self.timestamp(),
                                       horizontal_dilution=self.h_error,
                                       vertical_dilution=self.v_error)

    def kml(self, max_error=100000):
        if self.h_error < max_error and self.lat and self.lon:
            return '%f,%f,%d' % (float(self.lon)/10000000,float(self.lat)/10000000,self.alt)
        return ''

    def kml_gxcoord(self, max_error=100000):
        if self.h_error < max_error and self.lat and self.lon:
            coords = u'<gx:coord>%f %f %d</gx:coord>' % (float(self.lon)/10000000,float(self.lat)/10000000,self.alt)
            return coords
        return ''

    def kml_when(self, max_error=100000):
        if self.h_error < max_error and self.lat and self.lon:
            print self.timestamp
            return u'<when>%s</when>' % (self.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
            #return u'<when>2010-05-28T02:02:09Z</when>'
        return ''

    def gps_data(self):
        return {"timestamp":self.timestamp.get_timestamp(),"latitude":float(self.lat)/10000000,"longitude":float(self.lon)/10000000,"elevation":self.alt,"horizontal_error":self.h_error,"vertical_error":self.v_error}
    
        
class System(SGPSObject):
    frame_id = 0x03
    states = {
        0: 'error code %(rfu)s',
        1: 'startup',
        2: 'standby',
        3: 'wake up',
        4: 'break begins',
        5: 'break ends *',
        6: 'gps on *',
        7: 'gps off *',
        8: 'battery low (%(rfu)s%)',
        9: 'charging (%(rfu)s%)',
        10: 'charging ends',
        11: 'wall power on',
        12: 'wall power off',
        13: 'changed profile to %(rfu)s',
        14: 'waypoint %(rfu)s',
        15: 'accelerometer off',
        16: 'accelerometer on',
        17: 'new track begins',
    }
    def __init__(self, data,time):
        data = data[1:]
        self.time = time
        self.offset  = array2uint16(data[0:2])
        self.msg = data[2]
        self.rfu = data[3]

    def __repr__(self):
        str = self.states.get(self.msg, 'unknown state %(state_id)s, RFU=%(rfu)s')
        message = str % {'state_id': self.msg, 'rfu': self.rfu}
        return '<%s %s %s ACCU: %.01f%%>' % (
            self.__class__.__name__,
            self.timestamp(),
            message,
            float(self.rfu)/2)
    
    def json(self):
        str = self.states.get(self.msg, 'unknown state %(state_id)s, RFU=%(rfu)s')
        message = str % {'state_id': self.msg, 'rfu': self.rfu}
        d = {'type':self.__class__.__name__,
             'msg_id':self.msg,
             'rfu':self.rfu,
             'message':message,
             'timestamp':''
             }
        if self.timestamp():
            d['timestamp'] = self.timestamp().isoformat()
            
        return json.dumps(d)    
     
    def gpx_element(self,position):
        str = self.states.get(self.msg, 'unknown state %(state_id)s, RFU=%(rfu)s')
        message = str % {'state_id': self.msg, 'rfu': self.rfu}
        
        return gpxpy.gpx.GPXWaypoint(  latitude=float(position.lat)/10000000, 
                                       longitude=float(position.lon)/10000000, 
                                       elevation=position.alt,
                                       time=self.timestamp(),
                                       horizontal_dilution=position.h_error,
                                       vertical_dilution=position.v_error,
                                       name=message
                                       )
    def debug_level(self):
        if self.msg in [1, 2, 4, 5, 9, 10, 11, 12, 13, 15, 15, 16, 17]:
            return 1
        return 2
    
    def timestamp(self):
        if self.time:
            return self.time.get_timestamp(self.offset)
        return None

    def is_valid(self):
        return True

class Unknown(SGPSObject):
    frame_id = 0xff
    data = []
    rfu = 0

    def __init__(self, data, timestamp):
        self.timestamp = None
        self.frame_id = data[0]
        self.data = data

    def __repr__(self):
        s = '<Unknown %s %s (%s)>' % (
            self.frame_id,
            " ".join(["%x" % x for x in self.data]),
            self.timestamp,
        )
        return s
    
    def json(self):
        d = {'type':self.__class__.__name__,
             'data':self.data}
        return json.dumps(d) 

    def is_valid(self):
        return True

class FrameRegistry(dict):
    time = Time
    unknown = Unknown

    def register(self, FrameClass):
        self[FrameClass.frame_id] = FrameClass

registry = FrameRegistry()
registry.register(Position)
registry.register(System)
