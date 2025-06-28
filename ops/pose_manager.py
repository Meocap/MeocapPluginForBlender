import json
from typing import Optional, List

import bpy
import mathutils

from ..glb import glb
from ..meocap_sdk import MeocapSDK, Addr, ErrorType, FrameReader, MeoFrame, Joint


class PoseBone:
    def __init__(self, idx):
        self.idx = idx
        self.rest_matrix_to_world = mathutils.Matrix.Identity(4).to_quaternion()
        self.rest_matrix_from_world = mathutils.Matrix.Identity(4).to_quaternion()


class PoseRootBone:
    def __init__(self):
        self.name = ""
        self.matrix_global_2_root_inverse = mathutils.Matrix.Identity(4)
        self.matrix_root_2_hip_inverse = mathutils.Matrix.Identity(4)
        self.matrix_global_hip = mathutils.Matrix.Identity(4)
        self.offset = mathutils.Vector([0, 0, 0])


def fill_all_pose(rots: List[mathutils.Quaternion], bone_names: List[str]):
    if bone_names[3] != "" or bone_names[6] != "" or bone_names[9] != "":
        if bone_names[3] == "":
            rots[6] = rots[3] @ rots[6]
        if bone_names[6] == "" and bone_names[9] != "":
            rots[3] = rots[3] @ rots[6] @ rots[9]
        elif bone_names[6] == "":
            rots[9] = rots[6] @ rots[9]
        elif bone_names[9] == "":
            rots[6] = rots[6] @ rots[9]
    if bone_names[13] == "" and bone_names[16] != "":
        rots[16] = rots[13] @ rots[16]
    if bone_names[14] == "" and bone_names[17] != "":
        rots[17] = rots[14] @ rots[17]
    return rots


