#convert
import sgps.frames
import sgps.data
import datetime


break_to_new_track_time = 3600 #1h


current_time = None

def array2uint32(a):
    return a[0]*0x1000000 + a[1]*0x10000 + a[2]*0x100 + a[3] 
    
def array2uint16(a):
    return a[0]*0x100 + a[1]

bin = open('data.bin','r');

def generate_object(f):
    #print f
    global current_time
    if f[0] == 0x01:
        current_time = sgps.frames.Time(f[1:])
        return current_time
    elif f[0] == 0x02 and len(f[1:]) == 15:
        return sgps.frames.Position(f[1:],current_time)
    elif f[0] == 0x03:
        return sgps.frames.System(f[1:],current_time)
    else:
        return sgps.frames.Unknown(f)


byte = 0
escape = 0
data_in = 1
data=[]
frame = []
escaped = False
while data_in:
    byte = ord(bin.read(1))
    
    if byte == 0x7e and escape:
        frame.append(byte)
        escape = False
        escaped = True
        print 'escape 0x7e'

    elif byte == 0x7e:
        # start escape
        escape = True
           
    elif byte == 0x7f and escape:
        # escape FF
        frame.append(0xFF)   
        escape = False 
        escaped = True
        print 'escape 0xFF'

    elif escape:
        #print new frame
        if len(frame) > 0:
            obj = generate_object(frame)
            obj.escaped = escaped
            escaped = False
            data.append(obj)
            
        frame = [byte]
        escape = False
        
    else:
        if byte == 0xff:
            data_in = False
            data.append(generate_object(frame))
        else:
            #print hex(byte)
            frame.append(byte)
    
bin.close()


def kml_break(time):
    return ''


