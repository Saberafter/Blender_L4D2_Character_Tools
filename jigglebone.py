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

import bpy
import os
import json
import re
from .resources import jiggleparams_presets 
from bpy.props import FloatProperty, FloatVectorProperty, BoolProperty, EnumProperty, StringProperty, CollectionProperty, IntProperty, PointerProperty


# 针对is_flexible参数创建列表
flexible_params = [
    # ('参数名称', 参数类型, 参数初始值),
    ('length', FloatProperty, 0),
    ('tip_mass', FloatProperty, 200),
    ('pitch_stiffness', FloatProperty, 50),
    ('pitch_damping', FloatProperty, 7),
    ('pitch_constraint', FloatVectorProperty, (0.0, 0.0), 2),
    ('pitch_friction', FloatProperty, 0),
    ('yaw_stiffness', FloatProperty, 50),
    ('yaw_damping', FloatProperty, 7),
    ('yaw_constraint', FloatVectorProperty, (0.0, 0.0), 2), 
    ('yaw_friction', FloatProperty, 0),
    ('allow_length_flex', BoolProperty), 
    ('along_stiffness', FloatProperty, 100),
    ('along_damping', FloatProperty, 0),
    ('angle_constraint', FloatProperty, 0)
]

# 针对has_base_spring参数创建列表
base_params = [
    ('stiffness', FloatProperty, 0),
    ('damping', FloatProperty, 0),
    ('left_constraint', FloatVectorProperty, (-0.3, 0.3), 2),
    ('left_friction', FloatProperty, 0),
    ('up_constraint', FloatVectorProperty, (-0.3, 0.3), 2),
    ('up_friction', FloatProperty, 0),
    ('forward_constraint', FloatVectorProperty, (-0.3, 0.3), 2),
    ('forward_friction', FloatProperty, 0),
    ('base_mass', FloatProperty, 0)
]


preset_dir = os.path.join(bpy.utils.resource_path('USER'), 'scripts', 'presets', 'L4D2 Character Tools')
json_path = os.path.join(preset_dir,"jiggleparams_presets.json")
jigglebone_preset_dict={}

# 定义飘骨列表
jigglebone_list = []

def get_params_for_menu(param_list):
    return [(param[0], param[0], '') for param in param_list]

# 生成全部可能选择的参数枚举列表
def get_selectable_params(self, context):
    selectable_params = []
    selectable_params.extend(get_params_for_menu(flexible_params))
    selectable_params.extend(get_params_for_menu(base_params))
    return selectable_params

# 写入json预设文件
def write_json():
    if not os.path.exists(preset_dir):
        os.makedirs(preset_dir)
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(jigglebone_preset_dict, f, ensure_ascii=False, indent=4)
    
def read_json():
    global jigglebone_preset_dict
    if not os.path.isdir(preset_dir):
        os.makedirs(preset_dir)

    if not os.path.exists(json_path):
        print(f"找不到文件: {json_path}，将使用 jiggleparams_presets.py 中的字典并创建一个新的 json 文件。")
        jigglebone_preset_dict = jiggleparams_presets.presets
        write_json()  
    else:
        with open(json_path, 'r', encoding='utf-8') as f:
            jigglebone_preset_dict = json.load(f)


# 调用函数读取或创建json文件
read_json()

# 添加/覆盖预设
def add_preset(name, preset):
    jigglebone_preset_dict[name] = preset  
    write_json()

# 删除预设
def delete_preset(name):
    if name in jigglebone_preset_dict:
        del jigglebone_preset_dict[name]
        write_json()

# 获取预设菜单项
def get_preset_item(self, context):
    preset_items = []
    read_json()
    for preset_name in jigglebone_preset_dict.keys():
        preset_items.append((preset_name, preset_name, ""))
    return preset_items

def update_bone_list_selection(scene, depsgraph):
    # 获取当前的Armature对象
    obj = bpy.context.active_object
    # 检查对象是否为Armature并且处于POSE或EDIT模式
    if obj and obj.type == 'ARMATURE' and obj.mode in {'POSE', 'EDIT'}:
        armature = obj
        # 获取自定义骨骼列表
        jigglebone_list = scene.jigglebone_list
        # 更新骨骼的选中状态
        selected_indices = []  # 创建一个列表来存储选中骨骼的索引
        for index, jigglebone_item in enumerate(jigglebone_list):
            if bone := armature.data.bones.get(jigglebone_item.name):
                jigglebone_item.selected = bone.select
                if bone.select:
                    selected_indices.append(index)  # 将选中骨骼的索引添加至列表
        scene['selected_bones_indices'] = selected_indices  # 将索引列表存储于场景属性中，用于之后跳转

