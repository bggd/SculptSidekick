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
    "version": (0, 0, 8),
    "location": "",
    "warning": "",
    "category": "3D View",
}

import os
import bpy
import bl_ui


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
    bl_label = "Sculpt Sidekick Viewport"
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


builtin_brushes = [
    ("builtin_brush.Draw", "Draw", "brush.sculpt.draw"),
    ("builtin_brush.Draw Sharp", "Draw Sharp", "brush.sculpt.draw_sharp"),
    ("builtin_brush.Clay", "Clay", "brush.sculpt.clay"),
    ("builtin_brush.Clay Strips", "Clay Strips", "brush.sculpt.clay_strips"),
    ("builtin_brush.Clay Thumb", "Clay Thumb", "brush.sculpt.clay_thumb"),
    ("builtin_brush.Layer", "Layer", "brush.sculpt.layer"),
    ("builtin_brush.Inflate", "Inflate", "brush.sculpt.inflate"),
    ("builtin_brush.Blob", "Blob", "brush.sculpt.blob"),
    ("builtin_brush.Crease", "Crease", "brush.sculpt.crease"),
    ("builtin_brush.Smooth", "Smooth", "brush.sculpt.smooth"),
    ("builtin_brush.Flatten", "Flatten", "brush.sculpt.flatten"),
    ("builtin_brush.Fill", "Fill", "brush.sculpt.fill"),
    ("builtin_brush.Scrape", "Scrape", "brush.sculpt.scrape"),
    (
        "builtin_brush.Multi-plane Scrape",
        "Multi-plane Scrape",
        "brush.sculpt.multiplane_scrape",
    ),
    ("builtin_brush.Pinch", "Pinch", "brush.sculpt.pinch"),
    ("builtin_brush.Grab", "Grab", "brush.sculpt.grab"),
    ("builtin_brush.Elastic Deform", "Elastic Deform", "brush.sculpt.elastic_deform"),
    ("builtin_brush.Snake Hook", "Snake Hook", "brush.sculpt.snake_hook"),
    ("builtin_brush.Thumb", "Thumb", "brush.sculpt.thumb"),
    ("builtin_brush.Pose", "Pose", "brush.sculpt.pose"),
    ("builtin_brush.Nudge", "Nudge", "brush.sculpt.nudge"),
    ("builtin_brush.Rotate", "Rotate", "brush.sculpt.rotate"),
    ("builtin_brush.Slide Relax", "Slide Relax", "brush.sculpt.topology"),
    ("builtin_brush.Boundary", "Boundary", "brush.sculpt.boundary"),
    ("builtin_brush.Cloth", "Cloth", "brush.sculpt.cloth"),
    ("builtin_brush.Simplify", "Simplify", "brush.sculpt.simplify"),
    ("builtin_brush.Mask", "Mask", "brush.sculpt.mask"),
    ("builtin_brush.Draw Face Sets", "Draw Face Sets", "brush.sculpt.draw_face_sets"),
    (
        "builtin_brush.Multires Displacement Eraser",
        "Multires Displacement Eraser",
        "brush.sculpt.displacement_eraser",
    ),
    (
        "builtin_brush.Multires Displacement Smear",
        "Multires Displacement Smear",
        "brush.sculpt.displacement_smear",
    ),
    ("builtin_brush.Paint", "Paint", "brush.sculpt.paint"),
    ("builtin_brush.Smear", "Smear", "brush.sculpt.smear"),
]

builtin_others = [
    ("builtin.box_mask", "Box Mask", "ops.sculpt.border_mask"),
    ("builtin.lasso_mask", "Lasso Mask", "ops.sculpt.lasso_mask"),
    ("builtin.line_mask", "Line Mask", "ops.sculpt.line_mask"),
    ("builtin.box_hide", "Box Hide", "ops.sculpt.border_hide"),
    ("builtin.box_face_set", "Box Face Set", "ops.sculpt.border_face_set"),
    ("builtin.lasso_face_set", "Lasso Face Set", "ops.sculpt.lasso_face_set"),
    ("builtin.box_trim", "Box Trim", "ops.sculpt.box_trim"),
    ("builtin.lasso_trim", "Lasso Trim", "ops.sculpt.lasso_trim"),
    ("builtin.line_project", "Line Project", "ops.sculpt.line_project"),
    None,
    ("builtin.mesh_filter", "Mesh Filter", "ops.sculpt.mesh_filter"),
    ("builtin.cloth_filter", "Cloth Filter", "ops.sculpt.cloth_filter"),
    ("builtin.color_filter", "Color Filter", "ops.sculpt.color_filter"),
    None,
    ("builtin.face_set_edit", "Edit Face Set", "ops.sculpt.face_set_edit"),
    ("builtin.mask_by_color", "Mask by Color", "ops.sculpt.mask_by_color"),
]


class SculptSidekickPieBrushMenu(
    bpy.types.Menu,
):
    bl_idname = "PIE_MT_SculptSidkickPieBrush"
    bl_label = "Pie SculptSidekick"
    bl_space_type = "VIEW_3D"

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
        global brush_icons

        sculpt_tool = context.tool_settings.sculpt.brush.sculpt_tool

        layout = self.layout

        pie = layout.menu_pie()
        pie.scale_y = 1.75
        pie.scale_x = 1.5

        space_type = context.space_data.type
        tool_active_id = getattr(
            bl_ui.space_toolsystem_common.ToolSelectPanelHelper._tool_active_from_context(
                context, space_type
            ),
            "idname",
            None,
        )

        col = pie.grid_flow(row_major=True, columns=2, align=True)

        for i in builtin_brushes:
            tool = i[0]
            name = f"builtin_brush.{i[1]}"
            icon = brush_icons[i[2]]

            col.operator(
                "wm.tool_set_by_id",
                text="",
                icon_value=icon,
                depress=tool == tool_active_id,
            ).name = name

        class FakeSelf:
            def __init__(self, layout):
                self.layout = layout

        col = pie.column()
        col.scale_y = 0.65
        col.scale_x = 0.7
        bl_ui.space_toolsystem_common.ToolSelectPanelHelper.draw_active_tool_header(
            context,
            col,
            show_tool_icon_always=True,
            tool_key=bl_ui.space_toolsystem_common.ToolSelectPanelHelper._tool_key_from_context(
                context, space_type=self.bl_space_type
            ),
        )
        if tool_active_id.startswith("builtin_brush"):
            settings = bl_ui.properties_paint_common.UnifiedPaintPanel.paint_settings(
                context
            )
            col.template_ID_preview(
                settings, "brush", new="brush.add", rows=3, cols=8, hide_buttons=True
            )
        col = col.box()
        obj = FakeSelf(col)
        bl_ui.space_view3d.VIEW3D_PT_sculpt_context_menu.draw(obj, context)

        col = pie.grid_flow(row_major=True, columns=2, align=True)
        for i in builtin_others:
            if i == None:
                col.separator()
                continue
            idname = i[0]
            icon = brush_icons[i[2]]
            col.operator(
                "wm.tool_set_by_id",
                text="",
                icon_value=icon,
                depress=idname == tool_active_id,
            ).name = idname


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

    for brush in builtin_brushes + builtin_others:
        if brush == None:
            continue
        filename = os.path.join(icons_directory, f"{brush[2]}.dat")
        icon_value = bpy.app.icons.new_triangles_from_file(filename)
        brush_icons[brush[2]] = icon_value


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