class PoseManager:
    def __init__(self):
        self.sdk = MeocapSDK(addr=Addr(a=127, b=0, c=0, d=1, port=14999))
        self.bones = [PoseBone(index) for index in range(24)]
        self.trans_offset = mathutils.Vector([0, 0, 0])
        self.has_connected = False
        self.has_init_bones = False
        self.recordings = []
        self.root = PoseRootBone()
        self.target_framerate = 60
        self.last_recording_interval: float = 0
        self.last_frame: Optional[MeoFrame] = None

    def connect(self, port) -> bool:
        self.sdk.addr.port = port
        if self.sdk.bind().ty != ErrorType.NONE:
            return False
        self.has_connected = True
        return True

    def close(self):
        self.sdk.close()
        self.has_connected = False

    def init_bones(self, ctx):
        nodes = ctx.scene.meocap_bone_map.nodes
        source_obj = ctx.scene.meocap_state.source_armature
        if source_obj is None:
            return
        if not len(nodes) == 24:
            return

        scene_obj_matrix_world = mathutils.Matrix.Identity(4)
        for obj in bpy.context.scene.objects:
            if obj.name == source_obj.name and obj.type == 'ARMATURE':
                scene_obj_matrix_world = obj.matrix_world
                # print(f"Found Scene Object: {obj.name}")
                break

        for i in range(22):
            node_name = nodes[i].name
            if node_name != "":
                pose_bone = source_obj.pose.bones.get(node_name)
                data_bone = source_obj.data.bones.get(node_name)
                if (data_bone is not None) and (pose_bone is not None):
                    pose_bone.rotation_mode = 'QUATERNION'
                    self.bones[
                        i].rest_matrix_to_world = scene_obj_matrix_world.to_quaternion() @ data_bone.matrix_local.to_quaternion()
                    self.bones[i].rest_matrix_from_world = self.bones[i].rest_matrix_to_world.inverted()
                    if i == 0:
                        cur_root_bone = data_bone
                        while cur_root_bone.parent is not None:
                            cur_root_bone = cur_root_bone.parent
                        self.root.name = cur_root_bone.name
                        self.root.matrix_root_2_hip_inverse = (
                                cur_root_bone.matrix_local.inverted() @ data_bone.matrix_local).inverted()
                        self.root.matrix_global_2_root_inverse = (
                                scene_obj_matrix_world @ cur_root_bone.matrix_local).inverted()
                        self.root.matrix_global_hip = scene_obj_matrix_world @ data_bone.matrix_local

                        self.trans_offset = mathutils.Vector(
                            [self.root.matrix_global_hip.translation.x, self.root.matrix_global_hip.translation.y,
                             self.root.matrix_global_hip.translation.z])

        self.has_init_bones = True

    def get_scale(self, ctx):
        scene = glb().scene(ctx)
        scale = 1.0
        if scene.meocap_state.scale_trans == "100x":
            scale = 100.0
        elif scene.meocap_state.scale_trans == "0.01x":
            scale = 0.01
        return scale

    def recv_and_perform(self, ctx):
        source_obj = ctx.scene.meocap_state.source_armature
        if source_obj is None:
            return
        if not self.has_init_bones:
            self.init_bones(ctx)

        scene_obj_matrix_world = mathutils.Matrix.Identity(4)
        for obj in bpy.context.scene.objects:
            if obj.name == source_obj.name and obj.type == 'ARMATURE':
                scene_obj_matrix_world = obj.matrix_world
                # print(f"Found Scene Object: {obj.name}")
                break

        if self.has_init_bones:
            frame = self.sdk.get_last_frame()
            if frame is not None:

                scene = glb().scene(ctx)
                scale = self.get_scale(ctx)
                rec = self.get_new_record(ctx, frame)

                if scene.meocap_state.is_recording:
                    if rec is not None:
                        self.recordings.append(rec)

                if rec is None:
                    return

                nodes = scene.meocap_bone_map.nodes
                scene.meocap_state.frame_id = frame.frame_id
                bone_names = [n.name for n in nodes]

                loc_rots = [j.loc_rot for j in frame.joints]
                loc_rots = fill_all_pose(loc_rots, bone_names)
                trans = frame.translation

                for i in range(22):
                    perform_bone = source_obj.pose.bones.get(bone_names[i])
                    if perform_bone is not None:
                        perform_bone.rotation_mode = 'QUATERNION'
                        new_pose = self.bones[i].rest_matrix_from_world @ loc_rots[i] @ self.bones[
                            i].rest_matrix_to_world
                        perform_bone.rotation_quaternion = new_pose
                        if i == 0 and self.root.name != '':
                            root_bone = source_obj.pose.bones.get(self.root.name)
                            if (root_bone is not None) and (not scene.meocap_state.lock_transition):
                                new_global_hip: mathutils.Matrix = self.root.matrix_global_hip
                                new_global_hip.translation = trans + self.trans_offset
                                new_local_matrix = self.root.matrix_global_2_root_inverse @ new_global_hip @ self.root.matrix_root_2_hip_inverse
                                new_local_matrix.translation *= scale
                                root_bone.location = new_local_matrix.translation

    def get_new_record(self, ctx, frame) -> Optional[MeoFrame]:
        scene = glb().scene(ctx)
        target_fps = float(scene.meocap_state.fps_rebuild)
        target_interval = 1000 / target_fps
        if target_fps < 60:
            if self.last_frame is not None:

                if frame.timestamp < self.last_frame.timestamp:
                    self.last_frame = frame
                    return frame

                if self.last_recording_interval > target_interval:
                    self.last_recording_interval = 0
                    self.last_frame = frame
                    return None

                new_interval = self.last_recording_interval + frame.timestamp - self.last_frame.timestamp
                if new_interval >= target_interval:
                    tick_time = target_interval - self.last_recording_interval
                    slerp_t = tick_time / (frame.timestamp - self.last_frame.timestamp)

                    new_joints = [
                        Joint(
                            pos=frame.joints[i].pos,
                            loc_rot=self.last_frame.joints[i].loc_rot.slerp(frame.joints[i].loc_rot, slerp_t),
                            glb_rot=frame.joints[i].glb_rot
                        )
                        for i in range(24)
                    ]

                    new_frame = MeoFrame(
                        frame_id=frame.frame_id,
                        src=frame.src,
                        joints=new_joints,
                        timestamp=frame.timestamp,
                        translation=self.last_frame.translation + (
                                frame.translation - self.last_frame.translation) * slerp_t
                    )

                    self.last_frame = frame
                    self.last_recording_interval = new_interval % target_interval
                    return new_frame

                else:
                    self.last_frame = frame
                    self.last_recording_interval = new_interval
            else:
                self.last_frame = frame
                self.last_recording_interval = 0
                return frame
        else:
            return frame

    def load_recording(self, ctx, path, frames):
        self.start_recording()
        for frame in frames:
            if frame is not None:
                rec = self.get_new_record(ctx, frame)
                if rec is not None:
                    self.recordings.append(rec)
        self.end_recording(ctx)

    def start_recording(self):
        self.recordings = []

    def end_recording(self, ctx):
        self.load_frames(ctx, "Meocap Recording", self.recordings)

    def load_frames(self, ctx, path, frames: List[MeoFrame]):
        bone_names = [n.name for n in glb().scene(ctx).meocap_bone_map.nodes]

        source_obj = ctx.scene.meocap_state.source_armature
        if source_obj is None:
            return
        action = bpy.data.actions.new(name=path)
        scale = self.get_scale(ctx)

        data_paths = ['pose.bones["%s"].rotation_quaternion' % n if n != "" else "" for n in bone_names]
        curves = [[action.fcurves.new(data_path=p, index=i) for i in range(4)] if p != "" else None for p in data_paths]
        for c in curves:
            if c is not None:
                for a in c:
                    a.keyframe_points.add(len(frames))

        if not self.has_init_bones:
            self.init_bones(ctx)

        for frame_i, frame in enumerate(frames):
            loc_rots = [j.loc_rot for j in frame.joints]
            loc_rots = fill_all_pose(loc_rots, bone_names)
            for i in range(22):
                if curves[i] is not None:
                    new_pose = self.bones[i].rest_matrix_from_world @ loc_rots[i] @ self.bones[i].rest_matrix_to_world
                    for axis in range(4):
                        curves[i][axis].keyframe_points[frame_i].co = (
                            frame_i,
                            new_pose[axis]
                        )
        # translation
        root_bone_name = self.root.name
        root_data_path = 'pose.bones["%s"].location' % root_bone_name
        trans_curves = [action.fcurves.new(data_path=root_data_path, index=i) for i in range(3)]

        for c in trans_curves:
            c.keyframe_points.add(len(frames))

        scene = glb().scene(ctx)
        if not scene.meocap_state.lock_transition:
            for frame_i, frame in enumerate(frames):
                trans = frame.translation
                trans = [trans.x, trans.y, trans.z]
                for axis in range(3):
                    trans_curves[axis].keyframe_points[frame_i].co = (
                        frame_i,
                        trans[axis]
                    )

        source_obj.animation_data_create()
        source_obj.animation_data.action = action


