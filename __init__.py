# -*- coding: UTF-8 -*-
bl_info = {
    "name": "💝L4D2 Character Tools",
    "author": "Merami",
    "version": (1, 0 , 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > 💝",
    "description": "A plugin designed to enhance the efficiency of creating Left 4 Dead 2 character mods.",
    "doc_url" : "",
    "tracker_url" : "https://space.bilibili.com/42971",
    "category": "3D View",
}

import bpy
from . import vrd
from . import jigglebone
from . import flex
from . import bone_modify
from .resources import bone_dict
from bpy.app import translations

class L4D2_PT_GeneralTools(bpy.types.Panel):
    bl_label = "🛠️ General Tools"
    bl_idname = "L4D2_PT_CharacterToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝"

    def draw(self, context):
        layout = self.layout
        # 使用 split 布局类型调整左右列的宽度比例
        split = layout.split(factor=0.25)
        col_left = split.column()
        col_right = split.column()
        # 在左列添加标签
        col_left.label(text="Valve Rig:")
        col_left.label(text="Custom Rig:")
        # 下拉框
        col_right.prop_search(context.scene, "Valve_Armature", bpy.data, "armatures", text="")
        col_right.prop_search(context.scene, "Custom_Armature", bpy.data, "armatures", text="", icon="MOD_ARMATURE")

        bone_modify.L4D2_PT_BoneModifyPanel.draw(self, context)

        row = layout.row()
        row.operator("l4d2.remove_constraint", text="Remove All Constraint", icon="X").action = 'REMOVE_ALL'
        # row.operator("l4d2.remove_constraint", text="Cancel Y RotationConstraint", icon="X").action = 'REMOVE_ROT_Y'
        row.operator("l4d2.remove_constraint", text="Remove TransformConstraint", icon="X").action = 'REMOVE_TRANS'
        row = layout.row()
        row.operator("l4d2.rename_bones_operator", icon="GREASEPENCIL")

        layout.prop(context.scene, "bl_is_detailed", text="Bone Mapping Management", icon="TRIA_DOWN" if context.scene.bl_is_detailed else "TRIA_RIGHT")

        if context.scene.bl_is_detailed:
            bone_modify.VIEW3D_PT_CustomBoneDictManager.draw(self, context)

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
            
        row = layout.row()
        split = layout.split(factor=0.25)
        col_left = split.column()
        col_right = split.column()
        # 在左列添加标签
        col_left.scale_y = 2
        col_left.operator("l4d2.merge_vertex_groups")
        if context.active_object is not None:
            # 创建两个下拉框，用于选择要合并的顶点组
            col_right.prop_search(context.scene, "vertex_group_name_1", context.active_object, "vertex_groups", text="", icon="RADIOBUT_ON")
            col_right.prop_search(context.scene, "vertex_group_name_2", context.active_object, "vertex_groups", text="", icon="RADIOBUT_OFF")



class L4D2_PT_VRDTools(bpy.types.Panel):
    bl_label = "🕹️ VRD Tools"
    bl_idname = "L4D2_PT_VRDToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝"
    bl_options = {'DEFAULT_CLOSED'} 
    def draw(self, context):
        layout = self.layout
        vrd.L4D2_PT_VRDPanel.draw(self, context)

class L4D2_PT_JiggleBoneTools(bpy.types.Panel):
    bl_label = "🪄 JiggleBone Tools"
    bl_idname = "L4D2_PT_jiggleboneToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝"
    bl_options = {'DEFAULT_CLOSED'} 
    def draw(self, context):
        layout = self.layout
        jigglebone.JigglebonePanel.draw(self, context)

class L4D2_PT_FlexTools(bpy.types.Panel):
    bl_label = "😇 Flex Tools"
    bl_idname = "L4D2_PT_shapekeyToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝"
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
    

# 定义操作类
class L4D2_OT_MergeVertexGroups(bpy.types.Operator):
    bl_idname = "l4d2.merge_vertex_groups"
    bl_label = "Merge Vertex Group"
    bl_description = "Merge the weight of the vertex group in the second column into the vertex group in the first column\nsuitable for special cases where there is no bone, but the vertex group has weight"
    def execute(self, context):
        # 获取当前选中的物体
        obj = context.active_object

        # 获取顶点组
        vertex_group_1 = obj.vertex_groups[context.scene.vertex_group_name_1]
        vertex_group_2 = obj.vertex_groups[context.scene.vertex_group_name_2]

        # 遍历物体的顶点
        for vertex in obj.data.vertices:
            # 获取顶点在顶点组2中的权重
            try:
                weight_2 = vertex_group_2.weight(vertex.index)
            except RuntimeError:
                weight_2 = 0.0

            # 如果顶点在顶点组2中有权重，则将权重添加到顶点组1
            if weight_2 > 0.0:
                vertex_group_1.add([vertex.index], weight_2, 'ADD')

        # 删除顶点组2
        obj.vertex_groups.remove(vertex_group_2)

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
    L4D2_OT_MergeVertexGroups,
    L4D2_MT_SelectBonesMenu,
    L4D2_OT_select_pattern,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vertex_group_name_1 = bpy.props.StringProperty(name="Vertex Group 1")
    bpy.types.Scene.vertex_group_name_2 = bpy.props.StringProperty(name="Vertex Group 2")
    bpy.types.Object.select_pattern = bpy.props.StringProperty(default="*hair*")
    bpy.types.Scene.bl_is_detailed = bpy.props.BoolProperty(name="详细信息", default=False)
    bone_modify.register()
    vrd.register()
    jigglebone.register()
    flex.register()
    from .translation import translation_dict
    translations.register(bl_info['name'], translation_dict)

def unregister():
    translations.unregister(bl_info['name'])
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.vertex_group_name_1
    del bpy.types.Scene.vertex_group_name_2
    del bpy.types.Object.select_pattern
    bone_modify.unregister()
    vrd.unregister()
    flex.unregister()
