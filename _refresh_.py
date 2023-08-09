from importlib import reload
import sys
import bpy

from . import operators, panel, pie_menu, preferences


def reload_modules():
    if not bpy.context.preferences.view.show_developer_ui:
        return

    reload(operators)
    reload(panel)
    reload(pie_menu)
    reload(preferences)
    reload(sys.modules[__name__])
