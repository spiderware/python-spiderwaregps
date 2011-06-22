#convert
import sgps.frames


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
    elif f[0] == 0x02:
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
while data_in:
    byte = ord(bin.read(1))
    
    if byte == 0x7e and escape:
        frame.append(byte)
        escape = False
        print 'escape 0x7e'

    elif byte == 0x7e:
        # start escape
        escape = True
           
    elif byte == 0x7f and escape:
        # escape FF
        frame.append(0xFF)   
        escape = False 
        print 'escape 0xFF'

    elif escape:
        #print new frame
        if len(frame) > 0:
            data.append(generate_object(frame))
            
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



header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>test.kmz</name>
	<description><![CDATA[<h3></h3><b><i></i></b><br><p></p><br><p></p>]]></description>
	<Style id="track_n">
      <IconStyle>
        <scale>.5</scale>
        <Icon>
          <href>http://earth.google.com/images/kml-icons/track-directional/track-none.png</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <scale>0</scale>
      </LabelStyle>

    </Style>
    <!-- Highlighted track style -->
    <Style id="track_h">
      <IconStyle>
        <scale>1.2</scale>
        <Icon>
          <href>http://earth.google.com/images/kml-icons/track-directional/track-none.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <StyleMap id="track">
      <Pair>
        <key>normal</key>
        <styleUrl>#track_n</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#track_h</styleUrl>
      </Pair>
    </StyleMap>
    <!-- Normal multiTrack style -->
    <Style id="multiTrack_n">
      <IconStyle>
        <Icon>
          <href>http://earth.google.com/images/kml-icons/track-directional/track-0.png</href>
        </Icon>
      </IconStyle>
      <LineStyle>
        <color>99ffac59</color>
        <width>6</width>
      </LineStyle>

    </Style>
    <!-- Highlighted multiTrack style -->
    <Style id="multiTrack_h">
      <IconStyle>
        <scale>1.2</scale>
        <Icon>
          <href>http://earth.google.com/images/kml-icons/track-directional/track-0.png</href>
        </Icon>
      </IconStyle>
      <LineStyle>
        <color>99ffac59</color>
        <width>8</width>
      </LineStyle>
    </Style>
    <StyleMap id="multiTrack">
      <Pair>
        <key>normal</key>
        <styleUrl>#multiTrack_n</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#multiTrack_h</styleUrl>
      </Pair>
    </StyleMap>
    <!-- Normal waypoint style -->
    <Style id="waypoint_n">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pal4/icon61.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <!-- Highlighted waypoint style -->
    <Style id="waypoint_h">
      <IconStyle>
        <scale>1.2</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pal4/icon61.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <StyleMap id="waypoint">
      <Pair>
        <key>normal</key>
        <styleUrl>#waypoint_n</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#waypoint_h</styleUrl>
      </Pair>
    </StyleMap>
    <Style id="lineStyle">
      <LineStyle>
        <color>99ffac59</color>
        <width>6</width>
      </LineStyle>
    </Style>
    <Schema id="schema">
      <gx:SimpleArrayField name="heartrate" type="int">
        <displayName>Heart Rate</displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="cadence" type="int">
        <displayName>Cadence</displayName>
      </gx:SimpleArrayField>
      <gx:SimpleArrayField name="power" type="float">
        <displayName>Power</displayName>
      </gx:SimpleArrayField>
    </Schema>
"""



footer = """
</Document>
</kml>
"""

track_template = """
<Placemark>
    <name>%(name)s</name>
	<styleUrl>#multiTrack</styleUrl>
	<gx:Track>
	    %(when)s
	    %(coord)s
    </gx:Track>
</Placemark>
"""


tracks = [[]]

kml = ''
for x in data:
    #print x.description()
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
        if not len(track):
            continue
        kml_when = ''
        kml_coord = ''
        for pos in track:
            kml_when += pos.kml_when(150)+' '
        for pos in track:
            kml_coord += pos.kml_gxcoord(150)+' '
        kml += (track_template % {
                        'name': u'Trip starting at %s' % track[0].timestamp,
                        'when': kml_when,
                        'coord': kml_coord,})

print tracks
f = open('out.kml','w')
f.write(header+kml+footer)
f.close()
