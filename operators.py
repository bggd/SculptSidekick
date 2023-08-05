import bpy


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
