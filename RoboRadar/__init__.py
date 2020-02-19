#!/usr/bin/python3

__all__ = ['VideoEngines', 'Radar', ]
__version__ = '0.1.0'
__author__ = 'David Johnston'

import os
import sys
from enum import Enum
import ctypes

try:
    from RoboRadar import config
    from RoboRadar.fields import fields, fieldFiles, fieldNames, fieldThemes
    import RoboRadar.robots as robots
except ImportError:
    import config
    from fields import fields, fieldFiles, fieldNames, fieldThemes
    import robots

config.load_config()
conf = config.get_config()

robotList = robots.getRobots()

# Force program to run as a package/module. Recommended for compatibility.
# This is designed to run as a module, but this can cause issues when
# developing in IDLE. Non-module mode is of low priority, and may not work AT
# ALL!!!
# Default: True
# FORCE_RUN_AS_MODULE = True

if (conf["SYSTEM"]["FORCE_RUN_AS_MODULE"]) and __package__ is None:
    print("""Not running as module, restarting. Please run using 'py -m
RoboRadar.__init__'""")
    existingcwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__))[:-10])
    os.system("py -m RoboRadar.__init__")
    os.chdir(existingcwd)
    exit()


'''
============================

- DEFINITIONS -

============================

These are standard definitions for the program to use.
Do not mess with these unless you know what you are doing!
'''


class VideoEngines(Enum):
    native = "native"
    numpy = "numpy"
    pygame = "pygame"


VERSION = "1.0.0"

'''
============================

- CONFIG -

============================

Default configuration stored alongside the program.
These are the settings that will be loaded into an .ini file the
first time RoboRadar is run.
'''

# Number of FPS to run the screen at. Recommended 30, 60, or the refresh rate
# of the monitor
# Default: 60
# FPS = 60

# Team number of FRC Team
# Default: 0
# TEAM_NUMBER = 0

# NetworkTables server address, leave this unchanged to use the team number.
# Each {}{} will be filled with part of the team number
# Default: "10.{}.{}.2"
# SERVER_ADDRESS = "10.{}.{}.2"

# Set the starting screen width and height
# Default: 480, 640
# INITIAL_SCREEN_WIDTH, INITIAL_SCREEN_HEIGHT = 480, 640

# Enable/disable antialiased polygons and lines
# Default: True
# ANTIALIASING = True

# Enable/disable filled polygons (gives everything a wireframe look. NOT
# recommended)
# Default: True
# FILLED_POLYGONS = True

# Set video engine for graphics
# Default: pygame
# VIDEO_ENGINE = VideoEngines.pygame

# Set starting field
# Default: "FRC_2020"
# DEFAULT_FIELD = "FRC_2020"

# Dont mess with this. It WILL cause syncing issues
'''CONFIG = {
    "FPS": FPS,
    "TEAM_NUMBER": TEAM_NUMBER,
    "SERVER_ADDRESS": SERVER_ADDRESS,
    "INITIAL_SCREEN_WIDTH": INITIAL_SCREEN_WIDTH,
    "INITIAL_SCREEN_HEIGHT": INITIAL_SCREEN_HEIGHT,
    "ANTIALIASING": ANTIALIASING,
    "FILLED_POLYGONS": FILLED_POLYGONS,
    "VIDEO_ENGINE": VIDEO_ENGINE,
    "DEFAULT_FIELD": DEFAULT_FIELD
    }
'''

if VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.pygame:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
    import pygame.gfxdraw
    import pygame.locals
else:
    raise ValueError

_pgFlag = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF


def start_independent(flags=_pgFlag):
    '''Start an independent RoboRadar WindowsError
flags: flags for pygame.display.set_mode'''
    appid = 'ShortSirkit.RoboRadar.RoboRadar.1_0_0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    pygame.init()

    screen = pygame.display.set_mode(
        conf["VIDEO"]["SCREEN_DIMENSIONS"],
        pygame.RESIZABLE | flags)
    pygame.display.set_caption("RoboRadar v{} - Team {}".format(
        VERSION,
        conf["TEAM"]["NUMBER"])
        )
    pygame.display.set_icon(pygame.image.load(__file__[:-11] + "icon.png"))

    clock = pygame.time.Clock()

    r = Radar(conf["VIDEO"]["SCREEN_DIMENSIONS"])
    r.loadField(conf["FIELD"]["NAME"])
    bb = robotList["BoxBot"]()
    r.add_ds(bb)

    while True:
        screen.fill((249, 249, 249))

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.locals.VIDEORESIZE:
                r.resize(event.size)
                screen = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.RESIZABLE
                    )

        # Update.

        screen.blit(r.pygame_render(), (0, 0))

        # Draw.
        pygame.display.flip()
        clock.tick(conf["VIDEO"]["FPS"])


