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
    bl_label = "Sculpt Sidekick Viewport"
    # bl_options = {'DEFAULT_CLOSED'}

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


class SculptSidekickDyntopoPanel(SculptSidekickBase, bpy.types.Panel):
    bl_idname = "UI_PT_SculptSidkickDyntopo"
    bl_label = ""

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


class SculptSidekickRemeshPanel(SculptSidekickBase, bpy.types.Panel):
    bl_idname = "UI_PT_SculptSidkickRemesh"
    bl_label = "Sculpt Sidekick Remesh"
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
