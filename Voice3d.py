
from . import commands
from .lib import fusionAddInUtils as futil
from xmlrpc.server import SimpleXMLRPCServer
import threading
from . import functions as f
from . import target_assignment as ta
import adsk.core
server = None

def run(context):
    try:
        if context == "quit":
            raise Exception("Quit")
        global server
        ta.assign_letters_to_visible_faces()
        server = SimpleXMLRPCServer(("localhost", 8000))
        server.register_function(f.parse_command, "parse_command")
        # Run the server in a separate thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        f.parse_command("command: camera_move\n" + "\n" + "destination:  |   | 0 0 1")
        print("Server is running...")

    except:
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