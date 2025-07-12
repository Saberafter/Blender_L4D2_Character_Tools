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
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > 💝LCT",
    "description": "A plugin designed to enhance the efficiency of creating Left 4 Dead 2 character mods.",
    "doc_url" : "",
    "tracker_url" : "https://space.bilibili.com/42971",
    "category": "3D View",
}

import bpy
import logging
import sys
from . import vrd
from . import weights
from . import jigglebone
from . import flex
from . import bone_modify
# from . import bone_mapping
from .resources import bone_dict
import requests
import json
from threading import Thread
from bpy.app.translations import pgettext_iface as _

# 重定向Blender控制台输出的类
class NullWriter:
    def write(self, string):
        pass

class UpdateChecker:
    def __init__(self):
        self._has_update = False
        self._latest_version = None
        self._download_url = None
        self._release_notes = None  # 添加发布说明
        
    def check_for_update(self):
        try:
            api_url = "https://api.github.com/repos/Saberafter/Blender_L4D2_Character_Tools/releases/latest"
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = tuple(map(int, data['tag_name'].replace('v', '').split('.')))
                current_version = bl_info['version']
                
                self._latest_version = latest_version
                self._download_url = data['html_url']
                self._release_notes = data['body']  # 获取发布说明
                self._has_update = latest_version > current_version
                
        except Exception as e:
            print(f"Update check failed: {str(e)}")
    
    @property
    def release_notes(self):
        return self._release_notes
            
    @property
    def has_update(self):
        return self._has_update
        
    @property
    def latest_version(self):
        return self._latest_version
        
    @property
    def download_url(self):
        return self._download_url

# 创建更新检查器实例
update_checker = UpdateChecker()

def parse_markdown(text):
    """简单的 Markdown 解析"""
    if not text:
        return []
    
    lines = []
    for line in text.split('\n'):
        # 移除 Markdown 标记符号但保留缩进结构
        line = line.strip()
        # 处理标题
        if line.startswith('# '):
            line = line[2:]
        elif line.startswith('## '):
            line = '  ' + line[3:]
        elif line.startswith('### '):
            line = '    ' + line[4:]
        # 处理列表
        elif line.startswith('- '):
            line = '• ' + line[2:]
        elif line.startswith('* '):
            line = '• ' + line[2:]
        elif line.startswith('1. '):
            line = line[3:]  # 保留数字列表的数字
            
        if line:  # 只添加非空行
            lines.append(line)
    
    return lines

class L4D2_OT_CheckUpdate(bpy.types.Operator):
    bl_idname = "l4d2.check_update"
    bl_label = "Check for updates"
    bl_description = "Check if there is a new version of the plugin"
    
    _timer = None
    _checking = False
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            if not self._checking:
                self._checking = True
                update_checker.check_for_update()
                
                def draw_popup(self, context):
                    layout = self.layout
                    layout.scale_y = 0.7
                    
                    if update_checker.has_update:
                        current_ver = '.'.join(map(str, bl_info['version']))
                        new_ver = '.'.join(map(str, update_checker.latest_version))
                        
                        col = layout.column(align=True)
                        col.label(text=_("Update Available!"), icon='INFO')
                        col.label(text=_("Current version:") + f" v{current_ver}")
                        col.label(text=_("Latest version:") + f" v{new_ver}")
                        
                        layout.separator(factor=0.5)
                        col = layout.column(align=True)
                        col.label(text=_("Update Notes:"), icon='TEXT')
                        
                        release_notes = update_checker.release_notes or "No update notes available"
                        parsed_notes = parse_markdown(release_notes)
                        
                        for line in parsed_notes:
                            col.label(text=line)
                        
                        layout.separator(factor=0.5)
                        row = layout.row()
                        row.scale_y = 1.2
                        props = row.operator("wm.url_open", text=_("Go to download page"), icon='URL')
                        props.url = update_checker.download_url
                    else:
                        col = layout.column(align=True)
                        col.label(text=_("You are using the latest version"), icon='INFO')
                        col.label(text=_("Current version:") + f" v{'.'.join(map(str, bl_info['version']))}")

                bpy.context.window_manager.popup_menu(draw_popup, 
                    title=_("Update Available!") if update_checker.has_update else _("Version Check"))
                
                if self._timer:
                    context.window_manager.event_timer_remove(self._timer)
                return {'FINISHED'}
                
        return {'PASS_THROUGH'}
    
    def execute(self, context):
        if not self._timer:
            self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        return {'CANCELLED'}
    
    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)

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

