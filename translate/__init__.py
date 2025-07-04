import ast
import re

import bpy

from . import zh_CN


def get_language_list():
    try:
        bpy.context.preferences.view.language = ""
    except TypeError as e:
        matches = re.findall(r'\(([^()]*)\)', e.args[-1])
        return ast.literal_eval(f"({matches[-1]})")


class TranslationHelper:
    def __init__(self, name: str, data: dict, lang='zh_CN'):
        self.name = name
        self.translations_dict = dict()

        for src, src_trans in data.items():
            key = ("Operator", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans
            key = ("*", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans

    def register(self):
        bpy.app.translations.register(self.name, self.translations_dict)

    def unregister(self):
        bpy.app.translations.unregister(self.name)


translate = None


def register():
    global translate

    language = "zh_CN"
    all_language = get_language_list()
    if language not in all_language:
        if language == "zh_CN":
            language = "zh_HANS"
        elif language == "zh_HANS":
            language = "zh_CN"
    translate = TranslationHelper(f"MeocapPluginForBlender_{language}", zh_CN.data, lang=language)
    translate.register()


def unregister():
    global translate
    translate.unregister()
    translate = None
