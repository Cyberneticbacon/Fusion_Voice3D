
from .lib import fusionAddInUtils as futil
import adsk.core
import traceback
app = adsk.core.Application.get()
ui = app.userInterface
from . import grab_target as gt
from . import Voice3d
from . import target_assignment as ta
from . import construction_point as cp
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
    def get_coordinates(self):
        target = self.get_target()
        if isinstance(target, adsk.fusion.BRepFace):
            return target.pointOnFace
        elif isinstance(target, adsk.fusion.BRepEdge):
            return target.pointOnEdge
        elif isinstance(target, adsk.fusion.BRepVertex):
            return target.geometry
        
class Destination:
    def __init__(self, length: str = None, prep: str = None, destination: Target = None):
        if " " in length:
            self.length = Length(float(length.split(" ")[0]), length.split(" ")[1])
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
    def get_coordinates(self, target: Target = None):
        if target is None:
            return "No target"
        else:
            if self.destination is None:
                if self.prep == "above":
                    return target.get_target().get_coordinates() + adsk.core.Vector3D.create(0, 0, self.length.length)
                if self.prep == "below":
                    return target.get_target().get_coordinates() + adsk.core.Vector3D.create(0, 0, -self.length.length)
                if self.prep == "left":
                    return target.get_target().get_coordinates() + adsk.core.Vector3D.create(-self.length.length, 0, 0)
                if self.prep == "right":
                    return target.get_target().get_coordinates() + adsk.core.Vector3D.create(self.length.length, 0, 0)
                if self.prep == "front":
                    return target.get_target().get_coordinates() + adsk.core.Vector3D.create(0, -self.length.length, 0)
                if self.prep == "back":
                    return target.get_target().get_coordinates() + adsk.core.Vector3D.create(0, self.length.length, 0)
                
                return target.get_coordinates()
            else:
                return self.destination.get_coordinates()






def camera_move(targets: list, destination: Destination):
    app = adsk.core.Application.get()
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
                edgeCollection = adsk.core.ObjectCollection.create()
                edgeCollection.add(target)
                filletInput.addConstantRadiusEdgeSet(edgeCollection, adsk.core.ValueInput.createByString(str(distance)), True)
                filletInput.isRollingBallCorner = True
                constRadiusInput = filletInput.edgeSetInputs.addConstantRadiusEdgeSet(edgeCollection, adsk.core.ValueInput.createByString(str(distance)), True)
                constRadiusInput.continuity = adsk.fusion.SurfaceContinuityTypes.TangentSurfaceContinuityType
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
                fillets.add(filletInput)

                
    except:
        return traceback.format_exc()
    return "Fillet added"

def move(targets: list, destination: Destination):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        root_comp = design.rootComponent
        move_features = root_comp.features.moveFeatures
        for target in targets:
            target = target.get_target()
            if isinstance(target, adsk.fusion.BRepFace):
                moveInput = move_features.createInput(target)
                distance = destination.get_distance()
                moveInput.setToEntity(adsk.fusion.BRepEntity.cast(target), adsk.core.ValueInput.createByString(str(distance)))
                move_features.add(moveInput)
            if isinstance(target, adsk.fusion.BRepEdge):
                moveInput = move_features.createInput(target)
                distance = destination.get_distance()
                moveInput.setToEntity(adsk.fusion.BRepEntity.cast(target), adsk.core.ValueInput.createByString(str(distance)))
                move_features.add(moveInput)
    except:
        return traceback.format_exc()
    return "Moved"

def offset_feature(targets: list, destination: Destination):
    try:
        app = adsk.core.Application.get()
        design = app.activeProduct
        root_comp = design.rootComponent
        offset_features = root_comp.features.offsetFeatures
        distance = destination.get_distance()
        object_collection = adsk.core.ObjectCollection.create()
        for target in targets:
            target = target.get_target()
            object_collection.add(target)
        offsetInput = offset_features.createInput(object_collection, distance=adsk.core.ValueInput.createByString(str(distance)), operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        offset_features.add(offsetInput)
    except:
        return traceback.format_exc()
    return "Offset"


def undo(targets: list, destination: Destination):
    app = adsk.core.Application.get()
    timeline = app.activeProduct.timeline
    timeline.markerPosition = timeline.markerPosition - 1
    return "Undone"

def clear_after_undo(targets: list, destination: Destination):
    app = adsk.core.Application.get()
    timeline = app.activeProduct.timeline
    timeline.deleteAllAfterMarker()
    return "Cleared after undo"




def redo(targets: list, destination: Destination):
    app = adsk.core.Application.get()
    ui = app.userInterface
    timeline = app.activeProduct.timeline
    timeline.markerPosition = timeline.markerPosition + 1
    return "Redone"
    
def construct(targets: list, destination: Destination):
    #location = destination.get_coordinates(targets[0])
    location = targets[0].get_coordinates()
    if location == None:
        return "no location"
    point = cp.Construction_Point(location.x, location.y, location.z)
    return point.draw_point()
'''
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
'''

def view_edges(targets: list, destination: Destination):
    ta.grab_list_of_targets("edge")
    return "Edges viewed"
def view_faces(targets: list, destination: Destination):
    ta.grab_list_of_targets("face")
    return "Faces viewed"
def view_vertices(targets: list, destination: Destination):
    ta.grab_list_of_targets("vertex")
    return "Vertices viewed"
def view_all(targets: list, destination: Destination):
    ta.grab_list_of_targets("all")
    return "All viewed"

def get_target_type(target):
    return type(target.get_target())



command_dict = {
        "camera_move": camera_move,
        "extrude": extrude,
        "fillet": fillet,
        "move": move,
        "edges": view_edges,
        "faces": view_faces,
        "vertices": view_vertices,
        "all": view_all,
        "offset": offset_feature,
        "undo": undo,
        "redo": redo,
        "present": clear_after_undo,
        "construct": construct
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
        if command not in ["edges", "faces", "vertices", "all"]:
            ta.grab_list_of_targets("default")
        return c
        return command, targets, destination
    except Exception as e:
        print(f"error parsing command: " + traceback.format_exc())
        return "error parsing command: " + traceback.format_exc()