class L4D2_PT_BoneTools(bpy.types.Panel):
    bl_label = "🦴 Bone Tools"
    bl_idname = "L4D2_PT_CharacterToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"
    bl_options = {'DEFAULT_CLOSED'} 
    
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
        row.operator("l4d2.remove_constraint", text="Remove TransformConstraint", icon="X").action = 'REMOVE_TRANS'
        
        row = layout.row()
        row.operator("l4d2.rename_bones_operator", icon="GREASEPENCIL")
        row = layout.row()
        row.operator("l4d2.unbind_keep_shape", icon="CONSTRAINT_BONE")

        # 骨骼映射管理折叠面板
        layout.prop(context.scene, "bone_mapping_management", text="Bone Mapping Management", icon="TRIA_DOWN" if context.scene.bone_mapping_management else "TRIA_RIGHT")

        # 如果展开，则显示骨骼映射UI
        if context.scene.bone_mapping_management:
            box = layout.box()
            col = box.column()
            
            # 预设操作按钮
            row = col.row(align=True)
            
            # 使用当前预设名称作为下拉菜单的显示文本
            row.operator_menu_enum("l4d2.select_preset", "preset_name", text=context.scene.active_preset_name)
            
            # 预设管理按钮
            row.operator("l4d2.create_preset", icon="ADD", text="").preset_name = context.scene.active_preset_name
            row.operator("l4d2.import_preset", icon="IMPORT", text="")
            row.operator("l4d2.export_preset", icon="EXPORT", text="").preset_name = context.scene.active_preset_name
            row.operator("l4d2.delete_preset", icon="X", text="").preset_name = context.scene.active_preset_name
            
            col.separator()
            
            # 标签页
            row = col.row()
            row.prop(context.scene, "mapping_ui_tab", expand=True)
            
            # UI列表
            row = col.row()
            row.template_list("BONE_UL_MappingList", "", context.scene, "mapping_list",
                             context.scene, "mapping_list_index", rows=5)
            
            # 底部按钮
            row = col.row()
            row.operator("mapping.add_new_mapping")
            row.operator("mapping.apply_changes")

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

class L4D2_PT_UtilityTools(bpy.types.Panel):
    bl_label = "⚙️ Utilities"
    bl_idname = "L4D2_PT_UtilityToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"
    bl_options = {'DEFAULT_CLOSED'} 
    
    def draw(self, context):
        layout = self.layout
        # 添加更新检查按钮
        row = layout.row()
        row.operator("l4d2.check_update", icon="FILE_REFRESH")
        if update_checker.has_update:
            row = layout.row()
            row.label(text=_("New version available:") + f" {'.'.join(map(str, update_checker.latest_version))}")
            row.operator("wm.url_open", text=_("Download"), icon="URL").url = update_checker.download_url

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
        # 只检查是否有活动对象且是骨架
        return (context.active_object is not None and
                context.active_object.type == 'ARMATURE')

    def execute(self, context):
        armature = context.active_object
        
        # 记录原始模式
        original_mode = armature.mode
        
        # 切换到姿态模式
        if original_mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        
        # 根据action类型执行不同操作
        try:
            if self.action == 'REMOVE_ALL':
                # 检查是否有约束
                has_constraints = False
                for bone in armature.pose.bones:
                    if bone.constraints:
                        has_constraints = True
                        break
                        
                if not has_constraints:
                    self.report({'ERROR'}, "没有找到约束")
                    return {'CANCELLED'}
                    
                # 移除所有约束
                count = self._remove_all_constraints(armature)
                self.report({'INFO'}, f"已移除 {count} 个约束")
                
            elif self.action == 'REMOVE_TRANS':
                # 检查是否有选中的骨骼
                if not context.selected_pose_bones:
                    self.report({'ERROR'}, "未选择骨骼")
                    return {'CANCELLED'}
                    
                # 检查选中的骨骼是否有变换约束
                has_transform = False
                for bone in context.selected_pose_bones:
                    if any(c.type == 'TRANSFORM' for c in bone.constraints):
                        has_transform = True
                        break
                        
                if not has_transform:
                    self.report({'ERROR'}, "没有找到约束")
                    return {'CANCELLED'}
                    
                # 移除变换约束
                count = self._remove_transform_constraints(context.selected_pose_bones)
                self.report({'INFO'}, f"已移除 {count} 个变换约束")
                
            return {'FINISHED'}
                
        finally:
            # 无论操作成功还是失败，都恢复到原始模式
            if original_mode != 'POSE':
                bpy.ops.object.mode_set(mode=original_mode)
            else:
                bpy.ops.object.mode_set(mode='OBJECT')  # 姿态模式特殊处理为返回物体模式
    
    def _remove_all_constraints(self, armature):
        """移除所有约束并返回移除数量"""
        count = 0
        for bone in armature.pose.bones:
            for constraint in bone.constraints[:]:
                bone.constraints.remove(constraint)
                count += 1
        return count

    def _remove_transform_constraints(self, selected_bones):
        """移除选中骨骼的变换约束并返回移除数量"""
        count = 0
        for bone in selected_bones:
            to_be_removed = [c for c in bone.constraints if c.type == 'TRANSFORM']
            for constraint in to_be_removed:
                bone.constraints.remove(constraint)
                count += 1
        return count

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
    L4D2_PT_BoneTools,
    L4D2_PT_VRDTools,
    L4D2_PT_JiggleBoneTools,
    L4D2_PT_FlexTools,
    L4D2_PT_UtilityTools,
    L4D2_OT_RemoveConstraint,
    L4D2_OT_SelectBones,
    L4D2_MT_SelectBonesMenu,
    L4D2_OT_select_pattern,
    L4D2_OT_CheckUpdate,
]


