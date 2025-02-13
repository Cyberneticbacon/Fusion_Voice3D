
from .lib import fusionAddInUtils as futil
import adsk.core
import traceback
app = adsk.core.Application.get()
ui = app.userInterface
from . import grab_target as gt
from . import Voice3d
from . import target_assignment as ta
class Length:
    def flip(self):
        self.length = self.length * -1
        return self.length
    def to_mm(self):
        if self.unit == "in":
            self.unit = "mm"
            self.length = self.length * 25.4
        if self.unit == "ft":
            self.unit = "mm"
            self.length = self.length * 304.8
        if self.unit == "yd":
            self.unit = "mm"
            self.length = self.length * 914.4
        if self.unit == "mi":
            self.unit = "mm"
            self.length = self.length * 1609344
    def __init__(self, length: float, unit: str = None):
        self.length = length
        self.unit = unit
        self.to_mm()
    def to_str(self):
        return f"{self.length} {self.unit}"
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
    def __init__(self, length: str = None, prep: str = None, destination: Target = None):
        if " " in length:
            self.length = Length(int(length.split(" ")[0]), length.split(" ")[1])
        else:
            if length == "":
                length = 0
            self.length = Length(int(length))
        if prep == "from":
            self.length.flip()
        self.prep = prep
        self.destination = destination

    def get_distance(self, target: Target = None):
        if target is None:
            return self.length.to_str()
        else:
            if self.prep == "to":
                return self.length.to_str()
            if self.prep in ["from", "past"]:
                return target.get_target().distance_to(self.destination.get_target()) + self.length.to_str()

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
        if isinstance(face, adsk.fusion.BRepFace):
            distance = destination.get_distance()
            extent_distance = adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString(str(distance)))
            start_from = adsk.fusion.FromEntityStartDefinition.create(face, adsk.core.ValueInput.createByString("0 mm"))
            extrudeInput = extrudes.createInput(face, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extrudeInput.setOneSideExtent(extent_distance, adsk.fusion.ExtentDirections.PositiveExtentDirection)
            extrudeInput.startExtent = start_from
            extrudes.add(extrudeInput)
    print("done")
    
    return "Extruded"

def fillet(targets: list, destination: Destination):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        root_comp = design.rootComponent
        fillets = root_comp.features.filletFeatures
        for target in targets:
            target = target.get_target()
            if isinstance(target, adsk.fusion.BRepEdge):
                filletInput = fillets.createInput()
                distance = destination.get_distance()
                filletInput.addConstantRadiusEdgeSet(target, adsk.core.ValueInput.createByString(str(distance)))
                fillets.add(filletInput)
            if isinstance(target, adsk.fusion.BRepFace):
                filletInput = fillets.createInput()
                distance = destination.get_distance()
                edgeCollection = adsk.core.ObjectCollection.create()
                for edge in target.edges:
                    edgeCollection.add(edge)
                filletInput.addConstantRadiusEdgeSet(edgeCollection, adsk.core.ValueInput.createByString(str(distance)), True)
                filletInput.isRollingBallCorner = True
                constRadiusInput = filletInput.edgeSetInputs.addConstantRadiusEdgeSet(edgeCollection, adsk.core.ValueInput.createByString(str(distance)), True)
                constRadiusInput.continuity = adsk.fusion.SurfaceContinuityTypes.TangentSurfaceContinuityType
                h = fillets.add(filletInput)

                
    except:
        return traceback.format_exc()
    return "Fillet added"






import adsk.core, adsk.fusion, adsk.cam, traceback

def push_pull(targets: list, destination: Destination):

    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Press Pull Command')

        # Get the Press Pull Command
        cmdDef = ui.commandDefinitions.itemById('FusionPressPullCommand')
        
        # Event handler to modify the inputs before command is shown
        def commandCreatedHandler(args: adsk.core.CommandCreatedEventArgs):
            inputs = args.command.commandInputs
            input = inputs.itemById('Selection')
            if input:
                for target in targets:
                    input.addSelection(target.get_target())
            # Modify the inputs here (for example, changing the distance of the pull)
            distance = destination.get_distance(targets[0])
            distanceInput = inputs.itemById('Distance')
            if distanceInput:
                distanceInput.value = adsk.core.ValueInput.createByReal(distance)

            # Optionally, other inputs can be modified similarly, based on available input IDs

        # Hook up the event handler
        cmdDef.commandCreated.add(commandCreatedHandler)

        # Execute the command
        cmdDef.execute()

    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(str(e)))




def get_target_type(target):
    return type(target.get_target())



command_dict = {
        "add": add, 
        "camera_move": camera_move,
        "extrude": extrude,
        "push_pull": push_pull,
        "fillet": fillet
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
        ta.assign_letters_to_visible_faces()
        return c
        return command, targets, destination
    except Exception as e:
        print(f"error parsing command: " + traceback.format_exc())
        return "error parsing command: " + traceback.format_exc()


def run_command(command: str):
    command, targets, destination = parse_command(command)
    
    return command_dict[command](targets, destination)
