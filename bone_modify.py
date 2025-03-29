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
import json
import os
from .resources import bone_dict

preset_dir = os.path.join(bpy.utils.resource_path('USER'), 'scripts', 'presets', 'L4D2 Character Tools')
COMMON_MAPPING_FILE_PATH = os.path.join(preset_dir,"bone_dict.json")
MAPPING_PRESETS_DIR = os.path.join(preset_dir, "mapping_presets")
current_bone_mapping = {}
current_unique_mapping = {}
current_common_mapping = {}

def simplify_bonename(n):
    return n.lower().translate(dict.fromkeys(map(ord, u" _.")))

# 保存骨骼字典到文件
def save_common_mapping(common_mapping_dict):
    try:
        with open(COMMON_MAPPING_FILE_PATH, 'w') as f:
            json.dump(common_mapping_dict, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存文件时发生错误: {e}")

# 使用全局变量从文件加载骨骼字典
def load_common_mapping():
    global current_common_mapping
    # 确保预设目录存在，如果不存在则创建它
    if not os.path.isdir(preset_dir):
        os.makedirs(preset_dir)
    if os.path.isfile(COMMON_MAPPING_FILE_PATH):
        try:
            with open(COMMON_MAPPING_FILE_PATH, 'r') as f:
                current_common_mapping = json.load(f)
        except json.JSONDecodeError as e:
            print(f"读取JSON文件时发生解析错误: {e}")
            # 如果解析错误，转而使用 bone_dict.py 里的字典
            current_common_mapping = bone_dict.common_mapping
            save_common_mapping(current_common_mapping)  # 将 python 字典写入新的 json 文件
    else:
        print(f"找不到文件: {COMMON_MAPPING_FILE_PATH}，将使用 bone_dict.py 中的字典并创建一个新的 json 文件。")
        current_common_mapping = bone_dict.common_mapping
        save_common_mapping(current_common_mapping)  # 将 python 字典写入新的 json 文件

# 初始化函数
def initialize_mapping_presets():
    print("开始初始化预设...")
    if not os.path.exists(MAPPING_PRESETS_DIR):
        os.makedirs(MAPPING_PRESETS_DIR)
        print(f"创建预设目录: {MAPPING_PRESETS_DIR}")
        
    # 检查并创建默认预设
    default_preset_path = os.path.join(MAPPING_PRESETS_DIR, "Valve_L4D2.json")
    if not os.path.exists(default_preset_path):
        default_preset = {
            "name": "Valve_L4D2",
            "official_mapping": bone_dict.bone_mapping,
            "unique_mapping": {}
        }
        
        try:
            with open(default_preset_path, 'w', encoding='utf-8') as f:
                json.dump(default_preset, f, indent=4, ensure_ascii=False)
            print("成功创建默认预设文件")
        except Exception as e:
            print(f"创建默认预设时发生错误: {str(e)}")

def error_handler(func):
    """统一的错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"{func.__name__} 发生错误: {str(e)}")
            return False
    return wrapper

class MappingDataManager:
    @staticmethod
    @error_handler
    def get_temp_data(context):
        """获取temp_data中的所有映射数据"""
        return {
            'official': json.loads(context.scene.mapping_temp_data.temp_official_mapping),
            'unique': json.loads(context.scene.mapping_temp_data.temp_unique_mapping),
            'common': json.loads(context.scene.mapping_temp_data.temp_common_mapping)
        }

    @staticmethod
    @error_handler
    def save_temp_data(context, temp_data):
        """保存映射数据到temp_data"""
        for key, value in temp_data.items():
            setattr(context.scene.mapping_temp_data, f'temp_{key}_mapping', json.dumps(value))
        return True

    @staticmethod
    def _add_mapping_item(scene, official, common, source_tab, custom_bones):
        """添加一个映射项到UI列表"""
        item = scene.mapping_list.add()
        item.official_bone = official
        item.common_bone = common
        item.source_tab = source_tab
        
        for custom_name in custom_bones:
            bone = item.custom_bones.add()
            bone.name = custom_name
            bone.is_selected = False

    @staticmethod
    @error_handler
    def update_ui_list(context):
        """更新UI列表显示"""
        scene = context.scene
        scene.mapping_list.clear()
        
        temp_data = MappingDataManager.get_temp_data(context)
        if not temp_data:
            return False
            
        added_commons = set()
        
        if scene.mapping_ui_tab == 'ALL':
            # 全部映射：显示所有映射关系
            # 首先添加所有官方映射
            for official, commons in temp_data['official'].items():
                for common in commons:
                    if common not in added_commons:
                        added_commons.add(common)
                        MappingDataManager._add_mapping_item(scene, official, common, 'ALL',
                            temp_data['common'].get(common, []) or temp_data['unique'].get(common, []))
            
            # 然后添加所有独立映射（不在官方映射中的通用骨骼映射）
            for common, customs in temp_data['unique'].items():
                if common not in added_commons:
                    added_commons.add(common)
                    MappingDataManager._add_mapping_item(scene, "", common, 'UNIQUE', customs)
            
            # 最后添加所有通用映射（不在官方映射和独立映射中的通用骨骼映射）
            for common, customs in temp_data['common'].items():
                if common not in added_commons:
                    added_commons.add(common)
                    MappingDataManager._add_mapping_item(scene, "", common, 'COMMON', customs)
                    
        elif scene.mapping_ui_tab == 'UNIQUE':
            # 独立映射：显示不在通用映射中的映射关系，以及来源为UNIQUE的映射
            for common, customs in temp_data['unique'].items():
                if common not in temp_data['common'] or any(item.source_tab == 'UNIQUE' for item in scene.mapping_list):
                    MappingDataManager._add_mapping_item(scene, "", common, 'UNIQUE', customs)
        
        else:  # COMMON
            # 通用映射：显示在通用映射中的映射关系，以及来源为COMMON的映射
            for common, customs in temp_data['common'].items():
                if common in temp_data['common'] or any(item.source_tab == 'COMMON' for item in scene.mapping_list):
                    MappingDataManager._add_mapping_item(scene, "", common, 'COMMON', customs)
        
        return True

    @staticmethod
    @error_handler
    def remove_mapping(context, list_index):
        """删除一个映射关系"""
        scene = context.scene
        item = scene.mapping_list[list_index]
        temp_data = MappingDataManager.get_temp_data(context)
        if not temp_data:
            return False
        
        # 根据标签页删除相应数据
        if scene.mapping_ui_tab == 'ALL':
            if item.official_bone:
                temp_data['official'].pop(item.official_bone, None)
            if item.common_bone:
                temp_data['unique'].pop(item.common_bone, None)
                temp_data['common'].pop(item.common_bone, None)
        else:
            key = 'unique' if scene.mapping_ui_tab == 'UNIQUE' else 'common'
            if item.common_bone:
                temp_data[key].pop(item.common_bone, None)
        
        return MappingDataManager.save_temp_data(context, temp_data)

    @staticmethod
    @error_handler
    def remove_custom_bone(context, list_index, bone_name):
        """从映射中删除自定义骨骼"""
        item = context.scene.mapping_list[list_index]
        temp_data = MappingDataManager.get_temp_data(context)
        if not temp_data or not item.common_bone:
            return False
        
        # 从所有映射中删除骨骼
        for key in ['common', 'unique']:
            if item.common_bone in temp_data[key]:
                if bone_name in temp_data[key][item.common_bone]:
                    temp_data[key][item.common_bone].remove(bone_name)
                    if not temp_data[key][item.common_bone]:
                        del temp_data[key][item.common_bone]
        
        return MappingDataManager.save_temp_data(context, temp_data)

    @staticmethod
    @error_handler
    def save_ui_list(context):
        """保存UI列表到temp_data"""
        scene = context.scene
        temp_data = MappingDataManager.get_temp_data(context)
        if not temp_data:
            return False

        # 创建新的字典来存储更新后的映射
        new_official = dict(temp_data['official'])  # 保留原有的映射
        new_unique = dict(temp_data['unique'])  # 保留原有的映射
        temp_common = dict(temp_data['common'])  # 保留原有的映射

        # 创建集合来跟踪已处理的骨骼名称
        processed_common_bones = set()

        # 第一遍遍历：收集所有需要处理的官方骨骼名称
        official_to_common = {}  # 临时存储当前UI列表中的官方骨骼到通用骨骼的映射
        for item in scene.mapping_list:
            if item.official_bone and item.common_bone:
                official_to_common[item.official_bone] = item.common_bone

        # 处理官方映射的更新
        for official, common in official_to_common.items():
            # 检查是否存在使用相同通用骨骼的其他官方骨骼
            for old_official in list(new_official.keys()):
                if old_official != official and new_official[old_official] == [common]:
                    del new_official[old_official]  # 删除旧的映射
            new_official[official] = [common]  # 添加或更新映射

        # 第二遍遍历：处理通用骨骼和自定义骨骼的映射
        for item in scene.mapping_list:
            # 确保每个骨骼名称只出现一次
            custom_bones = list(dict.fromkeys([bone.name for bone in item.custom_bones]))
            
            # 如果这个通用骨骼已经处理过，跳过它
            if item.common_bone in processed_common_bones:
                continue
            
            # 将当前通用骨骼添加到已处理集合
            if item.common_bone:
                processed_common_bones.add(item.common_bone)

            # 如果有通用骨骼和自定义骨骼，根据source_tab决定存储位置
            if item.common_bone and custom_bones:
                # 检查是否需要更新通用骨骼名称
                old_common = None
                # 在官方映射中查找并更新
                for off_key, off_val in list(new_official.items()):
                    if off_val and off_val[0] != item.common_bone and set(custom_bones) == set(new_unique.get(off_val[0], [])):
                        old_common = off_val[0]
                        new_official[off_key] = [item.common_bone]

                # 在独立映射中查找并更新
                for uni_key, uni_val in list(new_unique.items()):
                    if uni_key != item.common_bone and set(uni_val) == set(custom_bones):
                        old_common = uni_key
                        del new_unique[uni_key]

                # 在通用映射中查找并更新
                for com_key, com_val in list(temp_common.items()):
                    if com_key != item.common_bone and set(com_val) == set(custom_bones):
                        old_common = com_key
                        del temp_common[com_key]

                # 根据source_tab决定存储位置
                if item.source_tab == 'COMMON' or (item.source_tab == 'ALL' and item.common_bone in temp_common):
                    # 存储到通用映射
                    temp_common[item.common_bone] = custom_bones
                else:
                    # 存储到独立映射
                    new_unique[item.common_bone] = custom_bones

        # 更新temp_data
        temp_data = {
            'official': new_official,
            'unique': new_unique,
            'common': temp_common
        }
        
        return MappingDataManager.save_temp_data(context, temp_data)

    @staticmethod
    def load_preset_data(context, preset_name):
        """从预设文件加载数据并更新全局变量和Blender属性"""
        global current_bone_mapping, current_unique_mapping, current_common_mapping
        
        preset_path = os.path.join(MAPPING_PRESETS_DIR, f"{preset_name}.json")
        if not os.path.exists(preset_path):
            return False, f"预设 {preset_name} 不存在!"
            
        try:
            with open(preset_path, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            # 更新全局变量
            current_bone_mapping = preset_data.get('official_mapping', {})
            current_unique_mapping = preset_data.get('unique_mapping', {})
            load_common_mapping()  # 加载通用映射
            
            # 更新Blender属性
            for prefix in ['main', 'temp']:
                data = getattr(context.scene, f'mapping_{prefix}_data')
                setattr(data, f'{prefix}_official_mapping', json.dumps(current_bone_mapping))
                setattr(data, f'{prefix}_unique_mapping', json.dumps(current_unique_mapping))
                setattr(data, f'{prefix}_common_mapping', json.dumps(current_common_mapping))
            
            # 更新当前活动预设名称
            context.scene.active_preset_name = preset_name
            
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    @error_handler
    def save_mapping_preset(context, preset_name):
        """保存当前映射到预设文件"""
        if not preset_name:
            return False
            
        preset_path = os.path.join(MAPPING_PRESETS_DIR, f"{preset_name}.json")
        try:
            # 从temp_data获取当前映射数据
            temp_data = MappingDataManager.get_temp_data(context)
            if not temp_data:
                return False
            
            # 准备预设数据
            preset_data = {
                "name": preset_name,
                "official_mapping": temp_data['official'],
                "unique_mapping": temp_data['unique']
            }
            
            # 保存到预设文件
            with open(preset_path, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=4, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"保存预设时发生错误: {str(e)}")
            return False

    @staticmethod
    def update_mapping_list(self, context):
        """当标签页改变时的回调函数"""
        # 如果是从其他标签页切换过来的（self不为None），先保存当前列表的修改
        if self is not None:
            print("检测到标签页切换，保存当前列表修改...")
            if not MappingDataManager.save_ui_list(context):
                print("保存当前列表修改失败")
                return None
        
        # 更新UI列表
        if not MappingDataManager.update_ui_list(context):
            print("更新UI列表失败")
            return None
        
        return None

class L4D2_OT_RiggingOperator(bpy.types.Operator):
    bl_idname = "l4d2.rigging_operator"
    bl_label = "Align Bone"
    bl_description = "Align bones by batch adding copy location constrains to the bones\nThe mechanism of bone alignment is based on the mapping dictionary\n1、Ensure the TPOSE is approximately consistent\n2、Make sure the name of the skeleton is the same as the name of the first level under the skeleton"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 原理:
        # 通过批量添加复制位置的骨骼约束来自动对骨，
        # 对骨匹配机制来源于脚本内置字典，
        # 使用之前请确保两具骨架的TPOSE姿势是一致或近似一致的（例如大拇指的旋转角度）。

        # 检查：
        # 脚本运行前需要手动设置两具骨架的名字，
        # 骨骼映射关系字典在外置文件lib.py中，可在括号中补充更多对应骨骼名字

        # 流程：
        # 脚本运行开始于对齐盆骨Y轴前，
        # 脚本运行结束于添加骨骼约束（对骨）完毕后。
        # 请应用静置姿态后清除两具骨架的骨骼约束再开始后续操作。

        # 开始执行：
        # 加载全局的骨骼名字典
        load_common_mapping()

        # 开始执行：
        # 获取A骨架和B骨架
        armature_A = context.scene.Valve_Armature
        armature_B = context.scene.Custom_Armature

        # 确保在物体模式
        if bpy.context.active_object is not None:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        else:
            # 如果没有活动对象，尝试选择骨架A作为活动对象
            bpy.context.view_layer.objects.active = armature_A
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # 设置骨架A为姿势模式
        bpy.ops.object.select_all(action='DESELECT')
        armature_A.select_set(True)
        bpy.context.view_layer.objects.active = armature_A
        bpy.ops.object.mode_set(mode='POSE')

        # 已添加约束的骨骼名集合
        added_constraints = set()

        for bone in armature_B.data.bones:
            # 简化骨骼名，并使用简化后的骨骼名在字典 common_mapping 中查找对应的键
            simplified_name = simplify_bonename(bone.name)
            bone_name_from_global_bones = next((key for key, value in current_common_mapping.items() if simplified_name in value), None)
            # 如果找到了键，那么就将这个键用于在字典 bone_dict.bone_mapping 中查找对应的键
            if bone_name_from_global_bones:
                bone_name_in_mapping = next((key for key, value in bone_dict.bone_mapping.items() if bone_name_from_global_bones in value), None)
                # 如果在字典 bone_dict.bone_mapping 中找到了匹配的键，那么就将该键用于创建骨架A的骨骼约束，并将约束目标设置为当前遍历到的骨架B的骨骼
                if bone_name_in_mapping:
                    constraint_target_bone_name = bone.name
                    bone_A_name = bone_name_in_mapping
                    # 判断骨骼名是否在 armature_A 的 pose 骨骼中
                    if bone_A_name in armature_A.pose.bones:
                        # 如果在，则为该骨骼添加约束，并记录到集合中
                        constraint = armature_A.pose.bones[bone_A_name].constraints.new('COPY_LOCATION')
                        constraint.target = armature_B
                        constraint.subtarget = constraint_target_bone_name
                        constraint.head_tail = 0
                        # 将骨骼名添加到已添加约束的集合中
                        added_constraints.add(bone_A_name)


        # 通过备选字典尝试添加任何遗漏的骨骼约束
        for bone_A_name, bone_B_names in bone_dict.bone_mapping.items():
            # 如果骨骼名已经在第一次循环中添加了约束，则跳过
            if bone_A_name in added_constraints:
                continue

            for bone_B_name in bone_B_names:
                # 尝试从 B 骨架中获取骨骼
                bone_B = armature_B.pose.bones.get(bone_B_name)
                if not bone_B:
                    print(f"Bone '{bone_B_name}' not found in armature B")
                    continue

                # 尝试从 A 骨架中获取骨骼
                bone_A = armature_A.pose.bones.get(bone_A_name)
                if not bone_A:
                    print(f"Bone '{bone_A_name}' not found in armature A")
                    continue

                # 为 A 骨架中的骨骼添加复制位置的骨骼约束
                constraint = bone_A.constraints.new('COPY_LOCATION')
                constraint.target = armature_B
                constraint.subtarget = bone_B.name
                constraint.head_tail = 0

                # 添加当前骨骼到集合中，避免未来重复添加约束
                added_constraints.add(bone_A_name)
                
        # 取消A骨架中名为 ValveBiped.Bip01_Pelvis 的骨骼的复制位置约束中的Z轴约束
        pelvis_bone_A = armature_A.pose.bones.get('ValveBiped.Bip01_Pelvis')
        if pelvis_bone_A:
            for constraint in pelvis_bone_A.constraints:
                if constraint.type == 'COPY_LOCATION' and constraint.target == armature_B:
                    constraint.use_z = False

        # 骨骼约束添加完成
        return {'FINISHED'}

class L4D2_OT_GraftingOperator(bpy.types.Operator):
    bl_idname = "l4d2.grafting_operator"
    bl_label = "Graft Bone"
    bl_description = "Automatically set the parent-child level of bones based on bone mapping relationships"
    bl_options = {'REGISTER', 'UNDO'}

    threshold = 0.01  # 设置阈值

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "未选中骨架对象或选中的不是骨架类型")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')  # 切换到编辑模式
        arm = obj.data
        edit_bones = arm.edit_bones

        # 当前选中的骨骼列表
        selected_bones = [bone for bone in edit_bones if bone.select]

        # 如果有选中的骨骼
        if selected_bones:
            for bone in selected_bones:
                if bone.name in bone_dict.bone_mapping.keys():
                    for target_bone in selected_bones:
                        if bone != target_bone:
                            # 计算距离
                            distance = (bone.head - target_bone.head).length
                            if distance < self.threshold:
                                # 在设置父级之前，检查是否有骨骼连接并处理
                                if target_bone.use_connect:
                                    target_bone.use_connect = False
                                # 设置父子关系
                                target_bone.parent = bone
                elif bone.name in bone_dict.bone_mapping.values():
                    # 直接设置为字典中键的子级
                    for parent_name, child_names in bone_dict.bone_mapping.items():
                        if bone.name in child_names:
                            parent_bone = edit_bones.get(parent_name)
                            if parent_bone:
                                if bone.use_connect:
                                    bone.use_connect = False
                                bone.parent = parent_bone
                else:
                    # 如果骨骼名称不在bone_dict.bone_mapping的值当中，简化骨骼名称
                    simplified_name = simplify_bonename(bone.name)
                    for parent_name, child_names in current_common_mapping.items():
                        if simplified_name in child_names:
                            for map_par_name, map_child_names in bone_dict.bone_mapping.items():
                                if parent_name in map_child_names:
                                    parent_bone = edit_bones.get(map_par_name)
                                    if parent_bone:
                                        if bone.use_connect:
                                            bone.use_connect = False
                                        bone.parent = parent_bone

        # 没有选中的骨骼时，先按照原有的bone_mapping设置父子关系
        else:
            for parent_name, child_names in bone_dict.bone_mapping.items():
                parent_bone = edit_bones.get(parent_name)
                if parent_bone is None:
                    continue
                for child_name in child_names:
                    child_bone = edit_bones.get(child_name)
                    if child_bone:
                        if child_bone.use_connect:
                            child_bone.use_connect = False
                        child_bone.parent = parent_bone
            # 然后再按照新增的current_common_mapping处理机制设置父子关系
            for bone in edit_bones:
                simplified_name = simplify_bonename(bone.name)
                for parent_name, child_names in current_common_mapping.items():
                    if simplified_name in child_names:
                        for map_par_name, map_child_names in bone_dict.bone_mapping.items():
                            if parent_name in map_child_names:
                                parent_bone = edit_bones.get(map_par_name)
                                if parent_bone:
                                    if bone.use_connect:
                                        bone.use_connect = False
                                    bone.parent = parent_bone


        bpy.ops.object.mode_set(mode='POSE')  # 返回姿态模式
        return {'FINISHED'}

class L4D2_OT_RenameBonesOperator(bpy.types.Operator):
    bl_idname = "l4d2.rename_bones_operator"
    bl_label = "Rename Bone"
    bl_description = "Rename custom bone names to Valve bone names based on bone mapping relationships"

    def execute(self, context):
        # 加载全局的骨骼名字典
        load_common_mapping()

        # 获取当前骨架
        armature_obj = context.active_object
        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "未选中骨架对象或选中的不是骨架类型")
            return {'CANCELLED'}

        # 确保在物体模式
        bpy.ops.object.mode_set(mode='OBJECT')

        # 使用bonenames字典进行骨骼重命名
        for bone in armature_obj.data.bones:
            simplified_name = simplify_bonename(bone.name)
            for bone_key, bone_val in current_common_mapping.items():
                if simplified_name in bone_val:
                    bone.name = bone_key
                    break

        # 使用bonemapping字典进行骨骼重命名
        for bone in armature_obj.data.bones:
            for bone_key, bone_vals in bone_dict.bone_mapping.items():
                if bone.name in bone_vals:
                    bone.name = bone_key
                    break

        return {'FINISHED'}

class L4D2_PT_BoneModifyPanel(bpy.types.Panel):
    bl_label = "L4D2 Character Tools"
    bl_idname = "L4D2_PT_CharacterToolsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"

    def draw(self, context):
        layout = self.layout
        layout.operator("l4d2.rigging_operator", icon="GROUP_BONE")
        layout.operator("l4d2.grafting_operator", icon="GP_ONLY_SELECTED")

# 预设管理面板
class L4D2_PT_PresetManagerPanel(bpy.types.Panel):
    bl_label = "预设管理"
    bl_idname = "L4D2_PT_PresetManagerPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"
    bl_options = {'DEFAULT_CLOSED'} 

    def draw(self, context):
        layout = self.layout
        
        # 新建预设按钮
        row = layout.row(align=True)
        row.operator("l4d2.create_preset", icon="ADD", text="新建预设")
        
        # 获取预设文件列表
        preset_files = []
        if os.path.exists(MAPPING_PRESETS_DIR):
            for file in os.listdir(MAPPING_PRESETS_DIR):
                if file.endswith('.json'):
                    preset_files.append(file[:-5])  # 去掉.json后缀
        
        if preset_files:
            # 预设列表
            box = layout.box()
            for preset_name in preset_files:
                row = box.row(align=True)
                # 加载预设按钮
                load_op = row.operator("l4d2.load_preset", icon="FILE_REFRESH", text="", emboss=False)
                load_op.preset_name = preset_name
                # 预设名称
                row.label(text=preset_name)
                # 导出预设按钮
                export_op = row.operator("l4d2.export_preset", icon="EXPORT", text="", emboss=False)
                export_op.preset_name = preset_name
                # 删除预设按钮
                delete_op = row.operator("l4d2.delete_preset", icon="X", text="", emboss=False)
                delete_op.preset_name = preset_name
        
        # 导入预设按钮
        row = layout.row()
        row.operator("l4d2.import_preset", icon="IMPORT", text="导入预设")

class L4D2_OT_UnbindAndKeepShape(bpy.types.Operator):
    """Maintain shape and transformation when breaking bone parent-child relationships"""
    bl_idname = "l4d2.unbind_keep_shape"
    bl_label = "Unbind Preserve Shape"
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def store_bone_world_matrices(armature, pose_bones):
        armature_matrix_world = armature.matrix_world
        world_matrices = {}
        for bone in pose_bones:
            world_matrices[bone.name] = armature_matrix_world @ bone.matrix
        return world_matrices

    @staticmethod
    def disconnect_pose_bones(armature, common_mapping):
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature.data.edit_bones
        for bone_name in common_mapping:
            bone = edit_bones.get(bone_name)
            if bone:
                bone.use_connect = False
                bone.parent = None
        # bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def apply_bone_world_matrices(armature, world_matrices):
        bpy.ops.object.mode_set(mode='POSE')
        for bone_name, world_matrix in world_matrices.items():
            bone = armature.pose.bones.get(bone_name)
            if bone:
                bone.matrix = armature.matrix_world.inverted() @ world_matrix
        # bpy.ops.object.mode_set(mode='OBJECT')

    def execute(self, context):
        armature = context.object
        selected_pose_bones = context.selected_pose_bones
        
        if not armature or not selected_pose_bones or armature.type != 'ARMATURE' or context.mode != 'POSE':
            self.report({'ERROR'}, "没有选择正确的骨骼或者不在姿态模式")
            return {'CANCELLED'}

        world_matrices = self.store_bone_world_matrices(armature, selected_pose_bones)
        self.disconnect_pose_bones(armature, [bone.name for bone in selected_pose_bones])
        self.apply_bone_world_matrices(armature, world_matrices)
        
        return {'FINISHED'}

# 预设管理相关的属性类
class MappingData(bpy.types.PropertyGroup):
    main_official_mapping: bpy.props.StringProperty(
        default=json.dumps(bone_dict.bone_mapping)
    )
    main_unique_mapping: bpy.props.StringProperty(
        default=json.dumps({})
    )
    main_common_mapping: bpy.props.StringProperty(
        default=json.dumps(bone_dict.common_mapping)
    )

class TempMappingData(bpy.types.PropertyGroup):
    temp_official_mapping: bpy.props.StringProperty(
        default=json.dumps(bone_dict.bone_mapping)
    )
    temp_unique_mapping: bpy.props.StringProperty(
        default=json.dumps({})
    )
    temp_common_mapping: bpy.props.StringProperty(
        default=json.dumps(bone_dict.common_mapping)
    )

# 新建预设操作符
class L4D2_OT_CreatePreset(bpy.types.Operator):
    bl_idname = "l4d2.create_preset"
    bl_label = "Create Preset"
    bl_description = "Create a new mapping preset"
    
    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        description="Enter name for the new preset",
        default="New_Preset"
    )
    
    def execute(self, context):
        print("开始创建新预设...")
        if not os.path.exists(MAPPING_PRESETS_DIR):
            os.makedirs(MAPPING_PRESETS_DIR)
            print(f"创建预设目录: {MAPPING_PRESETS_DIR}")
            
        preset_path = os.path.join(MAPPING_PRESETS_DIR, f"{self.preset_name}.json")
        if os.path.exists(preset_path):
            self.report({'ERROR'}, f"预设 {self.preset_name} 已存在!")
            return {'CANCELLED'}
            
        preset_data = {
            "name": self.preset_name,
            "official_mapping": {},
            "unique_mapping": {}
        }
        
        try:
            with open(preset_path, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=4, ensure_ascii=False)
            print(f"成功创建预设文件: {preset_path}")
            self.report({'INFO'}, f"预设 {self.preset_name} 创建成功!")
        except Exception as e:
            print(f"创建预设时发生错误: {str(e)}")
            self.report({'ERROR'}, f"创建预设失败: {str(e)}")
            return {'CANCELLED'}
            
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

# 删除预设操作符
class L4D2_OT_DeletePreset(bpy.types.Operator):
    bl_idname = "l4d2.delete_preset"
    bl_label = "Delete Preset"
    bl_description = "Delete selected mapping preset"
    
    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        description="Name of preset to delete"
    )
    
    def execute(self, context):
        print(f"准备删除预设: {self.preset_name}")
        preset_path = os.path.join(MAPPING_PRESETS_DIR, f"{self.preset_name}.json")
        
        if not os.path.exists(preset_path):
            self.report({'ERROR'}, f"预设 {self.preset_name} 不存在!")
            return {'CANCELLED'}
            
        try:
            os.remove(preset_path)
            print(f"成功删除预设文件: {preset_path}")
            self.report({'INFO'}, f"预设 {self.preset_name} 已删除!")
        except Exception as e:
            print(f"删除预设时发生错误: {str(e)}")
            self.report({'ERROR'}, f"删除预设失败: {str(e)}")
            return {'CANCELLED'}
            
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

# 加载预设操作符
class L4D2_OT_LoadPreset(bpy.types.Operator):
    bl_idname = "l4d2.load_preset"
    bl_label = "Load Preset"
    bl_description = "Load selected mapping preset"
    
    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        description="Name of preset to load"
    )
    
    def execute(self, context):
        print(f"准备加载预设: {self.preset_name}")
        
        # 加载预设数据
        success, error_msg = MappingDataManager.load_preset_data(context, self.preset_name)
        if not success:
            self.report({'ERROR'}, f"加载预设失败: {error_msg}")
            return {'CANCELLED'}
            
        # 更新UI列表
        if not MappingDataManager.update_ui_list(context):
            self.report({'ERROR'}, "更新UI列表失败")
            return {'CANCELLED'}
            
        self.report({'INFO'}, f"预设 {self.preset_name} 加载成功!")
        return {'FINISHED'}

# 导入预设操作符
class L4D2_OT_ImportPreset(bpy.types.Operator):
    bl_idname = "l4d2.import_preset"
    bl_label = "Import Preset"
    bl_description = "Import mapping preset from file"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        print(f"准备导入预设文件: {self.filepath}")
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, "选择的文件不存在!")
            return {'CANCELLED'}
            
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
                
            if not all(key in preset_data for key in ['name', 'official_mapping', 'unique_mapping']):
                self.report({'ERROR'}, "无效的预设文件格式!")
                return {'CANCELLED'}
                
            preset_name = preset_data['name']
            target_path = os.path.join(MAPPING_PRESETS_DIR, f"{preset_name}.json")
            
            if not os.path.exists(MAPPING_PRESETS_DIR):
                os.makedirs(MAPPING_PRESETS_DIR)
                
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=4, ensure_ascii=False)
                
            print(f"成功导入预设到: {target_path}")
            self.report({'INFO'}, f"预设 {preset_name} 导入成功!")
        except Exception as e:
            print(f"导入预设时发生错误: {str(e)}")
            self.report({'ERROR'}, f"导入预设失败: {str(e)}")
            return {'CANCELLED'}
            
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# 导出预设操作符
class L4D2_OT_ExportPreset(bpy.types.Operator):
    bl_idname = "l4d2.export_preset"
    bl_label = "Export Preset"
    bl_description = "Export mapping preset to file"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        description="Name of preset to export"
    )
    
    def execute(self, context):
        print(f"准备导出预设: {self.preset_name}")
        source_path = os.path.join(MAPPING_PRESETS_DIR, f"{self.preset_name}.json")
        
        if not os.path.exists(source_path):
            self.report({'ERROR'}, f"预设 {self.preset_name} 不存在!")
            return {'CANCELLED'}
            
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
                
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=4, ensure_ascii=False)
                
            print(f"成功导出预设到: {self.filepath}")
            self.report({'INFO'}, f"预设 {self.preset_name} 导出成功!")
        except Exception as e:
            print(f"导出预设时发生错误: {str(e)}")
            self.report({'ERROR'}, f"导出预设失败: {str(e)}")
            return {'CANCELLED'}
            
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.filepath = os.path.join(os.path.dirname(MAPPING_PRESETS_DIR), f"{self.preset_name}.json")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# 自定义骨骼列表项
class CustomBoneItem(bpy.types.PropertyGroup):
    """用于存储自定义骨骼信息的属性组"""
    name: bpy.props.StringProperty(
        name="Bone Name",
        description="骨骼名称",
        default=""
    )
    is_selected: bpy.props.BoolProperty(
        name="Is Selected",
        description="是否被选中",
        default=False
    )

# UI列表项
class MappingListItem(bpy.types.PropertyGroup):
    """用于存储映射信息的属性组"""
    official_bone: bpy.props.StringProperty(
        name="Official Bone",
        description="官方骨骼名称",
        default=""
    )
    common_bone: bpy.props.StringProperty(
        name="Common Bone",
        description="通用骨骼名称",
        default=""
    )
    custom_bones: bpy.props.CollectionProperty(
        type=CustomBoneItem,
        name="Custom Bones",
        description="自定义骨骼列表"
    )
    preferred_bone_index: bpy.props.IntProperty(
        name="Preferred Bone Index",
        description="首选骨骼在列表中的索引",
        default=0
    )
    source_tab: bpy.props.StringProperty(
        name="Source Tab",
        description="映射的来源标签页",
        default=""
    )

# 自定义骨骼下拉菜单
class MAPPING_MT_CustomBonesMenu(bpy.types.Menu):
    bl_idname = "MAPPING_MT_custom_bones_menu"
    bl_label = "自定义骨骼"
    
    def draw(self, context):
        layout = self.layout
        item = context.active_item
        
        # 如果没有骨骼，显示提示信息
        if len(item.custom_bones) == 0:
            layout.label(text="没有自定义骨骼", icon='INFO')
            layout.separator()
            return
            
        # 显示骨骼列表
        layout.label(text="选择首选骨骼:", icon='BONE_DATA')
        layout.separator()
        
        # 显示所有自定义骨骼
        for i, bone in enumerate(item.custom_bones):
            row = layout.row()
            # 当前选中的骨骼显示不同图标
            icon = 'LAYER_ACTIVE' if i == item.preferred_bone_index else 'LAYER_USED'
            op = row.operator("mapping.select_custom_bone", text=bone.name, icon=icon)
            op.list_index = context.scene.mapping_list.values().index(item)
            op.bone_index = i
            
        # 底部分割线
        layout.separator()
        layout.separator()

# UI列表
class BONE_UL_MappingList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            # 根据当前标签页显示不同的内容
            if context.scene.mapping_ui_tab == 'ALL':
                # 主布局分为三部分：官方骨骼、通用骨骼、自定义骨骼和按钮
                split = row.split(factor=0.45)  # 官方骨骼占40%
                
                # 左侧：官方骨骼名称和搜索/编辑按钮
                left_row = split.row(align=True)
                
                # 根据搜索模式显示不同的输入方式
                if context.scene.use_search_mode:
                    # 搜索模式：从当前骨架中选择
                    if context.active_object and context.active_object.type == 'ARMATURE':
                        left_row.prop_search(item, "official_bone", context.active_object.data, "bones", text="")
                    else:
                        left_row.prop(item, "official_bone", text="", emboss=False)
                else:
                    # 编辑模式：手动输入
                    left_row.prop(item, "official_bone", text="", emboss=False)
                
                # 搜索/编辑切换按钮
                left_row.operator("mapping.toggle_search_mode", text="", 
                                icon='VIEWZOOM' if context.scene.use_search_mode else 'GREASEPENCIL')
                
                # 右侧部分（通用骨骼、自定义骨骼和按钮）
                right_side = split.split(factor=0.4)  # 通用骨骼占右侧40%
                
                # 中间：通用骨骼名称
                middle_row = right_side.row(align=True)
                # 箭头和通用骨骼名称
                arrow_row = middle_row.row(align=True)
                arrow_row.scale_x = 0.3  # 缩小箭头占用的空间
                arrow_row.label(text="→")
                name_row = middle_row.row()
                name_row.prop(item, "common_bone", text="", emboss=False)
                
                # 右侧：自定义骨骼和按钮
                right_row = right_side.row(align=True)
                # 第二个箭头
                arrow_row = right_row.row(align=True)
                arrow_row.scale_x = 0.3
                arrow_row.label(text="→")
                
                # 自定义骨骼下拉菜单和按钮组
                custom_group = right_row.row(align=True)
                # 获取当前条目在列表中的索引
                current_index = data.mapping_list.values().index(item)
                
                # 显示下拉菜单
                custom_group.context_pointer_set("active_item", item)
                # 修改这里以显示首选骨骼
                display_name = item.custom_bones[item.preferred_bone_index].name if len(item.custom_bones) > 0 else "无"
                custom_group.menu(
                    "MAPPING_MT_custom_bones_menu",
                    text=display_name
                )
                
                # 添加[+]和[-]按钮，设置emboss=True以显示灰色背景
                custom_group.operator("mapping.add_custom_bone", text="", icon='ADD', emboss=True).list_index = current_index
                custom_group.operator("mapping.remove_custom_bone", text="", icon='REMOVE', emboss=True).list_index = current_index
                
                # 分隔的删除映射按钮，设置emboss=True以显示灰色背景
                row.operator("mapping.remove_mapping", text="", icon='X', emboss=True).list_index = current_index
            
            else:  # UNIQUE 或 COMMON 标签页
                # 主布局分为两部分：通用骨骼和自定义骨骼
                split = row.split(factor=0.45)  # 通用骨骼占40%
                
                # 左侧：通用骨骼名称
                left_row = split.row(align=True)
                left_row.prop(item, "common_bone", text="", emboss=False)
                
                # 右侧：自定义骨骼和按钮
                right_row = split.row(align=True)
                # 箭头
                arrow_row = right_row.row(align=True)
                arrow_row.scale_x = 0.3
                arrow_row.label(text="→")
                
                # 自定义骨骼下拉菜单和按钮组
                custom_group = right_row.row(align=True)
                # 获取当前条目在列表中的索引
                current_index = data.mapping_list.values().index(item)
                
                # 显示下拉菜单
                custom_group.context_pointer_set("active_item", item)
                # 修改这里以显示首选骨骼
                display_name = item.custom_bones[item.preferred_bone_index].name if len(item.custom_bones) > 0 else "无"
                custom_group.menu(
                    "MAPPING_MT_custom_bones_menu",
                    text=display_name
                )
                
                # 添加[+]和[-]按钮，设置emboss=True以显示灰色背景
                custom_group.operator("mapping.add_custom_bone", text="", icon='ADD', emboss=True).list_index = current_index
                custom_group.operator("mapping.remove_custom_bone", text="", icon='REMOVE', emboss=True).list_index = current_index
                
                # 分隔的删除映射按钮，设置emboss=True以显示灰色背景
                row.operator("mapping.remove_mapping", text="", icon='X', emboss=True).list_index = current_index

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # 根据搜索字符串过滤
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "official_bone")
        else:
            flt_flags = [self.bitflag_filter_item] * len(items)
            
        return flt_flags, []

# 标签页面板
class BONE_PT_MappingPanel(bpy.types.Panel):
    bl_label = "骨骼映射"
    bl_idname = "BONE_PT_mapping_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 标签页
        row = layout.row()
        row.prop(scene, "mapping_ui_tab", expand=True)
        
        # UI列表
        row = layout.row()
        row.template_list("BONE_UL_MappingList", "", scene, "mapping_list",
                         scene, "mapping_list_index", rows=5)
        
        # 底部按钮
        row = layout.row()
        row.operator("mapping.add_new_mapping", text="添加新映射")
        row.operator("mapping.apply_changes", text="应用更改")

# 操作符
class MAPPING_OT_AddNewMapping(bpy.types.Operator):
    bl_idname = "mapping.add_new_mapping"
    bl_label = "Add New Mapping"
    bl_description = "添加新的骨骼映射关系"
    
    def execute(self, context):
        print("开始添加新映射...")
        scene = context.scene
        
        # 创建新的列表项
        item = scene.mapping_list.add()
        
        # 根据当前标签页设置不同的默认值
        current_tab = scene.mapping_ui_tab
        print(f"当前标签页: {current_tab}")
        
        # 设置来源标签页
        item.source_tab = current_tab
        
        if current_tab == 'ALL':
            # 全部映射标签页：需要官方骨骼名称和通用骨骼名称
            item.official_bone = ""
            item.common_bone = ""
            print("添加全部映射项")
            
        elif current_tab == 'UNIQUE':
            # 独立映射标签页：只需要通用骨骼名称
            item.common_bone = ""
            print("添加独立映射项")
            
        else:  # COMMON
            # 通用映射标签页：只需要通用骨骼名称
            item.common_bone = ""
            print("添加通用映射项")
        
        # 创建自定义骨骼集合
        item.custom_bones.clear()  # 确保集合为空
        
        # 设置新项为当前选中项
        scene.mapping_list_index = len(scene.mapping_list) - 1
        print(f"新映射项索引: {scene.mapping_list_index}")
        
        return {'FINISHED'}

class MAPPING_OT_ApplyChanges(bpy.types.Operator):
    bl_idname = "mapping.apply_changes"
    bl_label = "Apply Changes"
    bl_description = "将当前UI列表的更改应用到预设文件"
    
    def execute(self, context):
        global current_bone_mapping, current_unique_mapping, current_common_mapping
        print("开始应用更改...")
        scene = context.scene
        
        # 保存当前UI列表内容到temp_data
        print("保存当前UI列表内容到temp_data...")
        if not MappingDataManager.save_ui_list(context):
            self.report({'ERROR'}, "保存UI列表到temp_data失败")
            return {'CANCELLED'}
        
        # 获取temp_data中的映射
        temp_data = MappingDataManager.get_temp_data(context)
        if not temp_data:
            self.report({'ERROR'}, "获取temp_data失败")
            return {'CANCELLED'}
        
        # 更新全局变量
        print("更新全局变量...")
        current_bone_mapping = temp_data['official']
        current_unique_mapping = temp_data['unique']
        current_common_mapping = temp_data['common']
        
        print("全局变量已更新:")
        print(f"current_bone_mapping: {current_bone_mapping}")
        print(f"current_unique_mapping: {current_unique_mapping}")
        print(f"current_common_mapping: {current_common_mapping}")
        
        # 保存到common_mapping文件
        save_common_mapping(current_common_mapping)
        
        # 保存到当前活动预设
        active_preset = scene.active_preset_name
        if MappingDataManager.save_mapping_preset(context, active_preset):
            self.report({'INFO'}, f"映射更改已应用并保存到预设 {active_preset}")
        else:
            self.report({'WARNING'}, "映射更改已应用，但保存到预设失败")
        
        return {'FINISHED'}

class MAPPING_OT_ToggleSearchMode(bpy.types.Operator):
    bl_idname = "mapping.toggle_search_mode"
    bl_label = "Toggle Search Mode"
    
    def execute(self, context):
        context.scene.use_search_mode = not context.scene.use_search_mode
        return {'FINISHED'}

# 自定义骨骼菜单操作符
class MAPPING_OT_SelectCustomBone(bpy.types.Operator):
    bl_idname = "mapping.select_custom_bone"
    bl_label = "Select Custom Bone"
    bl_description = "将选中的骨骼设为首选项"
    
    list_index: bpy.props.IntProperty()
    bone_index: bpy.props.IntProperty()
    
    def execute(self, context):
        item = context.scene.mapping_list[self.list_index]
        
        if self.bone_index >= len(item.custom_bones):
            self.report({'ERROR'}, "无效的骨骼索引!")
            return {'CANCELLED'}
            
        # 更新首选骨骼索引而不是移动骨骼
        item.preferred_bone_index = self.bone_index
        print(f"将骨骼 {item.custom_bones[self.bone_index].name} 设为首选项")
        
        return {'FINISHED'}

class MAPPING_OT_AddCustomBone(bpy.types.Operator):
    bl_idname = "mapping.add_custom_bone"
    bl_label = "Add Custom Bone"
    bl_description = "添加新的自定义骨骼"
    
    list_index: bpy.props.IntProperty()
    bone_name: bpy.props.StringProperty(name="骨骼名称")
    mode: bpy.props.EnumProperty(
        items=[
            ('SEARCH', "从骨架中选择", "从当前骨架中选择骨骼"),
            ('MANUAL', "手动输入", "手动输入骨骼名称")
        ],
        name="添加模式",
        default='SEARCH'
    )
    
    def draw(self, context):
        layout = self.layout
        
        # 选项卡
        row = layout.row()
        row.prop(self, "mode", expand=True)
        
        # 根据模式显示不同的输入方式
        if self.mode == 'SEARCH':
            # 搜索模式：从当前骨架中选择
            if context.active_object and context.active_object.type == 'ARMATURE':
                layout.prop_search(self, "bone_name", context.active_object.data, "bones", text="骨骼")
            else:
                layout.label(text="请选择一个骨架", icon='ERROR')
        else:
            # 手动输入模式
            layout.prop(self, "bone_name", text="骨骼")
    
    def execute(self, context):
        bone_name = self.bone_name.strip()
        
        if not bone_name:
            self.report({'ERROR'}, "骨骼名称不能为空!")
            return {'CANCELLED'}
        
        # 简化骨骼名称
        simplified_name = simplify_bonename(bone_name)
        
        # 获取当前列表项
        item = context.scene.mapping_list[self.list_index]
        
        # 检查是否已存在
        for bone in item.custom_bones:
            if bone.name == simplified_name:
                self.report({'ERROR'}, f"骨骼 {simplified_name} 已存在!")
                return {'CANCELLED'}
        
        # 添加新骨骼到列表末尾
        new_bone = item.custom_bones.add()
        new_bone.name = simplified_name
        
        # 如果是第一个添加的骨骼，将其设为首选项
        if len(item.custom_bones) == 1:
            item.preferred_bone_index = 0
        
        print(f"添加自定义骨骼: {simplified_name} 到索引 {self.list_index}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class MAPPING_OT_RemoveCustomBone(bpy.types.Operator):
    bl_idname = "mapping.remove_custom_bone"
    bl_label = "Remove Custom Bone"
    bl_description = "删除首选的自定义骨骼"
    
    list_index: bpy.props.IntProperty()
    
    def execute(self, context):
        item = context.scene.mapping_list[self.list_index]
        
        # 如果有骨骼，删除首选项
        if len(item.custom_bones) > 0:
            bone_to_remove = item.custom_bones[item.preferred_bone_index].name
            
            # 从UI列表中删除骨骼
            item.custom_bones.remove(item.preferred_bone_index)
            
            # 更新首选骨骼索引
            if len(item.custom_bones) > 0:
                item.preferred_bone_index = min(item.preferred_bone_index, len(item.custom_bones) - 1)
            else:
                item.preferred_bone_index = 0
                
            print(f"从列表 {self.list_index} 删除首选自定义骨骼: {bone_to_remove}")
            
            # 从temp_data中删除骨骼
            if not MappingDataManager.remove_custom_bone(context, self.list_index, bone_to_remove):
                self.report({'ERROR'}, "删除自定义骨骼失败")
                return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class MAPPING_OT_RemoveMapping(bpy.types.Operator):
    bl_idname = "mapping.remove_mapping"
    bl_label = "Remove Mapping"
    bl_description = "删除当前映射条目"
    
    list_index: bpy.props.IntProperty()
    
    def execute(self, context):
        # 先尝试删除映射数据
        if MappingDataManager.remove_mapping(context, self.list_index):
            try:
                # 如果映射数据删除成功，再删除UI列表中的条目
                context.scene.mapping_list.remove(self.list_index)
                # 更新当前选中项
                if context.scene.mapping_list_index >= len(context.scene.mapping_list):
                    context.scene.mapping_list_index = max(0, len(context.scene.mapping_list) - 1)
                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"删除UI列表条目时发生错误: {str(e)}")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "删除映射数据失败")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

# 更新classes列表
classes = [
    CustomBoneItem,  
    MappingListItem,  
    MappingData,
    TempMappingData,
    BONE_UL_MappingList,
    L4D2_OT_GraftingOperator,
    L4D2_OT_RiggingOperator,
    L4D2_OT_RenameBonesOperator,
    L4D2_OT_UnbindAndKeepShape,
    L4D2_OT_CreatePreset,
    L4D2_OT_DeletePreset,
    L4D2_OT_LoadPreset,
    L4D2_OT_ImportPreset,
    L4D2_OT_ExportPreset,
    L4D2_PT_BoneModifyPanel,
    L4D2_PT_PresetManagerPanel,
    BONE_PT_MappingPanel,
    MAPPING_OT_AddNewMapping,
    MAPPING_OT_ApplyChanges,
    MAPPING_OT_ToggleSearchMode,
    MAPPING_MT_CustomBonesMenu,
    MAPPING_OT_SelectCustomBone,
    MAPPING_OT_AddCustomBone,
    MAPPING_OT_RemoveCustomBone,
    MAPPING_OT_RemoveMapping
]


# 注册新的属性
def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            # 抑制重复注册的错误消息
            pass
    bpy.types.Scene.Valve_Armature = bpy.props.StringProperty(name="Valve Rig")
    bpy.types.Scene.Custom_Armature = bpy.props.StringProperty(name="Custom Rig")
    
    # 添加UI相关的属性
    bpy.types.Scene.mapping_main_data = bpy.props.PointerProperty(type=MappingData)
    bpy.types.Scene.mapping_temp_data = bpy.props.PointerProperty(type=TempMappingData)
    bpy.types.Scene.mapping_list = bpy.props.CollectionProperty(type=MappingListItem)
    bpy.types.Scene.mapping_list_index = bpy.props.IntProperty()
    bpy.types.Scene.mapping_ui_tab = bpy.props.EnumProperty(
        items=[
            ('ALL', "全部映射", ""),
            ('UNIQUE', "独立映射", ""),
            ('COMMON', "通用映射", "")
        ],
        default='ALL',
        update=MappingDataManager.update_mapping_list  # 更新回调函数引用
    )
    bpy.types.Scene.use_search_mode = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.active_preset_name = bpy.props.StringProperty(
        name="Active Preset",
        description="当前活动预设的名称",
        default="Valve_L4D2"
    )
    
    # 初始化预设
    initialize_mapping_presets()

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            # 抑制注销错误的消息
            pass
    
    # 删除所有属性
    try:
        del bpy.types.Scene.Valve_Armature
        del bpy.types.Scene.Custom_Armature
        del bpy.types.Scene.mapping_main_data
        del bpy.types.Scene.mapping_temp_data
        del bpy.types.Scene.mapping_list
        del bpy.types.Scene.mapping_list_index
        del bpy.types.Scene.mapping_ui_tab
        del bpy.types.Scene.use_search_mode
        del bpy.types.Scene.active_preset_name
    except Exception as e:
        # 抑制删除属性错误的消息
        pass