class Jigglebone_OT_AddPreset(bpy.types.Operator):
    bl_idname = "jigglebone.add_preset"
    bl_label = "Add/Overwrite Preset"
    bl_options = {'REGISTER', 'UNDO'}

    # 新增属性：预设的名字
    name: StringProperty(
        name="Preset Name",
        description="The name of the new preset. If this name is the same as an existing preset, the existing preset will be overwritten",
        default="New Preset"
    ) 

    # 新增方法：在弹出窗口中绘制属性
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'name', text="Preset Name")

    def execute(self, context):
        scene = context.scene
        bone = scene.jigglebone_list[scene.jigglebone_list_index]

        preset = dict()

        # 存储主要的开关状态
        preset['is_flexible'] = bone.is_flexible
        preset['has_base_spring'] = bone.has_base_spring

        # 参数列表待处理
        params = [(flexible_params, bone.is_flexible), (base_params, bone.has_base_spring)]
        for param_list, condition in params:
            if condition:
                # 如果开关打开
                for param_tuple in param_list:
                    name = param_tuple[0]
                    enable_name = 'enable_' + name
                
                    # 保存开关状态
                    if hasattr(bone, enable_name):
                        enable_value = getattr(bone, enable_name)
                        preset[enable_name] = enable_value

                    # 检查属性是否存在
                    if hasattr(bone, name):
                        # 获取参数值
                        value = getattr(bone, name)

                        # 保存参数值
                        if isinstance(value, bpy.types.bpy_prop_array):
                            value = list(value)
                        preset[name] = value
        
        # save generated preset into json file
        add_preset(self.name, preset)
        return {"FINISHED"}

    def invoke(self, context, event):
        # 当操作被调用时，弹出一个包含属性的对话窗口
        return context.window_manager.invoke_props_dialog(self)

class Jigglebone_OT_DeletePreset(bpy.types.Operator):
    bl_idname = "jigglebone.delete_preset"
    bl_label = "Delete Preset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        selected_preset_name = scene.jigglebone_presets.temp_preset_name
        
        delete_preset(selected_preset_name)  # 删除选中预设
        
        preset_names = list(jigglebone_preset_dict.keys())  # 获取所有预设的名称
      
        # 如果存在预设，就将第一个预设设为当前选中预设
        if preset_names:
            scene.jigglebone_presets.temp_preset_name = preset_names[0]
        
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
class Jigglebone_OT_ApplyPreset(bpy.types.Operator):
    bl_idname = "jigglebone.apply_preset"
    bl_label = "Apply Preset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        jigglebone_list = scene.jigglebone_list

        # 从新的 PresetPropertyGroup 中获取选中的预设名称
        selected_preset_name = scene.jigglebone_presets.temp_preset_name

        # 获取当前选中的骨骼
        bone_index = scene.jigglebone_list_index
        if bone_index < len(jigglebone_list):
            current_bone = jigglebone_list[bone_index]

            # 检查是否有骨骼被选中，适用于批量操作
            selected_bones = [bone for bone in jigglebone_list if bone.selected or (bone == current_bone and selected_preset_name)]

            for bone in selected_bones:
                if selected_preset_name in jigglebone_preset_dict:
                    preset = jigglebone_preset_dict[selected_preset_name]
                    bone.preset_name = selected_preset_name  # 更新骨骼的preset_name
                    for key, value in preset.items():
                        setattr(bone, key, value)
                else:
                    self.report({'ERROR'}, f"预设'{selected_preset_name}'不存在")
                    return {'CANCELLED'}
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "没有选中任何骨骼。")
            return {'CANCELLED'}
    
class PresetPropertyGroup(bpy.types.PropertyGroup):
    temp_preset_name: EnumProperty(items=get_preset_item) 

# 创建一个Jigglebone的PropertyGroup集合
class JigglebonePropertyGroup(bpy.types.PropertyGroup):
        name: StringProperty(name="骨骼名称") 
        selected: BoolProperty(name="选择切换", default=False, update=lambda self, context: JigglebonePropertyGroup.update_selection(self, context)) 

        is_flexible: BoolProperty(name="is_flexible", default=False) 
        has_base_spring: BoolProperty(name="has_base_spring", default=False) 
        # 用 for 循环生成参数
        for param in flexible_params + base_params:
            name = param[0]
            type_ = param[1]

            # 添加默认参数
            if type_ is FloatVectorProperty:
                default = param[2]
                size = param[3]
                exec(f'{name}: type_(name="{name}", default=default, size=size)')
            elif type_ is FloatProperty or type_ is IntProperty:
                default = param[2]
                exec(f'{name}: type_(name="{name}", default=default)')
            elif type_ is BoolProperty:
                continue

        # 然后，为每个参数创建对应的开关
        for param in flexible_params + base_params:
            name = param[0]
            exec(f'enable_{name}: BoolProperty(name="Enable {name}", default=False)')


        @staticmethod
        def update_selection(self, context):
            armature = context.active_object
            if armature is not None and armature.type == 'ARMATURE':
                if context.mode == 'POSE':
                    pose_bone = armature.pose.bones.get(self.name)
                    if pose_bone is not None:
                        pose_bone.bone.select = self.selected
                elif context.mode == 'EDIT_ARMATURE':
                    edit_bone = armature.data.edit_bones.get(self.name)
                    if edit_bone is not None:
                        edit_bone.select = self.selected

