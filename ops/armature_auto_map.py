from enum import Enum, auto
from typing import List, Optional

import bpy
from dataclasses import dataclass, field

from core import MeocapRetargetMap


@dataclass
class BoneChainNode:
    optional: bool
    smpl_idx: int
    parent_idx: Optional[int]
    children: List['BoneChainNode'] = field(default_factory=list)
    parent: Optional['BoneChainNode'] = field(default=None)


class BoneChain:
    def __init__(self, bones: List['BoneChainNode']):
        self.bones: List['BoneChainNode'] = bones
        self.bone_parents: List[Optional[int]] = [b.parent_idx for b in self.bones]

        for bone in self.bones:
            bone.children = []
            bone.parent = None
            if bone.parent_idx is not None:
                bone.parent = self.bones[bone.parent_idx]
                bone.parent.children.append(bone)


VRM_BONE_CHAIN = [
    BoneChainNode(False, 0, None),
    BoneChainNode(False, 1, 0),
    BoneChainNode(False, 2, 0),
    BoneChainNode(False, 3, 0),  # 3
    BoneChainNode(False, 4, 1),
    BoneChainNode(False, 5, 2),
    BoneChainNode(False, 6, 3),
    BoneChainNode(False, 7, 4),
    BoneChainNode(False, 8, 5),
    BoneChainNode(True, 9, 6),
    BoneChainNode(True, 10, 7),
    BoneChainNode(True, 11, 8),
    BoneChainNode(False, 12, 9),
    BoneChainNode(True, 13, 9),
    BoneChainNode(True, 14, 9),
    BoneChainNode(False, 15, 12),
    BoneChainNode(False, 16, 13),
    BoneChainNode(False, 17, 14),
    BoneChainNode(False, 18, 16),
    BoneChainNode(False, 19, 17),
    BoneChainNode(False, 20, 18),
    BoneChainNode(False, 21, 19)
]


class ArmatureAutoMap(bpy.types.Operator):
    bl_idname = "meocap.armature_auto_map"
    bl_label = "Auto Animate Map"
    @classmethod
    def poll(cls, ctx):
        return bpy.data.objects.get(ctx.active_object.meocap_auto_map_source_armature) is not None

    def execute(self, ctx):
        source = bpy.data.objects.get(ctx.active_object.rebocap_source_armature)
        if source and source.type == 'ARMATURE':
            armature_data: bpy.types.Armature = source.data

            def check_bone_node(bone: bpy.types.Bone, expect_node: BoneChainNode):

                if len(expect_node.children) == 2:
                    if not (expect_node.children[0].optional and expect_node.children[1].optional) and len(
                            bone.children) < 2:
                        return False, []
                    for b in bone.children:
                        if b.head.x < 0:
                            for b_peer in bone.children:
                                if b_peer.head.x > 0 and (b_peer.head.x + bone.head.x) < 0.05:
                                    result_l = check_bone_node(b, expect_node.children[0])
                                    result_r = check_bone_node(b_peer, expect_node.children[1])
                                    if result_l and result_r:
                                        return True, result_l[1] + result_r[1] + [(bone.name, expect_node.smpl_idx)]

                    if expect_node.children[0].optional and expect_node.children[1].optional:
                        return True, [(bone.name, expect_node.smpl_idx)]
                    return False, []

                elif len(expect_node.children) == 1:

                    if not expect_node.optional and len(bone.children) < 1:
                        return False, []

                    check_children_results = [check_bone_node(b, expect_node.children[0]) for b in bone.children]

                    if not any([r[0] for r in check_children_results]):
                        if expect_node.children[0].optional:
                            r, l = check_bone_node(bone, expect_node.children[0])
                            if r:
                                return True, l + [(bone.name, expect_node.smpl_idx)]
                        else:
                            return False, []
                    else:
                        return True, [next((r[1] for r in check_children_results if r[0]), None)] + [
                            (bone.name, expect_node.smpl_idx)]

                elif len(expect_node.children) == 0:
                    return True, [(bone.name, expect_node.smpl_idx)]
                else:
                    return False, []

            search_bone_chain = BoneChain(VRM_BONE_CHAIN)

            meocap_bone_map = ctx.scene.meocap_bone_map
            for armature_bone in armature_data.bones:
                ret, map_list = check_bone_node(armature_bone, search_bone_chain.bones[0])
                if ret:
                    meocap_bone_map['version'] = ''
                    print(map_list)
                    return {'FINISHED'}


        return {'FINISHED'}