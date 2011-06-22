#-*- coding: utf-8 -*-
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import GX_ElementMaker as GX

class TracksDocument(object):
    def __init__(self, tracks):
        self.tracks = tracks
    def build_xml(self):
        kml = KML.kml()
        doc = KML.Document(KML.name("Spiderware GPS Tracks"))
        for track in self.tracks:
            if track.has_positions:
                doc.append(KML.Placemark(KML.name("Track %s" % track.starts_at()),
                                        Track(track).build_xml()))
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