# 插件面板
class JigglebonePanel(bpy.types.Panel):
    bl_label = "L4D2 Jigglebone Tools"
    bl_idname = "L4D2_PT_jigglebone"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        scene = context.scene
        jigglebone_list = scene.jigglebone_list
        presets = scene.jigglebone_presets  # 独立的预设

        layout = self.layout
        row = layout.row()
        left = row.column_flow(columns=1, align=True)
        box = left.box().row()

        # 创建全选/反选二合一的按钮和反选按钮
        box_left = box.row(align=True)
        if jigglebone_list:
            # 判断是否全部选中
            if all(item.selected for item in jigglebone_list):
                box_left.operator('jigglebone.select_action', text='', emboss=False, icon='CHECKBOX_HLT').action = 'NONE'
            else:
                box_left.operator('jigglebone.select_action', text='', emboss=False, icon='CHECKBOX_DEHLT').action = 'ALL'
                if any(item.selected for item in jigglebone_list):
                    # 判断是否有选中项
                    box_left.operator('jigglebone.select_action', text='', emboss=False, icon='UV_SYNC_SELECT').action = 'INVERSE'
        box_right = box.row(align=False)
        box_right.alignment = 'LEFT'
        #box_right.operator('jigglebone.normal_rotate', text='法向旋转', icon='DRIVER_ROTATIONAL_DIFFERENCE')
        # 创建UIlist列表，展示Jigglebone的集合
        left.template_list("JIGGLEBONE_UL_List", "", scene, "jigglebone_list", scene, "jigglebone_list_index", rows=10)
        # 添加预设按钮
        box_right = left.box().row(align=True) 
        if jigglebone_list:
            bone = context.scene.jigglebone_list[context.scene.jigglebone_list_index]
            box_left.operator("jigglebone.update_selection", icon='FILE_REFRESH', text="")
            box_left.prop(presets, 'temp_preset_name', text='', icon='PRESET', translate=False)
            box_left.operator("jigglebone.apply_preset", text="", icon='IMPORT')
            box_left.operator("jigglebone.add_preset", text="", icon='ADD')
            box_left.operator("jigglebone.delete_preset", text="", icon='REMOVE')
        right = row.column(align=True)
        # 创建添加，删除，清空，上移，下移按钮
        right.scale_x = 1.2  # 保持按钮大小不变
        right.scale_y = 1.33
        right.operator('jigglebone.add_bone', text='', icon='ADD')
        right.operator('jigglebone.remove_bone', text='', icon='REMOVE')
        right.operator('jigglebone.clear_bone', text='', icon='TRASH') 
        right.operator('jigglebone.move_up_bone', text='', icon='TRIA_UP')
        right.operator('jigglebone.move_down_bone', text='', icon='TRIA_DOWN')
        right.separator()
        right.prop(context.scene, "Jigglebone_is_detailed", text="", icon="CURRENT_FILE" if context.scene.Jigglebone_is_detailed else "ASSET_MANAGER")
        right.operator('jigglebone.set_angle', text="", icon='MODIFIER')
        right.operator('jigglebone.apply_from_clipboard', text="", icon='PASTEFLIPDOWN')
        right.operator('jigglebone.import_all_from_clipboard', text="", icon='PASTEFLIPDOWN')
        
        row = layout.row()
        row.prop(context.scene, 'jigglebone_export_path')
        row = layout.row()
        row.operator("jigglebone.export_jigglebone", text="Copy to Clipboard", icon='COPYDOWN').action = 'CLIPBOARD'
        row.operator("jigglebone.export_jigglebone", text="Export to File", icon='FILE_NEW').action = 'FILE'
        row.operator("jigglebone.open_file", text="", icon='CURRENT_FILE').open_type = 'FILE'
        row.operator("jigglebone.open_file", text="", icon='FILE_FOLDER').open_type = 'FOLDER'
        if context.scene.Jigglebone_is_detailed:
            if jigglebone_list and scene.jigglebone_list_index < len(jigglebone_list):
                bone = jigglebone_list[scene.jigglebone_list_index]

                # 外层Box
                main_box = layout.box()
                #main_box.label(text="抖动参数设置", icon='PREFERENCES')
                
                # 将布局切成两部分
                split = main_box.split()

                def draw_param_box(param_list, box_title):
                    box = split.column().box()
                    box.prop(bone, box_title)

                    if getattr(bone, box_title):
                        for param in param_list:
                            name = param[0]
                            row = box.row(align=True)
                            # 用复选框的描述替代之前的单独标签
                            row.prop(bone, f'enable_{name}', text=name, translate=False)
                            
                            # 如果不是BoolProperty，则在同一行绘制值
                            if param[1] is not BoolProperty and getattr(bone, f'enable_{name}'):
                                row.prop(bone, name, text="")
                # 绘制 is_flexible 相关的UI元素
                draw_param_box(flexible_params, 'is_flexible')
                # 绘制 has_base_spring 相关的UI元素
                draw_param_box(base_params, 'has_base_spring')

# 创建UIList
# 定义一个UI列表用于显示骨骼
class JIGGLEBONE_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "selected", text="", emboss=False, icon='CHECKBOX_HLT' if item.selected else 'CHECKBOX_DEHLT')
            row.scale_x = 0.1
            row.label(text = str(index+1)) 
            row.scale_x = 0.9
            row.prop(item, "name", text="", emboss=False, icon='BONE_DATA')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='BONE_DATA')

