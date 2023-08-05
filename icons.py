import os
import bpy


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
