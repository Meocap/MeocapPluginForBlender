import bpy

class CreateRetargetConfig(bpy.types.Operator):
    bl_idname = "meocap.create_retarget_config"
    bl_label = "Create Retarget Config"

    def execute(self,ctx):
        print("Executing Init Retarget Config")
        if len(ctx.scene.meocap_bone_map.nodes) != 24:
            for i in range(24):
                new_node = ctx.scene.meocap_bone_map.nodes.add()
                new_node.name = f""
                new_node.lock = False
        return {'FINISHED'}
