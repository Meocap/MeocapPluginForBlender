import json
import os
import threading

import bpy
import requests

version = "0.0.0"
latest_version = "0.0.0"

try:
    fn = os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs"), "latest.json")
    with open(fn, 'r', encoding='utf-8') as f:
        data = json.load(f)
    version = data['version']
except:
    pass


def fetch_version_json():
    global latest_version
    response = requests.get("https://meocap-plugin-files.oss-cn-beijing.aliyuncs.com/plugins/blender/docs/latest.json")
    latest_version = response.json()["version"]


threading.Thread(target=fetch_version_json).start()


def get_armature_bones(ctx):
    armature_obj = bpy.data.objects.get(ctx.scene.meocap_state.source_armature)
    bones = []
    if armature_obj and armature_obj.type == 'ARMATURE':
        # 获取骨架中的所有骨骼
        bone_names = [bone.name for bone in armature_obj.data.bones]
        print(f"骨架 '{ctx.scene.meocap_state.source_armature}' 中的骨骼名称列表:")

        bones = [(n, n, "Armature Bone Object") for n in bone_names]

    return bones if bones else [("NONE", "None", "No armature available")]


class MeocapPanel(bpy.types.Panel):
    bl_idname = 'meocap_panel'
    bl_label = 'Meocap Performer'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MEOCAP"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bones = [
            "Pelvis(Hips)", "L_UpperLeg", "R_UpperLeg", "Spine", "L_LowerLeg", "R_LowerLeg",
            "Chest", "L_Foot", "R_Foot", "UpperChest", "L_Toes", "R_Toes",
            "Neck", "L_Shoulder", "R_Shoulder", "Head", "L_UpperArm", "R_UpperArm",
            "L_LowerArm", "R_LowerArm", "L_Hand", "R_Hand", "L_Palm", "R_Palm",
        ]
        self.bones_map = ['' for _ in range(24)]
        self.center_bone = [0, 3, 6, 9, 12, 15]
        self.left_bone = [1, 4, 7, 10, 13, 16, 18, 20]
        self.right_bone = [2, 5, 8, 11, 14, 17, 19, 21]
        self.side_names = [self.bones[i][2:] for i in self.left_bone]
        self.version = version
        self.latest_version = latest_version

    def draw(self, ctx):
        layout = self.layout
        col = layout.column()

        row = col.row(align=True)
        row.label(text=bpy.app.translations.pgettext_iface("Now plugin version: ") + self.version)
        row = col.row(align=True)
        row.label(text=bpy.app.translations.pgettext_iface("Latest plugin version: ") + self.latest_version)

        if self.latest_version != self.version:
            row = col.row(align=True)
            row.operator("meocap.open_plugins", text="Update Available!!!", icon='PINNED')

        row = col.row(align=True)
        row.label(text="Source Port")
        row.prop(ctx.scene.meocap_state, "bind_port")

        row = col.row(align=True)
        row.label(text=f"{bpy.app.translations.pgettext_iface('FrameId')}:{ctx.scene.meocap_state.frame_id}")
        row = col.row(align=True)

        if ctx.scene.meocap_state.has_connected:
            row.operator('meocap.disconnect', text='Disconnect', icon='LINKED')
        else:
            row.operator('meocap.connect', text='Connect', icon='UNLINKED')

        row = col.row(align=True)
        row.label(text="Performer")
        row.prop_search(ctx.scene.meocap_state, "source_armature", ctx.scene, "objects")

        row = col.row(align=True)
        row.label(text="Target FPS")
        row.prop(ctx.scene.meocap_state, "fps_rebuild")

        row = col.row(align=True)
        if ctx.scene.meocap_state.is_recording:
            row.operator('meocap.end_recording', text='End Recording', icon='MODIFIER_OFF')
        else:
            row.operator('meocap.start_recording', text='Start Recording', icon='MODIFIER_ON')

        bone_map = ctx.scene.meocap_bone_map
        if len(bone_map.nodes) == 24:
            row = col.row(align=True)
            row.operator('meocap.load_recording', text='Load Recording to Animation', icon='ANIM_DATA')

        if len(bone_map.nodes) != 24:
            row = col.row(align=True)
            row.operator('meocap.create_retarget_config', text='Create Retarget Config', icon='BONE_DATA')
            return

        if True:
            box = layout.box()
            box.label(text="NOTE: The model's rest pose must be T-POSE")
            box.label(text="Bind Bones", icon='ARMATURE_DATA')
            box.label(text="bones marked with an * are optional.")

            row = box.row(align=True)
            row.operator('meocap.auto_map_bone_vrm_ext', text='Auto Detect Bones(VRM Ext.)', icon='AUTO')

            row = box.row(align=True)
            row.operator('meocap.auto_map_bone_clear', text='Clear Bones', icon='BONE_DATA')

            box.separator()

            row = box.row(align=True)
            row.operator('meocap.import_retarget_config', text='Import Retarget Config', icon='IMPORT')

            row = box.row(align=True)
            row.operator('meocap.export_retarget_config', text='Export Retarget Config', icon='EXPORT')

            row = box.row(align=True)
            column = row.column(align=True)
            column.label(text="Config Preset:")
            column = row.column(align=True)
            column.prop(ctx.scene.meocap_state, "preset_items")
            column = row.column(align=True)
            column.operator('meocap.apply_preset_config', text='Apply', icon='IMPORT')

            row = box.row(align=True)
            column = row.column(align=True)
            column.prop(ctx.scene.meocap_state, "pure_input_mode")
            column = row.column(align=True)
            column.prop(ctx.scene.meocap_state, "lock_transition")
            row = box.row(align=True)
            row.prop(ctx.scene.meocap_state, "scale_trans")
            box.separator()

            row = box.row(align=True).split(factor=0.15, align=True)

            column_label = row.column(align=True)
            column_center = row.column(align=True)

            # column_lock = row.column()

            for i in range(len(self.center_bone)):
                idx = self.center_bone[i]
                name = self.bones[idx]
                column_label.label(text=name)
                if ctx.scene.meocap_state.pure_input_mode:
                    column_center.prop(bone_map.nodes[idx], "name")
                else:
                    column_center.prop_search(bone_map.nodes[idx], "name", bone_map.nodes[idx], "available_bones")
                # column_lock.prop(bone_map.nodes[idx], "lock")

            factor = 0.15
            column = box.column(align=True)
            column.separator()

            split = column.row(align=True).split(factor=factor)
            split.separator()
            row = split.row(align=True)
            row.label(text="Left")
            row.label(text="Right")

            for i in range(len(self.side_names)):
                idx = self.left_bone[i]
                name = self.side_names[i]

                split = column.row(align=True).split(factor=factor, align=True)
                split.label(text=name)
                row = split.row(align=True)

                if ctx.scene.meocap_state.pure_input_mode:
                    row.prop(bone_map.nodes[idx], "name")
                else:
                    row.prop_search(bone_map.nodes[idx], "name", bone_map.nodes[idx], "available_bones")

                # column_left_lock.prop(bone_map.nodes[idx], "lock")

                idx = idx + 1
                if ctx.scene.meocap_state.pure_input_mode:
                    row.prop(bone_map.nodes[idx], "name")
                else:
                    row.prop_search(bone_map.nodes[idx], "name", bone_map.nodes[idx], "available_bones")
