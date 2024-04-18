import kivi_importer_blender

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

from bpy.props import PointerProperty

classes = (
    kivi_importer_blender.KiviImportOperator,
    kivi_importer_blender.KiviImporterProperties,
    kivi_importer_blender.KiviImporterMainPanel,
    kivi_importer_blender.KiviInfoSubpanel
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.kivi_importer_properties = PointerProperty(type=kivi_importer_blender.KiviImporterProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.kivi_importer_properties
