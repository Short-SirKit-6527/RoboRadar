import time
import math
from networktables import NetworkTables

import logging

logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize()
nt = NetworkTables.getTable("RoboRadar")

i = 0
while True:
    nt.putNumber("posX", 60*math.cos(i))
    nt.putNumber("posY", 60*math.sin(i))

    nt.putNumber("posR", i)
    nt.putNumber("posRSin", math.sin(i))
    nt.putNumber("posRCos", math.cos(i))
    nt.putNumber("posRTan", math.tan(i))
    time.sleep(0.01)
    i += 0.01
