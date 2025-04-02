import adsk.core, adsk.fusion, adsk.cam, traceback
class Construction_Point:
    POINT_IMAGE = "./Construction_Point.png"
    POINT_TYPE = adsk.fusion.CustomGraphicsPointTypes.UserDefinedCustomGraphicsPointType
    INDEX_LIST = []  # Assuming we want to use the first index for the point
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        connected_points = []
        point = None  # Placeholder for the point object in Fusion 360
    
    def draw_point(self):
        # Draw a point at the location of the Construction_Point using the Fusion 360 CustomGraphics API
        try:
            app = adsk.core.Application.get()
            design = app.activeProduct
            root_comp = design.rootComponent
            custom_graphics = root_comp.customGraphicsGroups.add()  # Create a new custom graphics group
            
            # Create a cube using 4 points
            half_length = 0.075
            # Half of the square's side length in centimeters
            points = [
                self.x - half_length, self.y - half_length, self.z + half_length,
                self.x + half_length, self.y - half_length, self.z + half_length,
                self.x + half_length, self.y + half_length, self.z + half_length,
                self.x - half_length, self.y + half_length, self.z + half_length,
                self.x - half_length, self.y - half_length, self.z - half_length,
                self.x + half_length, self.y - half_length, self.z - half_length,
                self.x + half_length, self.y + half_length, self.z - half_length,
                self.x - half_length, self.y + half_length, self.z - half_length,
                

            ]
            
            # Convert points to coordinates
            coords = adsk.fusion.CustomGraphicsCoordinates.create(points)
            
            # Add the square to the custom graphics group
            # Define vertex indices for the square (two triangles forming the square)
            vertexIndices = [0, 1, 2, 0, 2, 3,
                             4, 5, 6, 4, 6, 7,
                             0, 1, 5, 0, 5, 4,
                             2, 3, 7, 2, 7, 6,
                             0, 3, 7, 0, 7, 4,
                             1, 2, 6, 1, 6, 5]
            
            # Add the square to the custom graphics group
            mesh = custom_graphics.addMesh(coords, vertexIndices, [], [])

            self.point = mesh  # Store the point object for later deletion
            app.activeViewport.refresh()
            return "Square drawn at ({}, {}, {}) with side length of 50 pixels".format(self.x, self.y, self.z)
        except Exception as e:
            return f"Failed to draw square: {str(e)}"

    def delete_point(self):
        # Delete the point from the Fusion 360 CustomGraphics API
        if self.point:
            self.point.deleteMe()
            self.point = None
        return "Point deleted at ({}, {}, {})".format(self.x, self.y, self.z)
        
        

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
    