def register():
    # 临时禁止控制台输出
    old_stdout = sys.stdout
    sys.stdout = NullWriter()
    
    # 先注册其他模块，使用try-except抑制消息输出
    try:
        bone_modify.register()
    except Exception as e:
        pass
    try:
        vrd.register()
    except Exception as e:
        pass
    try:
        jigglebone.register()
    except Exception as e:
        pass
    try:
        flex.register()
    except Exception as e:
        pass
    try:
        weights.register()
    except Exception as e:
        pass
    # bone_mapping.register()
    
    # 然后注册本模块的类
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            # 抑制重复注册的错误消息
            pass

    # 最后注册属性
    bpy.types.Scene.vertex_group_name_1 = bpy.props.StringProperty(name="Vertex Group 1")
    bpy.types.Scene.vertex_group_name_2 = bpy.props.StringProperty(name="Vertex Group 2")
    bpy.types.Object.select_pattern = bpy.props.StringProperty(default="*hair*")
    bpy.types.Scene.bone_mapping_management = bpy.props.BoolProperty(
        name="Bone Mapping Management",
        description="Bone Mapping Management",
        default=False
    )
    
    # 确保骨骼映射所需的属性已注册 (由bone_modify模块处理)
    if not hasattr(bpy.types.Scene, "mapping_ui_tab"):
        bpy.types.Scene.mapping_ui_tab = bpy.props.EnumProperty(
            name="映射显示",
            description="选择要显示的映射类型",
            items=[
                ('ALL', "全部映射", "显示所有类型的映射关系"),
                ('UNIQUE', "独立映射", "只显示独立于通用映射的自定义映射"),
                ('COMMON', "通用映射", "只显示通用骨骼到自定义骨骼的映射"),
                ('AXIS', "轴控制", "管理官方骨骼的轴向约束设置")
            ],
            default='ALL',
            update=bone_modify.MappingDataManager.update_mapping_list
        )
    
    if not hasattr(bpy.types.Scene, "active_preset_name"):
        bpy.types.Scene.active_preset_name = bpy.props.StringProperty(
            name="当前预设",
            default="Valve_L4D2"
        )
    
    if not hasattr(bpy.types.Scene, "use_search_mode"):
        bpy.types.Scene.use_search_mode = bpy.props.BoolProperty(
            name="搜索模式",
            default=False
        )
    
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
    try:
        if bpy.app.version < (4, 0, 0):
            lct_zh_CN.register()
        else:
            lct_zh_CN.register()
            lct_zh_HANS.register()
    except Exception as e:
        pass
        
    # 恢复标准输出
    sys.stdout = old_stdout

def unregister():
    # 先移除翻译
    try:
        if bpy.app.version < (4, 0, 0):
            lct_zh_CN.unregister()
        else:
            lct_zh_CN.unregister()
            lct_zh_HANS.unregister()
    except:
        pass

    # 移除属性
    try:
        if hasattr(bpy.types.Scene, "vertex_group_name_1"):
            del bpy.types.Scene.vertex_group_name_1
        if hasattr(bpy.types.Scene, "vertex_group_name_2"):
            del bpy.types.Scene.vertex_group_name_2
        if hasattr(bpy.types.Object, "select_pattern"):
            del bpy.types.Object.select_pattern
        if hasattr(bpy.types.Scene, "bone_mapping_management"):
            del bpy.types.Scene.bone_mapping_management
            
        # 移除骨骼映射相关属性（但这些属性通常由bone_modify模块管理）
        if hasattr(bpy.types.Scene, "mapping_ui_tab"):
            del bpy.types.Scene.mapping_ui_tab
        if hasattr(bpy.types.Scene, "active_preset_name"):
            del bpy.types.Scene.active_preset_name
        if hasattr(bpy.types.Scene, "use_search_mode"):
            del bpy.types.Scene.use_search_mode
            
        if hasattr(bpy.types.Scene, "Valve_Armature"):
            del bpy.types.Scene.Valve_Armature
        if hasattr(bpy.types.Scene, "Custom_Armature"):
            del bpy.types.Scene.Custom_Armature
    except:
        pass

    # 注销本模块的类
    for cls in reversed(classes):
        try:
            if hasattr(cls, 'bl_rna'):
                bpy.utils.unregister_class(cls)
        except:
            pass

    # 最后注销其他模块
    try:
        bone_modify.unregister()
    except:
        pass
    try:
        vrd.unregister()
    except:
        pass
    try:
        flex.unregister()
    except:
        pass
    try:
        weights.unregister()
    except:
        pass
    # bone_mapping.unregister()
    try:
        jigglebone.unregister()
    except:
        pass
