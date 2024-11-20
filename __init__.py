import bpy
from . import ops
from . import core

bl_info = {
    "name": "Meocap",
    "author": "Meocap Tech",
    "description": "",
    "blender": (3, 0, 0),
    "version": (0, 0, '0 (BETA)'),
    "location": "",
    "warning": "",
    "category": "Meocap"
}

class_list = [
    ops.MeocapRetargetMap,
    core.MeocapRetargetNode,
    core.MeocapState,

]


@bpy.app.handlers.persistent
def reset_property_values(_):
    bpy.context.scene.open = False
    bpy.context.scene.recording = False
    # bind_bones = bpy.context.scene.bind_bones
    # bind_bones.clear()
    # for i in range(len(joints)):
    #     bone = bind_bones.add()
    #     bone.key = REBOCAP_JOINT_NAMES[i]
    #     bone.value = joints[i]


def register():
    bpy.app.handlers.load_post.append(reset_property_values)
    for item in class_list:
        bpy.utils.register_class(item)
    core.register_types()


def unregister():
    if reset_property_values in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(reset_property_values)
    for item in class_list:
        bpy.utils.unregister_class(item)
