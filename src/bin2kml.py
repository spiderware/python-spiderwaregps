#convert
import sgps.frames


def array2uint32(a):
    return a[0]*0x1000000 + a[1]*0x10000 + a[2]*0x100 + a[3] 
    
def array2uint16(a):
    return a[0]*0x100 + a[1]

bin = open('data.bin','r');

def generate_object(f):
    print f
    if f[0] == 0x01:
        return sgps.frames.Time(f[1:])
    elif f[0] == 0x02:
        return sgps.frames.Position(f[1:])
    elif f[0] == 0x03:
        return sgps.frames.System(f[1:])
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

kml = ''
for x in data:
    #print x.description()
    if x.frame_id == 0x02:
        kml += x.kml(150)
        kml += ' ' 



header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>test.kmz</name>
	<description><![CDATA[<h3></h3><b><i></i></b><br><p></p><br><p></p>]]></description>
	<Style id="line">
		<LineStyle>
			<color>7f0000ff</color>
			<width>4</width>
		</LineStyle>
	</Style>
	<Placemark>
		<styleUrl>#line</styleUrl>
		<LineString>
			<coordinates>
            """



footer = """
			</coordinates>
		</LineString>
	</Placemark>
	<Folder>
		<name>Geolives</name>
		<ScreenOverlay>
			<name>Geolives</name>
			<Icon>
				<href>http://www.geolives.ch/flash/logobig.gif</href>
			</Icon>
			<overlayXY x="0" y="-1" xunits="fraction" yunits="fraction"/>
			<screenXY x="0.01" y="0.02" xunits="fraction" yunits="fraction"/>
			<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>
			<size x="0" y="0" xunits="fraction" yunits="fraction"/>
		</ScreenOverlay>
	</Folder>
</Document>
</kml>
"""

print header,kml,footer
f = open('out.kml','w')
f.write(header+kml+footer)
f.close()
