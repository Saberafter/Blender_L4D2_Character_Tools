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
from bpy.props import FloatProperty, BoolProperty, IntProperty, CollectionProperty, StringProperty, EnumProperty
from .resources import flex_dict
from .resources import flexmix_presets

# 预设目录路径
preset_dir = os.path.join(bpy.utils.resource_path('USER'), 'scripts', 'presets', 'L4D2 Character Tools')
# JSON文件路径
flexmix_dict_path = os.path.join(preset_dir, 'flex_dict.json')
flexmix_presets_path = os.path.join(preset_dir, 'flexmix_presets.json')

flexmix_dict = {}
key_notes = {}
key_mapping = {}

# 存储非零形态键值的全局列表
current_shape_keys_values = []

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

bpy.types.Scene.flex_keys_enum = EnumProperty(items=init_enum_items,
                                                        update=update_enum)

# 捕捉非零形态键值的操作
class L4D2_OT_StoreShapeKeys(bpy.types.Operator):
    """Capture Non-Zero Deformation Shape Keys"""
    bl_idname = "l4d2.store_shape_keys"
    bl_label = "Shape Keys Capture"

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
            print("非零形态键记录: ", current_shape_keys_values)  # 用于调试

        return {'FINISHED'}
           
class L4D2_OT_AddToDict(bpy.types.Operator):
    """Add the captured shape key values into the currently selected dictionary key"""
    bl_idname = "l4d2.add_to_dict"
    bl_label = "Add to Dict"

    def execute(self, context):
        selected_key = context.scene.flex_keys_enum
        global current_shape_keys_values, flexmix_dict
        if selected_key and current_shape_keys_values:
            current_shape_dict = {name: value for name, value in current_shape_keys_values}
            flexmix_dict[selected_key].append(current_shape_dict)
            save_flexmix_dict(flexmix_dict, key_notes)  # 保存字典到文件
            context.scene.flex_keys_enum = selected_key  # 触发下拉列表的 update 函数，以刷新当前显示的属性
        return {'FINISHED'}

class L4D2_OT_DeleteFlexKeyPair(bpy.types.Operator):
    bl_idname = "l4d2.delete_flex_key_pair"
    bl_label = "Delete Key-Value Pair"
    group_index: IntProperty()  # 组索引，现在直接从1开始以匹配UI表现
    key_id: StringProperty()
    enum_index: IntProperty()  # 枚举索引，从1开始

    def execute(self, context):
        print("正在删除键值对，枚举索引:", self.enum_index, "组索引:", self.group_index, "键ID:", self.key_id)

        selected_key = context.scene.flex_keys_enum
        print("选择的键:", selected_key)

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
                update_enum(context.scene, context)
                
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "无效的组索引,请检查下拉菜单。")
        else:
            self.report({'ERROR'}, "选择的键不存在于字典中。")

        return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
class L4D2_OT_AddNewFlexKey(bpy.types.Operator):
    """Add a new key to the dictionary"""
    bl_idname = "l4d2.add_new_flex_key"
    bl_label = "Add New Key"
    new_key_name: StringProperty(name="Name")
    new_key_note: StringProperty(name="Note")  # 新增：新建键的备注


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        key_name = self.new_key_name
        # 添加判断，如果键名称为空
        if key_name == '':
            self.report({'ERROR'}, f"键名称不能为空!")
            return {'CANCELLED'}
        if key_name in flexmix_dict:
            self.report({'ERROR'}, f"键 '{key_name}' 已经存在!")
            return {'CANCELLED'}


        # 添加新键到字典
        flexmix_dict[key_name] = []
        key_notes[key_name] = self.new_key_note  # 新增：设置新建键的备注
        save_flexmix_dict(flexmix_dict, key_notes)  # 修改：保存时带上 key_notes 字典

        # 更新下拉菜单枚举项
        bpy.types.Scene.flex_keys_enum = EnumProperty(items=init_enum_items(context, None),
                                                                update=update_enum)

        self.report({'INFO'}, f"已添加新键 '{key_name}'.")
        context.scene.flex_keys_enum = key_name  # 选择新添加的键
        return {'FINISHED'}
    
    def draw(self, context):  # 加入此方法，给对话框添加输入字段
        self.layout.prop(self, "new_key_name")
        self.layout.prop(self, "new_key_note")

