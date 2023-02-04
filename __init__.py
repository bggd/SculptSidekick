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
    "name": "SculptSidekick",
    "author": "birthggd",
    "description": "Sculpt Sidekick",
    "blender": (2, 80, 0),
    "version": (0, 0, 4),
    "location": "",
    "warning": "",
    "category": "3D View",
}

import os
import bpy


remesh_mode_items = [("VOXEL", "Voxel", ""), ("QUAD", "Quad", "")]


class SculptSidekickProperty(bpy.types.PropertyGroup):
    remesh_mode: bpy.props.EnumProperty(items=remesh_mode_items)
    dyntopo_show: bpy.props.BoolProperty(
        name="Show or Hide Option for Dyntopo functions", default=True
    )


class SculptSidekickFlipToolbarOp(bpy.types.Operator):
    bl_idname = "sculpt_sidekick.flip_toolbar"
    bl_label = "Flip Toolbar"

    def execute(self, context):
        toolbar = None
        for i in context.area.regions:
            if i.type == "TOOLS":
                toolbar = i
        if toolbar:
            with context.temp_override(region=toolbar):
                return bpy.ops.screen.region_flip()
        return {"CANCELLED"}


class SculptSidekickFlipSidebarOp(bpy.types.Operator):
    bl_idname = "sculpt_sidekick.flip_sidebar"
    bl_label = "Flip Sidebar"

    def execute(self, context):
        sidebar = None
        for i in context.area.regions:
            if i.type == "UI":
                sidebar = i
        if sidebar:
            with context.temp_override(region=sidebar):
                return bpy.ops.screen.region_flip()
        return {"CANCELLED"}


class SculptSidekickPanel(bpy.types.Panel):
    bl_idname = "UI_PT_SculptSidkick"
    bl_label = "Sculpt Sidekick"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sculpt Sidekick"
    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.mode != "SCULPT":
            return False
        obj = context.active_object
        if not obj:
            return False
        if obj.type != "MESH":
            return False

        return True

    def draw(self, context):
        sidekick = context.scene.sidekick_properties

        sculpt = context.scene.tool_settings.sculpt

        layout = self.layout

        is_active = True
        if not context.sculpt_object.use_dynamic_topology_sculpting:
            is_active = False

        toolbar_is_flip = False
        for i in context.area.regions:
            if i.type == "TOOLS" and i.alignment == "RIGHT":
                toolbar_is_flip = True
        sidebar_is_flip = False
        for i in context.area.regions:
            if i.type == "UI" and i.alignment == "LEFT":
                sidebar_is_flip = True
        flip = layout.row()
        flip_heading = flip.row()
        flip_heading.alignment = "RIGHT"
        flip_heading.label(text="Flip")
        flip.operator(
            "sculpt_sidekick.flip_toolbar", text="Toolbar", depress=toolbar_is_flip
        )
        flip.operator(
            "sculpt_sidekick.flip_sidebar", text="Sidebar", depress=sidebar_is_flip
        )

        wire = layout.row(align=True)
        wire.prop(context.space_data.overlay, "show_wireframes", text="")
        wire_opacity = wire.row()
        wire_opacity.prop(
            context.space_data.overlay, "wireframe_opacity", text="Wireframe Opacity"
        )

        if not context.space_data.overlay.show_overlays:
            wire.active = False
            wire_opacity.active = False
        if not context.space_data.overlay.show_wireframes:
            wire_opacity.active = False


