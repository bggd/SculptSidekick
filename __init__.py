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
    "version": (2, 1, 0),
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
from . import operators
from . import panel
from . import pie_menu
from .preferences import SculptSidekickPreferences

from . import _refresh_

_refresh_.reload_modules()

classList = (
    SculptSidekickProperty,
    SculptSidekickPreferences,
    pie_menu.SculptSidekickPieBrushMenu,
)


def register():
    icons.create_icons()

    for cls in classList:
        bpy.utils.register_class(cls)

    bpy.types.Scene.sidekick_properties = bpy.props.PointerProperty(
        type=SculptSidekickProperty
    )

    operators.register_classes()
    panel.register_classes()
    pie_menu.register()


def unregister():
    icons.release_icons()

    for cls in reversed(classList):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.sidekick_properties

    operators.unregister_classes()
    panel.unregister_classes()
    pie_menu.unregister()


if __name__ == "__main__":
    register()
