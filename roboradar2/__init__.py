#!/usr/bin/python3

__all__ = ['VideoEngines', 'Radar']
__version__ = '0.1.6'
__author__ = 'David Johnston'

import os
import sys
from enum import Enum
import argparse
if sys.platform == "win32":
    import ctypes

try:
    from roboradar import config
    from roboradar.fields import fields, fieldFiles, fieldNames, fieldThemes
    import roboradar.robots as robots
    # import roboradar.utils as utils
except ImportError:
    import config
    from fields import fields, fieldFiles, fieldNames, fieldThemes
    import robots
    # import utils

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


class VideoEngines(Enum):
    native = "native"
    numpy = "numpy"
    pygame = "pygame"
    opencv = "opencv"


VERSION = __version__


if VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.pygame:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
    import pygame.gfxdraw
    import pygame.locals
else:
    raise ValueError

_pgFlag = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF


def start_independent(flags=_pgFlag):
    '''Start an independent RoboRadar window.
flags: flags for pygame.display.set_mode'''
    if sys.platform == "win32":
        appid = 'ShortSirkit.RoboRadar.RoboRadar.' + __version__.replace(".", "_")
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    if VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.pygame:
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


if __name__ == "__main__" or __name__ == "independent":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', action='store_true')
    options = parser.parse_args()
    if options.l:
        conf["ROBOT"]["IP_ADDRESS"] = "127.0.0.1"
        conf["ROBOT"]["IP_ADDRESS_SET"] = True
        config.set_config(conf)
    else:
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
            conf["TEAM"]["NUMBER"] = int(conf["TEAM"]["NUMBER"])
        if len(str(conf["TEAM"]["NUMBER"])) > 4:
            print("Invalid TEAM.NUMBER. TEAM.NUMBER must be 4 digits or less.")
            exit(1)
        config.set_nt_address(conf["TEAM"]["NUMBER"])
    conf = config.get_config()
    start_independent()