class L4D2_OT_RenameFlexKey(bpy.types.Operator):
    """Rename the key currently selected in the drop-down menu"""
    bl_idname = "l4d2.rename_flex_key"
    bl_label = "Rename Key"
    new_key_name: StringProperty(name="Name")
    new_key_note: StringProperty(name="Note")  # 新增：重命名键后的备注

    def invoke(self, context, event):
        selected_key = context.scene.flex_keys_enum
        if not selected_key:
            self.report({'ERROR'}, "没有选中任何键")
            return {'CANCELLED'}
        self.new_key_name = selected_key
        self.new_key_note = key_notes.get(self.new_key_name, "")  # 加入此行，初始化新键备注的值
        return context.window_manager.invoke_props_dialog(self)  # 加入此行，创建一个包含操作属性的对话框

    def execute(self, context):
        global flexmix_dict
        global key_notes
        old_key_name = context.scene.flex_keys_enum
        new_key_name = self.new_key_name
        old_key_note = key_notes.get(old_key_name, "")
        new_key_note = self.new_key_note

        # 添加判断，如果新键名为空
        if new_key_name == '':
            self.report({'ERROR'}, f"键名称不能为空!")
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
                    self.report({'INFO'}, f"键 '{old_key_name}' 已重命名为 '{new_key_name}'.")
                elif new_key_name == old_key_name and new_key_note != old_key_note:
                    self.report({'INFO'}, f"键 '{old_key_name}' 的备注已更改。")
                elif new_key_name != old_key_name and new_key_note != old_key_note:
                    self.report({'INFO'}, f"键 '{old_key_name}' 已重命名为 '{new_key_name}'，且备注已更改。")
            else:
                new_flexmix_dict[key] = value
                new_key_notes[key] = key_notes.get(key, "")  # 保留原来的备注

        # 替换原字典和备注字典
        flexmix_dict = new_flexmix_dict
        key_notes = new_key_notes
        save_flexmix_dict(flexmix_dict, key_notes)  # 保存时带上 key_notes 字典

        # 更新下拉菜单枚举项
        bpy.types.Scene.flex_keys_enum = EnumProperty(items=init_enum_items(context, None),
                                                                update=update_enum)
        context.scene.flex_keys_enum = new_key_name  # 选择已重命名的键
        return {'FINISHED'}
    
    def draw(self, context):  # 加入此方法，给对话框添加输入字段
        self.layout.prop(self, "new_key_name")
        self.layout.prop(self, "new_key_note")

