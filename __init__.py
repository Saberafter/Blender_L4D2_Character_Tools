# Copyright (C) <2024> <Merami>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: UTF-8 -*-
bl_info = {
    "name": "💝L4D2 Character Tools",
    "author": "Merami",
    "version": (1, 0 , 4),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > 💝LCT",
    "description": "A plugin designed to enhance the efficiency of creating Left 4 Dead 2 character mods.",
    "doc_url" : "",
    "tracker_url" : "https://space.bilibili.com/42971",
    "category": "3D View",
}

import bpy
from . import vrd
from . import weights
from . import jigglebone
from . import flex
from . import bone_modify
from . import weights
from .resources import bone_dict


class TranslationHelper():
    def __init__(self, name: str, data: dict, lang='zh_CN'):
        self.name = name
        self.translations_dict = dict()

        for src, src_trans in data.items():
            key = ("Operator", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans
            key = ("*", src)
            self.translations_dict.setdefault(lang, {})[key] = src_trans

    def register(self):
        try:
            bpy.app.translations.register(self.name, self.translations_dict)
        except(ValueError):
            pass

    def unregister(self):
        bpy.app.translations.unregister(self.name)

from . import translation

lct_zh_CN = TranslationHelper('lct_zh_CN', translation.data)
lct_zh_HANS = TranslationHelper('lct_zh_HANS', translation.data, lang='zh_HANS')

class L4D2_PT_GeneralTools(bpy.types.Panel):
    bl_label = "🛠️ General Tools"
    bl_idname = "L4D2_PT_CharacterToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # 使用 split 布局类型调整左右列的宽度比例
        split = layout.split(factor=0.25)
        col_left = split.column()
        col_right = split.column()
        # 在左列添加标签
        col_left.label(text="Valve Rig:")
        col_left.label(text="Custom Rig:")
        # 下拉框
        col_right.prop(scene, "Valve_Armature", text="", icon="ARMATURE_DATA")

        col_right.prop(scene, "Custom_Armature", text="", icon="MOD_ARMATURE")


        bone_modify.L4D2_PT_BoneModifyPanel.draw(self, context)

        row = layout.row()
        row.operator("l4d2.remove_constraint", text="Remove All Constraint", icon="X").action = 'REMOVE_ALL'
        # row.operator("l4d2.remove_constraint", text="Cancel Y RotationConstraint", icon="X").action = 'REMOVE_ROT_Y'
        row.operator("l4d2.remove_constraint", text="Remove TransformConstraint", icon="X").action = 'REMOVE_TRANS'
        row = layout.row()
        row.operator("l4d2.rename_bones_operator", icon="GREASEPENCIL")
        row = layout.row()
        row.operator("l4d2.unbind_keep_shape", icon="CONSTRAINT_BONE")

        layout.prop(context.scene, "bone_mapping_management", text="Bone Mapping Management", icon="TRIA_DOWN" if context.scene.bone_mapping_management else "TRIA_RIGHT")

        if context.scene.bone_mapping_management:
            bone_modify.VIEW3D_PT_CustomBoneDictManager.draw(self, context)
        
        weights.L4D2_PT_WeightsPanel.draw(self, context)
        
        row = layout.row()
        row.menu("L4D2_MT_select_bones_menu", icon="DOWNARROW_HLT")
        
        if context.object:  
            split = layout.split(factor=0.25)
            col_left = split.column()
            col_right = split.column()
            col_left.operator("select.by_pattern")
            col_right.prop(context.object, 'select_pattern', text="")
        else:
            row = layout.row()
            row.operator("select.by_pattern")
            


class L4D2_PT_VRDTools(bpy.types.Panel):
    bl_label = "🕹️ VRD Tools"
    bl_idname = "L4D2_PT_VRDToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"
    bl_options = {'DEFAULT_CLOSED'} 
    def draw(self, context):
        layout = self.layout
        vrd.L4D2_PT_VRDPanel.draw(self, context)

class L4D2_PT_JiggleBoneTools(bpy.types.Panel):
    bl_label = "🪄 JiggleBone Tools"
    bl_idname = "L4D2_PT_jiggleboneToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"
    bl_options = {'DEFAULT_CLOSED'} 
    def draw(self, context):
        layout = self.layout
        jigglebone.JigglebonePanel.draw(self, context)

class L4D2_PT_FlexTools(bpy.types.Panel):
    bl_label = "😇 Flex Tools"
    bl_idname = "L4D2_PT_shapekeyToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"
    bl_options = {'DEFAULT_CLOSED'} 
    def draw(self, context):
        layout = self.layout
        flex.L4D2_PT_ShapeKeyPanel.draw(self, context)

class L4D2_OT_RemoveConstraint(bpy.types.Operator):
    bl_idname = "l4d2.remove_constraint"
    bl_label = "Remove Bone Constraint"
    bl_description = "Bulk Remove Constraints from Selected Bones"
    action: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.active_object.type == 'ARMATURE' and
                context.active_object.mode == 'POSE')

    def execute(self, context):
        # 根据action的值，调用不同的函数
        if self.action == 'REMOVE_ALL':
            return self.remove_all_constraints(context)
        elif self.action == 'REMOVE_ROT_Y':
            return self.remove_rotation_constraint_y(context)
        elif self.action == 'REMOVE_TRANS':
            return self.remove_transform_constraints(context)

    def remove_all_constraints(self, context):
        armature = context.active_object
        for bone in armature.pose.bones:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)
        return {'FINISHED'}

    def remove_rotation_constraint_y(self, context):
        obj = context.object
        for bone in context.selected_pose_bones:
            for constraint in bone.constraints:
                if constraint.type == 'COPY_ROTATION':
                    constraint.use_y = False
                    print("已移除骨骼", bone.name, "的旋转约束中的Y轴约束")
        return {'FINISHED'}

    def remove_transform_constraints(self, context):
        obj = context.object
        for bone in context.selected_pose_bones:
            to_be_removed = [c for c in bone.constraints if c.type == 'TRANSFORM']
            for constraint in to_be_removed:
                bone.constraints.remove(constraint)
                print("已删除骨骼", bone.name, "的变换约束")
        return {'FINISHED'}

