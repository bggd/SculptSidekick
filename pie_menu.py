import bpy
import bl_ui

from .icons import builtin_brushes, builtin_others, brush_icons


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
