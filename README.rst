####################################
spiderware gps tracker binary format
####################################

python-spiderwaregps is a library to decode and convert the custom binary tracking format of the spiderware gps tracker.

gps states
==========

::

    0 error, RFU=error code
    1 start up
    2 stand by
    3 wake up
    4 break begins
    5 break ends
    6 gps on
    7 gps off
    8 battery low , RFU=percent
    9 charging begins, RFU=percent
    10 charging ends
    11 wall power on
    12 wall power off
    13 changed profile, RFU=id
    14 waypoint, RFU=id
    15 accelerometer off
    16 accelerometer on

data format
===========


::

    escape: 0x7E 
    
    frame format:
    0x7E [data] [next frame or 0xFF]
    
    escaped values
    0x7E -> 0x7E7E
    0xFF -> 0x7E7F
    
    info frame
    Type:       1 Byte (0x00)
    HW:       2 Byte | hardware version
    FW:       2 Byte | software version
    Batt:       2 Byte | battery state
    ??? more ???
    
    time frame
    Type:       1 Byte (0x01)
    Time:       5 Byte | 2 Byte week, 3 Byte second
            -------
            6 Byte
    
    location
    Type:       1 Byte (0x02)
    Time:       2 Byte | offest to time frame in s (max 18h)
    lon,lat:     8 Byte | result=value/10'000'000
    h_acc.     1 Byte | (*1)
    alt, acc:   3 Byte
    flas:       1 Byte
            -------
            16 Byte
    
    state frame
    Type:       1 Byte (0x03)
    Time:       2 Byte | offest to time frame in s max 18h
    State:      1 Byte | new state
    RFU:       1 Byte | depens on on new state
            -------
            5 Byte
    
    
    *1)  result = value & 0x7F
         if value > 0x7F:
             result = result * 8
         # 0..128, 0..1024 