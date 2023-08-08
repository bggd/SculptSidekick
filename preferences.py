import bpy

from . import pie_menu


def update_fn_piemenu(self, context):
    addon = context.preferences.addons[__package__]
    prefs = addon.preferences

    if prefs.use_piemenu:
        pie_menu.enable_pie_menu()
    else:
        pie_menu.disable_pie_menu()


class SculptSidekickPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    use_piemenu: bpy.props.BoolProperty(default=True, update=update_fn_piemenu)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Pie menu: Hotkey: 'W'")
        row.prop(self, "use_piemenu", text="")
