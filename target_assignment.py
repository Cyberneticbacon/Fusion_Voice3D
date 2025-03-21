import adsk.fusion
import adsk.core
from adsk.core import Vector3D
import configparser
'''
class TargetType:
    dict = {
        "face": 0.0,
        "edge": 1.0,
        "vertex": 2.0,
        "all": 3.0
        }'
'''
def grab_point_on_target(target):
    if isinstance(target, adsk.fusion.BRepFace):
        return target.pointOnFace
    elif isinstance(target, adsk.fusion.BRepEdge):
        return target.pointOnEdge
    elif isinstance(target, adsk.fusion.BRepVertex):
        return target.geometry

app = adsk.core.Application.get()
ui = app.userInterface

def grab_list_of_targets(type = "default"):
    if type == "default":
        type = "face"
    design = app.activeProduct
    cam_point = app.activeViewport.camera.eye
    component = design.rootComponent
    bodies = component.bRepBodies
    user_params = design.userParameters
    '''
    if type == "default":
        type = user_params.itemByName("voice_3d_default_type").value
    else:
        user_params.itemByName("voice_3d_default_type").value =  adsk.core.ValueInput.createByReal(TargetType.dict[type])
    '''
    target_list = []
    if type == "face":
        # Grab all faces
        for body in bodies:
            for face in body.faces:
                target_list.append(face)
    elif type == "edge":
        # Grab all edges
        for body in bodies:
            for edge in body.edges:
                target_list.append(edge)
    elif type == "vertex":
        for body in bodies:
            for vertex in body.vertices:
                target_list.append(vertex)
    elif type == "all":
        for body in bodies:
            for face in body.faces:
                target_list.append(face)
            for edge in body.edges:
                target_list.append(edge)
            for vertex in body.vertices:
                target_list.append(vertex)
    color_names = ["BLUE", "GREEN", "YELLOW", "PURPLE", "CYAN"]
    color_wheel = [adsk.core.Color.create(0, 0, 120, 122), adsk.core.Color.create(0, 120, 0, 122), adsk.core.Color.create(120, 120, 0, 122), adsk.core.Color.create(120, 0, 120, 122), adsk.core.Color.create(0, 120, 120, 122)]
    color_effect = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0, 0, 120, 122))
    color_index = 0
    design = app.activeProduct
    attribs = design.findAttributes('talon.labels', 'color:letter')
    temp_graphics = component.customGraphicsGroups.item(0)
    while temp_graphics.count > 0:
        temp_graphics.item(0).deleteMe()
    for attrib in attribs:
        attrib.deleteMe()    
    letter = 'A'
    for target in target_list:
        try:
            letter = chr(ord(letter) + 1)
            if letter > 'Z':
                letter = 'A'  # Reset to 'A' after 'Z'
                color_index += 1
                color_effect = adsk.fusion.CustomGraphicsSolidColorEffect.create(color_wheel[color_index % len(color_wheel)])
            print(f"Face ID: {target.tempId}, Letter: {letter}")
            target.attributes.add("talon.labels", "color:letter", color_names[color_index % len(color_names)] + ":" + letter)

            startPoint = grab_point_on_target(target)
            endPoint = adsk.core.Point3D.create(startPoint.x, startPoint.y, startPoint.z)
            dist_to_camera = app.activeViewport.camera.eye.vectorTo(startPoint)
            dist_to_camera.normalize()
            dist_to_camera.scaleBy(-1)
            endPoint.translateBy(adsk.core.Vector3D.create(dist_to_camera.x, dist_to_camera.y + 0.225, dist_to_camera.z + 0.155))
            coordinates = [startPoint.x, startPoint.y, startPoint.z, endPoint.x, endPoint.y, endPoint.z]
            customGraphicsCoordinates = adsk.fusion.CustomGraphicsCoordinates.create(coordinates)
            line = temp_graphics.addLines(customGraphicsCoordinates, [0, 1], False)
            line.weight = 2
            line.color = color_effect
            letterPosition = endPoint
            transform = adsk.core.Matrix3D.create()
            if isinstance(target, adsk.fusion.BRepFace):
                (result, faceNormal) = target.evaluator.getNormalAtPoint(startPoint)
                print("face")
            elif isinstance(target, adsk.fusion.BRepEdge):
                (result, faceNormal) = target.evaluator.getTangent(parameter=0)
                print("edge")
            elif isinstance(target, adsk.fusion.BRepVertex):
                faceNormal = adsk.core.Vector3D.create(0, 0, 1)
                result = True
                print("vertex")
            if not result:
                faceNormal.normalize()
                faceNormal.scaleBy(0.5)
            cameraNormal = app.activeViewport.camera.eye.vectorTo(startPoint)
            cameraNormal.normalize()
            cameraNormal.scaleBy(0.5)
            upVector = app.activeViewport.camera.upVector
            upVector.normalize()
            transform.setToRotateTo(Vector3D.create(0, 0, 1), cameraNormal)
            transform.setToRotateTo(Vector3D.create(0, 1, 0), upVector)
            transform.translation = adsk.core.Vector3D.create(letterPosition.x, letterPosition.y, letterPosition.z)
            text = temp_graphics.addText(letter, "Arial", 0.33, transform)
            text.isOutlined = True
            text.outlineColor = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0, 0, 0, 255))
            text.color = color_effect
            
        except Exception as e:
            #ui.messageBox(traceback.format_exc())
            print(f"Error: {e}")
    app.activeViewport.refresh()