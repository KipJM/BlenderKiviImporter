bl_info = {
    "name": "Kivi Motion Importer",
    "description": "Converts Kivi Motion Recording (.mrec)s to animation keyframes",
    "author": "Kip",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "3D View > Side Panel > KIVI",
    "support": "COMMUNITY",
    "category": "Animation"
}

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )

import kivi_importer_core

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class KiviImporterProperties(PropertyGroup):
    motion_file_path: StringProperty(
        name="Recording File",
        description="Choose a KIVI motion recording file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
        # update=
    )

    target_obj: PointerProperty(type=bpy.types.Object)

# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class KiviImportOperator(Operator):
    bl_label = "Import KIVI .mrec"
    bl_idname = "kivi.import_motion_recording"
    bl_description = "Apply the contents of the KIVI Motion recording file to the object's animation keyframes"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        properties = scene.kivi_importer_properties
        return properties.target_obj is not None and properties.motion_file_path is not None

    def execute(self, context):
        scene = context.scene
        properties = scene.kivi_importer_properties

        kivi_importer_core.import_file(bpy.path.abspath(properties.motion_file_path), properties.target_obj)

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class KiviImporterPanel(Panel):
    bl_label = "KIVI Motion Importer"
    bl_idname = "OBJECT_PT_kivi_importer_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "KIVI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        properties = scene.kivi_importer_properties

        layout.prop(properties, "motion_file_path")
        layout.prop_search(properties, "target_obj", context.scene, "objects", text="Select target object")

        layout.separator(factor=1.5)
        layout.operator("kivi.import_motion_recording")


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    KiviImportOperator,
    KiviImporterProperties,
    KiviImporterPanel
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.kivi_importer_properties = PointerProperty(type=KiviImporterProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.kivi_importer_properties


if __name__ == "__main__":
    register()