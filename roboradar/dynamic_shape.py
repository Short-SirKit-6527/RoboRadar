from abc import ABC, abstractmethod
import math


class DynamicShape(ABC):
    x = 0
    y = 0
    r = 0
    d = None
    rsin = None
    rcos = None
    rtan = None

    @abstractmethod
    def getShapes(self):
        '''This method is called once per frame.
it should return a list of shapes to be drawn on the screen.'''
        pass

    def draw(self, r_adjust=0):
        shapes = self.getShapes()
        if self.d is None:
            r = self.r
        else:
            r = math.radians(self.d)
        if r_adjust == 0:
            if self.rsin is None:
                rsin = math.sin(r)
            else:
                rsin = self.rsin
            if self.rcos is None:
                rcos = math.cos(r)
            else:
                rcos = self.rcos
            # This next section is commented out because it may be needed in
            # the future, but for now isn't needed. Therefore if I don't need
            # to do the calculations, I won't waste the cycles.
            '''if self.rtan is None:
                rtan = math.tan(r)
            else:
                rtan = self.rtan'''
        else:
            r = r + r_adjust
            rsin = math.sin(r)
            rcos = math.cos(r)
        for shape in shapes:
            if shape["type"] == "polygon" or shape["type"] == "line":
                if shape["coordinate-space"] == "local":
                    points = []
                    for point in shape["points"]:
                        x = point[0] * rcos - point[1] * rsin + self.x
                        y = point[0] * rsin + point[1] * rcos + self.y
                        points.append((x, y))
                    shape["points"] = points
                    yield shape