class Radar:
    _dsArray = []

    def __init__(
                 self, dimensions,
                 interface=conf["VIDEO"]["ENGINE"],
                 *args, **kwargs):
        self.dimensions = dimensions
        self.fieldIndex = None
        self.field = None
        if VideoEngines[interface] is VideoEngines.pygame:
            self._init_pygame(*args, **kwargs)

    def loadField(self, search, *args, **kwargs):
        if isinstance(search, int) and 0 <= int(search) < len(fields):
            self.fieldIndex = search
        else:
            self.fieldIndex = fieldFiles.get(search, None)
        if self.fieldIndex is None:
            self.fieldIndex = fieldNames.get(search, None)
        if self.fieldIndex is None:
            self.fieldIndex = fieldThemes.get(search, None)
        if self.fieldIndex is None:
            raise ValueError
        self.field = fields[self.fieldIndex]
        self._loadField_engineSpecific()

    def resize(self, dimensions):
        self.dimensions = dimensions
        self._resize_engineSpecific()

    def add_ds(self, ds):
        self._dsArray.append(ds)

    def _init_pygame(self, *args, **kwargs):
        self._loadField_engineSpecific = self._loadField_pygame
        self._visibleSurface = pygame.Surface(self.dimensions)
        self._resize_engineSpecific = self._resize_pygame

    def _loadField_pygame(self):
        self._resize_pygame()

    def _resize_pygame(self):
        fd = self.field.Data
        dimen = self.dimensions
        self._visibleSurface = pygame.Surface(dimen)
        self._visibleSurface.fill((0, 0, 0))
        if fd["width"] / fd["height"] <= dimen[0] / dimen[1]:
            height = dimen[1]
            width = fd["width"] / fd["height"] * height
        else:
            width = dimen[0]
            height = fd["height"] / fd["width"] * width
        self._offset = (
            int((dimen[0] - width) / 2),
            int((dimen[1] - height) / 2)
            )
        self._staticHeight, self._staticWidth = int(height), int(width)
        self._staticSurface = pygame.Surface(
            (self._staticWidth,  self._staticHeight)
            )
        for shape in fd["static-shapes"]:
            self._pygame_draw(shape, self._staticSurface)

    def _pygame_convertCoordinateSpace(self, points, offset=(0, 0)):
        p = []
        center = self.field.Data["center"]
        dimen = (self.field.Data["width"], self.field.Data["height"])
        for point in points:
            x = (point[0] + center[0]) / dimen[0] * self._staticWidth
            y = (-point[1] + center[1]) / dimen[1] * self._staticHeight
            p.append((int(x + offset[0]), int(y + offset[1])))
        return p

    def _pygame_draw(self, shape, surface, offset=(0, 0)):
        p = self._pygame_convertCoordinateSpace(shape["points"], offset)
        if shape["type"] == "polygon":
            if "filled" in shape["style"]:
                pygame.gfxdraw.filled_polygon(
                    surface,
                    p,
                    shape["color"]
                    )
            if "outline" in shape["style"]:
                pygame.gfxdraw.polygon(
                    surface,
                    p,
                    shape["color"]
                    )
            if "aa" in shape["style"]:
                pygame.gfxdraw.aapolygon(
                    surface,
                    p,
                    shape["color"]
                    )
        elif shape["type"] == "line":
            if "outline" in shape["style"]:
                pygame.gfxdraw.line(
                    surface,
                    p[0][0],
                    p[0][1],
                    p[1][0],
                    p[1][1],
                    shape["color"]
                    )
            if "aa" in shape["style"]:
                pygame.gfxdraw.aapolygon(
                    surface,
                    p,
                    shape["color"]
                    )

    def pygame_render(self):
        self._visibleSurface.fill((0, 0, 0))
        self._visibleSurface.blit(self._staticSurface, self._offset)
        for ds in self._dsArray:
            for shape in ds.draw(self.field.Data["orientation"]):
                self._pygame_draw(shape, self._visibleSurface, self._offset)
        return self._visibleSurface


if __name__ == "__main__":
    if conf["TEAM"]["NUMBER"] == 0:
        num = input("TEAM.NUMBER option is set to 0, please enter one: ")
        try:
            conf["TEAM"]["NUMBER"] = float(num.strip())
        except ValueError:
            print("No TEAM.NUMBER entered, or non-numeric input given.")
            exit(1)
    if conf["TEAM"]["NUMBER"] <= 0:
        print("Invalid TEAM.NUMBER. TEAM.NUMBER must be greater than 0.")
        exit(1)
    if int(conf["TEAM"]["NUMBER"]) != conf["TEAM"]["NUMBER"]:
        print("Invalid TEAM.NUMBER. TEAM.NUMBER must be an integer.")
        exit(1)
    if not isinstance(conf["TEAM"]["NUMBER"], int):
        config["TEAM"]["NUMBER"] = int(config["TEAM"]["NUMBER"])
    if len(str(conf["TEAM"]["NUMBER"])) > 4:
        print("Invalid TEAM.NUMBER. TEAM.NUMBER must be 4 digits or less.")
        exit(1)
    config.set_nt_address(conf["TEAM"]["NUMBER"])
    conf = config.get_config()
    start_independent()
