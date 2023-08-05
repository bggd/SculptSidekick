# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Sculpt Sidekick",
    "author": "birthggd",
    "description": "Sculpt Sidekick",
    "blender": (2, 80, 0),
    "version": (0, 0, 9),
    "location": "",
    "warning": "",
    "category": "3D View",
}

import bpy
import bl_ui


remesh_mode_items = [("VOXEL", "Voxel", ""), ("QUAD", "Quad", "")]


class SculptSidekickProperty(bpy.types.PropertyGroup):
    remesh_mode: bpy.props.EnumProperty(items=remesh_mode_items)
    dyntopo_show: bpy.props.BoolProperty(
        name="Show or Hide Option for Dyntopo functions", default=True
    )


from . import icons
from .operators import SculptSidekickFlipToolbarOp, SculptSidekickFlipSidebarOp
from .panel import (
    SculptSidekickPanel,
    SculptSidekickDyntopoPanel,
    SculptSidekickRemeshPanel,
)
from .pie_menu import SculptSidekickPieBrushMenu

classList = (
    SculptSidekickProperty,
    SculptSidekickFlipToolbarOp,
    SculptSidekickFlipSidebarOp,
    SculptSidekickPanel,
    SculptSidekickDyntopoPanel,
    SculptSidekickRemeshPanel,
    SculptSidekickPieBrushMenu,
)


addon_keymaps = []


def register():
    icons.create_icons()

    for cls in classList:
        bpy.utils.register_class(cls)

    bpy.types.Scene.sidekick_properties = bpy.props.PointerProperty(
        type=SculptSidekickProperty
    )

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="Sculpt")
        kmi = km.keymap_items.new("wm.call_menu_pie", "W", "PRESS")
        kmi.properties.name = "PIE_MT_SculptSidkickPieBrush"
        addon_keymaps.append((km, kmi))


def unregister():
    icons.release_icons()

    for cls in reversed(classList):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.sidekick_properties

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
