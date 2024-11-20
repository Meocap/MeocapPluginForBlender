import bpy


class MeocapRetargetNode(bpy.types.PropertyGroup):
    prop_name_field: bpy.props.StringProperty(name="Bone Name")
    prop_lock_field: bpy.props.BoolProperty(name="Lock")


class MeocapRetargetMap(bpy.types.PropertyGroup):
    nodes: bpy.props.CollectionProperty(type=MeocapRetargetNode)
    version: bpy.props.StringProperty(name="Map Version")


class MeocapState(bpy.types.PropertyGroup):
    has_connected: bpy.props.BoolProperty(name="Connected")
    bind_port: bpy.props.IntProperty(
        name="Bind Port",
        default=14999,
        max=65535,
        min=0
    )
    source_armature_type: bpy.props.EnumProperty(
        name="Armature Type",
        description="Choose an option for [Auto Armature Map]'s source armature type",
        items=[
            ('OPTION_VRM', "VRM-like",
             "VRM-like 24-joints Armature: VRoid(.vrm) or MMD(.pmx) or [mixamo fbx] or [Unity Mecanim]"),
            ('OPTION_METAHUMAN', "MetaHuman-like", "Unreal MetaHuman Armature"),
        ]
    )
    source_armature = bpy.props.StringProperty(
        name='Armature Source'
    )


def register_types():
    bpy.types.Object.meocap_auto_map_source_armature = bpy.props.StringProperty(
        name='Armature Source'
    )

    bpy.types.Scene.meocap_bone_map = bpy.props.PointerProperty(type=MeocapRetargetMap)

    bpy.types.Scene.meocap_state = bpy.props.PointerProperty(type=MeocapState)