header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
    <name>Tracks.kml</name>
    <Style id="sn_coffee">
        <IconStyle>
            <scale>0.5</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/shapes/coffee.png</href>
            </Icon>
            <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
        </IconStyle>
        <LabelStyle>
            <scale>0.5</scale>
        </LabelStyle>
        <ListStyle>
        </ListStyle>
    </Style>
    <StyleMap id="msn_ylw-pushpin">
        <Pair>
            <key>normal</key>
            <styleUrl>#sn_ylw-pushpin0</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#sh_ylw-pushpin</styleUrl>
        </Pair>
    </StyleMap>
    <StyleMap id="msn_ylw-pushpin0">
        <Pair>
            <key>normal</key>
            <styleUrl>#sn_ylw-pushpin</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#sh_ylw-pushpin0</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="sn_ylw-pushpin">
        <IconStyle>
            <scale>0.5</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
            </Icon>
            <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
        </IconStyle>
        <LabelStyle>
            <scale>0.5</scale>
        </LabelStyle>
    </Style>
    <Style id="sh_ylw-pushpin">
        <IconStyle>
            <scale>1.3</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
            </Icon>
            <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
        </IconStyle>
    </Style>
    <StyleMap id="msn_coffee">
        <Pair>
            <key>normal</key>
            <styleUrl>#sn_coffee</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#sh_coffee</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="sh_coffee">
        <IconStyle>
            <scale>0.583333</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/shapes/coffee.png</href>
            </Icon>
            <hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
        </IconStyle>
        <LabelStyle>
            <scale>0.5</scale>
        </LabelStyle>
        <ListStyle>
        </ListStyle>
    </Style>
    <Style id="sh_ylw-pushpin0">
        <IconStyle>
            <scale>0.590909</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
            </Icon>
            <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
        </IconStyle>
        <LabelStyle>
            <scale>0.5</scale>
        </LabelStyle>
    </Style>
    <Style id="sn_ylw-pushpin0">
        <IconStyle>
            <scale>1.1</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>
            </Icon>
            <hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>
        </IconStyle>
    </Style>
    <Style id="track_red">
        <LineStyle>
            <color>ff0000ff</color>
            <width>2</width>
        </LineStyle>
    </Style>
    <Style id="track_blue">
        <LineStyle>
            <color>ffff00ff</color>
            <width>2</width>
        </LineStyle>
    </Style>
    <Style id="track_green">
        <LineStyle>
            <color>ff00ffff</color>
            <width>2</width>
        </LineStyle>
    </Style>
    <Folder>
        <name>Tracks</name>
        <open>0</open>
            """



footer = """
</Folder>
</Document>
</kml>
"""



#compile frames to data
compiled = []

styles = ['track_red','track_green','track_blue']

current_track = None
current_point = None
current_break = None
break_track = False

for x in data:
    if break_track:
        del current_track
        current_track = None
        break_track = False
    if x.frame_id == 0x03:
        if x.msg == 0x04:
            #break
            if not current_break:
                current_break = sgps.data.Break(current_point)
                current_break.timestamp = x.timestamp
        if x.msg == 14 and current_track:
            # add waypoint
            waypoint = sgps.data.Waypoint(current_point)
            waypoint.timestamp = x.timestamp
            current_track.waypoints.append(waypoint)
            #print waypoint.description()
        if x.msg == 0x11:   # new track
            del current_track
            current_track = None
            
    if x.frame_id == 0x02:
        #point
        
        #detect errors
        if x.lat == 0 or x.lon == 0:
            print 'ERROR 0', x.description()
        elif x.h_error <= 1:
            print 'ERROR 1a', x.description()
        elif x.h_error > 1000:
            print 'ERROR 1b', x.description()
        elif x.alt == 0:
            print 'ERROR 2', x.description()
        else:
            print x.timestamp,'\t',x.description()
            #print 'OK', x.description()
            current_point = sgps.data.Location(x.lon,x.lat,x.alt,x.h_error,x.v_error)
            current_point.timestamp = x.timestamp
            if not current_track:
                current_track = sgps.data.Track()
                compiled.append(current_track)
                
                #print "new track", 
            # make break ends
            if current_break:
                current_break.end = current_point.timestamp
                
                if current_break.time().seconds > 60*60*5:    
                    break_track = True
                elif current_break.time().seconds > 60*3:
                    # only show breaks bigger 3 min
                    current_track.breaks.append(current_break)
                #print current_break.description()
                current_break = None
            
                
            current_track.points.append(current_point)
            
kml = ''
i = 0

print compiled

for track in compiled:
    i+=1
    kml += """
    <Folder>
            <name>Track %d</name>
            <open>0</open>
            <Placemark>
                <name>Track %d</name>
                <styleUrl>%s</styleUrl>
                <LineString>
                    <tessellate>1</tessellate>
                    <coordinates>"""%(i,i,styles[i%3])
    
    for point in track.points:
        #print '\t',point.description()
        kml += point.kml(30)+' '
    
    kml += """        </coordinates>
                </LineString>
            </Placemark>
            <Folder>
                <name>Breaks</name>
                <open>1</open>"""
    
        
    for b in track.breaks:
        #print '\t',b.description()
        kml += b.kml()
        
        
    kml += """</Folder>"""
    
    # waypoints here!!!!
    
    kml += """</Folder>"""
    

f = open('out2.kml','w')
f.write(header+kml+footer)
f.close()

exit(0)





tracks = [[]]


kml = ''
for x in data:
    if 1:# x.frame_id == 0xff or x.frame_id == 0x02:
        print x.timestamp, x.description()
    if x.frame_id == 0x03:  # system
        if x.msg == 0x11:   # new track
            #kml += new_track
            tracks.append([])
    if x.frame_id == 0x02:
        tracks[-1].append(x)
        #kml += x.kml(150)
        #kml += ' ' 

for track in tracks:
    #print track
    if track: 
        kml += new_track
        for pos in track:
            kml += pos.kml()+' '

#print tracks
f = open('out.kml','w')
f.write(header+kml+footer)
f.close()