class Jigglebone_OT_SelectAction(bpy.types.Operator):
    bl_idname = 'jigglebone.select_action'
    bl_label = 'Manipulate the selection state of the list'
    bl_description = 'Select All/Deselect All/Invert Selection\nSynchronize selection with 3D view'
    bl_options = {'UNDO'}

    action: StringProperty(override={'LIBRARY_OVERRIDABLE'}) 

    def execute(self, context):
        jigglebone_list = context.scene.jigglebone_list

        def all():
            for bone in jigglebone_list:
                bone.selected = True
        
        def inverse():
            for bone in jigglebone_list:
                bone.selected = not bone.selected

        def none():
            for bone in jigglebone_list:
                bone.selected = False
            
        ops = {
            'ALL': all,
            'INVERSE': inverse,
            'NONE': none
        }

        ops[self.action]()

        return {'FINISHED'}
        
def update_enable_param(self, context):
    bone = context.scene.jigglebone_list[context.scene.jigglebone_list_index]
    if hasattr(bone, f"enable_{self.target_param}"):
        self.enable_param = getattr(bone, f"enable_{self.target_param}")

class Jigglebone_OT_SetAngle(bpy.types.Operator):
    """Batch customize settings for selected bones"""
    bl_idname = "jigglebone.set_angle"
    bl_label = "Parameter Step Setting"

    enable_param: BoolProperty(name="enable param", default=True, description="enable param")


    min_angle: FloatProperty(
        name="Minimum",
        description="The minimum value of the parameter",
        default=10.0
    ) 
    
    max_angle: FloatProperty(
        name="Maximum",
        description="The maximum value of the parameter",
        default=30.0
    ) 
    
    reverse_order: BoolProperty( 
        name="Reverse",
        description="Decrease parameter values instead of increasing",
        default=False
    ) 

    min_anglex: FloatProperty(
        name="Minimum X",
        description="The X component of the minimum value of the parameter",
        default=0
    ) 

    min_angley: FloatProperty(
        name="Minimum Y",
        description="The Y component of the minimum value of the parameter",
        default=0
    ) 

    max_anglex: FloatProperty(
        name="Maximum X",
        description="The X component of the maximum value of the parameter",
        default=0
    ) 

    max_angley: FloatProperty(
        name="Maximum Y",
        description="The Y component of the maximum value of the parameter",
        default=0
    ) 
    
    # Add optional parameter property
    target_param: EnumProperty(
        name="Target Parameter",
        description="Choose the parameter to be incremented or decremented",
        items=get_selectable_params,
        update=update_enable_param  # 绑定更新函数
    )
    
    def invoke(self, context, event):
        self.target_param = 'angle_constraint'  # 设置默认的参数
        # 根据选择的参数决定 enable_param 的初始状态
        bone = context.scene.jigglebone_list[context.scene.jigglebone_list_index]
        if hasattr(bone, f"enable_{self.target_param}"):
            self.enable_param = getattr(bone, f"enable_{self.target_param}")

        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'target_param', text="Parameter Selection")
        row = layout.row()
        # 如果当前参数为 BoolProperty，则不需要显示数值调整选项
        if self.target_param == "allow_length_flex":
            row = layout.row()
            row.prop(self, 'enable_param', text="Enable/Disable")
        else:
            row = layout.row()
            row.prop(self, 'enable_param', text="Enable/Disable")
            row.prop(self, 'reverse_order')

            param_is_vector = self.target_param in [param[0] for param in flexible_params + base_params if param[1] is FloatVectorProperty]
            
            split = layout.split(factor=0.5)
            col1 = split.column()   
            col2 = split.column()
            if param_is_vector:
                col1.prop(self, "min_anglex")
                col1.prop(self, "max_anglex")

                col2.prop(self, "min_angley")
                col2.prop(self, "max_angley")
            else:
                layout.prop(self, 'min_angle')
                layout.prop(self, 'max_angle')
            


    def execute(self, context):
        selected_bones = [bone for bone in context.scene.jigglebone_list if bone.selected]
        
        if not selected_bones:
            self.report({'ERROR'}, "没有选中的骨骼")
            return {'CANCELLED'}
        
        # 由于 allow_length_flex 是特殊处理的，没有向量属性，所以单独判断
        if self.target_param == "allow_length_flex":
            for bone in selected_bones:
                # 对于 allow_length_flex，只设置它的开关属性 enable_allow_length_flex
                if hasattr(bone, f"enable_{self.target_param}"):
                    setattr(bone, f"enable_{self.target_param}", self.enable_param)
        else:
            # 如果不是 allow_length_flex，继续之前的逻辑
            increment = (self.max_angle - self.min_angle) / (len(selected_bones) - 1) if len(selected_bones) > 1 else 0
            value = self.min_angle

            is_vector_property = self.target_param in [param[0] for param in flexible_params + base_params if param[1] is FloatVectorProperty]
            if is_vector_property:  
                increment_x = (self.max_anglex - self.min_anglex) / (len(selected_bones) - 1) if len(selected_bones) > 1 else 0
                increment_y = (self.max_angley - self.min_angley) / (len(selected_bones) - 1) if len(selected_bones) > 1 else 0
                value_x = self.min_anglex
                value_y = self.min_angley
            
            for index, bone in enumerate(selected_bones):
                if hasattr(bone, f"enable_{self.target_param}"):
                    setattr(bone, f"enable_{self.target_param}", self.enable_param)
                    
                if is_vector_property:  
                    current_value = (value_x + increment_x * index, value_y + increment_y * index)
                    setattr(bone, self.target_param, current_value)
                else:
                    current_value = value + increment * index if not self.reverse_order else self.max_angle - increment * index
                    setattr(bone, self.target_param, current_value)
        
        return {'FINISHED'}

