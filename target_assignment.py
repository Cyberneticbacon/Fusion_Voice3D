import adsk.fusion
import adsk.core
from adsk.core import Vector3D
import threading



app = adsk.core.Application.get()
def grab_list_of_targets(type):
    design = design = app.activeProduct
    cam_point = app.activeViewport.camera.eye
    component = design.rootComponent
    bodies = component.bRepBodies
    target_list = []
    if type == "face":
        for body in bodies:
            for face in body.faces:
                target_list.append(component.findBRepUsingRay(cam_point, face.pointOnFace, adsk.fusion.BRepEntityTypes.BRepFaceEntityType).item(0))
    elif type == "edge":
        for body in bodies:
            for edge in body.edges:
                target_list.append(component.findBRepUsingRay(cam_point, edge.pointOnEdge, adsk.fusion.BRepEntityTypes.BRepEdgeEntityType).item(0))
    elif type == "bodies":
        for body in bodies:
            target_list.append(body)
    target_list = list(set(target_list))
    
    color_names = ["BLUE", "GREEN", "RED", "YELLOW", "PURPLE", "CYAN"]
    color_wheel = [adsk.core.Color.create(0, 0, 120, 122), adsk.core.Color.create(0, 120, 0, 122), adsk.core.Color.create(120, 0, 0, 122), adsk.core.Color.create(120, 120, 0, 122), adsk.core.Color.create(120, 0, 120, 122), adsk.core.Color.create(0, 120, 120, 122)]
    color_effect = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0, 0, 120, 122))
    color_index = 0
    if component.customGraphicsGroups.count > 0:
        component.customGraphicsGroups.item(0).deleteMe()
    design = app.activeProduct
    attribs = design.findAttributes('talon.labels', 'color:letter')
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
            temp_graphics = component.customGraphicsGroups.add()
            startPoint = target.pointOnFace
            endPoint = adsk.core.Point3D.create(target.pointOnFace.x, target.pointOnFace.y, target.pointOnFace.z)
            dist_to_camera = app.activeViewport.camera.eye.vectorTo(target.pointOnFace)
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
            (result, faceNormal) = target.evaluator.getNormalAtPoint(target.pointOnFace)
            if not result:
                faceNormal.normalize()
                faceNormal.scaleBy(0.5)
            cameraNormal = app.activeViewport.camera.eye.vectorTo(target.pointOnFace)
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
            print(f"Error: {e}")
    app.activeViewport.refresh()







def assign_letters_to_visible_faces_private():
    design = app.activeProduct
    root_comp = design.rootComponent
    bodies = root_comp.bRepBodies
    letter = 'A'
    color_names = ["BLUE", "GREEN", "RED", "YELLOW", "PURPLE", "CYAN"]
    color_wheel = [adsk.core.Color.create(0, 0, 120, 122), adsk.core.Color.create(0, 120, 0, 122), adsk.core.Color.create(120, 0, 0, 122), adsk.core.Color.create(120, 120, 0, 122), adsk.core.Color.create(120, 0, 120, 122), adsk.core.Color.create(0, 120, 120, 122)]
    color_effect = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0, 0, 120, 122))
    color_index = 0
    while root_comp.customGraphicsGroups.count > 0:
        root_comp.customGraphicsGroups.item(0).deleteMe()
    
    design = app.activeProduct
    attribs = design.findAttributes('talon.labels', 'color:letter')
    for attrib in attribs:
        attrib.deleteMe()
    for body in bodies:
        for face in body.faces:
            try: 
                    letter = chr(ord(letter) + 1)
                    if letter > 'Z':
                        letter = 'A'  # Reset to 'A' after 'Z'
                        color_index += 1
                        color_effect = adsk.fusion.CustomGraphicsSolidColorEffect.create(color_wheel[color_index % len(color_wheel)])
                    
                    # Assign a letter to the visible face
                    print(f"Face ID: {face.tempId}, Letter: {letter}")
                    face.attributes.add("talon.labels", "color:letter", color_names[color_index % len(color_names)] + ":" + letter)
                    # Increment the letter
                    tempGraphics = root_comp.customGraphicsGroups.add()
                    startPoint = face.pointOnFace
                    endPoint = adsk.core.Point3D.create(face.pointOnFace.x, face.pointOnFace.y, face.pointOnFace.z)
                    
                    dist_to_camera = app.activeViewport.camera.eye.vectorTo(face.pointOnFace)
                    dist_to_camera.normalize()
                    dist_to_camera.scaleBy(-1)
                    endPoint.translateBy(adsk.core.Vector3D.create(dist_to_camera.x, dist_to_camera.y + 0.225, dist_to_camera.z + 0.155))
                    
                    coordinates = [startPoint.x, startPoint.y, startPoint.z, endPoint.x, endPoint.y, endPoint.z]
                    customGraphicsCoordinates = adsk.fusion.CustomGraphicsCoordinates.create(coordinates)

                    line = tempGraphics.addLines(customGraphicsCoordinates, [0, 1], False)
                    line.weight = 2
                    line.color = color_effect
                    
                    letterPosition = endPoint
                    transform = adsk.core.Matrix3D.create()
                    
                    (result, faceNormal) = face.evaluator.getNormalAtPoint(face.pointOnFace)
                    if not result:
                        faceNormal.normalize()
                        faceNormal.scaleBy(0.5)
                    
                    cameraNormal = app.activeViewport.camera.eye.vectorTo(face.pointOnFace)
                    cameraNormal.normalize()
                    cameraNormal.scaleBy(0.5)
                    
                    upVector = app.activeViewport.camera.upVector
                    upVector.normalize()
                    
                    transform.setToRotateTo(Vector3D.create(0, 0, 1), cameraNormal)
                    transform.setToRotateTo(Vector3D.create(0, 1, 0), upVector)
                    transform.translation = adsk.core.Vector3D.create(letterPosition.x, letterPosition.y, letterPosition.z)
                    
                    text = tempGraphics.addText(letter, "Arial", 0.33, transform)
                    text.isOutlined = True
                    text.outlineColor = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0, 0, 0, 255))
                    text.color = color_effect
                    
                    
            except Exception as e:
                print(f"Error: {e}")

    app.activeViewport.refresh()
    return "Letters assigned to visible faces"

def assign_letters_to_visible_faces():
    thread = threading.Thread(target=assign_letters_to_visible_faces_private)
    thread.start()
    return "Letters assigned to visible faces"

    