pose_manager: Optional[PoseManager] = None
meocap_timer = None


def create_pose_manager():
    global pose_manager
    pose_manager = PoseManager()
    return pose_manager


def stop_all():
    global pose_manager
    pose_manager.close()


class MeocapConnect(bpy.types.Operator):
    bl_idname = 'meocap.connect'
    bl_label = 'Connect'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init()

    def init(self):
        pass

    def execute(self, ctx):
        global pose_manager
        if (pose_manager is not None) and (pose_manager.has_connected is False):
            scene = glb().scene(ctx)
            if not pose_manager.connect(scene.meocap_state.bind_port):
                return {'CANCELLED'}
            global meocap_timer
            ctx.window_manager.modal_handler_add(self)
            meocap_timer = ctx.window_manager.event_timer_add(1 / 60, window=ctx.window)
            scene.meocap_state.has_connected = True
            return {'RUNNING_MODAL'}

        return {'CANCELLED'}

    def modal(self, ctx, evt):
        global pose_manager
        if not pose_manager.has_connected:
            return {'PASS_THROUGH'}
        pose_manager.recv_and_perform(ctx)
        return {'PASS_THROUGH'}


class MeocapDisconnect(bpy.types.Operator):
    bl_idname = 'meocap.disconnect'
    bl_label = 'Disconnect'

    def execute(self, ctx):
        scene = glb().scene(ctx)
        pose_manager.close()
        global meocap_timer
        ctx.window_manager.event_timer_remove(meocap_timer)
        scene.meocap_state.has_connected = False
        return {'FINISHED'}


