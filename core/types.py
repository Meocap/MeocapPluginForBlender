import bpy
from ..glb import glb
from .data import armature_preset_items


def on_update_bind_bones(self, context):
    return on_update_skel(self, context)


def get_source_armature(self, context):
    pass


def on_update_skel(self, context):
    optional_bone = [9, 12, 7, 8, 10, 11, 20, 21]
    parent_bone = [-1, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 12, 13, 14, 16, 17, 18, 19, 20, 21]
    wide_bone = [3, 6, 9]
    glb().pose_manager.has_init_bones = False

    scene = glb().scene(context)

    am = scene.meocap_state.source_armature

    source = scene.meocap_state.source_armature
    bones = None

    if source is not None and source.type == 'ARMATURE':
        bones: bpy.types.Armature = source.data.bones

    if am != "Null" and bones is not None:
        if len(scene.meocap_bone_map.nodes) == 24:
            nodes = scene.meocap_bone_map.nodes
            node_names = [n.name for n in nodes]
            for index, node in enumerate(nodes):
                parent_index = parent_bone[index]
                children_bone = bones
                if parent_index != -1:
                    if parent_index in optional_bone and nodes[parent_index].name == "":
                        parent_index = parent_bone[parent_index]
                    if parent_index != -1 and nodes[parent_index].name != "":
                        for bone in bones:
                            if bone.name == nodes[parent_index].name:
                                children_bone = []

                                def get_all_children(b):
                                    nonlocal children_bone
                                    children_bone = children_bone + [_ for _ in b.children]
                                    for child in b.children:
                                        get_all_children(child)

                                get_all_children(bone)

                node.available_bones.clear()
                for bone in children_bone:
                    if (bone.name not in node_names) or bone.name == node_names[index]:
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
    armatures = []

    # 遍历场景中的所有对象
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            name = str(obj.name.encode('utf-8').decode('utf-8'))
            armatures.append((name, name, "Armature Object"))

    if armatures:
        return armatures
    else:
        return [("NONE", "None", "No armature available")]


scale_translation_items = [
    ("1x", "1x", "1x (NoScale)"),
    ("100x", "100x", "100x"),
    ("0.01x", "0.01x", "0.01x")
]


def get_preset_items(self, ctx):
    return [(t[0], t[1], t[2]) for t in armature_preset_items]


class MeocapRetargetMap(bpy.types.PropertyGroup):
    nodes: bpy.props.CollectionProperty(type=MeocapRetargetNode)
    version: bpy.props.StringProperty(name="Map Version")


def filter_on_armatures(self, obj):
    return obj.type == 'ARMATURE'


class MeocapState(bpy.types.PropertyGroup):
    has_connected: bpy.props.BoolProperty(name="Connected")
    pure_input_mode: bpy.props.BoolProperty(name="Pure Input")
    lock_transition: bpy.props.BoolProperty(name="Lock Transition")
    bind_port: bpy.props.IntProperty(
        name="",
        default=14999,
        max=65535,
        min=0
    )
    source_armature: bpy.props.PointerProperty(
        name="",
        type=bpy.types.Object,
        poll=filter_on_armatures,
        update=on_update_skel
    )
    frame_id: bpy.props.IntProperty(
        name="",
        default=0,
        max=1048576,
        min=0
    )
    scale_trans: bpy.props.EnumProperty(
        name="Translation Scale",
        items=scale_translation_items
    )
    preset_items: bpy.props.EnumProperty(
        name="",
        items=get_preset_items
    )
    is_recording: bpy.props.BoolProperty(name="Recording")


def register_types():
    bpy.types.Scene.meocap_bone_map = bpy.props.PointerProperty(type=MeocapRetargetMap)

    bpy.types.Scene.meocap_state = bpy.props.PointerProperty(type=MeocapState)