class L4D2_OT_DeleteFlexKey(bpy.types.Operator):
    """Delete the currently selected key and its key-value pair"""
    bl_idname = "l4d2.delete_flex_key"
    bl_label = "Delete Key"
    
    def execute(self, context):
        global flexmix_dict
        global key_notes  # 保证我们操作的是全局变量
        selected_key = context.scene.flex_keys_enum

        # 删除键及其数据
        if selected_key and selected_key in flexmix_dict:
            # 删除键
            del flexmix_dict[selected_key]
            if selected_key in key_notes:  # 如果备注中有此键，也一并删除
                del key_notes[selected_key]
            save_flexmix_dict(flexmix_dict, key_notes)  # 保存时同时保存备注

            # 更新下拉菜单
            update_flex_keys_enum_items()

            # 如果存在其他键，则自动选择第一个键
            keys = list(flexmix_dict.keys())
            if keys:
                context.scene.flex_keys_enum = keys[0]

            self.report({'INFO'}, f"键 '{selected_key}' 及其数据已删除")
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "没有找到键或键未选中")
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class L4D2_PT_ShapeKeyPanel(bpy.types.Panel):
    bl_label = "L4D2 ShapeKey Tools"
    bl_idname = "L4D2_PT_ShapeKey"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("l4d2.create_selected_key", icon="ADD")
        row.operator("l4d2.all_create",text = 'Batch Create', icon="ADD")
        layout.operator("l4d2.sort_shape_keys", icon="SORTSIZE")
        row = layout.row()
        row.operator("l4d2.store_shape_keys", icon= "ZOOM_ALL")
        row.operator("l4d2.add_to_dict", icon= "RNA_ADD")
        row = layout.row()



        obj = context.active_object
        if current_shape_keys_values and obj and obj.type == 'MESH' and obj.data.shape_keys:
            # 当当前形态键值列表有内容时，再绘制形态键显示框
            box = layout.box() 
            # 展示非零形态键
            for key_name, _ in current_shape_keys_values:
                key_block = obj.data.shape_keys.key_blocks.get(key_name)
                if key_block:
                    box.prop(key_block, "value", text=key_name, slider=True)
        row = layout.row(align=True)
        row.prop(context.scene, "flex_keys_enum", text='')
        row.operator("l4d2.add_new_flex_key", text="", icon="ADD")
        row.operator("l4d2.rename_flex_key", text="", icon="GREASEPENCIL")
        row.operator("l4d2.delete_flex_key", text="", icon="X") 
        key_name = context.scene.flex_keys_enum
        note_name = key_notes.get(key_name, "")
        box = layout.box()
        box.label(text=note_name)

        scene = context.scene
        last_group_index = None  # 为了区分不同列表的开始，这里指的是（enum_index, group_index）的组合
        box = None

        # attr格式: flex_key_group_{枚举索引}_{组索引}_{键索引}
        for attr in sorted((a for a in dir(scene) if a.startswith("flex_key_group_")), key=lambda x: (int(x.split("_")[3]), int(x.split("_")[4]), int(x.split("_")[5]))):
            enum_index, group_index, key_index = map(int, attr.split("_")[3:])

            if (enum_index, group_index) != last_group_index:
                box = layout.box()
                last_group_index = (enum_index, group_index)
                
            if box is not None:
                row = box.row()
                row.prop(scene, attr)
                
                # 传递 enum_index 和 key_id 给操作符
                op = row.operator("l4d2.delete_flex_key_pair", text="", icon="X")
                op.enum_index = enum_index
                op.group_index = group_index  # 直接添加组索引，不做调整
                op.key_id = "_".join(attr.split("_")[3:])


# UI列表项类定义
class FLEXMIX_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "selected", text="", emboss=False, icon='CHECKBOX_HLT' if item.selected else 'CHECKBOX_DEHLT')
            row.scale_x = 0.1
            row.label(text=str(index))  # 新增的代码: 在列表每一项前面加一个数字顺序
            row.scale_x = 0.9
            row.prop(item, "name", text="", emboss=False, icon='SHAPEKEY_DATA')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='SHAPEKEY_DATA')

    
class FlexmixItem(PropertyGroup):
    # 字典键的名字。对于每一个flexmix_dict中的键，都会有一个FlexmixItem
    name: StringProperty()
    selected: BoolProperty(default=False)
    
class L4D2_OT_FlexMixMoveUp(bpy.types.Operator):
    bl_idname = "l4d2.flexmix_move_up"
    bl_label = "Move Up"

    def execute(self, context):
        wm = context.window_manager
        moved_items_indices = [i for i, item in enumerate(wm.flexmix_items) if item.selected]

        if len(moved_items_indices) > 1:
            for i in moved_items_indices:
                if i > 0 and wm.flexmix_items:
                    wm.flexmix_items.move(i, i - 1)
            wm.flexmix_index = max(0, moved_items_indices[0] - 1)
            return {'FINISHED'}
        elif len(moved_items_indices) == 1 or wm.flexmix_index > 0:
            index = wm.flexmix_index
            wm.flexmix_items.move(index, index - 1)
            wm.flexmix_index = max(0, index - 1)
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "无法继续向上移动项目")
            return {'CANCELLED'}


