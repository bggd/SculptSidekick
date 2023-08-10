import bpy


class SculptSidekickBase:
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


class SculptSidekickPanel(SculptSidekickBase, bpy.types.Panel):
    bl_idname = "UI_PT_SculptSidkick"
    bl_label = "Sculpt Sidekick"

    def draw(self, context):
        pass


class SculptSidekickPanelViewport(SculptSidekickBase, bpy.types.Panel):
    bl_idname = "UI_PT_SculptSidkickViewport"
    bl_label = "Viewport"
    bl_parent_id = "UI_PT_SculptSidkick"
    bl_options = {"DEFAULT_CLOSED"}

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


from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
import bl_ui


class SCULPTSIDEKICK_MT_DyntopoPresets(bpy.types.Menu):
    bl_label = "New Presets"
    preset_subdir = "SculptSidekick/dyntopo_presets"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset


class SCULPTSIDEKICK_OT_AddDyntopoPresets(AddPresetBase, bpy.types.Operator):
    bl_idname = "sculpt_sidekick.dyntopo_preset_add"
    bl_label = "Add Dyntopo Presets"
    preset_menu = "SCULPTSIDEKICK_MT_DyntopoPresets"

    preset_defines = ["sculpt = bpy.context.scene.tool_settings.sculpt"]

    preset_values = [
        "sculpt.detail_type_method",
        "sculpt.constant_detail_resolution",
        "sculpt.detail_size",
        "sculpt.detail_percent",
        "sculpt.detail_refine_method",
    ]

    preset_subdir = "SculptSidekick/dyntopo_presets"


class SCULPTSIDEKICK_PT_Presets(PresetPanel, bpy.types.Panel):
    bl_label = "Dynto Presets"
    preset_subdir = "SculptSidekick/dyntopo_presets"
    preset_operator = "script.execute_preset"
    preset_add_operator = "sculpt_sidekick.dyntopo_preset_add"


class SculptSidekickDyntopoPanel(SculptSidekickBase, bpy.types.Panel):
    bl_idname = "UI_PT_SculptSidkickDyntopo"
    bl_label = ""
    bl_parent_id = "UI_PT_SculptSidkick"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout

        is_active = True
        if not context.sculpt_object.use_dynamic_topology_sculpting:
            is_active = False

        layout.operator(
            "sculpt.dynamic_topology_toggle",
            text="Dyntopo",
            icon="CHECKBOX_HLT" if is_active else "CHECKBOX_DEHLT",
            emboss=True,
        )

    def draw_header_preset(self, context):
        SCULPTSIDEKICK_PT_Presets.draw_panel_header(self.layout)

    def draw(self, context):
        sidekick = context.scene.sidekick_properties

        sculpt = context.scene.tool_settings.sculpt

        paint_settings = bl_ui.properties_paint_common.UnifiedPaintPanel.paint_settings(
            context
        )
        brush = None
        if context.sculpt_object and sculpt and paint_settings:
            brush = paint_settings.brush

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.active = context.sculpt_object.use_dynamic_topology_sculpting

        sub = col.column()
        sub.active = brush and brush.sculpt_tool != "MASK"
        if sculpt.detail_type_method in {"CONSTANT", "MANUAL"}:
            row = sub.row(align=True)
            row.prop(sculpt, "constant_detail_resolution", text="Resolution")
            props = row.operator(
                "sculpt.sample_detail_size", text="", icon="EYEDROPPER"
            )
            props.mode = "DYNTOPO"
        elif sculpt.detail_type_method == "BRUSH":
            sub.prop(sculpt, "detail_percent")
        else:
            sub.prop(sculpt, "detail_size")
        sub.prop(sculpt, "detail_refine_method", text="Refine Method")
        sub.prop(sculpt, "detail_type_method", text="Detailing")

        if sculpt.detail_type_method in {"CONSTANT", "MANUAL"}:
            col.operator("sculpt.detail_flood_fill")

        col.prop(sculpt, "use_smooth_shading")


class SculptSidekickRemeshPanel(SculptSidekickBase, bpy.types.Panel):
    bl_idname = "UI_PT_SculptSidkickRemesh"
    bl_label = "Remesh"
    bl_parent_id = "UI_PT_SculptSidkick"
    bl_options = {"DEFAULT_CLOSED"}

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


classes = (
    SculptSidekickPanel,
    SculptSidekickPanelViewport,
    SCULPTSIDEKICK_MT_DyntopoPresets,
    SCULPTSIDEKICK_OT_AddDyntopoPresets,
    SCULPTSIDEKICK_PT_Presets,
    SculptSidekickDyntopoPanel,
    SculptSidekickRemeshPanel,
)


def preset_menu(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.menu(
        SCULPTSIDEKICK_MT_DyntopoPresets.__name__,
        text=SCULPTSIDEKICK_MT_DyntopoPresets.bl_label,
    )
    row.operator(SCULPTSIDEKICK_OT_AddDyntopoPresets.bl_idname, text="", icon="ADD")
    row.operator(
        SCULPTSIDEKICK_OT_AddDyntopoPresets.bl_idname, text="", icon="REMOVE"
    ).remove_active = True


def register_classes():
    for cls in classes:
        bpy.utils.register_class(cls)

    # bpy.types.VIEW3D_PT_sculpt_dyntopo.prepend(preset_menu)
    SculptSidekickDyntopoPanel.prepend(preset_menu)


def unregister_classes():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # bpy.types.VIEW3D_PT_sculpt_dyntopo.remove(preset_menu)
    SculptSidekickDyntopoPanel.remove(preset_menu)