class SculptSidekickDyntopoPanel(bpy.types.Panel):
    bl_idname = "UI_PT_SculptSidkickDyntopo"
    bl_label = ""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sculpt Sidekick"

    @classmethod
    def poll(cls, context):
        if context.mode != "SCULPT":
            return False
        obj = context.active_object
        if not obj:
            return False
        if obj.type != "MESH":
            return False

        return True

    def draw_header(self, context):
        layout = self.layout

        is_active = True
        if not context.sculpt_object.use_dynamic_topology_sculpting:
            is_active = False

        layout.operator(
            "sculpt.dynamic_topology_toggle",
            text="Sculpt Sidekick Dyntopo",
            icon="CHECKBOX_HLT" if is_active else "CHECKBOX_DEHLT",
            emboss=True,
        )

    def draw(self, context):
        sidekick = context.scene.sidekick_properties

        sculpt = context.scene.tool_settings.sculpt

        layout = self.layout

        is_active = True
        if not context.sculpt_object.use_dynamic_topology_sculpting:
            is_active = False

        method = layout.column()
        method.active = is_active
        method.prop(sculpt, "detail_type_method", expand=True)
        cnst = layout.split(align=True, factor=0.9)
        cnst.prop(sculpt, "constant_detail_resolution")
        op_snpl = cnst.operator("sculpt.sample_detail_size", text="", icon="EYEDROPPER")
        op_snpl.mode = "DYNTOPO"
        rel = layout.column()
        rel.prop(sculpt, "detail_size")
        brush = layout.column()
        brush.prop(sculpt, "detail_percent")
        refine = layout.column()
        refine.active = is_active
        refine.prop(sculpt, "detail_refine_method", expand=True)
        fill = layout.column()
        fill.operator("sculpt.detail_flood_fill")
        if (
            sculpt.detail_type_method == "CONSTANT"
            or sculpt.detail_type_method == "MANUAL"
        ):
            rel.active = False
            brush.active = False
        elif sculpt.detail_type_method == "RELATIVE":
            cnst.active = False
            brush.active = False
        elif sculpt.detail_type_method == "BRUSH":
            cnst.active = False
            rel.active = False
        if not is_active:
            rel.active = False
            cnst.active = False
            brush.active = False


class SculptSidekickRemeshPanel(bpy.types.Panel):
    bl_idname = "UI_PT_SculptSidkickRemesh"
    bl_label = "Sculpt Sidekick Remesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sculpt Sidekick"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        if context.mode != "SCULPT":
            return False
        obj = context.active_object
        if not obj:
            return False
        if obj.type != "MESH":
            return False

        return True

    def draw(self, context):
        sidekick = context.scene.sidekick_properties

        sculpt = context.scene.tool_settings.sculpt

        layout = self.layout

        mode = layout.row()
        mode.prop(sidekick, "remesh_mode", expand=True)

        remesh = layout.column()
        if sidekick.remesh_mode == "VOXEL":
            remesh.operator("object.voxel_remesh")
            remesh.operator("object.voxel_size_edit", icon="VIEW_ORTHO")
            remesh.use_property_split = True
            remesh.use_property_decorate = False
            mesh = context.active_object.data
            vsize = remesh.row(align=True)
            vsize.prop(mesh, "remesh_voxel_size")
            op_snpl = vsize.operator(
                "sculpt.sample_detail_size", text="", icon="EYEDROPPER"
            )
            op_snpl.mode = "VOXEL"
            remesh.prop(mesh, "remesh_voxel_adaptivity")
            remesh.prop(mesh, "use_remesh_fix_poles")
            col = remesh.column(heading="Preserve", align=True)
            col.prop(mesh, "use_remesh_preserve_volume", text="Volume")
            col.prop(mesh, "use_remesh_preserve_paint_mask", text="Paint Mask")
            col.prop(mesh, "use_remesh_preserve_sculpt_face_sets", text="Face Sets")
            col.prop(mesh, "use_remesh_preserve_vertex_colors", text="Color Attributes")
        else:
            remesh.operator("object.quadriflow_remesh")

        remesh.separator()
        sym = remesh.row()
        sym.operator("sculpt.symmetrize")
        sym.prop(sculpt, "symmetrize_direction", text="")


