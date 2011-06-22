from .parser import parse
from .frames import registry, Position, System, Unknown, Time

def generate_frame_object(frame, frame_types=None):
    frame_types = frame_types or registry
    if frame[0] == frame_types.time.frame_id:
        return frame_types.time(data=frame[1:])
    FrameType = frame_types.get(frame[0], None)
    if FrameType:
        return FrameType(data=frame[1:])
    return frame_types.unknown(frame_id=frame[0], data=frame[1:])

class FrameIteratorMixin(object):
    def filtered_frames(self, types):
        for item in self.frames:
            if item.__class__ in types:
                yield item
    @property
    def positions(self):
        return self.filtered_frames([Position])

    @property
    def system_messages(self):
        return self.filtered_frames([System])

    @property
    def times(self):
        return self.filtered_frames([Time])

    @property
    def unknown_frames(self):
        return self.filtered_frames([Unknown])

class Track(FrameIteratorMixin):
    """
    a single Track composed of multiple Positions and System messages
    """
    def __init__(self):
        self.frames = []

    def starts_at(self):
        for frame in self.times:
            return frame.timestamp
        return None

    @property
    def has_positions(self):
        for pos in self.positions:
            return True
        return False

class GPSFile(FrameIteratorMixin):
    def __init__(self, raw_frames, frame_types=None):
        self.frame_types = frame_types or registry
        current_time_entry = None
        current_track = Track()
        self.tracks = [current_track]
        for raw_frame in raw_frames:
            obj = generate_frame_object(
                        frame=raw_frame,
                        frame_types=self.frame_types)
            if isinstance(obj, self.frame_types.time):
                current_time_entry = obj
            elif isinstance(obj, System) and obj.msg == 11:
                # start a new track
                current_track = Track()
                self.tracks.append(current_track)
            else:
                if current_time_entry:
                    obj.timestamp = current_time_entry.timestamp
            if obj.is_valid():
                current_track.frames.append(obj)

    @property
    def frames(self):
        """
        shortcut iterator that iterates over all frames in all tracks
        """
        for track in self.tracks:
            for frame in track.frames:
                yield frame

    @classmethod
    def from_file(cls, file):
        raw_frames = parse(file)
        return cls(raw_frames=raw_frames)

    @classmethod
    def from_filename(cls, filename):
        return cls.from_file(open(filename, 'r'))




