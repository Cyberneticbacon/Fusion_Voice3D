import adsk.core, adsk.fusion, adsk.cam

def grab_target(letter, color="BLUE"):
    app = adsk.core.Application.get()
    design = app.activeProduct
    attribs = design.findAttributes('talon.labels', 'color:letter')
    for attrib in attribs:
        if attrib.value == f"{color}:{letter}":
            return attrib.parent
    print(f"Target with {color} {letter} not found")
    return None
        