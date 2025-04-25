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

# -*- coding: utf-8 -*-
import bpy
import os
import re
import json
from bpy.types import PropertyGroup
from bpy.props import FloatProperty, BoolProperty, IntProperty, CollectionProperty, StringProperty, EnumProperty, PointerProperty
from .resources import flex_dict
from .resources import flexmix_presets
from bpy.app.translations import pgettext_iface as _

# 防止递归更新的标志
is_updating_from_plugin = False

# 预设目录路径
preset_dir = os.path.join(bpy.utils.resource_path('USER'), 'scripts', 'presets', 'L4D2 Character Tools')
# JSON文件路径
flexmix_dict_path = os.path.join(preset_dir, 'flex_dict.json')
flexmix_presets_path = os.path.join(preset_dir, 'flexmix_presets.json')

flexmix_dict = {}
key_notes = {}
key_mapping = {}

# 形态键捕获项定义
class FlexCapturedKey(PropertyGroup):
    name: StringProperty(name=_("Name"), description=_("The shape key name"))
    value: FloatProperty(
        name=_("Value"), 
        description=_("The shape key value"),
        min=0.0, 
        max=1.0,
        precision=3,
        step=1,
        update=lambda self, context: update_shape_key_from_plugin(self, context)
    )

# 从插件更新模型上的形态键值
def update_shape_key_from_plugin(self, context):
    global is_updating_from_plugin
    # 防止递归更新
    if is_updating_from_plugin:
        return
    
    # 设置标志，表示正在从插件更新
    is_updating_from_plugin = True
    
    try:
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.data.shape_keys:
            # 查找对应的形态键并更新其值
            shape_key = obj.data.shape_keys.key_blocks.get(self.name)
            if shape_key:
                shape_key.value = self.value
    finally:
        # 确保标志被重置
        is_updating_from_plugin = False

# 处理器函数，监测形态键变化
def depsgraph_update_post_handler(scene):
    global is_updating_from_plugin
    # 如果禁用监测或正在从插件更新，则不处理
    if not scene.enable_flex_monitoring or is_updating_from_plugin:
        return
    
    # 获取活动对象
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH' or not obj.data.shape_keys:
        # 如果没有合适的对象或形态键，清空捕获列表
        if len(scene.captured_shape_keys) > 0:
            scene.captured_shape_keys.clear()
        return
    
    # 遍历所有形态键
    for shape_key in obj.data.shape_keys.key_blocks:
        # 跳过基础形态键
        if shape_key == obj.data.shape_keys.reference_key:
            continue
        
        # 检查形态键值
        if shape_key.value > 0:
            # 查找是否已在捕获列表中
            found = False
            for captured in scene.captured_shape_keys:
                if captured.name == shape_key.name:
                    # 更新值
                    if abs(captured.value - shape_key.value) > 0.001:  # 添加一点容差
                        is_updating_from_plugin = True
                        captured.value = shape_key.value
                        is_updating_from_plugin = False
                    found = True
                    break
            
            # 如果不在列表中，添加它
            if not found:
                item = scene.captured_shape_keys.add()
                item.name = shape_key.name
                item.value = shape_key.value
        else:
            # 如果形态键值为0，从列表中移除
            for i, captured in enumerate(scene.captured_shape_keys):
                if captured.name == shape_key.name:
                    scene.captured_shape_keys.remove(i)
                    break

