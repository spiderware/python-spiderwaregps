import datetime


system_flags = ['error, RFU=error code',
'start up',
'stand by',
'wake up',
'break begins',
'break ends *',
'gps on *',
'gps off *',
'battery low , RFU=percent',
'charging begins, RFU=percent',
'charging ends',
'wall power on',
'wall power off',
'changed profile, RFU=id',
'waypoint, RFU=id',
'accelerometer off',
'accelerometer on',
'new track begins','18','19','20','21','22','23','','','','','','','','',]


def array2uint32(a):
    return a[0]*0x1000000 + a[1]*0x10000 + a[2]*0x100 + a[3] 
  
def array2uint24(a):
    return a[0]*0x10000 + a[1]*0x100 + a[2] 
    
def array2uint16(a):
    #print a
    return a[0]*0x100 + a[1]
    
    
def gpstime2datetime(weeks,tow):
    return datetime.datetime(1980,1,6) + datetime.timedelta(weeks=weeks,seconds=tow)


class SGPSObject(object):
    timestamp = 0
    escaped = False
    pass

class Time(SGPSObject):
    frame_id = 0x01
    tow = 0
    week = 0
    
    
    def __init__(self, data):
        self.week = array2uint16(data[0:2])
        self.tow = array2uint24(data[2:5])
        #print self.week,self.tow
        #print datetime.timedelta(weeks=self.weeks)
        self.timestamp = gpstime2datetime(self.week,self.tow)
        
    def description(self):
        h = self.tow/60
        m = (self.tow-h*60)/3600
        s = self.tow-h*60-m*3600
        return '<Time %d:%d:%d>'%(h,m,s)
        
    def get_timestamp(self,offset=0):
        return self.timestamp + datetime.timedelta(seconds=offset)
        
class Position(SGPSObject):
    frame_id = 0x02
    offset = 0
    lat = 0.0
    lon = 0.0
    alt = 0
    v_error = 0
    h_error = 0
    flags = 0
    data = []
    
    def __init__(self, data, time):
        self.data = data
        self.offset  = array2uint16(data[0:2])   
        self.timestamp = time.get_timestamp(self.offset)
        self.lat = array2uint32(data[2:6])   
        self.lon = array2uint32(data[6:10]) 
        self.alt = array2uint16(data[10:12])    
        self.h_error = data[12]   
        #print h_error 
        self.v_error = data[13]
        self.flags =   data[14]
        #print h
        


        #ERRRRRRRORRRRRRRRRRR
        
        if(self.lat & 0x80000000):
            self.lat = -0x100000000 + self.lat
        if(self.lon & 0x80000000):
            self.lon = -0x100000000 + self.lon
        if(self.alt & 0x8000):
            self.alt = -0x10000 + self.alt
    
    
    def description(self):
        s = '<Position '+str(len(self.data))+'\t'+str(self.escaped)+'\t'
        for x in self.data:
            s += ' %.2x' % x
        return s+' %f / %f (+/- %dm) \t%dm (+/- %dm) escaped: %s>'%(float(self.lat)/10000000,float(self.lon)/10000000,self.h_error,self.alt,self.v_error,str(self.escaped))
    
    def kml(self, max_error=100000):
        if self.h_error < max_error and self.lat and self.lon:
            return '%f,%f,%d' % (float(self.lon)/10000000,float(self.lat)/10000000,self.alt)
        return ''
        
class System(SGPSObject):
    frame_id = 0x03
    msg = 0
    rfu = 0
    offset = 0
    
    def __init__(self, data, time_frame=0):
        self.offset  = array2uint16(data[0:2])   
        self.timestamp = time_frame.get_timestamp(self.offset)
        self.msg = data[2]   
        self.rfu = data[3]
        
    def description(self):
        #print self.msg
        return '<System %s, %d, escaped: %s>'%(system_flags[self.msg],self.rfu,str(self.escaped))
    
    
    
    
    
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




    
