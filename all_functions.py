import adsk.core
import traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        result = ''
        cmdDef = adsk.core.CommandDefinition.cast(None)
        for cmdDef in ui.commandDefinitions:
            if result == '':
                result = cmdDef.name + ', ' + cmdDef.id
            else:
                result += '\n' + cmdDef.name + ', ' + cmdDef.id
        
        output = open('FusionCommands.txt', 'w')
        output.writelines(result)
        output.close()
        ui.messageBox('Finished wrting to FusionCommands.txt')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))