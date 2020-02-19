#!/usr/bin/python3

import logging
from networktables import NetworkTables
from . import Robot, config

conf = config.get_config()

logging.basicConfig(level=logging.DEBUG)


class NetworkTableBot(Robot):

    def __init__(self, *args, **kwargs):
        NetworkTables.initialize(server=kwargs.get(
            "server",
            conf["ROBOT"]["IP_ADDRESS"]
            ))
        self.nt = NetworkTables.getTable("RoboRadar")

    @property
    def x(self):
        return self.nt.getNumber("posX", 0)

    @property
    def y(self):
        return self.nt.getNumber("posY", 0)

    @property
    def r(self):
        return self.nt.getNumber("posR", 0)

    '''@property
    def rsin(self):
        return self.nt.getNumber("posRSin", 1)

    @property
    def rcos(self):
        return self.nt.getNumber("posRCos", 0)

    @property
    def rtan(self):
        return self.nt.getNumber("posRTan", 0)'''

    def getTeamColor(self):
        # return purple if no color defined
        return tuple(self.nt.getNumberArray("color", (255, 0, 255)))


class BoxBot(NetworkTableBot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def w(self):
        return self.nt.getNumber("boxbotW", 27)

    @property
    def h(self):
        return self.nt.getNumber("boxbotH", 32)

    @classmethod
    def getInfo(cls):
        data = {
            "name": "BoxBot",
            "units": "inches",
            }
        return data

    def getShapes(self):
        w = self.w / 2
        h = self.h / 2
        shapes = [
            {
                 "name": "bumpers",
                 "type": "polygon",
                 "style": ("filled", "aa"),
                 "color": self.getTeamColor(),
                 "layer": 0,
                 "coordinate-space": "local",
                 "points": [
                     (-(w+3.25), (h+3.25)),
                     ((w+3.25), (h+3.25)),
                     ((w+3.25), -(h+3.25)),
                     (-(w+3.25), -(h+3.25))
                     ]
                 },
            {
                "name": "frame",
                "type": "polygon",
                "style": ("filled", "aa"),
                "color": (128, 128, 128),
                "layer": 0,
                "coordinate-space": "local",
                "points": [
                    (-w, h),
                    (w, h),
                    (w, -h),
                    (-w, -h)
                    ]
                },
            {
                "name": "pointer",
                "type": "line",
                "style": ("outline"),
                "color": (0, 0, 0),
                "layer": 0,
                "coordinate-space": "local",
                "points": [
                    (0, 0),
                    (0, h),
                    ]
                },
            {
                "name": "arrow",
                "type": "line",
                "style": ("outline"),
                "color": (0, 255, 0),
                "layer": 0,
                "coordinate-space": "local",
                "points": [
                    (0, 0),
                    (0, (h+8)),
                    ]
                }
            ]
        return shapes


# print(BoxBot())


types = {
    "BoxBot": BoxBot
    }
