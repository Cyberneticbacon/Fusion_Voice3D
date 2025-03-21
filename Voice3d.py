
import adsk.fusion
from . import commands
from .lib import fusionAddInUtils as futil
from xmlrpc.server import SimpleXMLRPCServer
import threading
from . import functions as f
from . import target_assignment as ta
import adsk.core
from . import find_ids as fi
from . import all_functions as af
import adsk.fusion as fusion

server = None

def run(context):
    try:
        if context == "quit":
            raise Exception("Quit")
        global server
        app = adsk.core.Application.get()
        ui = app.userInterface
        # add user parameters
        user_params = app.activeProduct.userParameters
        if user_params.itemByName("voice_3d_default_type") is None:
            user_params.add('voice_3d_default_type', adsk.core.ValueInput.createByReal(0.0), "cm", "Default target type for voice3d, face, edge, vertex, or all")
        

        temp_graphics = app.activeProduct.rootComponent.customGraphicsGroups.add()
        construction_points = app.activeProduct.rootComponent.customGraphicsGroups.add()
        ta.grab_list_of_targets("face")
        server = SimpleXMLRPCServer(("localhost", 8000))
        server.register_function(f.parse_command, "parse_command")
        # Run the server in a separate thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("Server is running...")

    except Exception as e:
        ui.messageBox('Failed:\n{}'.format(str(e)))
        futil.handle_error('run')


def stop(context):
    try:
        futil.clear_handlers()
        #threading.Thread(target=server.shutdown).start()
        app = adsk.core.Application.get()
        root_comp = app.activeProduct.rootComponent
        while root_comp.customGraphicsGroups.count > 0:
            root_comp.customGraphicsGroups.item(0).deleteMe()
        server.shutdown()
    except Exception as e:
        print(f"Error: {e}")
        futil.handle_error('stop')