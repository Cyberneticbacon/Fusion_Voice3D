
from .lib import fusionAddInUtils as futil
import adsk.core
import traceback
app = adsk.core.Application.get()
from . import grab_target as gt
from . import Voice3d
class Target:
    def __init__(self, name: str):
        self.name = name.upper()
        # BLUE C
    def get_target(self):
        if " " in self.name:
            target = gt.grab_target(self.name.split(" ")[1], self.name.split(" ")[0])
        else:
            target = gt.grab_target(self.name)
        # use descriptors to filter target
        return target
class Destination:
    def __init__(self, length: float = None, prep: str = None, destination: Target = None):
        if prep == "from":
            self.length = length * -1
        else:
            self.length = length
        self.prep = prep
        self.destination = destination
    def get_distance(self, target: Target = None):
        if target is None:
            return self.length
        else:
            if self.prep == "to":
                return self.length
            if self.prep in ["from", "past"]:
                return target.get_target().distance_to(self.destination.get_target()) + self.length
        

            

def add(x, y):
    return x + y

def camera_move(targets: list, destination: Destination):
    cam = app.activeViewport.camera
    if len(targets) == 0:
        x, y, z = destination.destination.name.split(" ")
        cam.eye = adsk.core.Point3D.create(float(x), float(y), float(z))
        cam.target = adsk.core.Point3D.create(0, 0, 0)
        cam.upVector = adsk.core.Vector3D.create(0, 1, 0)
    else:
        pass
    cam.isFitView = True
    app.activeViewport.camera = cam
    app.activeViewport.refresh()
    return "Camera moved"

def create_profile(face: adsk.fusion.BRepFace):
    app = adsk.core.Application.get()
    design = app.activeProduct
    root_comp = design.rootComponent

    # Create a sketch on the selected face
    sketch = root_comp.sketches.add(face)

    # Project the face's edges
    for edge in face.edges:
        sketch.project(edge)

    return sketch.profiles.item(0)
def extrude(targets: list, destination: Destination):
    app = adsk.core.Application.get()
    design = app.activeProduct
    root_comp = design.rootComponent
    extrudes = root_comp.features.extrudeFeatures
    print("here")
    for target in targets:
        face = target.get_target()
        print(type(face))
        #return str(type(face))
        if isinstance(face, adsk.fusion.BRepFace):
            '''
            extent_distance = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString(str(destination.get_distance(target))))
            start_from = adsk.fusion.FromEntityStartDefinition.create(face, adsk.core.ValueInput.createByString("0 mm"))
            extrudeInput = extrudes.createInput(face, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
            extrudeInput.startExtent = start_from
            extrudes.add(extrudeInput)
            '''
            '''
            prof = create_profile(face)
            if not prof:
                raise ValueError("Target is not a valid profile")
            extrudes.addSimple(face, adsk.core.ValueInput.createByString(str(destination.get_distance(target))), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            '''
            comp = face.body.parentComponent
            extrudes = comp.features.extrudeFeatures
            extrudeFeats = comp.features.extrudeFeatures
            distance = adsk.core.ValueInput.createByString(str(destination.get_distance(target)))
            x = extrudeFeats.addSimple(face, distance,  adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            return "EEE"
            


            #a.extrude(destination.get_distance(target))
    print("done")
    return "Extruded"

command_dict = {
        "add": add, 
        "camera_move": camera_move,
        "extrude": extrude
    }

#['command: camera_move', '', 'destination:  |   | 0 0 1']
def parse_command(command: str):
    if command == "quit":
        return "stopped"
    try:
        lines = command.split("\n")
        command = lines[0].split(": ")[1]
        print(command)
        targetString = lines[1]
        targets = []
        if targetString != "":
            for target in targetString.split("|"):
                target = target.split(": ")[1]
                targets.append(Target(target))
        destinationString = lines[2].split(": ")[1]
        length, prep, target_destination = destinationString.split(" | ")
        target_destination = Target(target_destination)
        destination = Destination(length= length, prep= prep, destination= target_destination)
        c = command_dict[command](targets, destination)
        return c
        return command, targets, destination
    except Exception as e:
        print(f"error parsing command: " + traceback.format_exc())
        return "error parsing command: " + traceback.format_exc()
def run_command(command: str):
    command, targets, destination = parse_command(command)
    return command_dict[command](targets, destination)
