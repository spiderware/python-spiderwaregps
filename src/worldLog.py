import sys, argparse
import gpxpy
import gpxpy.gpx

import sgps.decoder
import sgps.frames
import sgps.device


def binary_string(data,size):
    ret = ''
    for i in xrange(size):
        if data&1:
            ret+='1'
        else:
            ret += '0'
        data = data >> 1
    return ret[::-1]

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='worldLog')
    parser.add_argument('cmd', metavar='cmd', choices=['erase', 'convert' ,'info'],help='the command')
    parser.add_argument('-i', type=argparse.FileType('rb'), help='input file. If not given, the device will be used.')
    parser.add_argument('-o', help='output file')
    
    args = parser.parse_args()
    
    
    raw_data = []
    
    if args.cmd == 'convert':
        # reading data
        if args.i:
            for byte in args.i.read():
                raw_data.append(ord(byte))
        else:
            print 'reading device...'
            d = sgps.device.WorldLogUSB()
            d.find()
            try:
                d.open_device()
            except IndexError:
                print 'Device not found'
                exit(1)
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
                raw_data += d.get_memory(current,100)
                current += 100
                current_pc = current / pc
                #print current_pc, printed_pc
                if current_pc > printed_pc:
                    for i in xrange(current_pc-printed_pc):
                        sys.stdout.write('#')
                        sys.stdout.flush()
                    printed_pc = current_pc
            print '|'
        # decoding
        decoder = sgps.decoder.Decoder()
        decoder.decode(raw_data)
            
        # output
        if not args.o:
                # print data on terminal
                print 'converting to terminal output'
                #print raw_data
                for item in decoder.data:
                    if item.__class__.__name__ == 'System':
                        if item.debug_level() <= 0:
                            print item
                    else:
                        print item
                pass
            
        ##################################################    
        # JSON generation
        elif args.o[-5:] == '.json':
            print 'converting to JSON'
            file = open(sys.argv[3],'w')
            for item in decoder.data:
                file.write(item.json())
            file.close()
            print 'JSON file: "%s" created'%sys.argv[3]
    
        ##################################################    
        # BIN generation
        elif args.o[-4:] == '.bin':
            # write file to disk (BIN format)
            print 'saving as BIN'
            fh = open(args.o,'wb')
            for x in raw_data:
                fh.write(chr(x))
            fh.close()
            print 'BIN file: "%s" created'%args.o
            
        ##################################################    
        # GPX generation
        elif args.o[-4:] == '.gpx':
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
            filter = ['Position','TrackStart']
            for frame in decoder.objects(filter):
                if frame.__class__.__name__ == "Position":
                    gpx_segment.points.append(frame.gpx_element())
                if frame.__class__.__name__ == "TrackStart":
                    gpx_track = gpxpy.gpx.GPXTrack()
                    gpx.tracks.append(gpx_track)
                    gpx_segment = gpxpy.gpx.GPXTrackSegment()
                    gpx_track.segments.append(gpx_segment)
            
    
            
            
            # now the pois
            filter = ['POI']
            for frame in decoder.objects(filter):
                if frame.__class__.__name__ in filter:
                    gpx.waypoints.append(frame.gpx_element())
                
            with open(args.o, 'w') as f:
                read_data = f.write(gpx.to_xml())
                f.closed
                
            print 'GPX file "%s" created'%sys.argv[3]
        else:
            print "unknown output format:",  sys.argv[3]
            exit(1) 
                
    elif args.cmd == 'erase':
        d.erase_memory()
        print 'erasing memory...'
        print 'MEM  : %.02f'%(float(d.get_memory_state())/1024),'kByte'
    
    elif args.cmd == 'info':
        print 'reading info from USB device'
        d = sgps.device.WorldLogUSB()
        d.find()
        try:
            d.open_device()
        except IndexError:
            print 'Device not found'
            exit(1)
            
        mem = d.get_memory_state()
    
        print 'MEM  : %.02f'%(float(mem)/1024),'kByte'
        print 'FLAGS:',binary_string(d.get_device_state(),32)
        print_flags(d.get_device_state())
        vbat, charge = d.get_battery_status()
        print 'BATTERY: %.02fV, %.02f%%'%(vbat, charge)
        d.get_unique_id()
        d.get_device_info()