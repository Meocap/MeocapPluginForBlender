from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from ..core import MeocapState, MeocapRetargetMap
    from ..ops import PoseManager


class SceneVars:
    meocap_state: 'MeocapState'
    meocap_bone_map: 'MeocapRetargetMap'


class GlobalStore:
    pose_manager: 'PoseManager'

    def scene(self,ctx) -> SceneVars:
        return ctx.scene

    def pose_manager(self) -> 'PoseManager':
        return self.pose_manager


_store = None


def glb() -> GlobalStore:
    global _store
    if _store is None:
        _store = GlobalStore()
    return _store
