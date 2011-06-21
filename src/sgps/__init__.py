from .parser import parse
from .frames import registry

def generate_frame_object(frame, frame_types=None):
    frame_types = frame_types or registry
    if frame[0] == frame_types.time.frame_id:
        return frame_types.time(data=frame[1:])
    FrameType = frame_types.get(frame[0], None)
    if FrameType:
        return FrameType(data=frame[1:])
    return frame_types.unknown(frame_id=frame[0], data=frame[1:])

class SpiderwareGPS(object):
    def __init__(self, raw_frames, frame_types=None):
        self.frame_types = frame_types or registry
        self.frames = []
        self.latest_time_entry = None
        current_time = None
        for raw_frame in raw_frames:
            obj = generate_frame_object(
                        frame=raw_frame,
                        frame_types=self.frame_types)
            if isinstance(obj, self.frame_types.time):
                self.latest_time_entry = obj
            else:
                obj.timestamp = self.latest_time_entry.timestamp
                self.frames.append(obj)

    @classmethod
    def from_file(cls, file):
        raw_frames = parse(file)
        return cls(raw_frames=raw_frames)

    @classmethod
    def from_filename(cls, filename):
        return cls.from_file(open(filename, 'r'))




