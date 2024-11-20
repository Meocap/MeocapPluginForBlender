import socket
import json
from dataclasses import dataclass, field
from typing import List, Optional
import mathutils  # Blender's built-in math library


@dataclass
class AnyClass:
    pass


@dataclass
class UniversalFrame:
    frame_id: int
    raw_pose: List[float]
    optimized_pose: List[float]
    glb_opt_pose: List[float]
    translation: List[float]
    joint_positions: List[float]
    joint_velocity: List[float]
    contact: List[float]
    extra_result: Optional[List[AnyClass]]


@dataclass
class SkelJoint:
    pos: List[float]  # 3 elements


@dataclass
class SkelBase:
    bones: List[SkelJoint]  # 24 elements
    floor_y: float


@dataclass
class Joint:
    pos: List[float]  # 3 elements
    glb_rot: List[float]  # 4 elements (quaternion)
    loc_rot: List[float]  # 4 elements (quaternion)


@dataclass
class Addr:
    a: int
    b: int
    c: int
    d: int
    port: int

    def to_socket_addr(self):
        return (f'{self.a}.{self.b}.{self.c}.{self.d}', self.port)

    @classmethod
    def from_socket_addr(cls, socket_addr):
        ip, port = socket_addr
        a, b, c, d = map(int, ip.split('.'))
        return cls(a, b, c, d, port)


@dataclass
class MeoFrame:
    frame_id: int
    translation: List[float]  # 3 elements
    joints: List[Joint]  # 24 elements
    src: Addr
    left_joints: List[Joint] = field(default_factory=list)
    right_joints: List[Joint] = field(default_factory=list)


class Status:
    def __init__(self, ty, info):
        self.ty = ty
        self.info = info


class ErrorType:
    NONE = 0
    SOCKET = 1
    INVALID_PARAMETER = 2
    DATA_CORRUPTED = 3


class MeocapSDK:
    def __init__(self, addr: Addr):
        self.socket = None
        self.addr = addr

    def bind(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(self.addr.to_socket_addr())
            self.socket.settimeout(0.25)
        except socket.error as e:
            return Status(ErrorType.SOCKET, e.errno)
        return Status(ErrorType.NONE, 0)

    def send_skel(self, skel: SkelBase):
        try:
            data = json.dumps({"SetSkel": skel}).encode('utf-8')
            self.socket.sendto(data, self.addr.to_socket_addr())
        except Exception as e:
            return Status(ErrorType.SOCKET, str(e))
        return Status(ErrorType.NONE, 0)

    def recv_frame(self) -> Optional[MeoFrame]:
        try:
            data, src = self.socket.recvfrom(65536)
            frame_json = json.loads(data.decode('utf-8'))
            frame = UniversalFrame(**frame_json)

            meo_frame = MeoFrame(
                frame_id=frame.frame_id,
                translation=frame.translation,
                joints=[Joint([0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]) for _ in range(24)],
                src=Addr.from_socket_addr(src)
            )

            for i in range(24):
                rot = frame.glb_opt_pose[i * 9:(i + 1) * 9]
                pos = frame.joint_positions[i * 3:(i + 1) * 3]
                rot_matrix = mathutils.Matrix()
                rot_matrix[0][0:3] = rot[0], rot[1], rot[2]
                rot_matrix[1][0:3] = rot[3], rot[4], rot[5]
                rot_matrix[2][0:3] = rot[6], rot[7], rot[8]
                r_glb = rot_matrix.to_quaternion()
                meo_frame.joints[i].pos = pos
                meo_frame.joints[i].glb_rot = [r_glb.x, r_glb.y, r_glb.z, r_glb.w]

                rot = frame.glb_opt_pose[i*9:(i+1)*9]
                rot_matrix = mathutils.Matrix()
                rot_matrix[0][0:3] = rot[0], rot[1], rot[2]
                rot_matrix[1][0:3] = rot[3], rot[4], rot[5]
                rot_matrix[2][0:3] = rot[6], rot[7], rot[8]
                r_loc = rot_matrix.to_quaternion()
                meo_frame.joints[i].loc_rot = [r_loc.x, r_loc.y, r_loc.z, r_loc.w]
            return meo_frame
        except Exception as e:
            return None


    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None
        return Status(ErrorType.NONE, 0)

# Example usage in Blender:
# addr = Addr(127, 0, 0, 1, 8080)
# connection = UdpConnection(addr)
# status = connection.bind()
# if status.ty == ErrorType.NONE:
#     frame = connection.recv_frame()
#     if frame:
#         print(f"Received frame {frame.frame_id}")
# connection.close()
