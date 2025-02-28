import struct
import os
import sys
from typing import List

import mathutils

from .sdk import MeoFrame,Joint

addon_libs_path = os.path.join(os.path.dirname(__file__), "libs")
if addon_libs_path not in sys.path:
    sys.path.append(addon_libs_path)
from .universal_pb2 import Frame


class BinaryReader:
    def __init__(self, data: bytes):
        self.data = data
        self.position = 0

    def read_uint32(self) -> int:
        length = self.data[self.position:self.position + 4]
        self.position += 4
        return struct.unpack('>I', length)[0]

    def bytes(self) -> bytes:
        length = self.read_uint32()
        value = self.data[self.position:self.position + length]
        self.position += length
        return value

    def eof(self):
        return self.position >= len(self.data)


TRACKER_ATTRS = ["left_lower_arm", "right_lower_arm", "left_lower_leg", "right_lower_leg", "head", "hips",
                 "left_upper_arm", "right_upper_arm", "left_upper_leg", "right_upper_leg", "chest"]
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

class FrameReader:

    def __init__(self):
        self.frames = []

    def decode_recordings(self, file_path) -> List[MeoFrame]:
        self.frames = []
        with open(file_path, "rb") as f:
            data = f.read()

        reader = BinaryReader(data)
        i = 0
        while not reader.eof():
            frame_data = reader.bytes()
            frame = Frame()
            frame.ParseFromString(frame_data)
            joints = []
            for attr in POSE_ATTRS:
                loc_rot = getattr(frame.optimized_pose, attr)
                glb_rot = getattr(frame.glb_opt_pose, attr)
                pos = getattr(frame.joint_positions, attr)
                joints.append(Joint(
                    loc_rot=mathutils.Quaternion(mathutils.Vector([loc_rot.w, loc_rot.i, -loc_rot.k, loc_rot.j])),
                    glb_rot=mathutils.Quaternion(mathutils.Vector([glb_rot.w, glb_rot.i, -glb_rot.k, glb_rot.j])),
                    pos=[pos.x,pos.y,pos.z]
                ))
            meo_frame = MeoFrame(
                frame_id=frame.frame_id,
                translation=mathutils.Vector((frame.translation.x, frame.translation.y, frame.translation.z)),
                src=None,
                joints=joints,
                timestamp=i*(1000/60)
            )
            i = i + 1
            self.frames.append(meo_frame)

        return self.frames