POSE_ATTRS = [
    "pelvis",  # 骨盆
    "left_hip",  # 左大腿
    "right_hip",  # 右大腿
    "spine1",  # 第一腰椎骨
    "left_knee",  # 左膝盖
    "right_knee",  # 右膝盖
    "spine2",  # 第二腰椎骨
    "left_ankle",  # 左脚踝
    "right_ankle",  # 右脚踝
    "spine3",  # 第三腰椎骨
    "left_foot",  # 左脚
    "right_foot",  # 右脚
    "neck",  # 脖子
    "left_clavicle",  # 左肩胛骨
    "right_clavicle",  # 右肩胛骨
    "head",  # 头
    "left_shoulder",  # 左肩
    "right_shoulder",  # 右肩
    "left_elbow",  # 左肘
    "right_elbow",  # 右肘
    "left_wrist",  # 左手腕
    "right_wrist",  # 右手腕
    "left_hand",  # 左手
    "right_hand"  # 右手
]


class MeocapLoadRecording(bpy.types.Operator):
    bl_idname = "meocap.load_recording"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.meorecording",  # 这里设置默认扩展名限制
        options={'HIDDEN'}
    )

    def execute(self, ctx):

        try:
            rd = FrameReader()
            frames = rd.decode_recordings(self.filepath)
            text = bpy.app.translations.pgettext_iface("Read Meocap Recording file: %s with %i frames")
            self.report({'INFO'}, text % (self.filepath, len(frames)))
            pose_manager.load_recording(ctx, self.filepath, frames)



        except Exception as e:
            text = bpy.app.translations.pgettext_iface("Failed to Read file: %s")
            self.report({'ERROR'}, text % str(e))
        return {'FINISHED'}

    def invoke(self, ctx, event):
        ctx.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MeocapStartRecording(bpy.types.Operator):
    bl_idname = "meocap.start_recording"
    bl_label = "Start"

    def execute(self, ctx):
        glb().scene(ctx).meocap_state.is_recording = True
        global pose_manager
        pose_manager.start_recording()
        return {'FINISHED'}


class MeocapEndRecording(bpy.types.Operator):
    bl_idname = "meocap.end_recording"
    bl_label = "End"

    def execute(self, ctx):
        glb().scene(ctx).meocap_state.is_recording = False
        global pose_manager
        pose_manager.end_recording(ctx)
        return {'FINISHED'}


class MeocapImportRetargetConfig(bpy.types.Operator):
    bl_idname = "meocap.import_retarget_config"
    bl_label = "Import"
    bl_options = {'REGISTER', 'UNDO'}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.meoretarget",  # 这里设置默认扩展名限制
        options={'HIDDEN'}
    )

    def execute(self, ctx):

        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                bone_names = json.load(file)
                if len(bone_names) == 24:
                    for i, n in enumerate(glb().scene(ctx).meocap_bone_map.nodes):
                        n.name = bone_names[i]
            text = bpy.app.translations.pgettext_iface("Open Meocap Retarget file: %s")
            self.report({'INFO'}, text % self.filepath)
        except Exception as e:
            text = bpy.app.translations.pgettext_iface("Failed to Open file: %s")
            self.report({'ERROR'}, text % str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, ctx, event):
        ctx.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MeocapExportRetargetConfig(bpy.types.Operator):
    bl_idname = "meocap.export_retarget_config"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(
        default="*.meoretarget",  # 这里设置默认扩展名限制
        options={'HIDDEN'}
    )

    def execute(self, ctx):
        if not self.filepath.endswith(".meoretarget"):
            self.filepath += ".meoretarget"
        bone_names = [n.name for n in glb().scene(ctx).meocap_bone_map.nodes]
        try:
            with open(self.filepath, "w+", encoding="utf-8") as file:
                json.dump(bone_names, file, ensure_ascii=False, indent=4)
            text = bpy.app.translations.pgettext_iface("Save Meocap Retarget file: %s")
            self.report({'INFO'}, text % self.filepath)
        except Exception as e:
            text = bpy.app.translations.pgettext_iface("Failed to Save file: %s")
            self.report({'ERROR'}, text % str(e))
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, ctx, event):
        ctx.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
