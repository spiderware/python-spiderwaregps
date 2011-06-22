#-*- coding: utf-8 -*-
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX

styles_xml = '''
<base>
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
<Style id="waypoint_n">
  <IconStyle>
    <Icon>
      <href>http://maps.google.com/mapfiles/kml/pal4/icon61.png</href>
    </Icon>
  </IconStyle>
</Style>
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
</base>'''

class TracksDocument(object):
    def __init__(self, tracks):
        self.tracks = tracks
    def build_xml(self):
        kml = KML.kml()
        doc = KML.Document(KML.name("Spiderware GPS Tracks"))
        styles = etree.fromstring(styles_xml)
        for style in styles:
            doc.append(style)
        for track in self.tracks:
            if track.has_positions:
                doc.append(KML.Placemark(
                    KML.name("Track %s" % track.starts_at()),
                    KML.styleUrl('#multiTrack'),
                    Track(track).build_xml(),
                    )
                )
        kml.append(doc)
        return kml

    def render_xml(self):
        doc = self.build_xml()
        return etree.tostring(doc, pretty_print=True)
    

class Track(object):
    def __init__(self, track):
        self.track = track

    def build_xml(self):
        track = GX.Track(
        )
        for position in self.track.positions:
            track.append(KML.when("%s" % (
                    position.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),)
            ))
        for position in self.track.positions:
            track.append(GX.coord("%f %f %d" % (
                                float(position.lon)/10000000,
                                float(position.lat)/10000000,
                                position.alt))
            )
        return track