# 创建添加骨骼的操作
class Jigglebone_OT_AddBone(bpy.types.Operator):
    bl_idname = "jigglebone.add_bone"
    bl_label = "Add Jigglebone to the list"
    bl_description = "Supports multiple selection and addition in the 3D view and outline view"

    def execute(self, context):
        scene = context.scene
        selected_bones = []
        
        if context.mode == 'POSE':
            selected_bones = context.selected_pose_bones
        elif context.mode == 'EDIT_ARMATURE':
            selected_bones = context.selected_editable_bones
        elif context.mode == 'OBJECT' and context.active_object and context.active_object.type == 'ARMATURE':
            selected_bones = [bone for bone in context.active_object.data.bones if bone.select]

        if not selected_bones:  # 检查是否选择了骨骼
            self.report({'ERROR'}, "没有选中的骨骼!")  # 如果没有，报错并停止执行操作
            return {'CANCELLED'}

        for b in selected_bones:
            if not any(bone.name == b.name for bone in scene.jigglebone_list):
                bone = scene.jigglebone_list.add()
                bone.name = b.name

        scene.jigglebone_list_index = len(scene.jigglebone_list) - 1

        return {'FINISHED'}

# 创建删除骨骼的操作
class Jigglebone_OT_RemoveBone(bpy.types.Operator):
    bl_idname = "jigglebone.remove_bone"
    bl_label = "Remove selected bones from the list"
    bl_description = "Priority: delete the selected bones in the 3D view first;\nif there are no selected bones, delete the checked items;\nif there are no checked items, delete the highlighted items"

    def execute(self, context):
        scene = context.scene
        list = scene.jigglebone_list
        # 确保 bpy.context.object 不为 None
        if bpy.context.object is None:
            return {'FINISHED'}
        # 获取当前模式
        mode = bpy.context.object.mode

        # 如果在姿态/编辑/对象模式中
        if mode in ['POSE', 'EDIT', 'OBJECT']:
            # 获取选中的骨骼的名字
            selected_bones = [bone.name for bone in bpy.context.object.data.bones if bone.select]
            bones_removed = False
            for bone_name in selected_bones:
                # 如果骨骼在列表中，找到它的索引并删除它
                if bone_name in list:
                    bone_index = list.find(bone_name)
                    list.remove(bone_index)
                    bones_removed = True

            # 如果没有骨骼被删除，那么删除列表中选中的骨骼
            if not bones_removed:
                # 获取所有选中的骨骼
                selected_list_bones = [bone for bone in list if bone.selected]

                # 如果有多个骨骼被选中，对每个骨骼进行删除操作
                if len(selected_list_bones) > 1:
                    # 从后向前遍历，防止删除过程中改变了骨骼的顺序
                    for bone in reversed(selected_list_bones):
                        bone_index = list.find(bone.name)
                        list.remove(bone_index)
                else:  # 如果只有一个骨骼被选中，就像原来那样删除
                    index = scene.jigglebone_list_index
                    list.remove(index)
                    # 更新索引
                    scene.jigglebone_list_index = min(index, len(list) - 1)

        # 更新索引以防止超出范围
        scene.jigglebone_list_index = min(scene.jigglebone_list_index, len(list) - 1)

        return {'FINISHED'}

# 创建清空骨骼的操作
class Jigglebone_OT_ClearBone(bpy.types.Operator):
    bl_idname = "jigglebone.clear_bone"
    bl_label = "Clear the bone list"
    bl_description = "Remove all bones in the list"
    def execute(self, context):
        scene = context.scene
        list = scene.jigglebone_list

        list.clear()

        return {'FINISHED'}

# 创建上移骨骼的操作
class Jigglebone_OT_MoveUpBone(bpy.types.Operator):
    bl_idname = "jigglebone.move_up_bone"
    bl_label = "Move Up"
    bl_description = "Support multi-selection, otherwise only move the selected highlighted bones"
    def execute(self, context):
        scene = context.scene
        list = scene.jigglebone_list
        index = scene.jigglebone_list_index

        # 获取所有选中的骨骼
        selected_bones = [bone for bone in list if bone.selected]

        # 如果有多个骨骼被选中，对每个骨骼进行上移操作
        if len(selected_bones) > 1:
            for bone in selected_bones:
                bone_index = list.find(bone.name)
                if bone_index > 0:  # 如果不是第一个骨骼，就上移
                    list.move(bone_index, bone_index - 1)
        else:  # 如果只有一个骨骼被选中，就像原来那样上移
            list.move(index, index - 1)
            scene.jigglebone_list_index = index - 1

        return {'FINISHED'}

