import bpy
from ..glb import glb
def on_update_bind_bones(self, context):
    return on_update_skel(self, context)


def on_update_skel(self, context):
    optional_bone = [9, 12, 7, 8, 10, 11, 20, 21]
    parent_bone = [-1, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 12, 13, 14, 16, 17, 18, 19, 20, 21]
    wide_bone = [3, 6, 9]
    glb().pose_manager.has_init_bones = False

    scene = glb().scene(context)

    am = scene.meocap_state.source_armature
    source = bpy.data.objects.get(scene.meocap_state.source_armature)
    bones = None
    if source and source.type == 'ARMATURE':
        bones: bpy.types.Armature = source.data.bones

    if am != "Null" and bones is not None:
        if len(scene.meocap_bone_map.nodes) == 24:
            nodes = scene.meocap_bone_map.nodes
            for index, node in enumerate(nodes):
                parent_index = parent_bone[index]
                children_bone = bones
                if parent_index != -1:
                    if parent_index in optional_bone and nodes[parent_index].name == "":
                        parent_index = parent_bone[parent_index]
                    if parent_index != -1 and nodes[parent_index].name != "":
                        for bone in bones:
                            if bone.name == nodes[parent_index].name:
                                if index in wide_bone:
                                    children_bone = []
                                    def get_all_children(b):
                                        nonlocal children_bone
                                        children_bone = children_bone + [_ for _ in b.children]
                                        for child in b.children:
                                            get_all_children(child)
                                    get_all_children(bone)
                                else:
                                    children_bone = bone.children
                node.available_bones.clear()
                for bone in children_bone:
                    new_available = node.available_bones.add()
                    new_available.name = bone.name
    return None


class StringItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="")


class MeocapRetargetNode(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="", update=on_update_bind_bones)
    lock: bpy.props.BoolProperty(name="")
    available_bones: bpy.props.CollectionProperty(type=StringItem)


def get_armature_items(self, ctx):
    """动态获取场景中的骨架名称列表"""
    armatures = [
        (obj.name, obj.name, "Armature Object")
        for obj in bpy.data.objects if obj.type == 'ARMATURE'
    ]
    return armatures if [("Null", "No Set", "Null Value")] + armatures else [("NONE", "None", "No armature available")]


class MeocapRetargetMap(bpy.types.PropertyGroup):
    nodes: bpy.props.CollectionProperty(type=MeocapRetargetNode)
    version: bpy.props.StringProperty(name="Map Version")


class MeocapState(bpy.types.PropertyGroup):
    has_connected: bpy.props.BoolProperty(name="Connected")
    bind_port: bpy.props.IntProperty(
        name="",
        default=14999,
        max=65535,
        min=0
    )
    source_armature: bpy.props.EnumProperty(
        name="",
        description="Choose an armature from the scene",
        items=get_armature_items,
        update=on_update_skel
    )
    frame_id: bpy.props.IntProperty(
        name="",
        default=0,
        max=1048576,
        min=0
    )
    is_recording: bpy.props.BoolProperty(name="Recording")




def register_types():
    bpy.types.Scene.meocap_bone_map = bpy.props.PointerProperty(type=MeocapRetargetMap)

    bpy.types.Scene.meocap_state = bpy.props.PointerProperty(type=MeocapState)