class L4D2_OT_FlexMixMoveDown(bpy.types.Operator):
    bl_idname = "l4d2.flexmix_move_down"
    bl_label = "Move Down"

    def execute(self, context):
        wm = context.window_manager
        moved_items_indices = [i for i, item in enumerate(wm.flexmix_items) if item.selected]

        if len(moved_items_indices) > 1:
            for i in reversed(moved_items_indices):
                if i < len(wm.flexmix_items) - 1:
                    wm.flexmix_items.move(i, i + 1)
            wm.flexmix_index = min(len(wm.flexmix_items) - 1, moved_items_indices[-1] + 1)
            return {'FINISHED'}
        elif len(moved_items_indices) == 1 or wm.flexmix_index < len(wm.flexmix_items) - 1:
            index = wm.flexmix_index
            wm.flexmix_items.move(index, index + 1)
            wm.flexmix_index = min(len(wm.flexmix_items) - 1, index + 1)
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "无法继续向下移动项目")
            return {'CANCELLED'}

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
    items = [(k, k, "") for k in presets.keys()]
    return items

def update_presets(self, context):
    # 获取所有预设
    presets = load_presets()
    # 从 WindowManager 获取当前选中的预设名
    preset_name = context.window_manager.presets

    # 检查预设是否存在
    if preset_name in presets: 
        preset = presets[preset_name]

        # 清除当前项
        wm = context.window_manager
        wm.flexmix_items.clear()

        # 从预设加载项目
        for item_name in preset["order"]:
            item = wm.flexmix_items.add()
            item.name = item_name
            item.selected = preset["states"].get(item_name, False)


# 在窗口管理器中定义预设库
bpy.types.WindowManager.presets = EnumProperty(
    name="presets",
    description="Preset List",
    items=get_presets_items,
    update=update_presets  # 添加更新函数
)

# 保存预设的操作示例
class L4D2_OT_SaveFlexPreset(bpy.types.Operator):
    bl_idname = "l4d2.save_flex_preset"
    bl_label = "Save Preset"

    preset_name: StringProperty(name="Preset Name")  # 新增的预设名输入框

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        wm_items = context.window_manager.flexmix_items
        item_order = [item.name for item in wm_items if isinstance(item.name, (str, int, float, bool, type(None)))]
        item_states = {item.name: item.selected for item in wm_items if isinstance(item.selected, (str, int, float, bool, type(None)))}

        presets = load_presets()
        preset_content = {"order": item_order, "states": item_states}
        
        presets[self.preset_name] = preset_content  # 将预设名作为键，保存键值对
        save_presets(presets) 

        return {'FINISHED'}

class L4D2_OT_FlexSelectAction(bpy.types.Operator):
    bl_idname = 'l4d2.select_action'
    bl_label = 'Manipulate the selection state of the list'
    bl_description = 'Select All/Deselect All/Invert Selection'
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
    bl_label = "Create Shape Keys"
    bl_description = 'Create shape keys based on the key selected in the drop-down menu'

    def execute(self, context):
        obj = context.object
        shape_keys = obj.data.shape_keys

        if not shape_keys:
            self.report({'ERROR'}, "对象上没有形态键数据。")
            return {'CANCELLED'}

        selected_key = context.scene.flex_keys_enum

        used_as_final = set()
        auxiliary_keys = set()
        
        bpy.context.object.show_only_shape_key = False
        bpy.context.object.use_shape_key_edit_mode = False
        
        create_key(selected_key, obj, shape_keys, used_as_final, auxiliary_keys, is_direct_key=True)
        
        add_shape_keys_to_scene_property(context, list(used_as_final))


        return {'FINISHED'}


