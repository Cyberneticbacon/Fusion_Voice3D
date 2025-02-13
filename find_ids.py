import adsk.core, adsk.fusion, adsk.cam, traceback
app = adsk.core.Application.get()
ui = app.userInterface
class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
            """ Custom event handler to capture command input IDs when a command is created. """
                    
            def __init__(self, ui):
                super().__init__()
                
        
            def notify(self, args):

                """ This method is called when the command is created. """
                ui.messageBox("Select a command to see its input IDs.")
                try:
                    cmd = adsk.core.Command.cast(args.command)
                    inputs = cmd.commandInputs
        
                    # Collect input IDs and types
                    input_info = [f"Input ID: {input.id}\nInput Type: {input.__class__.__name__}" for input in inputs]
        
                    # Create a message string
                    input_info_str = "\n\n".join(input_info) if input_info else "No inputs found."
        
                    # Show the inputs in a message box
                    ui.messageBox(f"Command Inputs:\n\n{input_info_str}")
        
                except Exception as e:
                    ui.messageBox(f'Error in CommandCreatedHandler:\n{str(e)}')
        
        
def show_command_input_ids_in_message_box(cmdDef: adsk.core.CommandDefinition):
    try:
        adsk.autoTerminate(False)
        app = adsk.core.Application.get()
        ui = app.userInterface


        # Event handler for the commandCreated event
        eventHandler = CommandCreatedHandler(ui)
        ui.commandCreated.add(eventHandler)
        # Connect to the commandCreated event.
        cmdDef.commandCreated.add(eventHandler)
        # Execute the command, triggering the commandCreated event
        
        cmdDef.execute()
        
    except Exception as e:
        ui = adsk.core.Application.get().userInterface
        if ui:
            ui.messageBox(f'Failed:\n{str(e)}')