# 保存骨骼字典到文件
def save_flexmix_dict(mix_dict, key_notes):
    data = {
        "flexmix_dict": mix_dict,
        "key_notes": key_notes
    }
    try:
        with open(flexmix_dict_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存文件时发生错误: {e}")

# 使用全局变量从文件加载骨骼字典
def load_flexmix_dict():
    global flexmix_dict, key_notes
    if os.path.isfile(flexmix_dict_path):
        try:
            with open(flexmix_dict_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                flexmix_dict = data.get("flexmix_dict", flex_dict.mix_dict)  # 从flex_dict导入的备用值
                key_notes = data.get("key_notes", flex_dict.key_notes)  # 同上
        except json.JSONDecodeError as e:
            print(f"读取JSON文件时发生解析错误: {e}")
            flexmix_dict = flex_dict.mix_dict  # 使用备用值
            key_notes = flex_dict.key_notes  # 同上
            save_flexmix_dict(flexmix_dict, key_notes)  # 将 python 字典写入新的 json 文件
    else:
        # 创建默认的flex_dict.json文件
        print(f"找不到文件: {flexmix_dict_path}，将使用 flex_dict.py 中的字典并创建一个新的 json 文件。")
        flexmix_dict = flex_dict.mix_dict
        key_notes = flex_dict.key_notes
        save_flexmix_dict(flexmix_dict, key_notes)

load_flexmix_dict() 

# 更新键值对数值的函数，并保存到 JSON 文件
def update_flex_key_value(self, context, enum_index, group_index, key_id):
    selected_key = context.scene.flex_keys_enum
    if selected_key in flexmix_dict:
        flex_list = flexmix_dict[selected_key]
        if group_index < len(flex_list):
            # 根据 key_id 获取实际键名
            key_name = key_mapping.get(key_id)
            if key_name:
                # 更新字典中的值
                flex_list[group_index][key_name] = getattr(context.scene, f"flex_key_group_{key_id}")
                # 保存更新后的字典到 JSON 文件中
                save_flexmix_dict(flexmix_dict, key_notes)


# 重新定义属性并附加更新回调
def create_or_update_prop(enum_index, group_index, key_index, key, value):
    # 生成唯一标识符
    key_id = f"{enum_index - 1}_{group_index + 1}_{key_index + 1}"
    key_mapping[key_id] = key  # 保存到 key_mapping 字典中

    prop_name = f"flex_key_group_{key_id}"

    # 定义更新函数
    def update_prop(self, context):
        update_flex_key_value(self, context, enum_index, group_index, key_id)

    setattr(bpy.types.Scene, prop_name, FloatProperty(name=key, default=value, min=0.0, max=1.0, update=update_prop))

# 更新枚举项的回调函数
def update_enum(self, context):
    flex_key_selected = context.scene.flex_keys_enum
    # 清空 key_mapping
    global key_mapping
    key_mapping = {}

    # 删除已有的动态属性
    for flex_key in [f for f in dir(context.scene) if f.startswith("flex_key_group_")]:
        delattr(bpy.types.Scene, flex_key)

    if flex_key_selected in flexmix_dict:
        # 获取枚举项的索引值
        enum_items = init_enum_items(None, context)
        selected_index = next(index for index, item in enumerate(enum_items) if item[0] == flex_key_selected) + 1

        selected_list = flexmix_dict.get(flex_key_selected)
        if selected_list is not None:
            for list_index, group in enumerate(selected_list):
                for key_index, (key, value) in enumerate(group.items()):
                    create_or_update_prop(selected_index, list_index, key_index, key, value)

# 当UIList索引更改时触发此函数
def update_flexmix_index(self, context):
    global key_mapping
    key_mapping = {}

    # 删除已有的动态属性
    for flex_key in [f for f in dir(context.scene) if f.startswith("flex_key_group_")]:
        delattr(bpy.types.Scene, flex_key)

    # 检查索引是否有效
    wm = context.window_manager
    if wm.flexmix_index < 0 or wm.flexmix_index >= len(wm.flexmix_items):
        return
    
    # 获取当前选中的项目名称
    selected_key = wm.flexmix_items[wm.flexmix_index].name
    
    if selected_key in flexmix_dict:
        # 使用全局字典序号作为enum_index
        all_keys = list(flexmix_dict.keys())
        if selected_key in all_keys:
            selected_index = all_keys.index(selected_key) + 1
            
            selected_list = flexmix_dict.get(selected_key)
            if selected_list is not None:
                for list_index, group in enumerate(selected_list):
                    for key_index, (key, value) in enumerate(group.items()):
                        create_or_update_prop(selected_index, list_index, key_index, key, value)

# 更新下拉菜单枚举项的函数
def update_flex_keys_enum_items():
    items = init_enum_items(None, bpy.context)
    bpy.types.Scene.flex_keys_enum = EnumProperty(
        name="Flex Keys",
        description="Select a flex key",
        items=items,
        update=update_enum
    )
  
# 初始化下拉菜单枚举项的函数
def init_enum_items(self, context):
    items = [(k, str(i)+'. '+k, "") for i, k in enumerate(flexmix_dict.keys(), start=0)] if flexmix_dict.keys() else []
    return items

# 分割比例更新函数
def update_split_ratio(self, context):
    # 这里不需要特别的更新逻辑，因为属性变更会自动触发界面重绘
    pass

# 注册场景属性：分割比例
bpy.types.Scene.flex_split_ratio = FloatProperty(
    name="Split Ratio",
    description="调整左右分栏的分割比例",
    default=0.5,
    min=0.1,
    max=0.9,
    precision=2,
    update=update_split_ratio
)

bpy.types.Scene.flex_keys_enum = EnumProperty(items=init_enum_items,
                                                        update=update_enum)

# 捕捉非零形态键值的操作
class L4D2_OT_StoreShapeKeys(bpy.types.Operator):
    """Capture Non-Zero Deformation Shape Keys"""
    bl_idname = "l4d2.store_shape_keys"
    bl_label = _("Shape Keys Capture")

    def execute(self, context):
        obj = bpy.context.active_object
        if obj and obj.type == 'MESH' and obj.data.shape_keys:
            global current_shape_keys_values
            current_shape_keys_values.clear()  # 清空列表
            # 只记录值非零的形态键
            current_shape_keys_values = [
                (shape_key.name, shape_key.value)
                for shape_key in obj.data.shape_keys.key_blocks
                if shape_key.value != 0 and shape_key != obj.data.shape_keys.reference_key
            ]
            self.report({'INFO'}, f"{_('Non-zero shape keys recorded:')} '{current_shape_keys_values}' ")
            print("非零形态键记录: ", current_shape_keys_values)  # 用于调试

        return {'FINISHED'}
           
class L4D2_OT_AddToDict(bpy.types.Operator):
    """Add the captured shape key values into the currently selected dictionary key"""
    bl_idname = "l4d2.add_to_dict"
    bl_label = _("Add to Dict")

    def execute(self, context):
        wm = context.window_manager
        scene = context.scene
        global flexmix_dict
        
        # 检查是否有项目被选中
        if wm.flexmix_index < 0 or wm.flexmix_index >= len(wm.flexmix_items):
            self.report({'ERROR'}, _("Please select an expression from the list first"))
            return {'CANCELLED'}
        
        selected_key = wm.flexmix_items[wm.flexmix_index].name
        
        # 使用实时捕获的形态键
        if len(scene.captured_shape_keys) == 0:
            self.report({'ERROR'}, _("No active shape keys detected, please adjust shape key values in the Shape Keys panel first"))
            return {'CANCELLED'}
        
        # 创建形态键字典
        current_shape_dict = {captured.name: captured.value for captured in scene.captured_shape_keys}
        
        if selected_key:
            # 确保要插入的表情键存在于字典中
            if selected_key not in flexmix_dict:
                flexmix_dict[selected_key] = []
            
            # 添加到字典
            flexmix_dict[selected_key].append(current_shape_dict)
            save_flexmix_dict(flexmix_dict, key_notes)  # 保存字典到文件
            
            # 触发更新函数，刷新当前显示的属性
            update_flexmix_index(context.window_manager, context)
            self.report({'INFO'}, f"{_('Shape keys added:')} '{selected_key}' ")
        
        return {'FINISHED'}

class L4D2_OT_DeleteFlexKeyPair(bpy.types.Operator):
    bl_idname = "l4d2.delete_flex_key_pair"
    bl_label = _("Delete Key-Value Pair")
    group_index: IntProperty()  # 组索引，现在直接从1开始以匹配UI表现
    key_id: StringProperty()
    enum_index: IntProperty()  # 枚举索引，从1开始

    def execute(self, context):
        wm = context.window_manager
        
        # 获取当前选中的表情键
        if wm.flexmix_index < 0 or wm.flexmix_index >= len(wm.flexmix_items):
            self.report({'ERROR'}, _("No valid expression key selected"))
            return {'CANCELLED'}
            
        selected_key = wm.flexmix_items[wm.flexmix_index].name
        print("正在删除键值对，选择的键:", selected_key, "组索引:", self.group_index, "键ID:", self.key_id)

        if selected_key in flexmix_dict:
            flex_list = flexmix_dict[selected_key]
            # 注意这里 group_index 在删除时要减1，以匹配内部列表的索引基础
            adjusted_group_index = self.group_index - 1
            if adjusted_group_index < len(flex_list):
                current_group = flex_list[adjusted_group_index]
                key_name = key_mapping.get(self.key_id)
                if key_name:
                    # 使用 pop 删除键值对并忽略不存在的键
                    current_group.pop(key_name, None)
                
                # 如果当前组为空，则从列表中删除
                if not current_group:
                    flex_list.pop(adjusted_group_index)
                
                # 更新保存，触发UI更新
                save_flexmix_dict(flexmix_dict, key_notes)
                update_flexmix_index(wm, context)
                self.report({'INFO'}, f"{_('Shape key')} '{selected_key}' {_('data deleted')}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, _("Invalid group index, please check the dropdown menu."))
        else:
            self.report({'ERROR'}, _("Selected key does not exist in the dictionary."))

        return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
class L4D2_OT_AddNewFlexKey(bpy.types.Operator):
    """Add a new key to the dictionary"""
    bl_idname = "l4d2.add_new_flex_key"
    bl_label = _("Add New Key")
    new_key_name: StringProperty(name=_("Name"))
    new_key_note: StringProperty(name=_("Note"))  # 新增：新建键的备注


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        key_name = self.new_key_name
        # 添加判断，如果键名称为空
        if key_name == '':
            self.report({'ERROR'}, _("Key name cannot be empty!"))
            return {'CANCELLED'}
        if key_name in flexmix_dict:
            self.report({'ERROR'}, f"{_('Key')} '{key_name}' {_('already exists!')}")
            return {'CANCELLED'}


        # 添加新键到字典
        flexmix_dict[key_name] = []
        key_notes[key_name] = self.new_key_note  # 新增：设置新建键的备注
        save_flexmix_dict(flexmix_dict, key_notes)  # 修改：保存时带上 key_notes 字典

        # 添加新项到 UIList
        wm = context.window_manager
        item = wm.flexmix_items.add()
        item.name = key_name
        item.selected = False
        wm.flexmix_index = len(wm.flexmix_items) - 1  # 选择新添加的项目

        self.report({'INFO'}, f"{_('New key added:')} '{key_name}'.")
        return {'FINISHED'}
    
    def draw(self, context):  # 加入此方法，给对话框添加输入字段
        self.layout.prop(self, "new_key_name")
        self.layout.prop(self, "new_key_note")

class L4D2_OT_RenameFlexKey(bpy.types.Operator):
    """Rename the key currently selected in the drop-down menu"""
    bl_idname = "l4d2.rename_flex_key"
    bl_label = _("Rename Key")
    new_key_name: StringProperty(name=_("Name"))
    new_key_note: StringProperty(name=_("Note"))  # 新增：重命名键后的备注

    def invoke(self, context, event):
        wm = context.window_manager
        if wm.flexmix_index < 0 or wm.flexmix_index >= len(wm.flexmix_items):
            self.report({'ERROR'}, _("No key selected"))
            return {'CANCELLED'}
            
        selected_key = wm.flexmix_items[wm.flexmix_index].name
        self.new_key_name = selected_key
        self.new_key_note = key_notes.get(self.new_key_name, "")  # 初始化新键备注的值
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        global flexmix_dict
        global key_notes
        wm = context.window_manager
        
        if wm.flexmix_index < 0 or wm.flexmix_index >= len(wm.flexmix_items):
            self.report({'ERROR'}, _("No key selected"))
            return {'CANCELLED'}
            
        old_key_name = wm.flexmix_items[wm.flexmix_index].name
        new_key_name = self.new_key_name
        old_key_note = key_notes.get(old_key_name, "")
        new_key_note = self.new_key_note

        # 添加判断，如果新键名为空
        if new_key_name == '':
            self.report({'ERROR'}, _("Key name cannot be empty!"))
            return {'CANCELLED'}
            
        # 新建一个有序的空字典和备注字典
        new_flexmix_dict = {}
        new_key_notes = {}
        for key, value in flexmix_dict.items():
            # 在遍历到旧键名的位置插入新键名
            if key == old_key_name:
                new_flexmix_dict[new_key_name] = flexmix_dict[old_key_name]
                new_key_notes[new_key_name] = new_key_note  # 新键的备注
                if new_key_name != old_key_name and new_key_note == old_key_note:
                    self.report({'INFO'}, f"{_('Key')} '{old_key_name}' {_('has been renamed to')} '{new_key_name}'.")
                elif new_key_name == old_key_name and new_key_note != old_key_note:
                    self.report({'INFO'}, f"{_('Note for key')} '{old_key_name}' {_('has been changed.')}")
                elif new_key_name != old_key_name and new_key_note != old_key_note:
                    self.report({'INFO'}, f"{_('Key')} '{old_key_name}' {_('renamed to')} '{new_key_name}' {_('and note changed.')}")
            else:
                new_flexmix_dict[key] = value
                new_key_notes[key] = key_notes.get(key, "")  # 保留原来的备注

        # 替换原字典和备注字典
        flexmix_dict = new_flexmix_dict
        key_notes = new_key_notes
        save_flexmix_dict(flexmix_dict, key_notes)  # 保存时带上 key_notes 字典

        # 更新 UIList 中的项目名称
        wm.flexmix_items[wm.flexmix_index].name = new_key_name
        
        # 更新相关 UI 元素
        update_flexmix_index(wm, context)
        
        return {'FINISHED'}
    
    def draw(self, context):  # 加入此方法，给对话框添加输入字段
        self.layout.prop(self, "new_key_name")
        self.layout.prop(self, "new_key_note")

class L4D2_OT_DeleteFlexKey(bpy.types.Operator):
    """Delete the currently selected key and its key-value pair"""
    bl_idname = "l4d2.delete_flex_key"
    bl_label = _("Delete Key")
    
    def execute(self, context):
        global flexmix_dict
        global key_notes  # 保证我们操作的是全局变量
        wm = context.window_manager
        
        # 检查是否有选中的项目
        if wm.flexmix_index < 0 or wm.flexmix_index >= len(wm.flexmix_items):
            self.report({'WARNING'}, _("Key not found or not selected"))
            return {'CANCELLED'}
            
        selected_key = wm.flexmix_items[wm.flexmix_index].name

        # 删除键及其数据
        if selected_key and selected_key in flexmix_dict:
            # 删除键
            del flexmix_dict[selected_key]
            if selected_key in key_notes:  # 如果备注中有此键，也一并删除
                del key_notes[selected_key]
            save_flexmix_dict(flexmix_dict, key_notes)  # 保存时同时保存备注

            # 从 UIList 中删除项目
            wm.flexmix_items.remove(wm.flexmix_index)
            
            # 调整选择的索引
            if len(wm.flexmix_items) > 0:
                if wm.flexmix_index >= len(wm.flexmix_items):
                    wm.flexmix_index = len(wm.flexmix_items) - 1
            else:
                wm.flexmix_index = -1

            self.report({'INFO'}, f"{_('Key')} '{selected_key}' {_('and its data have been deleted')}")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, _("Key not found or not selected"))
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class L4D2_PT_ShapeKeyPanel(bpy.types.Panel):
    bl_label = _("L4D2 ShapeKey Tools")
    bl_idname = "L4D2_PT_ShapeKey"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        
        # 上方按钮区域
        row = layout.row()
        row.operator("l4d2.create_selected_key", icon="ADD")
        row.operator("l4d2.all_create", text=_('Batch Create'), icon="ADD")
        layout.operator("l4d2.sort_shape_keys", icon="SORTSIZE")
        
        # 实时监测开关
        monitor_row = layout.row()
        monitor_row.prop(scene, "enable_flex_monitoring", text=_("Capture & Add Shape Keys to Expression Group"), icon="SHAPEKEY_DATA")
        
        # 当前捕获的形态键区域
        if scene.enable_flex_monitoring:
            captured_box = layout.box()
            captured_box.label(text=_("Current Active Shape Keys"), icon="KEY_HLT")
            
            # 如果有捕获的形态键，显示它们
            if len(scene.captured_shape_keys) > 0:
                for captured in scene.captured_shape_keys:
                    row = captured_box.row()
                    row.prop(captured, "value", text=captured.name, slider=True)
                
                # 添加到当前表情的按钮
                add_row = layout.row()
                add_row.scale_y = 1.2
                if wm.flexmix_index >= 0 and wm.flexmix_index < len(wm.flexmix_items):
                    selected_key = wm.flexmix_items[wm.flexmix_index].name
                    add_row.operator("l4d2.add_to_dict", text=f"{_('Add to')} '{selected_key}'", icon="RNA_ADD")
                else:
                    add_row.operator("l4d2.add_to_dict", text=_("Please select an expression first"), icon="RNA_ADD")
                    add_row.enabled = False
            else:
                captured_box.label(text=_("No active shape keys detected"), icon="INFO")
                layout.label(text=_("Please adjust shape key values in the Shape Keys panel"), icon="ERROR")
        
        # 1. 预设管理区域 - 独立显示
        preset_box = layout.box()
        preset_row = preset_box.row(align=True)
        preset_row.label(text=_("Preset:"), icon='PRESET')
        # 增加菜单宽度
        preset_row.scale_x = 3.0
        preset_row.prop(wm, "presets", text="")
        preset_row.scale_x = 1.0
        preset_row.operator("l4d2.save_flex_preset", text="", icon="FILE_TICK")
        preset_row.operator("l4d2.delete_flex_preset", text="", icon="TRASH")
        
        # 创建左右分栏，使用场景属性作为分割因子
        split = layout.split(factor=context.scene.flex_split_ratio)
        
        # 左侧：表情列表和操作按钮
        left_col = split.column()
        
        # 列表上方按钮区域 - 全选按钮与删除/上移/下移按钮放在同一行
        select_box = left_col.box()
        select_row = select_box.row()
        
        # 左侧的全选/反选按钮
        button_left = select_row.row(align=True)
        
        # 参考jigglebone.py的逻辑，动态显示全选/反选按钮
        if len(wm.flexmix_items) > 0:
            # 检查是否所有项目都已选中
            if all(item.selected for item in wm.flexmix_items):
                # 如果全部选中，显示取消全选按钮
                button_left.operator('l4d2.select_action', text="", icon='CHECKBOX_HLT').action = 'NONE'
            else:
                # 如果未全部选中，显示全选按钮
                button_left.operator('l4d2.select_action', text="", icon='CHECKBOX_DEHLT').action = 'ALL'
                
                # 检查是否有任何项目选中
                if any(item.selected for item in wm.flexmix_items):
                    # 如果有选中项，显示反选按钮
                    button_left.operator('l4d2.select_action', text="", icon='UV_SYNC_SELECT').action = 'INVERSE'
        
        # 右侧的操作按钮（删除/上移/下移）
        button_right = select_row.row(align=True)
        button_right.alignment = 'RIGHT'
        button_right.operator("l4d2.add_new_flex_key", text="", icon='ADD')
        button_right.operator("l4d2.rename_flex_key", text="", icon='GREASEPENCIL')
        button_right.operator("l4d2.delete_flex_key", icon='X', text="")
        button_right.operator("l4d2.flexmix_move_up", icon='TRIA_UP', text="")
        button_right.operator("l4d2.flexmix_move_down", icon='TRIA_DOWN', text="")
        
        # 主列表区域
        list_row = left_col.row()
        list_row.template_list(
            "FLEXMIX_UL_List", "", 
            wm, "flexmix_items", 
            wm, "flexmix_index",
            rows=21  # 增加行数，更好地利用垂直空间
        )
        
        # 右侧：当前选中表情的详细信息（形态键组合）
        right_col = split.column()
        
        # 显示选中项和备注信息 - 移到右侧栏
        if wm.flexmix_index >= 0 and wm.flexmix_index < len(wm.flexmix_items):
            selected_item = wm.flexmix_items[wm.flexmix_index]
            
            # 显示选中项信息框
            info_box = right_col.box()
            
            # 第一排：显示Selected
            title_row = info_box.row()
            title_row.label(text=f"{_('Selected:')} {selected_item.name}", icon='SHAPEKEY_DATA')
            
            # 第二排：显示Note
            if selected_item.name in key_notes and key_notes[selected_item.name]:
                note_row = info_box.row()
                note_row.label(text=f"{_('Note:')} {key_notes[selected_item.name]}", icon='INFO')
            else:
                note_row = info_box.row()
                note_row.label(text=_("Note: None"), icon='INFO')
            
            # 显示与当前选择的表情相关的动态属性（形态键组合）
            selected_key = selected_item.name
            
            if selected_key in flexmix_dict:
                scene = context.scene
                last_group_index = None
                
                # 如果没有组合，显示提示信息
                if not flexmix_dict[selected_key]:
                    right_col.label(text=_("No shape key combinations defined"), icon='ERROR')
                
                # 按组索引和键索引排序显示动态属性
                for attr in sorted((a for a in dir(scene) if a.startswith("flex_key_group_")), 
                                  key=lambda x: (int(x.split("_")[3]), int(x.split("_")[4]), int(x.split("_")[5]))):
                    enum_index, group_index, key_index = map(int, attr.split("_")[3:])
                    
                    if (enum_index, group_index) != last_group_index:
                        box = right_col.box()
                        box.label(text=f"{_('Combination')} {group_index}", icon='GROUP')
                        last_group_index = (enum_index, group_index)
                        
                    row = box.row()
                    row.prop(scene, attr)
                    
                    # 传递参数给删除操作符
                    op = row.operator("l4d2.delete_flex_key_pair", text="", icon="X")
                    op.enum_index = enum_index
                    op.group_index = group_index
                    op.key_id = "_".join(attr.split("_")[3:])
        else:
            right_col.label(text=_("Select a flex key from the list"), icon='INFO')

        # 添加分割比例滑块
        box = layout.box()
        box.prop(context.scene, "flex_split_ratio", slider=True)

# UI列表项类定义
class FLEXMIX_UL_List(bpy.types.UIList):
    # 添加搜索过滤功能
    filter_name: StringProperty(
        name=_("Search"),
        description=_("Filter items by name"),
        default=""
    )
    
    use_filter_invert: BoolProperty(
        name=_("Invert Filter"),
        description=_("Invert filter"),
        default=False
    )
    
    # 类属性：用于存储外部搜索条件
    _search_term = ""
    
    @classmethod
    def set_search_term(cls, term):
        cls._search_term = term if term else ""
    
    # 实现过滤功能
    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        
        # 首先检查是否有内置搜索文本
        if self.filter_name:
            for i, item in enumerate(items):
                if self.filter_name.lower() not in item.name.lower():
                    filtered[i] &= ~self.bitflag_filter_item
            
            # 如果需要反转过滤结果
            if self.use_filter_invert:
                for i in range(len(filtered)):
                    filtered[i] ^= self.bitflag_filter_item
        
        # 然后检查是否有类共享的搜索条件
        elif FLEXMIX_UL_List._search_term:
            search_term = FLEXMIX_UL_List._search_term.lower()
            for i, item in enumerate(items):
                if search_term not in item.name.lower():
                    filtered[i] &= ~self.bitflag_filter_item
        
        # 返回过滤结果和排序方法（这里不做排序）
        return filtered, []

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # 创建一个启用鼠标点击的行
            row = layout.row(align=True)
            
            # 复选框 - 用于预设编辑
            row.prop(item, "selected", text="", emboss=False, icon='CHECKBOX_HLT' if item.selected else 'CHECKBOX_DEHLT')
            
            # 显示索引
            row.scale_x = 0.1
            row.label(text=f"{index:02d}")
            row.scale_x = 1.0
            
            # 使用操作符按钮来显示项目名称和处理点击事件 - 只用于高亮选中，不改变复选框状态
            is_active = index == context.window_manager.flexmix_index
            props = row.operator("l4d2.toggle_item_selection", text=item.name, emboss=False, 
                               icon='KEYFRAME_HLT' if is_active else 'SHAPEKEY_DATA')
            props.index = index
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='SHAPEKEY_DATA')

    def draw_filter(self, context, layout):
        # 绘制搜索过滤UI
        row = layout.row(align=True)
        row.prop(self, "filter_name", text="", icon='VIEWZOOM')
        row.prop(self, "use_filter_invert", text="", icon='ARROW_LEFTRIGHT')

class FlexmixItem(PropertyGroup):
    # 字典键的名字。对于每一个flexmix_dict中的键，都会有一个FlexmixItem
    name: StringProperty()
    selected: BoolProperty(default=False)
    
class L4D2_OT_FlexMixMoveUp(bpy.types.Operator):
    bl_idname = "l4d2.flexmix_move_up"
    bl_label = _("Move Up")

    def execute(self, context):
        wm = context.window_manager
        # 获取所有选中项的索引，并按照从小到大排序
        selected_indices = [i for i, item in enumerate(wm.flexmix_items) if item.selected]
        selected_indices.sort()
        
        if not selected_indices:
            # 如果没有选中项但有当前索引，则使用当前索引
            if wm.flexmix_index >= 0 and wm.flexmix_index < len(wm.flexmix_items):
                selected_indices = [wm.flexmix_index]
            else:
                self.report({'INFO'}, _("Cannot move: No item selected"))
                return {'CANCELLED'}
        
        # 检查是否有项目已在顶部（索引为0）
        if min(selected_indices) == 0:
            self.report({'INFO'}, _("Cannot move further up: Item already at the top"))
            return {'CANCELLED'}
        
        # 从小到大移动项目，这样可以保证索引不会因为移动而变化
        moved = False
        for i in selected_indices:
            if i > 0:  # 确保不会移动顶部项目
                wm.flexmix_items.move(i, i - 1)
                moved = True
        
        # 更新当前索引，指向第一个移动的项目的新位置
        if moved and selected_indices:
            wm.flexmix_index = selected_indices[0] - 1
        
        return {'FINISHED'}


class L4D2_OT_FlexMixMoveDown(bpy.types.Operator):
    bl_idname = "l4d2.flexmix_move_down"
    bl_label = _("Move Down")

    def execute(self, context):
        wm = context.window_manager
        # 获取所有选中项的索引，并按照从大到小排序（反向）
        selected_indices = [i for i, item in enumerate(wm.flexmix_items) if item.selected]
        selected_indices.sort(reverse=True)  # 从大到小排序
        
        if not selected_indices:
            # 如果没有选中项但有当前索引，则使用当前索引
            if wm.flexmix_index >= 0 and wm.flexmix_index < len(wm.flexmix_items):
                selected_indices = [wm.flexmix_index]
            else:
                self.report({'INFO'}, _("Cannot move: No item selected"))
                return {'CANCELLED'}
        
        # 检查是否有项目已在底部
        if max(selected_indices) >= len(wm.flexmix_items) - 1:
            self.report({'INFO'}, _("Cannot move further down: Item already at the bottom"))
            return {'CANCELLED'}
        
        # 从大到小移动项目，这样可以保证索引不会因为移动而变化
        moved = False
        for i in selected_indices:
            if i < len(wm.flexmix_items) - 1:  # 确保不会移动底部项目
                wm.flexmix_items.move(i, i + 1)
                moved = True
        
        # 更新当前索引，指向第一个移动的项目（在反向排序中是最后一个）的新位置
        if moved and selected_indices:
            wm.flexmix_index = selected_indices[-1] + 1
        
        return {'FINISHED'}

def save_presets(presets):
    with open(flexmix_presets_path, 'w') as f:
        json.dump(presets, f, ensure_ascii=False, indent=4)  # 在这里添加了indent参数

def load_presets():
    if os.path.isfile(flexmix_presets_path):
        with open(flexmix_presets_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(f"解析 JSON 文件时出错: {e}")
                return {}
    else:
        print(f"找不到文件: {flexmix_presets_path}，将使用 flexmix_presets.py 中的字典并创建一个新的 json 文件。")
        presets = flexmix_presets.presets
        save_presets(presets)
        

def get_presets_items(self, context):
    presets = load_presets()
    # 添加"All"选项作为第一个选项
    items = [("All", "All Flexes", "Show all expressions, do not use preset filtering")]
    # 添加预设选项
    items.extend([(k, k, "") for k in presets.keys()])
    return items

def update_presets(self, context):
    # 获取WindowManager和当前选择的预设名
    wm = context.window_manager
    preset_name = wm.presets
    
    # 清除当前项
    wm.flexmix_items.clear()
    
    # 如果选择"All"，则加载所有表情
    if preset_name == "All":
        # 遍历flexmix_dict中的所有键
        for key in flexmix_dict.keys():
            item = wm.flexmix_items.add()
            item.name = key
            item.selected = False
    else:
        # 处理正常预设
        presets = load_presets()
        if preset_name in presets:
            preset = presets[preset_name]
            # 从预设加载项目
            for item_name in preset["order"]:
                if item_name in flexmix_dict:  # 只添加存在于flexmix_dict中的键
                    item = wm.flexmix_items.add()
                    item.name = item_name
                    item.selected = preset["states"].get(item_name, False)
    
    # 确保至少有一个元素被选中
    if len(wm.flexmix_items) > 0:
        wm.flexmix_index = 0

# 在窗口管理器中定义预设库
bpy.types.WindowManager.presets = EnumProperty(
    name=_("presets"),
    description=_("Preset List"),
    items=get_presets_items,
    update=update_presets  # 添加更新函数
)

# 保存预设的操作示例
class L4D2_OT_SaveFlexPreset(bpy.types.Operator):
    bl_idname = "l4d2.save_flex_preset"
    bl_label = _("Save Preset")

    preset_name: StringProperty(name=_("Preset Name"))  # 预设名输入框

    def invoke(self, context, event):
        # 如果当前预设是"All"，则默认新预设名为空
        if context.window_manager.presets == "All":
            self.preset_name = ""
        else:
            # 否则使用当前预设名作为默认值
            self.preset_name = context.window_manager.presets
            
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if not self.preset_name:
            self.report({'ERROR'}, _("Preset name cannot be empty"))
            return {'CANCELLED'}
            
        if self.preset_name == "All":
            self.report({'ERROR'}, _("Cannot use reserved name 'All' as preset name"))
            return {'CANCELLED'}
            
        wm_items = context.window_manager.flexmix_items
        item_order = [item.name for item in wm_items if isinstance(item.name, (str, int, float, bool, type(None)))]
        item_states = {item.name: item.selected for item in wm_items if isinstance(item.selected, (str, int, float, bool, type(None)))}

        presets = load_presets()
        preset_content = {"order": item_order, "states": item_states}
        
        # 检查是否覆盖已有预设
        is_new = self.preset_name not in presets
        presets[self.preset_name] = preset_content  # 将预设名作为键，保存键值对
        save_presets(presets)
        
        if is_new:
            self.report({'INFO'}, f"{_('New preset')} '{self.preset_name}' {_('created')}")
        else:
            self.report({'INFO'}, f"{_('Preset')} '{self.preset_name}' {_('updated')}")
            
        # 设置当前预设为新保存的预设
        context.window_manager.presets = self.preset_name

        return {'FINISHED'}

class L4D2_OT_FlexSelectAction(bpy.types.Operator):
    bl_idname = 'l4d2.select_action'
    bl_label = _('Manipulate the selection state of the list')
    bl_description = _('Select All/Deselect All/Invert Selection')
    bl_options = {'UNDO'}

    action: StringProperty()

    def execute(self, context):
        wm = context.window_manager

        if self.action == 'ALL':
            for item in wm.flexmix_items:
                item.selected = True
        elif self.action == 'INVERSE':
            for item in wm.flexmix_items:
                item.selected = not item.selected
        elif self.action == 'NONE':
            for item in wm.flexmix_items:
                item.selected = False

        return {'FINISHED'}

# 定义一个辅助函数，用于将创建的形态键添加到场景属性中
def add_shape_keys_to_scene_property(context, key_names):
    # 获取当前场景
    scene = context.scene
    # 如果场景中已经有了存储创建键名称集合的属性，则更新这个集合
    if "created_keys" in scene:
        # 将新创建的键名称添加到集合中
        created_keys_set = set(scene["created_keys"]).union(key_names)
    else:
        # 如果场景没有该属性，则创建一个新集合
        created_keys_set = set(key_names)
    # 更新场景的属性
    scene["created_keys"] = list(created_keys_set)

def check_basis_name(shape_keys):
    return '基型' if '基型' in shape_keys.key_blocks else 'Basis'

def create_key(key_name, obj, shape_keys, used_as_final, auxiliary_keys, is_direct_key=False):
    if key_name in flexmix_dict:
        print(f"正在尝试创建形状键: {key_name}")
        mixes = flexmix_dict[key_name]
        was_created = False  # 追踪是否创建了对应的键
        if not mixes:  # 如果mixes为空列表,表示需要创建一个空的形态键
            # 这里我们假设如果形状键块不存在,我们需要先创建一个
            basis_key_name = check_basis_name(shape_keys)

            # 使用设定的基型键名称进行检查和创建  
            if basis_key_name not in shape_keys.key_blocks:
                obj.shape_key_add(name=basis_key_name, from_mix=False)
            # 创建一个新的形态键,没有任何变化
            obj.shape_key_add(name=key_name, from_mix=False)
            was_created = True

        # 遍历需要混合的形态键组合
        for mix in mixes:
            # 检查组合中的每一个单独键是否已经存在
            for sub_key in mix:
                # 如果任一键不存在,则递归创建它
                if sub_key.lower() not in [k.name.lower() for k in shape_keys.key_blocks.values()]:
                    print(f"形状键 {sub_key} 不存在,正在尝试创建...")
                    # 注意这里传入is_direct_key=False因为我们在这个阶段创建的是辅助的形态键
                    create_key(sub_key, obj, shape_keys, used_as_final, auxiliary_keys, is_direct_key=False)
                else:
                    print(f"形状键 {sub_key} 已存在。")
            # 创建当前的形态键前确认所需的键都存在
            if all(k.lower() in [sk.name.lower() for sk in shape_keys.key_blocks.values()] for k in mix):
                # 确保所有现有的形态键都设置为0
                for key_block in shape_keys.key_blocks:
                    key_block.value = 0.0
                # 根据mix字典激活需要的形态键
                for mix_key, mix_value in mix.items():
                    # 获取形状键时忽略大小写
                    found_key = next((sk for sk in shape_keys.key_blocks.values() if sk.name.lower() == mix_key.lower()), None)
                    if found_key: # 确保找到了对应的键
                        found_key.value = mix_value
                # 创建混合的形态键
                obj.shape_key_add(from_mix=True)
                new_key = shape_keys.key_blocks[-1]
                new_key.name = key_name
                was_created = True
                # 重置用于混合的形态键的值为0
                for mix_key in mix:
                    # 可能也需要执行大小写不敏感的匹配来查找对应的键
                    found_key = next((sk for sk in shape_keys.key_blocks.values() if sk.name.lower() == mix_key.lower()), None)
                    if found_key: # 确保找到了对应的键
                        found_key.value = 0.0
                break  # 成功创建形态键,结束循环
        if not was_created and is_direct_key:
            # 检查是否所有需要混合的键都不存在 
            can_mix = any(sub_key in shape_keys.key_blocks for mix in mixes for sub_key in mix)
            # 如果无法混合(即所有需要混合的键都不存在),则创建一个空的键
            if not can_mix:
                basis_key_name = check_basis_name(shape_keys)

                # 使用设定的基型键名称进行检查和创建
                if basis_key_name not in shape_keys.key_blocks:
                    obj.shape_key_add(name=basis_key_name, from_mix=False)
                obj.shape_key_add(name=key_name, from_mix=False)
                was_created = True
                used_as_final.add(key_name)
                print(f"由于相关键都不存在,已创建空键：{key_name}")

        # 如果当前键已被创建
        if was_created:
            # 如果这是直接由用户指定创建的,添加到used_as_final集合
            if is_direct_key:
                used_as_final.add(key_name)
                print(f"成功创建键：{key_name} 并将其标志为最终使用")
                
                # 在此处立即删除辅助键
                keys_to_remove = auxiliary_keys - used_as_final
                for aux_key_name in keys_to_remove:
                    key_index = obj.data.shape_keys.key_blocks.find(aux_key_name)
                    if key_index != -1:
                        obj.active_shape_key_index = key_index
                        bpy.ops.object.shape_key_remove()
                        print(f"删除未使用的辅助键：{aux_key_name}")
                # 清空辅助键集合
                auxiliary_keys.clear()
                        
            # 否则如果它不是已有的辅助键,则添加到auxiliary_keys集合
            else:
                if key_name not in auxiliary_keys:
                    auxiliary_keys.add(key_name)
                    print(f"辅助键 '{key_name}' 加入到集合中")

class L4D2_OT_CreateSelectedKey(bpy.types.Operator):
    bl_idname = "l4d2.create_selected_key"
    bl_label = _("Create Shape Keys")
    bl_description = _('Create shape keys based on the key selected in the drop-down menu')

    def execute(self, context):
        obj = context.object
        wm = context.window_manager

        # 检查是否有模型被选中
        if obj is None:
            self.report({'ERROR'}, _("Need to select a model before proceeding."))
            return {'CANCELLED'}
        # 检查选中的对象是否是网格对象
        if obj.type != 'MESH':
            self.report({'ERROR'}, _("Selected object is not a mesh model. Please select a mesh model to proceed."))
            return {'CANCELLED'}
        shape_keys = obj.data.shape_keys
        if not shape_keys:
            self.report({'ERROR'}, _("No shape key data on the object."))
            return {'CANCELLED'}
            
        # 检查是否有选中的表情项目
        if wm.flexmix_index < 0 or wm.flexmix_index >= len(wm.flexmix_items):
            self.report({'ERROR'}, _("Please select an expression from the list first"))
            return {'CANCELLED'}

        selected_key = wm.flexmix_items[wm.flexmix_index].name

        used_as_final = set()
        auxiliary_keys = set()
        
        bpy.context.object.show_only_shape_key = False
        bpy.context.object.use_shape_key_edit_mode = False
        
        create_key(selected_key, obj, shape_keys, used_as_final, auxiliary_keys, is_direct_key=True)
        
        add_shape_keys_to_scene_property(context, list(used_as_final))

        return {'FINISHED'}


class L4D2_OT_AllCreate(bpy.types.Operator):
    bl_idname = "l4d2.all_create"
    bl_label = _("Batch Create")
    bl_description = _('Batch create shape keys in custom order')
    
    def execute(self, context):
        wm = context.window_manager
        obj = context.object
        # 检查是否有模型被选中
        if obj is None:
            self.report({'ERROR'}, _("Need to select a model before proceeding."))
            return {'CANCELLED'}

        # 检查选中的对象是否是网格对象
        if obj.type != 'MESH':
            self.report({'ERROR'}, _("Selected object is not a mesh model. Please select a mesh model to proceed."))
            return {'CANCELLED'}

        shape_keys = obj.data.shape_keys

        if not shape_keys:
            self.report({'ERROR'}, _("No shape key data on the object."))
            return {'CANCELLED'}

        # 获取用户选择的目标键（从主面板的 UIList 中）
        selected_keys = [item.name for item in wm.flexmix_items if item.selected] 
        
        if not selected_keys:
            self.report({'ERROR'}, _("Please select the expressions to create from the main panel list first"))
            return {'CANCELLED'}

        # 初始化最终使用和辅助键集合
        used_as_final = set()
        auxiliary_keys = set()
        # 退出形态键锁定/编辑模式
        bpy.context.object.show_only_shape_key = False
        bpy.context.object.use_shape_key_edit_mode = False
        # 遍历所有选择的目标键并创建它们
        for key_name in selected_keys:
            create_key(key_name, obj, shape_keys, used_as_final, auxiliary_keys, is_direct_key=True)
        # 将创建的键添加到场景属性中
        add_shape_keys_to_scene_property(context, list(used_as_final))
        print(f"标记为最终使用的键: {used_as_final}")
        
        self.report({'INFO'}, f"{_('Batch created')} {len(used_as_final)} {_('shape keys')}")
        return {'FINISHED'}


class L4D2_OT_SortShapeKeys(bpy.types.Operator):
    bl_idname = "l4d2.sort_shape_keys"
    bl_label = _("Organize Shape Keys")
    bl_description = _('Automatically delete useless shape keys and organize the shape key list\nBe sure to backup')

    def execute(self, context):
        obj = context.object
        # 检查选中的对象是否是网格对象
        if obj.type != 'MESH':
            self.report({'ERROR'}, _("Selected object is not a mesh model. Please select a mesh model to proceed."))
            return {'CANCELLED'}
        # 检查基础形态键的名称并适应不同语言环境
        def check_basis_name():
            basis_name = '基型' if '基型' in shape_keys.keys() else 'Basis'
            print(f"检测到基础形态键的名称为: {basis_name}")  # 打印基础形态键名称
            return basis_name
        
        # 如果场景中包含了 created_keys 属性，保存创建的键名
        if "created_keys" in context.scene:
            created_keys = set(context.scene["created_keys"])
        else:
            self.report({'ERROR'}, _("Tracking information not found. Please create shape keys using the plugin first."))
            return {'CANCELLED'}

        # 退出形态键锁定/编辑模式
        bpy.context.object.show_only_shape_key = False
        bpy.context.object.use_shape_key_edit_mode = False
        
        # 获取当前对象的形态键集合
        shape_keys = bpy.context.object.data.shape_keys.key_blocks
        
        # 找到基础形态键的正确名称 ('基型' 或 'Basis') 并确保其位于第一位
        basis_name = check_basis_name()
        basis_index = shape_keys.keys().index(basis_name) if basis_name in shape_keys.keys() else None
        if basis_index is not None and basis_index != 0:
            bpy.context.object.active_shape_key_index = basis_index
            bpy.ops.object.shape_key_move(type='TOP')

        # 初始化删除计数器
        deleted_keys_count = 0
        
        # 遍历形态键集合，删除不是由特定操作创建的形态键
        for key in shape_keys[:]:  # 复制一份形态键列表用于遍历
            if key.name not in created_keys and key.name != basis_name:  # 如果键名不在创建列表中，并且不是基础形状键
                bpy.context.object.active_shape_key_index = shape_keys.keys().index(key.name)  # 设为活动形态键
                bpy.ops.object.shape_key_remove(all=False)  # 移除当前形态键
                deleted_keys_count += 1  # 删除计数器增加         
        self.report({'INFO'}, f"{_('Deleted')} {deleted_keys_count} {_('redundant shape keys.')}")

        return {'FINISHED'}

# 添加一个快速切换选择状态的操作符
class L4D2_OT_ToggleItemSelection(bpy.types.Operator):
    bl_idname = "l4d2.toggle_item_selection"
    bl_label = _("Toggle Item Selection")
    bl_description = _("Quickly toggle the selection state of the shape key")
    bl_options = {'UNDO', 'INTERNAL'}
    
    index: IntProperty(description=_("Index of the item to toggle"))
    
    def execute(self, context):
        wm = context.window_manager
        if self.index >= 0 and self.index < len(wm.flexmix_items):
            # 只更新活动索引，不改变复选框状态
            wm.flexmix_index = self.index
        return {'FINISHED'}

class L4D2_OT_DeleteFlexPreset(bpy.types.Operator):
    """Delete the currently selected preset"""
    bl_idname = "l4d2.delete_flex_preset"
    bl_label = _("Delete Preset")
    bl_description = _("Delete the currently selected preset. This action cannot be undone.")
    bl_options = {'REGISTER', 'UNDO'} # 添加UNDO选项，虽然文件操作本身不可撤销，但选择更改可以

    @classmethod
    def poll(cls, context):
        # 仅当选中的不是"All"时才启用
        return context.window_manager.presets != "All"

    def invoke(self, context, event):
        # 显示确认对话框
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        wm = context.window_manager
        selected_preset = wm.presets

        # 再次确认不是 "All" (虽然 poll 应已阻止)
        if selected_preset == "All":
            self.report({'ERROR'}, _("Cannot delete the 'All' preset."))
            return {'CANCELLED'}

        presets = load_presets()

        # 检查预设是否存在于字典中
        if selected_preset not in presets:
            self.report({'ERROR'}, f"{_('Preset')} '{selected_preset}' {_('not found, cannot delete.')}")
            # 可能是列表未及时刷新导致的陈旧数据，将选择重置为 'All'
            wm.presets = "All"
            return {'CANCELLED'}

        # 删除预设
        del presets[selected_preset]
        save_presets(presets)

        self.report({'INFO'}, f"{_('Preset')} '{selected_preset}' {_('has been deleted.')}")

        # 删除后将选择重置为 "All" 以刷新列表
        wm.presets = "All"

        return {'FINISHED'}

classes = [
    L4D2_OT_AddToDict,
    L4D2_OT_DeleteFlexKeyPair,
    L4D2_OT_CreateSelectedKey,
    L4D2_OT_AllCreate,
    L4D2_OT_SortShapeKeys,
    L4D2_OT_AddNewFlexKey,
    L4D2_OT_RenameFlexKey,
    FLEXMIX_UL_List,
    L4D2_OT_FlexMixMoveUp,
    L4D2_OT_FlexMixMoveDown,
    FlexmixItem,
    L4D2_OT_DeleteFlexKey,
    L4D2_OT_FlexSelectAction,
    L4D2_OT_SaveFlexPreset,
    L4D2_OT_ToggleItemSelection,  # 添加新的操作符
    L4D2_OT_DeleteFlexPreset,   # 注册新的删除预设操作符
    L4D2_PT_ShapeKeyPanel,  # 确保面板也被注册
]

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            # 抑制重复注册的错误消息
            pass
    
    try:
        # 注册新的捕获项类
        bpy.utils.register_class(FlexCapturedKey)
        
        # 注册窗口管理器属性
        bpy.types.WindowManager.flexmix_items = CollectionProperty(type=FlexmixItem)
        bpy.types.WindowManager.flexmix_index = IntProperty(update=update_flexmix_index) # 当前选中的列表项索引
        
        # 注册场景属性
        bpy.types.Scene.enable_flex_monitoring = BoolProperty(
            name=_("Capture & Add Shape Keys to Expression Group"),
            description=_("Automatically capture shape key changes and display below"),
            default=False
        )
        
        bpy.types.Scene.captured_shape_keys = CollectionProperty(
            type=FlexCapturedKey,
            name=_("Captured Shape Keys"),
            description=_("List of currently captured non-zero shape keys")
        )
        
        # 注册预设属性
        if not hasattr(bpy.types.WindowManager, "presets"):
            bpy.types.WindowManager.presets = EnumProperty(
                name=_("presets"),
                description=_("Preset List"),
                items=get_presets_items,
                update=update_presets  # 添加更新函数
            )
        
        load_presets()
        
        # 加载表情数据
        if not flexmix_dict:
            load_flexmix_dict()
        
        # 添加依赖图更新处理器
        bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post_handler)
            
    except Exception as e:
        # 抑制属性注册错误的消息
        print(f"注册属性时发生错误: {e}")

def unregister():
    # 移除依赖图更新处理器
    if depsgraph_update_post_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post_handler)
    
    try:
        # 注销捕获项类
        bpy.utils.unregister_class(FlexCapturedKey)
    except Exception as e:
        # 抑制错误
        pass
    
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            # 抑制注销错误的消息
            pass
    
    try:
        del bpy.types.WindowManager.flexmix_items
        del bpy.types.WindowManager.flexmix_index
        del bpy.types.Scene.enable_flex_monitoring
        del bpy.types.Scene.captured_shape_keys
    except Exception as e:
        # 抑制删除属性错误的消息
        pass