class SculptSidekickPieBrushMenu(bpy.types.Menu):
    bl_idname = "PIE_MT_SculptSidkickPieBrush"
    bl_label = "Pie SculptSidekick"

    def draw(self, context):
        global brush_icons
        layout = self.layout

        pie = layout.menu_pie()
        pie.scale_y = 1.5

        col = pie.column(align=True)
        col.operator(
            "sculpt.sculptraw", text="    Draw", icon_value=brush_icons["draw"]
        )
        col.operator(
            "paint.brush_select", text="    Clay", icon_value=brush_icons["clay"]
        ).sculpt_tool = "CLAY"
        col.operator(
            "paint.brush_select",
            text="    Clay Strips",
            icon_value=brush_icons["clay_strips"],
        ).sculpt_tool = "CLAY_STRIPS"
        col.operator(
            "paint.brush_select", text="    Crease", icon_value=brush_icons["crease"]
        ).sculpt_tool = "CREASE"
        col.operator(
            "paint.brush_select", text="    Blob", icon_value=brush_icons["blob"]
        ).sculpt_tool = "BLOB"

        col.operator(
            "paint.brush_select",
            text="    Inflate/Deflate",
            icon_value=brush_icons["inflate"],
        ).sculpt_tool = "INFLATE"

        col = pie.column(align=True)
        col.operator(
            "paint.brush_select", text="    Grab", icon_value=brush_icons["grab"]
        ).sculpt_tool = "GRAB"
        col.operator(
            "paint.brush_select", text="    Nudge", icon_value=brush_icons["nudge"]
        ).sculpt_tool = "NUDGE"
        col.operator(
            "paint.brush_select", text="    Thumb", icon_value=brush_icons["thumb"]
        ).sculpt_tool = "THUMB"
        col.operator(
            "paint.brush_select",
            text="    Snakehook",
            icon_value=brush_icons["snake_hook"],
        ).sculpt_tool = "SNAKE_HOOK"
        col.operator(
            "paint.brush_select", text="    Rotate", icon_value=brush_icons["rotate"]
        ).sculpt_tool = "ROTATE"

        col = pie.column(align=True)
        col.operator(
            "paint.brush_select", text="    Smooth", icon_value=brush_icons["smooth"]
        ).sculpt_tool = "SMOOTH"
        col.operator(
            "paint.brush_select", text="    Flatten", icon_value=brush_icons["flatten"]
        ).sculpt_tool = "FLATTEN"
        col.operator(
            "paint.brush_select",
            text="    Scrape/Peaks",
            icon_value=brush_icons["scrape"],
        ).sculpt_tool = "SCRAPE"
        col.operator(
            "paint.brush_select", text="    Fill/Deepen", icon_value=brush_icons["fill"]
        ).sculpt_tool = "FILL"
        col.operator(
            "paint.brush_select",
            text="    Pinch/Magnify",
            icon_value=brush_icons["pinch"],
        ).sculpt_tool = "PINCH"
        col.operator(
            "paint.brush_select", text="    Layer", icon_value=brush_icons["layer"]
        ).sculpt_tool = "LAYER"
        col.operator(
            "paint.brush_select", text="    Mask", icon_value=brush_icons["mask"]
        ).sculpt_tool = "MASK"


classList = (
    SculptSidekickProperty,
    SculptSidekickFlipToolbarOp,
    SculptSidekickFlipSidebarOp,
    SculptSidekickPanel,
    SculptSidekickDyntopoPanel,
    SculptSidekickRemeshPanel,
    SculptSidekickPieBrushMenu,
)

brush_icons = {}


def create_icons():
    global brush_icons
    icons_directory = bpy.utils.system_resource("DATAFILES", path="icons")
    brushes = (
        "crease",
        "blob",
        "smooth",
        "draw",
        "clay",
        "clay_strips",
        "inflate",
        "grab",
        "nudge",
        "thumb",
        "snake_hook",
        "rotate",
        "flatten",
        "scrape",
        "fill",
        "pinch",
        "layer",
        "mask",
    )
    for brush in brushes:
        filename = os.path.join(icons_directory, f"brush.sculpt.{brush}.dat")
        icon_value = bpy.app.icons.new_triangles_from_file(filename)
        brush_icons[brush] = icon_value


def release_icons():
    global brush_icons
    for value in brush_icons.values():
        bpy.app.icons.release(value)


addon_keymaps = []


def register():
    create_icons()

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
    release_icons()

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