# 创建下移骨骼的操作
class Jigglebone_OT_MoveDownBone(bpy.types.Operator):
    bl_idname = "jigglebone.move_down_bone"
    bl_label = "Move Down"
    bl_description = "Support multi-selection, otherwise only move the selected highlighted bones"
    def execute(self, context):
        scene = context.scene
        list = scene.jigglebone_list

        # 获取所有选中的骨骼
        selected_bones = [bone for bone in list if bone.selected]

        # 如果有多个骨骼被选中，对每个骨骼进行下移操作
        if len(selected_bones) > 1:
            # 从后向前遍历，防止下移过程中改变了骨骼的顺序
            for bone in reversed(selected_bones):
                bone_index = list.find(bone.name)
                if bone_index < len(list) - 1:  # 如果不是最后一个骨骼，就下移
                    list.move(bone_index, bone_index + 1)
        else:  # 如果只有一个骨骼被选中，就像原来那样下移
            index = scene.jigglebone_list_index
            list.move(index, index + 1)
            scene.jigglebone_list_index = index + 1

        return {'FINISHED'}

# 操作符：从剪贴板应用设置
class Jigglebone_OT_ApplyFromClipboard(bpy.types.Operator):
    """Apply a set of floating bone text from the clipboard to the current selection"""
    bl_idname = "jigglebone.apply_from_clipboard"
    bl_label = "Apply jitter parameters from the clipboard (individually)"
    bl_options = {'REGISTER', 'UNDO'}

    def apply_settings_to_bone(self, bone, clipboard):
        # 先关闭所有参数的开关
        bone.is_flexible = False
        bone.has_base_spring = False
        for param in flexible_params + base_params:
            enable_name = 'enable_' + param[0]
            if hasattr(bone, enable_name):
                setattr(bone, enable_name, False)
        
        # 生成参数名称列表
        # flexible_param_names = [param[0] for param in flexible_params]
        # base_param_names = [param[0] for param in base_params]

        # 使用正则表达式匹配剪贴板中的参数，并应用到骨骼
        param_pattern = re.compile(r'(\w+)\s*([\d\s.-]+)?')
        for match in param_pattern.finditer(clipboard):
            name = match.group(1)
            value_str = match.group(2)
            enable_name = 'enable_' + name
            
            # 更新是否灵活和是否有基础弹簧的标志
            if name == 'is_flexible':
                bone.is_flexible = True
                continue  # 跳过下面的赋值步骤
            elif name == 'has_base_spring':
                bone.has_base_spring = True
                continue  # 跳过下面的赋值步骤
            
            # 如果有值，则设置之
            if value_str and hasattr(bone, name):
                value_str = value_str.strip()  # 删除尾随空格
                value = [float(v) for v in value_str.split()] if ' ' in value_str else float(value_str)
                setattr(bone, name, value)
            
            # 设置参数对应的开关
            if hasattr(bone, enable_name):
                setattr(bone, enable_name, True)

    def execute(self, context):
        clipboard = context.window_manager.clipboard
        scene = context.scene
        jigglebone_list = scene.jigglebone_list
        bone_index = scene.jigglebone_list_index

        # 如果当前有一个骨骼高亮显示
        if bone_index < len(jigglebone_list):
            current_bone = jigglebone_list[bone_index]

            # 确定应用设置的骨骼列表
            selected_bones = [bone for bone in jigglebone_list if bone.selected]
            
            # 如果当前骨骼没有被选中，或者没有其他骨骼被多选，则只对当前骨骼应用设置
            if not current_bone.selected or not any(bone.selected for bone in jigglebone_list if bone != current_bone):
                self.apply_settings_to_bone(current_bone, clipboard)
            else:
                # 否则，对所有选中的骨骼批量应用设置
                for bone in selected_bones:
                    self.apply_settings_to_bone(bone, clipboard)

            self.report({'INFO'}, "剪贴板中的预设已应用到选中的骨骼")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "没有选中的骨骼")
            return {'CANCELLED'}

class Jigglebone_OT_ImportAllFromClipboard(bpy.types.Operator):
    """Import all floating bone text from the clipboard to the current list"""
    bl_idname = "jigglebone.import_all_from_clipboard"
    bl_label = "Import jitter parameters from the clipboard (All)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        clipboard = bpy.context.window_manager.clipboard
        scene = context.scene
        
        # 正则表达式匹配单个飘骨块
        jigglebone_pattern = re.compile(r'\$jigglebone\s+"(.+?)"\s*\{(.+?)\}', re.DOTALL)
        matches = jigglebone_pattern.finditer(clipboard)
        
        # 遍历所有匹配到的飘骨块
        for match in matches:
            bone_name = match.group(1)
            bone_params = match.group(2)
            
            # 创建新飘骨对象并添加到jigglebone_list
            new_bone = scene.jigglebone_list.add()
            new_bone.name = bone_name
            
            # 调用apply_settings_to_bone方法应用参数
            self.apply_settings_to_bone(new_bone, bone_params)
        
        # 更新UI
        context.area.tag_redraw()
        return {'FINISHED'}

    def apply_settings_to_bone(self, bone, params):
        # 先关闭所有参数的开关
        bone.is_flexible = False
        bone.has_base_spring = False
        for param in flexible_params + base_params:
            enable_name = 'enable_' + param[0]
            if hasattr(bone, enable_name):
                setattr(bone, enable_name, False)
        
        # 使用正则表达式匹配参数，并应用到骨骼
        param_pattern = re.compile(r'(\w+)\s*([\d\s.-]+)?')
        for match in param_pattern.finditer(params):
            name = match.group(1)
            value_str = match.group(2)
            enable_name = 'enable_' + name
            
            # 更新是否灵活和是否有基础弹簧的标志
            if name == 'is_flexible':
                bone.is_flexible = True
                continue  # 跳过下面的赋值步骤
            elif name == 'has_base_spring':
                bone.has_base_spring = True
                continue  # 跳过下面的赋值步骤
            
            # 如果有值，则设置之
            if value_str and hasattr(bone, name):
                value_str = value_str.strip()  # 删除尾随空格
                value = [float(v) for v in value_str.split()] if ' ' in value_str else float(value_str)
                setattr(bone, name, value)
            
            # 设置参数对应的开关
            if hasattr(bone, enable_name):
                setattr(bone, enable_name, True)


