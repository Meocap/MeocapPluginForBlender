import bpy

class MeocapPanel(bpy.types.Panel):
    bl_idname = 'meocap_panel'
    bl_label = 'Connection'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MEOCAP"

    def draw(self, ctx):
        layout = self.layout
        col = layout.column()
        row = col.row(align=True)
        row.label(text="Port")
        row.prop(ctx.scene.meocap_state, "bind_port")
        row = col.row(align=True)
        row.label(text='Source Type')
        row.prop(ctx.scene.meocap_state, 'source_armature_type', text='')

        source = bpy.data.objects.get(ctx.active_object.meocap_states.source_armature)
        if source and source.type == 'ARMATURE':
            row = col.row(align=True)
            row.operator('meocap.armature_auto_map', text='Auto Detect', icon='BONE_DATA')
            col = layout.column()
            box = layout.box()
            box.label(text="Bind Bones",icon='ARMATURE_DATA')

            row = box.row(align=True).sp
