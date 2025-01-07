import os
import sys

import bpy


def open_url(url):
    if sys.platform == "win32":  # Windows
        os.system(f"start {url}")
    elif sys.platform == "darwin":  # macOS
        os.system(f"open {url}")
    elif sys.platform == "linux" or sys.platform == "linux2":  # Linux
        os.system(f"xdg-open {url}")
    else:
        print("Unsupported OS")


class MeocapOpenURL(bpy.types.Operator):
    bl_idname = 'meocap.open_plugins'
    bl_label = 'Update Available!!!'

    def execute(self, ctx):
        open_url("https://www.meocap.com/plugin")
        return {'FINISHED'}
