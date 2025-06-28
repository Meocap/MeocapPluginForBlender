import bpy

from . import core
from . import glb
from . import ops
from . import translate
from . import ui

bl_info = {
    "name": "Meocap",
    "author": "Meocap Tech",
    "description": "",
    "blender": (4, 0, 0),
    "version": (0, 1, '8 (BETA)'),
    "location": "",
    "warning": "",
    "category": "Meocap"
}

class_list = [
    core.StringItem,
    core.MeocapRetargetNode,
    core.MeocapRetargetMap,
    core.MeocapState,
    ui.MeocapPanel,
    ops.ArmatureAutoMap,
    ops.AutoMapBoneVRMExt,
    ops.CreateRetargetConfig,
    ops.AutoMapBoneClear,
    ops.MeocapConnect,
    ops.MeocapDisconnect,
    ops.MeocapLoadRecording,
    ops.MeocapImportRetargetConfig,
    ops.MeocapExportRetargetConfig,
    ops.MeocapStartRecording,
    ops.MeocapEndRecording,
    ops.AutoMapApplyPresetConfig,
    ops.MeocapOpenURL
]


@bpy.app.handlers.persistent
def reset_property_values(_):
    pass


def register():
    translate.register()
    bpy.app.handlers.load_post.append(reset_property_values)

    g = glb.glb()

    g.pose_manager = ops.create_pose_manager()

    for item in class_list:
        bpy.utils.register_class(item)
    core.register_types()


@bpy.app.handlers.persistent
def on_load(dummy):
    """在场景加载后检查并初始化数据"""
    pass


bpy.app.handlers.load_post.append(on_load)


def unregister():
    translate.unregister()
    ops.stop_all()
    if on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_load)
    if reset_property_values in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(reset_property_values)
    for item in class_list:
        bpy.utils.unregister_class(item)
