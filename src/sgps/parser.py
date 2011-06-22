def parse(file):
    """
    file is a file like object containing the binary data
    """
    escape = 0
    data_finished = False
    frame = []
    raw_frames = []
    
    while not data_finished:
        byte = ord(file.read(1))

        if byte == 0x7e and escape:
            frame.append(byte)
            escape = False
        elif byte == 0x7e:
            # start escape
            escape = True
        elif byte == 0x7f and escape:
            # escape FF
            frame.append(0xFF)
            escape = False
        elif escape:
            if len(frame) > 0:
                raw_frames.append(frame)
            frame = [byte]
            escape = False
        else:
            if byte == 0xff:
                data_finished = True
                raw_frames.append(frame)
            else:
                frame.append(byte)
    return raw_frames