class L4D2_OT_AllCreate(bpy.types.Operator):
    bl_idname = "l4d2.all_create"
    bl_label = ""
    bl_description = 'Batch create shape keys in custom order'
    
    def invoke(self, context, event):
        # 获取 WindowManager
        wm = context.window_manager

        # 清空现有的列表项
        wm.flexmix_items.clear()

        # 从flexmix_dict中填充列表项
        for key in flexmix_dict.keys():
            item = wm.flexmix_items.add()
            item.name = key

        # 重置当前选中的索引
        wm.flexmix_index = 0

        # 调用弹窗
        return wm.invoke_props_dialog(self, width=250)

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        row = layout.row()
        left = row.column_flow(columns=1, align=True)
        box = left.box().row()

        # 创建全选/反选二合一的按钮和反选按钮
        box_left = box.row(align=True)
        # 创建全选/反选按钮
        if wm.flexmix_items:
            if all(item.selected for item in wm.flexmix_items):
                op = box_left.operator('l4d2.select_action', text='', icon='CHECKBOX_HLT')
                op.action = 'NONE'
            else:
                op = box_left.operator('l4d2.select_action', text='', icon='CHECKBOX_DEHLT')
                op.action = 'ALL'
                # 如果有选中的项,则显示反选按钮
                if any(item.selected for item in wm.flexmix_items):
                    op_inverse = box_left.operator('l4d2.select_action', text='', icon='UV_SYNC_SELECT')
                    op_inverse.action = 'INVERSE'
        box_right = box.row(align=False)
        box_right.alignment = 'LEFT'
        # 添加UIList控件
        left.template_list("FLEXMIX_UL_List", "", wm, "flexmix_items", wm, "flexmix_index")
        # 添加预设控件
        row = layout.row()
        row.prop(wm, "presets", text="Preset")
        row.operator("l4d2.save_flex_preset", text="", icon="ADD")
        #row.operator("l4d2.load_flex_preset", text="", icon="IMPORT")

        # 绘制上下移操作按钮
        col = layout.column(align=True)
        col.operator("l4d2.flexmix_move_up", icon='TRIA_UP', text="")
        col.operator("l4d2.flexmix_move_down", icon='TRIA_DOWN', text="")

    def execute(self, context):
        wm = context.window_manager
        obj = context.object
        shape_keys = obj.data.shape_keys  

        if not shape_keys:
            self.report({'ERROR'}, "对象上没有形态键数据。")
            return {'CANCELLED'}

        # 获取用户选择的目标键
        selected_keys = [item.name for item in wm.flexmix_items if item.selected] 

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

        return {'FINISHED'}


class L4D2_OT_SortShapeKeys(bpy.types.Operator):
    bl_idname = "l4d2.sort_shape_keys"
    bl_label = "Organize Shape Keys"
    bl_description = 'Automatically delete useless shape keys and organize the shape key list\nBe sure to backup'

    def execute(self, context):
        # 检查基础形态键的名称并适应不同语言环境
        def check_basis_name():
            return '基型' if '基型' in shape_keys.keys() else 'Basis'

        # 如果场景中包含了 created_keys 属性，保存创建的键名
        if "created_keys" in context.scene:
            created_keys = set(context.scene["created_keys"])
        else:
            self.report({'WARNING'}, "没有找到创建键的跟踪信息。")
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

        # 遍历形态键集合，删除不是由特定操作创建的形态键
        for key in shape_keys[:]:  # 复制一份形态键列表用于遍历
            if key.name not in created_keys and key.name != basis_name:  # 如果键名不在创建列表中，并且不是基础形状键
                bpy.context.object.active_shape_key_index = shape_keys.keys().index(key.name)  # 设为活动形态键
                bpy.ops.object.shape_key_remove(all=False)  # 移除当前形态键

        return {'FINISHED'}


classes = [
    L4D2_OT_StoreShapeKeys,
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
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.flexmix_items = CollectionProperty(type=FlexmixItem)
    bpy.types.WindowManager.flexmix_index = IntProperty() # 当前选中的列表项索引
    load_presets()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