# 导出文件
class Jigglebone_OT_ExportJigglebone(bpy.types.Operator):
    bl_idname = "jigglebone.export_jigglebone"
    bl_label = "Export Jigglebone Context"
    bl_options = {'REGISTER', 'UNDO'}
    
    action: EnumProperty(
        items=[
            ('CLIPBOARD', "复制到剪贴板", "将飘骨文本复制到剪贴板"),
            ('FILE', "导出到文件", "将飘骨文本导出到文件"),
        ]
    ) 
    bpy.types.Scene.jigglebone_export_path = StringProperty(
        name="Export Path",
        subtype='FILE_PATH',  # 设置为 FILE_PATH，可以选择文件名
        default="//"
    )

    @staticmethod
    def format_property(name, value):
        if isinstance(value, list) or isinstance(value, bpy.types.bpy_prop_array):
            formatted_value = ' '.join(['{:.2f}'.format(v) if v % 1 else str(int(v)) for v in value])
            return f"{name} {formatted_value}"
        elif isinstance(value, float):
            return f"{name} {'{:.2f}'.format(value) if value % 1 else str(int(value))}"
        else:
            return f"{name} {value}"
    
    def add_param_section(self, bone, param_list):
        output = ""
        for param in param_list:
            name = param[0]
            enable_name = f'enable_{name}'
            if getattr(bone, enable_name):
                if param[1] == BoolProperty:
                    output += f"        {name}\n"
                else:
                    value = getattr(bone, name)
                    formatted_value = self.format_property(name, value)
                    output += f"        {formatted_value}\n"
        return output
    
    def generate_export_text(self, context):
        scene = context.scene
        jigglebone_list = scene.jigglebone_list

        output = ""
        for bone in jigglebone_list:
            bone_output = f'$jigglebone "{bone.name}"\n{{\n'
            if bone.is_flexible:
                bone_output += "    is_flexible\n    {\n"
                bone_output += self.add_param_section(bone, flexible_params)
                bone_output += "    }\n"
            if bone.has_base_spring:
                bone_output += "    has_base_spring\n    {\n"
                bone_output += self.add_param_section(bone, base_params)
                bone_output += "    }\n"
            bone_output += "}\n\n"
            output += bone_output
        return output

    def export_to_clipboard(self, text):
        bpy.context.window_manager.clipboard = text
        self.report({'INFO'}, "所选飘骨文本已经复制到剪贴板")

    def generate_export_text_selected(self, context):
        scene = context.scene
        jigglebone_list = scene.jigglebone_list

        output = ""
        for bone in jigglebone_list:
            if bone.selected:
                bone_output = f'$jigglebone "{bone.name}"\n{{\n'
                if bone.is_flexible:
                    bone_output += "    is_flexible\n    {\n"
                    bone_output += self.add_param_section(bone, flexible_params)
                    bone_output += "    }\n"
                if bone.has_base_spring:
                    bone_output += "    has_base_spring\n    {\n"
                    bone_output += self.add_param_section(bone, base_params)
                    bone_output += "    }\n"
                bone_output += "}\n\n"
                output += bone_output
        return output

    def export_to_file(self, text, filepath):
        # 将 '//' 转换为实际的文件路径
        filepath = bpy.path.abspath(filepath)
        # 检查路径是否只有目录，没有文件名
        if filepath.endswith(('\\', '/')):
            self.report({'ERROR'}, "请在导出路径提供一个具体的文件名")
            return {'CANCELLED'}
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(text)
            self.report({'INFO'}, f"飘骨文本已成功导出到 {filepath}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

    def execute(self, context):
        # 获取所有的骨骼列表
        jigglebone_list = context.scene.jigglebone_list
        # 判断当前操作是否是导出到剪贴板，并且列表中至少有一个骨骼被选中
        is_clipboard_action = self.action == 'CLIPBOARD'
        has_selected_bones = is_clipboard_action and any(bone.selected for bone in jigglebone_list)
        
        # 如果操作是导出到剪贴板，并且有选中的骨骼，只导出选中项的文本
        # 否则导出全部骨骼文本
        if has_selected_bones:
            text = self.generate_export_text_selected(context)
        else:
            text = self.generate_export_text(context)
        
        filepath = context.scene.jigglebone_export_path  # 这里从场景中获取用户设置的文件路径
        if not text:
            self.report({'ERROR'}, "无可导出的数据")
            return {'CANCELLED'}
        if is_clipboard_action:
            self.export_to_clipboard(text)
        else:
            # 导出到文件的逻辑保持原样，不受是否有选中项的影响
            if filepath:
                # 用户已经设定了输出路径，直接将文件保存到用户指定的路径
                self.export_to_file(text, filepath)
            else:
                # 用户尚未设定输出路径，提示用户需要设置一个输出路径
                self.report({'ERROR'}, "请先设置导出的文件路径！")
                return {'CANCELLED'}
        return {'FINISHED'}

class Jigglebone_OT_OpenFile(bpy.types.Operator):
    bl_idname = "jigglebone.open_file"
    bl_label = "Open File or Folder"
    bl_description = "Open the file or folder specified by 'Export Path'"

    # 枚举属性，允许用户选择是打开文件还是文件夹
    open_type: EnumProperty(
        name="打开类型",
        description="选择你要打开的是文件还是所在的文件夹",
        items=[
            ('FILE', "文件", "打开文件"),
            ('FOLDER', "文件夹", "打开包含文件的文件夹"),
        ],
        default='FILE',
    )

    def execute(self, context):
        # 获取之前用户指定的文件路径
        full_path = bpy.path.abspath(context.scene.jigglebone_export_path)

        # 如果选择打开文件
        if self.open_type == 'FILE':
            # 打开用户指定的文件
            if os.path.isfile(full_path):
                to_open = full_path
            else:
                self.report({'ERROR'}, "系统找不到指定的文件：" + full_path)
                return {'CANCELLED'}
        else:
            # 如果选择打开文件夹，获取文件所在的文件夹路径
            folder_path = os.path.dirname(full_path)
            if os.path.isdir(folder_path):
                to_open = folder_path
            else:
                self.report({'ERROR'}, "系统找不到指定的文件夹：" + folder_path)
                return {'CANCELLED'}

        # 根据不同的操作系统执行相应的打开命令
        try:
            if os.name == 'nt':  # Windows系统
                os.startfile(to_open)
            elif os.name == 'posix':  # Unix系统
                subprocess.call(('xdg-open', to_open))
        except Exception as e:
            self.report({'ERROR'}, "打开失败：" + str(e))
            return {'CANCELLED'}

        return {'FINISHED'}
    
class JIGGLEBONE_OT_UpdateSelection(bpy.types.Operator):
    """Manually update the jigglebone list"""
    bl_idname = "jigglebone.update_selection"
    bl_label = "Synchronize 3D view selection state and jump"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 执行更新列表的操作
        update_bone_list_selection(context.scene, None)
        if 'selected_bones_indices' in context.scene and context.scene['selected_bones_indices']:
            # 如果场景没有 'counter' 属性，初始化它
            if 'counter' not in context.scene:
                context.scene['counter'] = 0

            # 获得选中骨骼的个数
            num_bones = len(context.scene['selected_bones_indices'])

            # 确保 counter 的值没有超过可用的索引范围
            counter = context.scene['counter'] % num_bones

            context.scene.jigglebone_list_index = context.scene['selected_bones_indices'][counter]
            context.scene['counter'] = (counter + 1) % num_bones
            del context.scene['selected_bones_indices']  # 使用后从属性中删除
        return {'FINISHED'}

classes = [
    Jigglebone_OT_AddPreset,
    Jigglebone_OT_DeletePreset,
    Jigglebone_OT_ApplyPreset,
    Jigglebone_OT_SetAngle,
    JigglebonePropertyGroup,
    Jigglebone_OT_SelectAction,
    Jigglebone_OT_OpenFile,
    JIGGLEBONE_UL_List,
    Jigglebone_OT_AddBone,
    Jigglebone_OT_RemoveBone,
    Jigglebone_OT_ClearBone,
    Jigglebone_OT_MoveUpBone,
    Jigglebone_OT_MoveDownBone,
    Jigglebone_OT_ExportJigglebone,
    Jigglebone_OT_ApplyFromClipboard,
    PresetPropertyGroup,
    JIGGLEBONE_OT_UpdateSelection,
    Jigglebone_OT_ImportAllFromClipboard,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.jigglebone_list = CollectionProperty(type=JigglebonePropertyGroup)
    bpy.types.Scene.jigglebone_list_index = IntProperty(default=0)
    bpy.types.Scene.jigglebone_presets = PointerProperty(type=PresetPropertyGroup)
    # bpy.app.handlers.depsgraph_update_post.append(update_bone_list_selection)
    bpy.types.Scene.Jigglebone_is_detailed = BoolProperty(name="Jigglebone Parameters Panel", default=False)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.jigglebone_list
    del bpy.types.Scene.jigglebone_list_index
    del bpy.types.Scene.jigglebone_export_path
    del bpy.types.Scene.jigglebone_presets
    # bpy.app.handlers.depsgraph_update_post.remove(update_bone_list_selection)