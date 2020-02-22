#!/usr/bin/python3

__all__ = ['VideoEngines', 'Radar']
__version__ = '0.2.1'
__author__ = 'David Johnston'

import os
import sys
from enum import Enum
import argparse
if sys.platform == "win32":
    import ctypes

try:
    # raise ImportError  # Uncomment to force loading locals
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


if (conf["SYSTEM"]["FORCE_RUN_AS_MODULE"]) and __package__ is None:
    print("""Not running as module, restarting. Please run using 'py -m
RoboRadar.__init__'""")
    existingcwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__))[:-10])
    os.system("py -m roboradar.__init__")
    os.chdir(existingcwd)
    exit()


class VideoEngines(Enum):
    native = "native"
    numpy = "numpy"
    pygame = "pygame"
    tkinter = "tkinter"
    opencv = "opencv"


VERSION = __version__

if VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.pygame:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
    import pygame.gfxdraw
    import pygame.locals

    _independent_flags = pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
elif VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.tkinter:
    import tkinter
    _independent_flags = 0
else:
    raise ValueError


def _start_independent_pygame(flags=_independent_flags):
    '''Start an independent pygame RoboRadar window.
flags: flags for pygame.display.set_mode'''

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



def _start_independent_tkinter(flags=_independent_flags):
    '''Start an independent pygame RoboRadar window.
flags: flags'''
    class IndependentApp(tkinter.Tk):
        def __init__(self):
            tkinter.Tk.__init__(self)
            self.title("RoboRadar v{} - Team {}".format(
                VERSION,
                conf["TEAM"]["NUMBER"])
                )
            self.geometry("{w}x{h}".format(
                w=conf["VIDEO"]["SCREEN_DIMENSIONS"][0],
                h=conf["VIDEO"]["SCREEN_DIMENSIONS"][1]
                ))
            self.iconbitmap(__file__[:-11] + "icon.ico")
            self.protocol("WM_DELETE_WINDOW", self.on_exit)

            self.radar = Radar(conf["VIDEO"]["SCREEN_DIMENSIONS"], master=self)
            self.radar.tkinter_get_canvas().pack()
            self.radar.loadField(conf["FIELD"]["NAME"])

            self.bb = robotList["BoxBot"]()
            self.radar.add_ds(self.bb)

            self.after(1000 // conf["VIDEO"]["FPS"], self.update)

        def update(self, event=None):
            self.radar.tkinter_render()
            self.after(1000 // conf["VIDEO"]["FPS"], self.update)

        def on_exit(self):
            self.destroy()
            exit()

    root = IndependentApp()
    root.mainloop()


def start_independent(flags=_independent_flags):
    if sys.platform == "win32":
        appid = 'ShortSirkit.RoboRadar.RoboRadar'\
            + conf["VIDEO"]["ENGINE"].capitalize()\
            + '.' + __version__.replace(".", "_")
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    if VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.pygame:
        _start_independent_pygame(flags=flags)
    elif VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.tkinter:
        _start_independent_tkinter(flags=flags)


class Radar:
    _dsArray = []

    def __init__(
                 self, dimensions=conf["VIDEO"]["SCREEN_DIMENSIONS"],
                 interface=conf["VIDEO"]["ENGINE"],
                 *args, **kwargs):
        self.cnt = 0
        self.dimensions = dimensions
        self.fieldIndex = None
        self.field = None
        if VideoEngines[interface] is VideoEngines.pygame:
            self._init_pygame(*args, **kwargs)
        elif VideoEngines[interface] is VideoEngines.tkinter:
            self._init_tkinter(*args, **kwargs)

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
        self._dsArray[-1].number = self.cnt
        self.cnt += 1

    def _init_pygame(self, *args, **kwargs):
        self._loadField_engineSpecific = self._loadField_pygame
        self._visibleSurface = pygame.Surface(self.dimensions)
        self._resize_engineSpecific = self._resize_pygame

    def _init_tkinter(self, *args, **kwargs):
        self._loadField_engineSpecific = self._loadField_tkinter
        if len(args) >= 1:
            m = args[0]
        else:
            m = None
        self._master = kwargs.get("master", m)
        self._canvas = tkinter.Canvas(
                self._master,
                width=self.dimensions[0],
                height=self.dimensions[1],
                bg="#000000",
                bd=0
                )
        self._resize_engineSpecific = self._resize_tkinter

    def _loadField_pygame(self):
        self._resize_pygame()

    def _loadField_tkinter(self):
        self._canvas.delete("RoboRadar")
        fd = self.field.Data
        for shape in fd["static-shapes"]:
            if shape["type"] == "polygon":
                self._canvas.create_polygon(
                    [0] * len(shape["points"]) * 2,
                    fill="#{0:02x}{1:02x}{2:02x}".format(*shape["color"]),
                    tags=(
                        self._tkinter_get_name_tag(
                            "Background",
                            shape["name"]),
                        "RoboRadar-Background",
                        "RoboRadar"
                    )
                )
            if shape["type"] == "line":
                self._canvas.create_line(
                    [0] * len(shape["points"]) * 2,
                    fill="#{0:02x}{1:02x}{2:02x}".format(*shape["color"]),
                    tags=(
                        self._tkinter_get_name_tag(
                            "Background",
                            shape["name"]),
                        "RoboRadar-Background",
                        "RoboRadar"
                    )
                )
        self._resize_tkinter()

    def _tkinter_get_name_tag(self, family, name):
        return "RoboRadar-{}-{}".format(family, name)

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

    def _resize_tkinter(self):
        fd = self.field.Data
        dimen = self.dimensions
        self._canvas.config(
            width=self.dimensions[0],
            height=self.dimensions[1]
            )
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
        for shape in fd["static-shapes"]:
            self._tkinter_draw(shape, "Background", offset=self._offset)

    def _convertCoordinateSpace(self, points, offset=(0, 0)):
        p = []
        center = self.field.Data["center"]
        dimen = (self.field.Data["width"], self.field.Data["height"])
        for point in points:
            x = (point[0] + center[0]) / dimen[0] * self._staticWidth
            y = (-point[1] + center[1]) / dimen[1] * self._staticHeight
            p.append((int(x + offset[0]), int(y + offset[1])))
        return p

    def _tkinter_draw(self, shape, family, offset=(0, 0)):
        p = self._convertCoordinateSpace(shape["points"], offset)
        p_flat = []
        for point in p:
            p_flat.append(point[0])
            p_flat.append(point[1])
        tag = self._tkinter_get_name_tag(family, shape["name"])
        if shape["type"] == "polygon" or shape["type"] == "line":
            if "filled" in shape["style"]:
                self._canvas.coords(tag, *p_flat)

    def _pygame_draw(self, shape, surface, offset=(0, 0)):
        p = self._convertCoordinateSpace(shape["points"], offset)
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

    def tkinter_render(self):
        for ds in self._dsArray:
            for shape in ds.draw(self.field.Data["orientation"]):
                if len(self._canvas.find_withtag(self._tkinter_get_name_tag(
                        "DS{}".format(ds.number),
                        shape["name"]
                        ))) <= 0:
                    print(self._canvas.find_withtag(self._tkinter_get_name_tag(
                            "DS{}".format(ds.number),
                            shape["name"]
                            )))
                    if shape["type"] == "polygon":
                        self._canvas.create_polygon(
                            [0] * len(shape["points"]) * 2,
                            fill="#{0:02x}{1:02x}{2:02x}".format(
                                *shape["color"]),
                            tags=(
                                self._tkinter_get_name_tag(
                                    "DS{}".format(ds.number),
                                    shape["name"]),
                                "RoboRadar-Background",
                                "RoboRadar"
                            )
                        )
                    if shape["type"] == "line":
                        self._canvas.create_line(
                            [0] * len(shape["points"]) * 2,
                            fill="#{0:02x}{1:02x}{2:02x}".format(
                                *shape["color"]),
                            tags=(
                                self._tkinter_get_name_tag(
                                    "DS{}".format(ds.number),
                                    shape["name"]),
                                "RoboRadar-Background",
                                "RoboRadar"
                            )
                        )
                self._tkinter_draw(shape, "DS{}".format(ds.number), self._offset)

    def tkinter_get_canvas(self):
        return self._canvas

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
