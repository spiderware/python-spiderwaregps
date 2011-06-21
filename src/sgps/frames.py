import datetime

def array2uint32(a):
    return a[0]*0x1000000 + a[1]*0x10000 + a[2]*0x100 + a[3] 


def array2uint24(a):
    return a[0]*0x10000 + a[1]*0x100 + a[2] 


def array2uint16(a):
    return a[0]*0x100 + a[1]
    
    
def gpstime2datetime(weeks,tow):
    return datetime.datetime(1980,1,6) + datetime.timedelta(weeks=weeks,seconds=tow)


class SGPSObject(object):
    pass

class Time(SGPSObject):
    frame_id = 0x01
    tow = 0
    week = 0
    
    
    def __init__(self, data):
        self.week = array2uint16(data[0:2])
        self.tow = array2uint24(data[2:5])
        self.timestamp = gpstime2datetime(self.week,self.tow)
        
    def __repr__(self):
        h = self.tow/60
        m = (self.tow-h*60)/3600
        s = self.tow-h*60-m*3600
        return '<%s %d:%d:%d>' % (self.__class__.__name__, h,m,s)
        
    def get_timestamp(self, offset=0):
        return self.timestamp + datetime.timedelta(seconds=offset)
        
class Position(SGPSObject):
    frame_id = 0x02

    def __init__(self, data):
        self.timestamp = None
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

    def __repr__(self):
        return '<%s %f / %f (+/- %dm) \t%dm (+/- %dm)>' % (
                    self.__class__.__name__,
                    float(self.lat)/10000000,
                    float(self.lon)/10000000,
                    self.h_error,
                    self.alt,
                    self.v_error)

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
        
class System(SGPSObject):
    frame_id = 0x03

    def __init__(self, data):
        self.timestamp = None
        self.offset  = array2uint16(data[0:2])   
        self.msg = data[2]
        self.rfu = data[3]

    def __repr__(self):
        return '<%s %d, %d (%s)>' % (
            self.__class__.__name__,
            self.msg, self.rfu,
            self.timestamp)


class Unknown(SGPSObject):
#    frame_id = 0xff
    data = []
    rfu = 0

    def __init__(self, frame_id, data):
        self.timestamp = None
        self.frame_id = frame_id
        self.data = data

    def __repr__(self):
        s = '<Unknown %s %s (%s)>' % (
            self.frame_id,
            " ".join(["%x" % x for x in self.data]),
            self.timestamp,
        )
        return s

class FrameRegistry(dict):
    time = Time
    unknown = Unknown

    def register(self, FrameClass):
        self[FrameClass.frame_id] = FrameClass

registry = FrameRegistry()
registry.register(Position)
registry.register(System)