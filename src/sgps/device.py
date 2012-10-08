import usb.core
import usb.util

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