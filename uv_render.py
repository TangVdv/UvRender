import bpy
import os
from bpy.types import PropertyGroup, Operator, Panel

bl_info = {
    "name": "UV Animated Render",
    "description": "Render a scene with the UVs of selected meshes",
    "author": "TangVdv",
    "version": (1, 0),
    "blender": (3, 6, 5),
    "location": "VIEW_3D > N Panel > UV Render",
    "category": "Render",
    "github_url": "https://github.com/TangVdv/UvRender"
}

def main(self, context):
    pathOutput = context.scene.render_output
    if(pathOutput != ""):
        if(context.active_object.mode == "EDIT"):
            bpy.ops.object.editmode_toggle()
        mode = context.scene.render_select_mode.mode_enum
        collectionName = context.scene.render_select_col.col_enum
        objects = GetObjects(mode, collectionName)
        if(len(objects) > 0):
            pathOutput = os.path.dirname(bpy.data.filepath) + pathOutput
            frame_start = context.scene.render_frame_start
            frame_end = context.scene.render_frame_end
        else:
            self.report({"ERROR"}, "No mesh is selected")
            return
    else:
        self.report({"ERROR"}, "You must enter a path output !")
        return

    if SetCameraView(context) == False:
        self.report({"ERROR"}, "Camera not found")
        return
    
    SelectObjects(context, objects)
    
    for i in range(int(frame_start), int(frame_end)+1):
        GenerateUvRenderImage(context, i, pathOutput)

    return

def GenerateUvRenderImage(context, frame, pathOutput):
    context.scene.frame_set(frame)
    if(context.active_object.mode == "OBJECT"):
        bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.project_from_view(camera_bounds=False, correct_aspect=True, scale_to_bounds=False)
    name = f"{frame:04}"
    bpy.ops.uv.export_layout(filepath=pathOutput + str(name) +".png", size=(1024, 1024))

def SelectObjects(context, objects):
    for obj in objects:
        obj.select_set(True)
        context.view_layer.objects.active = obj

def SetCameraView(context):
    obj_camera = context.scene.camera
    if obj_camera is not None:
        context.view_layer.objects.active = obj_camera
        bpy.ops.view3d.object_as_camera()
        bpy.ops.object.select_all(action="DESELECT")
        return True
    else:
        return False

def GetObjects(mode, collectionName):
    objects = []
    match mode:
        case "SELECT":
            objects = GetMeshesOnly(bpy.context.selected_objects)

        case "COLLECTION":
            for col in bpy.data.collections:
                if col.name == collectionName:
                    objects = GetMeshesOnly(bpy.data.collections[collectionName].all_objects)

        case "ALL":
            objects = GetMeshesOnly(bpy.context.scene.objects)

    return objects

def GetMeshesOnly(objects):
    selectedObjects = []
    for obj in objects:
        if obj.type == "MESH":
            selectedObjects.append(obj)
    return selectedObjects

class UVRENDER_OT_UvRender(Operator):
    """Render scene with UV meshes"""
    bl_idname = "render.uv_render"
    bl_label = "UV Render"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        main(self, context)
        return {"FINISHED"}

class ModeProperties(PropertyGroup):
    mode_enum: bpy.props.EnumProperty(
        name="",
        items=[
            ("SELECT", "Meshes", "selected meshes selection mode"),
            ("COLLECTION", "Collection", "collection selection mode"),
            ("ALL", "All", "All meshes selection mode")
        ],
        default="SELECT"
    )

class CollectionProperties(PropertyGroup):
    def UpdateCollectionList(self, context):
        collectionList = []
        for col in bpy.data.collections:
            collectionList.append((col.name, col.name, ""))
        return collectionList

    col_enum: bpy.props.EnumProperty(
        name="",
        items=UpdateCollectionList,
        default=None
    )

class UVRENDER_PT_UvRenderPanel(Panel):
    """UvRender Panel"""
    bl_label = "UV Render"
    bl_idname = "UVRENDER_PT_UvRenderPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UV Render"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Render UV from mesh")

        col = layout.column()
        col.label(text="Mesh Selection mode")
        col.prop(context.scene.render_select_mode, "mode_enum")

        if(context.scene.render_select_mode.mode_enum == "COLLECTION"):
            col = layout.column()
            col.label(text="Collection name")
            col.prop(context.scene.render_select_col, "col_enum")

        layout.separator()

        row = layout.row()
        row.prop(context.scene, "render_frame_start", text="Frame Start")

        row = layout.row()
        row.prop(context.scene, "render_frame_end", text="Frame End")

        layout.separator()

        row = layout.row()
        row.prop(context.scene, "render_output", text="Output")

        layout.separator()

        row = layout.row()
        row.operator("render.uv_render", text="Render")

classes = (
    UVRENDER_OT_UvRender,
    ModeProperties,
    CollectionProperties,
    UVRENDER_PT_UvRenderPanel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.render_select_col = bpy.props.PointerProperty(
        type = CollectionProperties
    )

    bpy.types.Scene.render_select_mode = bpy.props.PointerProperty(
        type = ModeProperties
    )

    bpy.types.Scene.render_output = bpy.props.StringProperty(
        name = "Output",
        default = "",
        maxlen=1024,
        subtype="DIR_PATH"
    ) 

    bpy.types.Scene.render_frame_start = bpy.props.IntProperty(
        name = "Frame Start",
        default = 1,
        min = 0
    ) 

    bpy.types.Scene.render_frame_end = bpy.props.IntProperty(
        name = "Frame End",
        default = 250,
        min = 0
    ) 

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.render_select_col
    del bpy.types.Scene.render_select_mode
    del bpy.types.Scene.render_output
    del bpy.types.Scene.render_frame_start
    del bpy.types.Scene.render_frame_end

if __name__ == "__main__":
    register()
