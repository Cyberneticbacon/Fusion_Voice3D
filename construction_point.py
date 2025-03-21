import adsk.core, adsk.fusion, adsk.cam, traceback
class Construction_Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        connected_points = []
    
    def draw_point(self):
        # Draw a point at the location of the Construction_Point using the Fusion 360 CustomGraphics API
        coordinates = adsk.core.Point3D.create(self.x, self.y, self.z)
        app = adsk.core.Application.get()
        design = app.activeProduct
        root_comp = design.rootComponent
        custom_graphics = root_comp.customGraphicsGroups.item(1)
        point = custom_graphics.addPoint(coordinates)
        

    def connect(self, other):
        self.connected_points.append(other)
        other.connected_points.append(self)

    def disconnect(self, other):
        self.connected_points.remove(other)
        other.connected_points.remove(self)


    def __str__(self):
        return f"Construction_Point({self.x}, {self.y}, {self.z})"
    
    def __repr__(self):
        return f"Construction_Point({self.x}, {self.y}, {self.z})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __add__(self, other):
        return Construction_Point(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Construction_Point(self.x - other.x, self.y - other.y, self.z - other.z)
    

class Construction_Line:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
    
    def draw_line(self):
        # Draw a line between two Construction_Points using the Fusion 360 CustomGraphics API
        app = adsk.core.Application.get()
        design = app.activeProduct
        root_comp = design.rootComponent
        custom_graphics = root_comp.customGraphicsGroups.item(1)
        line = custom_graphics.addLine(self.point1, self.point2)
    
    def __str__(self):
        return f"Construction_Line({self.point1}, {self.point2})"
    
    def __repr__(self):
        return f"Construction_Line({self.point1}, {self.point2})"
    
    def __eq__(self, other):
        return self.point1 == other.point1 and self.point2 == other.point2
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def length(self):
        return ((self.point1.x - self.point2.x)**2 + (self.point1.y - self.point2.y)**2 + (self.point1.z - self.point2.z)**2)**0.5
    
    def midpoint(self):
        return Construction_Point((self.point1.x + self.point2.x) / 2, (self.point1.y + self.point2.y) / 2, (self.point1.z + self.point2.z) / 2)
    