class L4D2_OT_SelectBones(bpy.types.Operator):
    bl_idname = "l4d2.select_bones"
    bl_label = "选择骨骼"
    bl_description = "Select bones according to the bone set defined in the dictionary"

    action: bpy.props.StringProperty()

    def execute(self, context):
        armature = context.active_object
        if armature and armature.type == 'ARMATURE':
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')

            bones_to_select = set()
            if self.action == 'valve':
                bones_to_select.update(bone_dict.bone_mapping.keys())
            elif self.action == 'custom':
                for bone_list in bone_dict.bone_mapping.values():
                    bones_to_select.update(bone_list)

            keywords = set()
            if self.action in {'jigglebone', 'skirt', 'hair'}:
                excluded_bones = set(bone_dict.bone_mapping.keys())
                for bone_list in bone_dict.bone_mapping.values():
                    excluded_bones.update(bone_list)

                if self.action == 'jigglebone':
                    keywords.update(bone_dict.Jigglebone_list)
                    keywords.update(bone_dict.skirt_list)
                    keywords.update(bone_dict.hair_list)
                elif self.action == 'skirt':
                    keywords.update(bone_dict.skirt_list)
                elif self.action == 'hair':
                    keywords.update(bone_dict.hair_list)

                for bone in armature.pose.bones:
                    if any(keyword.lower() in bone.name.lower() for keyword in keywords):
                        if bone.name not in excluded_bones:
                            bones_to_select.add(bone.name)

            for bone_name in bones_to_select:
                bone = armature.pose.bones.get(bone_name)
                if bone:
                    bone.bone.select = True

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='POSE')

            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "当前活动对象不是骨架。")
            return {'CANCELLED'}

class L4D2_OT_select_pattern(bpy.types.Operator):
    bl_idname = "select.by_pattern"
    bl_label = "Select by pattern"
    bl_description = "By default, turn off case distinction and turn on merge selection"

    def execute(self, context):
        # 根据输入框的内容选择物体
        bpy.ops.object.select_pattern(pattern=context.object.select_pattern)
        return {'FINISHED'}

class L4D2_MT_SelectBonesMenu(bpy.types.Menu):
    bl_idname = "L4D2_MT_select_bones_menu"
    bl_label = "Bone Quick Select"

    def draw(self, context):
        layout = self.layout

        layout.operator('l4d2.select_bones', text="Valve Bone").action = 'valve'
        layout.operator('l4d2.select_bones', text="Custom Bone").action = 'custom'
        layout.operator('l4d2.select_bones', text="Jiggle Bone").action = 'jigglebone'
        layout.operator('l4d2.select_bones', text="Skirt Bone").action = 'skirt'
        layout.operator('l4d2.select_bones', text="Hair Bone").action = 'hair'


classes = [
    L4D2_PT_GeneralTools,
    L4D2_PT_VRDTools,
    L4D2_PT_JiggleBoneTools,
    L4D2_PT_FlexTools,
    L4D2_OT_RemoveConstraint,
    L4D2_OT_SelectBones,
    L4D2_MT_SelectBonesMenu,
    L4D2_OT_select_pattern,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vertex_group_name_1 = bpy.props.StringProperty(name="Vertex Group 1")
    bpy.types.Scene.vertex_group_name_2 = bpy.props.StringProperty(name="Vertex Group 2")
    bpy.types.Object.select_pattern = bpy.props.StringProperty(default="*hair*")
    bpy.types.Scene.bone_mapping_management = bpy.props.BoolProperty(
        name="Bone Mapping Management",
        description="Bone Mapping Management",
        default=False
    )
    bone_modify.register()
    vrd.register()
    jigglebone.register()
    flex.register()
    weights.register()
    bpy.types.Scene.Valve_Armature = bpy.props.PointerProperty(
        name="Valve Armature",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    bpy.types.Scene.Custom_Armature = bpy.props.PointerProperty(
        name="Custom Armature",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

    # 翻译
    if bpy.app.version < (4, 0, 0):
        lct_zh_CN.register()
    else:
        lct_zh_CN.register()
        lct_zh_HANS.register()

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vertex_group_name_1
    del bpy.types.Scene.vertex_group_name_2
    del bpy.types.Object.select_pattern
    bone_modify.unregister()
    vrd.unregister()
    flex.unregister()
    weights.unregister()
    # 翻译
    if bpy.app.version < (4, 0, 0):
        lct_zh_CN.unregister()
    else:
        lct_zh_CN.unregister()
        lct_zh_HANS.unregister()
