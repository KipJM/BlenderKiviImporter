import kivi_parser

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

def update_info(self, context):
    scene = context.scene
    properties = scene.kivi_importer_properties

    if properties.motion_file_path is "" or None:
        return

    if not kivi_parser.check_validity(bpy.path.abspath(properties.motion_file_path)):
        properties.valid_loaded = False
        return
    else:
        properties.valid_loaded = True

    version, script, scene, shot, framerate = kivi_parser.get_file_info(bpy.path.abspath(properties.motion_file_path))

    # Update info
    properties.info_version = version
    properties.info_script = script
    properties.info_scene = scene
    properties.info_shot = shot
    properties.info_framerate = framerate


class KiviImporterProperties(PropertyGroup):
    motion_file_path: StringProperty(
        name="Recording File",
        description="Choose a KIVI motion recording file:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
        update=update_info
    )

    target_obj: PointerProperty(type=bpy.types.Object)

    valid_loaded: BoolProperty(
        name="Valid File Loaded",
        description="True if a valid mrec file is loaded",
        default=False
    )

    info_version: StringProperty(
        name="Recorder Version",
        description="The version of the KIVI Recorder where this file is recorded",
        default="",
        maxlen=1024,
    )

    info_script: StringProperty(
        name="Script",
        description="Name of the script of this recording",
        default="",
        maxlen=1024,
    )

    info_scene: StringProperty(
        name="Scene",
        description="Name of the scene of this recording",
        default="",
        maxlen=1024,
    )

    info_shot: StringProperty(
        name="Shot",
        description="The shot index of this recording",
        default="",
    )

    info_framerate: StringProperty(
        name="Framerate",
        description="The framerate of this recording",
        default="",
    )


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
        return ((properties.target_obj is not None) and
                (properties.motion_file_path is not None and properties.motion_file_path != "")
                and properties.valid_loaded)

    def execute(self, context):
        scene = context.scene
        properties = scene.kivi_importer_properties

        kivi_importer_core.import_file(bpy.path.abspath(properties.motion_file_path), properties.target_obj)

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------


class KiviImporterPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "KIVI"
    bl_context = "objectmode"


class KiviImporterMainPanel(KiviImporterPanel, Panel):
    bl_label = "KIVI Motion Importer"
    bl_idname = "OBJECT_PT_kivi_importer_panel"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        properties = scene.kivi_importer_properties

        layout.prop(properties, "motion_file_path")
        layout.prop_search(properties, "target_obj", context.scene, "objects", text="Select target object")

        layout.separator(factor=2)
        if properties.motion_file_path is None or properties.motion_file_path == "":
            layout.label(text="Please choose a motion recording (.mrec) file.")
        elif not properties.valid_loaded:
            layout.label(text="File is not a valid mrec file!!")
        elif properties.target_obj is None:
            layout.label(text="Please select the target which you want the animation to apply to.")
        layout.operator("kivi.import_motion_recording")


class KiviInfoSubpanel(KiviImporterPanel, Panel):
    bl_idname = "OBJECT_PT_kivi_info_subpanel"
    bl_label = "File Info"
    bl_parent_id = "OBJECT_PT_kivi_importer_panel"

    @classmethod
    def poll(self, context):
        scene = context.scene
        properties = scene.kivi_importer_properties
        return (
                    properties.motion_file_path is not None or properties.motion_file_path != "") and properties.valid_loaded

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properties = scene.kivi_importer_properties

        layout.enabled = False
        layout.prop(properties, "info_script", text="Script")
        layout.prop(properties, "info_scene", text="Scene")
        layout.prop(properties, "info_shot", text="Shot")
        layout.separator()
        layout.prop(properties, "info_framerate", text="Framerate")
        layout.prop(properties, "info_version", text="Version")


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    KiviImportOperator,
    KiviImporterProperties,
    KiviImporterMainPanel,
    KiviInfoSubpanel
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
