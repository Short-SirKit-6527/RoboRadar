#!/usr/bin/python3

__all__ = ['VideoEngines', 'Radar']
__version__ = '0.3.0'
__author__ = 'David Johnston'

import os
import sys
from enum import Enum
import pint
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
ureg = pint.UnitRegistry()

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


try:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
    import pygame.gfxdraw
    import pygame.locals
    _independent_flags_pygame = pygame.RESIZABLE \
        | pygame.HWSURFACE \
        | pygame.DOUBLEBUF
except ImportError:
    print("pygame not installed")
try:
    import tkinter
    _independent_flags_tkinter = 0
except ImportError:
    print("tkinter not installed")

_independent_flags = 0


def _start_independent_pygame(
        flags=_independent_flags,
        engine_flags=_independent_flags_pygame
        ):
    '''Start an independent pygame RoboRadar window.
flags: flags for pygame.display.set_mode'''

    if VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.pygame:
        pygame.init()

        screen = pygame.display.set_mode(
            conf["VIDEO"]["SCREEN_DIMENSIONS"],
            pygame.RESIZABLE | engine_flags)
        pygame.display.set_caption(
            "RoboRadar v{} - Team {}".format(
                VERSION,
                conf["TEAM"]["NUMBER"]
                )
            )
        pygame.display.set_icon(
            pygame.image.load(
                __file__[:-11] + "icon.png"
                )
            )

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


def _start_independent_tkinter(
        flags=_independent_flags,
        engine_flags=_independent_flags_tkinter
        ):
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
            self.c = self.radar.tkinter_get_canvas()
            self.c.pack(fill=tkinter.BOTH, expand=1)
            self.c.bind("<Configure>", self.configure)
            self.radar.loadField(conf["FIELD"]["NAME"])

            self.bb = robotList["BoxBot"]()
            self.radar.add_ds(self.bb)

            self.after(1000 // conf["VIDEO"]["FPS"], self.update)

        def update(self, event=None):
            self.radar.tkinter_render()
            self.after(1000 // conf["VIDEO"]["FPS"], self.update)

        def configure(self, event=None):
            self.radar.resize((event.width, event.height))

        def on_exit(self):
            self.destroy()
            exit()

    root = IndependentApp()
    root.mainloop()


def start_independent(flags=_independent_flags, engine_flags=0):
    if sys.platform == "win32":
        appid = 'ShortSirkit.RoboRadar.RoboRadar'\
            + conf["VIDEO"]["ENGINE"].capitalize()\
            + '.' + __version__.replace(".", "_")
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
        ctypes.windll.user32.SetProcessDPIAware()
    if VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.pygame:
        _start_independent_pygame(flags=flags, engine_flags=engine_flags)
    elif VideoEngines[conf["VIDEO"]["ENGINE"]] is VideoEngines.tkinter:
        _start_independent_tkinter(flags=flags, engine_flags=engine_flags)


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
        self.units = self.field.Data["units"]
        self._unitify(self.field.Data["static-shapes"], self.units)
        u = ureg(self.units)
        self.field.Data["width"] = self.field.Data["width"] * u
        self.field.Data["height"] = self.field.Data["height"] * u
        self.field.Data["center"] = tuple(
            i * ureg(self.units) for i in self.field.Data["center"]
            )
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
                bd=0,
                highlightthickness=0
                )
        self._resize_engineSpecific = self._resize_tkinter

    def _loadField_pygame(self):
        self._resize_pygame()

    def _loadField_tkinter(self):
        self._canvas.delete("RoboRadar")
        self._resize_tkinter()

    def _tkinter_get_name_tag(self, family, name):
        return "RoboRadar-{}-{}".format(family, name)

    def _resize_pygame(self):
        fd = self.field.Data
        dimen = self.dimensions
        self._visibleSurface = pygame.Surface(dimen)
        self._visibleSurface.fill((0, 0, 0))
        if fd["width"].magnitude / fd["height"].magnitude <=\
                dimen[0] / dimen[1]:
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

    def _unitify(self, shapes, units):
        ''' This function handles making sure units are converted properly
This should be changed to be a generator that takes a generator so it can
directly use the output from DynamicShape.
'''
        if units is None:
            units = self.units
        for shape in range(len(shapes)):
            unit = ureg.parse_expression(shapes[shape].get("unit", units))
            for point in range(len(shapes[shape]["points"])):
                shapes[shape]["points"][point] = (
                    shapes[shape]["points"][point][0] * unit,
                    shapes[shape]["points"][point][1] * unit
                )

    def _convertCoordinateSpace(self, points, offset=(0, 0)):
        ''' This function has three jobs.
1. Scale coordinates to the screen size.
2. Apply offsets to move coordinates.
3. Convert and remove units before data is sent the graphics libraries.
'''
        p = []
        center = self.field.Data["center"]
        dimen = (
                 self.field.Data["width"].magnitude,
                 self.field.Data["height"].magnitude
                 )
        for point in points:
            try:
                pv = (point[0].to(self.units), point[1].to(self.units))
                pv = (pv[0].magnitude, pv[1].magnitude)
            except AttributeError:
                pv = point
            x = (pv[0] + center[0].magnitude) / dimen[0] * self._staticWidth
            y = (-pv[1] + center[1].magnitude) / dimen[1] * self._staticHeight
            p.append((int(x + offset[0]), int(y + offset[1])))
        return p

    def _tkinter_draw(self, shape, family, offset=(0, 0)):
        p = self._convertCoordinateSpace(shape["points"], offset)
        p_flat = []
        for point in p:
            p_flat.append(point[0])
            p_flat.append(point[1])
        tag = self._tkinter_get_name_tag(family, shape["name"])
        if shape["type"] == "polygon":
            if "filled" in shape["style"]:
                fill = "#{0:02x}{1:02x}{2:02x}".format(
                    *shape["color"])
            else:
                fill = ""
            if "outline" in shape["style"]:
                outline = "#{0:02x}{1:02x}{2:02x}".format(
                    *shape["color"])
            else:
                outline = ""
            if len(self._canvas.find_withtag(tag + "-l")) <= 0:
                self._canvas.create_polygon(
                    0, 0, 0, 0,
                    fill=fill,
                    outline=outline,
                    tags=(
                        tag + "-l",
                        tag,
                        "RoboRadar-" + family,
                        "RoboRadar"
                        )
                    )
            self._canvas.coords(tag, *p_flat)
        elif shape["type"] == "line":
            if len(self._canvas.find_withtag(tag + "-l")) <= 0:
                self._canvas.create_line(
                    0, 0, 0, 0,
                    fill="#{0:02x}{1:02x}{2:02x}".format(
                        *shape["color"]),
                    tags=(
                        tag + "-l",
                        tag,
                        "RoboRadar-" + family,
                        "RoboRadar"
                        )
                    )
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
            shapes = list(ds.draw(self.field.Data["orientation"]))
            self._unitify(shapes, ds.units)
            for shape in shapes:
                self._pygame_draw(shape, self._visibleSurface, self._offset)
        return self._visibleSurface

    def tkinter_render(self):
        for ds in self._dsArray:
            shapes = list(ds.draw(self.field.Data["orientation"]))
            self._unitify(shapes, ds.units)
            print(shapes)
            for shape in shapes:
                self._tkinter_draw(
                    shape,
                    "DS{}".format(
                        ds.number
                        ),
                    self._offset
                    )

    def tkinter_get_canvas(self):
        return self._canvas


if __name__ == "__main__" or __name__ == "independent":
    try:
        from roboradar import __main__
    except ImportError:
        import __main__
    __main__.start()
