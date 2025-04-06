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
from bpy.app.translations import pgettext_iface as _

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
    def _add_mapping_item(scene, official, common, source_tab, custom_bones, axis_controls=None):
        """添加一个映射项到UI列表，可选择性包含轴控制信息"""
        item = scene.mapping_list.add()
        item.official_bone = official
        item.common_bone = common
        item.source_tab = source_tab
        
        for custom_name in custom_bones:
            bone = item.custom_bones.add()
            bone.name = custom_name
            bone.is_selected = False

        # 如果提供了轴控制信息，则设置
        if axis_controls and official in axis_controls:
            controls = axis_controls[official]
            item.use_x = controls.get('use_x', True)
            item.use_y = controls.get('use_y', True)
            item.use_z = controls.get('use_z', True)
        # else: # 保留默认值 True，MappingListItem属性定义中已设置default=True

    @staticmethod
    @error_handler
    def update_ui_list(context):
        """更新UI列表显示"""
        scene = context.scene
        scene.mapping_list.clear()
        
        temp_data = MappingDataManager.get_temp_data(context)
        if not temp_data:
            return False
            
        # 加载轴控制信息
        bone_axis_controls = {}
        if 'bone_axis_controls' in scene:
            try:
                bone_axis_controls = json.loads(scene['bone_axis_controls'])
            except (json.JSONDecodeError, TypeError): # TypeError added for potential non-string data
                print("无法解析 bone_axis_controls 或数据类型错误")
                bone_axis_controls = {} # 使用空字典

        added_commons = set()
        
        if scene.mapping_ui_tab == 'ALL':
            # 全部映射：显示所有映射关系
            # 首先添加所有官方映射
            for official, commons in temp_data['official'].items():
                for common in commons:
                    if common not in added_commons:
                        added_commons.add(common)
                        # 查找对应的自定义骨骼
                        customs = temp_data['common'].get(common, []) or temp_data['unique'].get(common, [])
                        MappingDataManager._add_mapping_item(scene, official, common, 'ALL', customs, bone_axis_controls) # 传递轴控制信息
            
            # 然后添加所有独立映射（不在官方映射中的通用骨骼映射）
            for common, customs in temp_data['unique'].items():
                if common not in added_commons:
                    added_commons.add(common)
                    MappingDataManager._add_mapping_item(scene, "", common, 'UNIQUE', customs) # 不传递轴控制，因为没有官方骨骼关联
            
            # 最后添加所有通用映射（不在官方映射和独立映射中的通用骨骼映射）
            for common, customs in temp_data['common'].items():
                if common not in added_commons:
                    added_commons.add(common)
                    MappingDataManager._add_mapping_item(scene, "", common, 'COMMON', customs) # 不传递轴控制
                    
        elif scene.mapping_ui_tab == 'UNIQUE':
            # 独立映射：显示不在通用映射中的映射关系，以及来源为UNIQUE的映射
            for common, customs in temp_data['unique'].items():
                 # 保持原有逻辑，不显示或处理轴控制
                if common not in temp_data['common'] or any(item.source_tab == 'UNIQUE' for item in scene.mapping_list):
                     MappingDataManager._add_mapping_item(scene, "", common, 'UNIQUE', customs)
        
        elif scene.mapping_ui_tab == 'COMMON':
            # 通用映射：显示在通用映射中的映射关系，以及来源为COMMON的映射
             for common, customs in temp_data['common'].items():
                 # 保持原有逻辑，不显示或处理轴控制
                 if common in temp_data['common'] or any(item.source_tab == 'COMMON' for item in scene.mapping_list):
                     MappingDataManager._add_mapping_item(scene, "", common, 'COMMON', customs)
        
        elif scene.mapping_ui_tab == 'AXIS':
            # 轴控制标签页：只显示官方骨骼和它们的轴控制
            official_bones_processed = set()
            # --- 修改：移除 sorted()，直接按字典顺序迭代 ---
            for official_bone in temp_data['official'].keys(): # 按字典原始顺序（通常是预设文件顺序）迭代
                 if official_bone not in official_bones_processed:
                    # Common bone, source tab, and custom bones are not directly relevant here.
                    # Pass empty values for them. Pass axis controls to set use_x/y/z.
                    MappingDataManager._add_mapping_item(scene, official_bone, "", 'AXIS', [], bone_axis_controls)
                    official_bones_processed.add(official_bone)

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
            
            # 加载骨骼轴控制信息（如果有）
            bone_axis_controls = preset_data.get('bone_axis_controls', {})
            context.scene['bone_axis_controls'] = json.dumps(bone_axis_controls)
            
            # 更新映射列表中的轴控制设置
            if context.scene.mapping_list:
                for item in context.scene.mapping_list:
                    if item.official_bone in bone_axis_controls:
                        axis_control = bone_axis_controls[item.official_bone]
                        item.use_x = axis_control.get('use_x', True)
                        item.use_y = axis_control.get('use_y', True)
                        item.use_z = axis_control.get('use_z', True)
            
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
            
            # 获取骨骼轴控制信息
            bone_axis_controls = {}
            if 'bone_axis_controls' in context.scene:
                try:
                    bone_axis_controls = json.loads(context.scene['bone_axis_controls'])
                except (json.JSONDecodeError, TypeError):
                    # 如果解析失败，使用空字典
                    bone_axis_controls = {}
            
            # 如果没有从场景中获取到，则从映射列表中获取
            if not bone_axis_controls:
                for item in context.scene.mapping_list:
                    if item.official_bone:
                        bone_axis_controls[item.official_bone] = {
                            'use_x': item.use_x,
                            'use_y': item.use_y,
                            'use_z': item.use_z
                        }
            
            # 准备预设数据
            preset_data = {
                "name": preset_name,
                "official_mapping": temp_data['official'],
                "unique_mapping": temp_data['unique'],
                "bone_axis_controls": bone_axis_controls
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

# 在类定义前添加共享函数
def build_mapping_relation():
    """构建骨骼名称映射关系（共享函数）"""
    global current_bone_mapping, current_unique_mapping, current_common_mapping
    
    # 1. 构建通用骨骼到自定义骨骼的映射
    common_to_customs = {}
    for src_dict in [current_common_mapping, current_unique_mapping]:
        for common, customs in src_dict.items():
            if common not in common_to_customs:
                common_to_customs[common] = customs
            else:
                # 合并列表但避免重复项
                common_to_customs[common].extend([c for c in customs if c not in common_to_customs[common]])
    
    # 2. 构建官方骨骼到自定义骨骼的直接映射
    official_to_customs = {}
    for official, commons in current_bone_mapping.items():
        customs_list = []
        for common in commons:
            if common in common_to_customs:
                customs_list.extend(common_to_customs[common])
        if customs_list:
            official_to_customs[official] = customs_list
            
    return official_to_customs

def add_bone_constraints(armature_A, armature_B, official_to_customs):
    """添加骨骼约束（共享函数）
    
    Args:
        armature_A: 官方骨架对象
        armature_B: 自定义骨架对象
        official_to_customs: 官方骨骼到自定义骨骼的映射
        
    Returns:
        int: 添加的约束数量
    """
    # 为目标骨架中的所有骨骼预先创建简化名称映射
    simplified_bone_map = {simplify_bonename(bone.name): bone.name for bone in armature_B.data.bones}
    added_constraints = set()
    
    for official_bone_name, mapping_info in official_to_customs.items():
        # 跳过官方骨架中不存在的骨骼
        if official_bone_name not in armature_A.pose.bones:
            continue
            
        official_bone = armature_A.pose.bones[official_bone_name]
        
        # 统一处理映射信息格式
        if isinstance(mapping_info, dict):
            custom_bone_names = mapping_info.get('custom_bones', [])
            use_x = mapping_info.get('use_x', True)
            use_y = mapping_info.get('use_y', True)
            use_z = mapping_info.get('use_z', True)
        else:
            # 兼容旧格式
            custom_bone_names = mapping_info
            use_x = use_y = True
            use_z = official_bone_name != 'ValveBiped.Bip01_Pelvis'  # 特殊处理盆骨
        
        # 查找匹配的自定义骨骼
        for custom_name in custom_bone_names:
            simplified_name = simplify_bonename(custom_name)
            if simplified_name in simplified_bone_map:
                # 添加约束
                constraint = official_bone.constraints.new('COPY_LOCATION')
                constraint.target = armature_B
                constraint.subtarget = simplified_bone_map[simplified_name]
                constraint.head_tail = 0
                
                # 设置轴向控制
                constraint.use_x = use_x
                constraint.use_y = use_y
                constraint.use_z = use_z
                
                added_constraints.add(official_bone_name)
                print(f"添加约束: {official_bone_name} -> {simplified_bone_map[simplified_name]} (轴控制: X={use_x}, Y={use_y}, Z={use_z})")
                break
                
    return len(added_constraints)

# 替换prepare_armatures_for_rigging函数，拆分为两个专注的函数
def validate_armatures(context):
    """验证骨架对象是否存在（不更改模式）
    
    Returns:
        tuple: (armature_A, armature_B) 如果成功，否则 (None, None)
    """
    # 从场景获取骨架对象
    armature_A = context.scene.Valve_Armature
    armature_B = context.scene.Custom_Armature
    
    # 验证骨架对象
    if not armature_A or not armature_B:
        print("请先选择官方骨架和自定义骨架")
        return None, None
    
    return armature_A, armature_B

def set_armature_pose_mode(context, armature_A):
    """设置骨架为姿势模式
    
    Args:
        context: Blender上下文
        armature_A: 需要设置为姿势模式的骨架对象
    """
    # 确保在物体模式
    if context.active_object and context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # 选择骨架A并设为姿势模式
    bpy.ops.object.select_all(action='DESELECT')
    armature_A.select_set(True)
    context.view_layer.objects.active = armature_A
    bpy.ops.object.mode_set(mode='POSE')

# 嫁接辅助函数，避免重复代码
def graft_build_mappings():
    """构建骨骼映射关系，优化版
    
    返回:
        tuple: (官方骨骼到自定义骨骼的映射, 自定义骨骼到官方骨骼的映射)
    """
    # 使用全局映射变量
    global current_bone_mapping, current_unique_mapping, current_common_mapping
    
    # 构建最终所需的两个主要映射
    official_to_customs = {}  # 官方骨骼 -> 自定义骨骼列表
    custom_to_official = {}   # 自定义骨骼 -> 官方骨骼

    # 合并通用骨骼和独立骨骼映射
    common_to_customs = {}
    for mapping_dict in [current_unique_mapping, current_common_mapping]:
        for common, customs in mapping_dict.items():
            if common not in common_to_customs:
                common_to_customs[common] = customs
            else:
                # 去重合并
                common_to_customs[common] = list(set(common_to_customs[common] + customs))

    # 一次遍历构建所有映射
    for official, commons in current_bone_mapping.items():
        customs = []
        for common in commons:
            if common in common_to_customs:
                customs.extend(common_to_customs[common])
        
        if customs:
            official_to_customs[official] = customs
            # 同时构建反向映射
            for custom in customs:
                custom_to_official[custom] = official
    
    return official_to_customs, custom_to_official

def graft_process_selected_bones(edit_bones, selected_bones, official_to_customs, custom_to_official):
    """处理选中的骨骼，只基于映射关系，优化版
    
    Args:
        edit_bones: 编辑模式下的骨骼集合
        selected_bones: 选中的骨骼列表
        official_to_customs: 官方骨骼到自定义骨骼的映射
        custom_to_official: 自定义骨骼到官方骨骼的映射
        
    Returns:
        set: 已处理的骨骼名称集合
    """
    processed_bones = set()
    bone_by_name = {bone.name: bone for bone in edit_bones}
    official_bones_set = set(current_bone_mapping.keys())
    
    # 创建简化骨骼名称缓存
    simplified_custom_to_official = {}
    for custom, official in custom_to_official.items():
        simplified_custom = simplify_bonename(custom)
        simplified_custom_to_official[simplified_custom] = official
    
    # 处理选中的非官方骨骼
    for bone in selected_bones:
        if bone.name in official_bones_set:
            continue
            
        simplified_name = simplify_bonename(bone.name)
        official = simplified_custom_to_official.get(simplified_name)
        
        if official and official in bone_by_name:
            parent_bone = bone_by_name[official]
            if bone.use_connect:
                bone.use_connect = False
            bone.parent = parent_bone
            
            processed_bones.add(bone.name)
    
    return processed_bones

def graft_process_all_bones(edit_bones, official_to_customs, custom_to_official):
    """处理所有骨骼，基于映射关系的优化版
    
    Args:
        edit_bones: 编辑模式下的骨骼集合
        official_to_customs: 官方骨骼到自定义骨骼的映射
        custom_to_official: 自定义骨骼到官方骨骼的映射
        
    Returns:
        set: 已处理的骨骼名称集合
    """
    # 复用选定骨骼处理函数，获取所有非官方骨骼
    official_bones_set = set(current_bone_mapping.keys())
    non_official_bones = [bone for bone in edit_bones if bone.name not in official_bones_set]
    
    return graft_process_selected_bones(
        edit_bones, 
        non_official_bones, 
        official_to_customs, 
        custom_to_official
    )

def generate_grafting_preview(edit_bones, selected_bones, official_to_customs, custom_to_official):
    """生成骨骼嫁接预览数据
    
    Args:
        edit_bones: 编辑模式下的骨骼集合
        selected_bones: 选中的骨骼列表，如果为空则处理所有骨骼
        official_to_customs: 官方骨骼到自定义骨骼的映射
        custom_to_official: 自定义骨骼到官方骨骼的映射
        
    Returns:
        str: 骨骼嫁接预览文本
    """
    # 获取所有骨骼和官方骨骼
    bone_by_name = {bone.name: bone for bone in edit_bones}
    official_bones_set = set(current_bone_mapping.keys())
    
    # 优化：预计算所有简化骨骼名称及其映射关系
    simplified_to_official = {}
    
    # 如果有选中的骨骼，只处理选中的非官方骨骼
    bones_to_process = []
    if selected_bones:
        bones_to_process = [b for b in selected_bones if b.name not in official_bones_set]
    else:
        # 处理所有非官方骨骼
        bones_to_process = [b for b in edit_bones if b.name not in official_bones_set]
    
    # 创建映射关系
    mapping_preview_lines = []
    for bone in bones_to_process:
        simplified_name = simplify_bonename(bone.name)
        for custom, official in custom_to_official.items():
            if simplified_name == simplify_bonename(custom) and official in bone_by_name:
                mapping_preview_lines.append(f"{bone.name} -> {official} (映射关系)")
                break
    
    return "\n".join(mapping_preview_lines)

class L4D2_OT_BaseOperator:
    """骨骼操作基础类，用于减少代码重复"""
    mapping_source: bpy.props.StringProperty(default="", options={'HIDDEN'})
    preset_name: bpy.props.StringProperty(default="", options={'HIDDEN'})
    mapping_count: bpy.props.IntProperty(default=0, options={'HIDDEN'})
    common_count: bpy.props.IntProperty(default=0, options={'HIDDEN'})
    unique_count: bpy.props.IntProperty(default=0, options={'HIDDEN'})
    mapping_preview: bpy.props.StringProperty(options={'HIDDEN'})
    mapping_data: bpy.props.StringProperty(options={'HIDDEN'})
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)
    
    def _load_mapping_data(self, context):
        """加载骨骼映射数据"""
        global current_bone_mapping, current_unique_mapping, current_common_mapping
        load_common_mapping()
        
        if not current_bone_mapping or not current_common_mapping:
            success, error_msg = MappingDataManager.load_preset_data(context, context.scene.active_preset_name)
            if not success:
                self.report({'ERROR'}, f"无法加载预设数据: {error_msg}")
                return False
                
        print(f"使用预设: {context.scene.active_preset_name}")
        print(f"官方映射骨骼数: {len(current_bone_mapping)}")
        print(f"通用映射骨骼数: {len(current_common_mapping)}")
        print(f"独立映射骨骼数: {len(current_unique_mapping)}")
        return True
    
    def _get_mapping_source(self, context):
        """确定映射数据来源"""
        mapping_source = "Preset File"
        preset_name = context.scene.active_preset_name
        preset_path = os.path.join(MAPPING_PRESETS_DIR, f"{preset_name}.json")
        if preset_name == "None" or not os.path.exists(preset_path):
            mapping_source = "Memory Data"
        return mapping_source, preset_name
        
    def _prepare_base_data(self, context):
        # 加载基础数据
        self._load_mapping_data(context)
        
        # 获取映射来源
        mapping_source, preset_name = self._get_mapping_source(context)
        self.mapping_source = mapping_source
        self.preset_name = preset_name
        
        # 更新映射计数
        self.mapping_count = len(current_bone_mapping)
        self.common_count = len(current_common_mapping)
        self.unique_count = len(current_unique_mapping)

class RiggingConfirmItem(bpy.types.PropertyGroup):
    official_bone: bpy.props.StringProperty(
        name=_("Official Bone"),
        description=_("Official bone name"),
        default=""
    )
    custom_bone: bpy.props.StringProperty(
        name=_("Custom Bone"),
        description=_("Corresponding custom bone name"),
        default=""
    )
    use_x: bpy.props.BoolProperty(
        name="X",
        description=_("Use X axis constraint"),
        default=True
    )
    use_y: bpy.props.BoolProperty(
        name="Y",
        description=_("Use Y axis constraint"),
        default=True
    )
    use_z: bpy.props.BoolProperty(
        name="Z",
        description=_("Use Z axis constraint"),
        default=True
    )

class RIGGING_UL_MappingList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # 使用与表头相同的布局
            row = layout.row()
            
            # 序号列 - 显示从1开始的序号
            index_col = row.column()
            index_col.scale_x = 0.3  # 设置序号列宽度
            index_col.label(text=f"{index+1}")
            
            # 左侧列 - 官方骨骼
            left_item = row.split(factor=0.45)
            left_item.label(text=item.official_bone)
            
            # 右侧列 - 自定义骨骼和轴控制
            right_item = left_item.split(factor=0.6)
            
            # 中间列 - 自定义骨骼
            custom_col = right_item.column()
            custom_col.label(text=item.custom_bone)
            custom_col.alignment = 'CENTER'  # 设置自定义骨骼名称居中
            
            # 右侧列 - 轴控制
            axis_col = right_item.column()
            axis_row = axis_col.row(align=True)
            axis_row.prop(item, "use_x", text="X", toggle=True)
            axis_row.prop(item, "use_y", text="Y", toggle=True)
            axis_row.prop(item, "use_z", text="Z", toggle=True)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=f"{index+1}. {item.official_bone}")

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # 创建过滤标志列表
        flt_flags = [self.bitflag_filter_item] * len(items)
        
        # 如果有过滤文本，检查每个项是否匹配
        if data.filter_text:
            filter_text = data.filter_text.lower()
            for idx, item in enumerate(items):
                if filter_text not in item.official_bone.lower() and filter_text not in item.custom_bone.lower():
                    flt_flags[idx] = 0  # 不匹配
                
        return flt_flags, []

class GRAFTING_UL_MappingList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # 使用与表头相同的布局
            row = layout.row()
            
            # 序号列 - 显示从1开始的序号
            index_col = row.column()
            index_col.scale_x = 0.3  # 设置序号列宽度
            index_col.label(text=f"{index+1}")
            
            # 分割左右两列 - 父骨骼和子骨骼
            split = row.split(factor=0.5)
            
            # 左侧 - 父骨骼(官方)
            left_col = split.column()
            left_col.label(text=item.official_bone)
            
            # 右侧 - 子骨骼(自定义)
            right_col = split.column()
            right_col.label(text=item.custom_bone)
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=f"{index+1}. {item.official_bone} -> {item.custom_bone}")

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # 创建过滤标志列表
        flt_flags = [self.bitflag_filter_item] * len(items)
        
        # 如果有过滤文本，检查每个项是否匹配
        if data.filter_text:
            filter_text = data.filter_text.lower()
            for idx, item in enumerate(items):
                if filter_text not in item.official_bone.lower() and filter_text not in item.custom_bone.lower():
                    flt_flags[idx] = 0  # 不匹配
                
        return flt_flags, []

class L4D2_OT_RiggingConfirmOperator(bpy.types.Operator, L4D2_OT_BaseOperator):
    bl_idname = "l4d2.rigging_confirm"
    bl_label = "Confirm Bone Alignment"
    bl_description = "Confirm current mapping data and execute bone alignment operation"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    # 特有属性
    armature_a_name: bpy.props.StringProperty()
    armature_b_name: bpy.props.StringProperty()
    
    # 映射项集合
    mapping_items: bpy.props.CollectionProperty(type=RiggingConfirmItem)
    active_mapping_index: bpy.props.IntProperty(default=0)
    
    # 过滤字段
    filter_text: bpy.props.StringProperty(
        name="Filter",
        description="Filter by bone name",
        default=""
    )
    
    def draw(self, context):
        layout = self.layout
        
        # 显示基本信息
        box = layout.box()
        row = box.row()
        row.label(text=f"{_('Current Preset')}: {self.preset_name}")
        row.label(text=f"{_('Data Source')}: {self.mapping_source}")
        
        row = box.row()
        row.label(text=f"{_('Official Armature')}: {self.armature_a_name}")
        row.label(text=f"{_('Custom Armature')}: {self.armature_b_name}")
        
        # 显示映射统计信息
        row = box.row()
        row.label(text=f"{_('Total Mappings')}: {len(self.mapping_items)}")
        row.prop(self, "filter_text", text=_("Filter"), icon='VIEWZOOM')
        
        # 创建映射列表区域
        mapping_box = layout.box()
        mapping_box.label(text=_("Bone Mapping and Axis Control") + ":")
        
        # 创建分割布局
        split = mapping_box.split(factor=0.45)  # 55%给官方骨骼，45%给自定义骨骼和轴控制
        
        # 左侧布局 - 官方骨骼
        left_col = split.column()
        left_col.label(text="        " + _("Official Bone"))  # 添加空格增加前面的空隙
        
        # 右侧布局 - 自定义骨骼和轴控制
        right_split = split.split(factor=0.6)  # 右侧的60%给自定义骨骼，40%给轴控制
        middle_col = right_split.column()
        middle_col.label(text="  " + _("Custom Bone"))
        middle_col.alignment = 'CENTER'  # 设置表头居中
        
        right_col = right_split.column()
        right_col.label(text=_("Axis Control"))
        
        # 使用template_list创建滚动区域
        mapping_box.template_list(
            "RIGGING_UL_MappingList", "", 
            self, "mapping_items", 
            self, "active_mapping_index", 
            rows=20  # 显示行数，超过会自动出现滚动条
        )
        
        # 提示信息
        layout.label(text=_("Please adjust axis control settings and confirm to execute bone alignment"))
    
    def invoke(self, context, event):
        # 解析映射数据
        try:
            mapping_data = json.loads(self.mapping_data)
            self.mapping_items.clear()
            
            # 使用简化名称映射查找实际自定义骨骼名称
            armature_B = bpy.data.objects.get(self.armature_b_name)
            simplified_bone_map = {}
            if armature_B:
                simplified_bone_map = {simplify_bonename(bone.name): bone.name for bone in armature_B.data.bones}
            
            # 填充映射项
            for official_bone, data in mapping_data.items():
                if isinstance(data, dict):  # 新格式
                    custom_bones = data.get('custom_bones', [])
                    use_x = data.get('use_x', True)
                    use_y = data.get('use_y', True)
                    use_z = data.get('use_z', True)
                else:  # 旧格式
                    custom_bones = data
                    use_x = use_y = True
                    use_z = official_bone != 'ValveBiped.Bip01_Pelvis'
                
                # 为每个官方骨骼添加一个映射项
                if custom_bones:
                    # 找到第一个存在的自定义骨骼
                    custom_bone = ""
                    for custom_name in custom_bones:
                        simplified_name = simplify_bonename(custom_name)
                        if simplified_name in simplified_bone_map:
                            custom_bone = simplified_bone_map[simplified_name]
                            break
                    
                    if custom_bone:
                        item = self.mapping_items.add()
                        item.official_bone = official_bone
                        item.custom_bone = custom_bone
                        item.use_x = use_x
                        item.use_y = use_y
                        item.use_z = use_z
            
        except (json.JSONDecodeError, TypeError) as e:
            self.report({'ERROR'}, f"{_('Failed to parse mapping data')}: {str(e)}")
            return {'CANCELLED'}
        
        return super().invoke(context, event)
    
    def execute(self, context):
        # 查找官方和自定义骨架对象
        armature_A = bpy.data.objects.get(self.armature_a_name)
        armature_B = bpy.data.objects.get(self.armature_b_name)
        
        if not armature_A or not armature_B:
            self.report({'ERROR'}, _("Could not find armature objects"))
            return {'CANCELLED'}
        
        # 设置骨架姿势模式
        set_armature_pose_mode(context, armature_A)
        
        # 构建映射数据
        official_to_customs = {}
        simplified_bone_map = {simplify_bonename(bone.name): bone.name for bone in armature_B.data.bones}
        
        # 从映射项中获取设置
        for item in self.mapping_items:
            if not item.official_bone or not item.custom_bone:
                continue
                
            # 查找原始的自定义骨骼名称
            custom_bones = [item.custom_bone]
            
            # 构建包含轴控制信息的映射
            official_to_customs[item.official_bone] = {
                'custom_bones': custom_bones,
                'use_x': item.use_x,
                'use_y': item.use_y,
                'use_z': item.use_z
            }
        
        # 添加骨骼约束
        constraint_count = add_bone_constraints(armature_A, armature_B, official_to_customs)
        
        # 报告结果
        self.report({'INFO'}, f"{_('Alignment completed, added')} {constraint_count} {_('bone constraints')}")
        
        return {'FINISHED'}

class GraftingConfirmItem(bpy.types.PropertyGroup):
    official_bone: bpy.props.StringProperty(
        name="父骨骼",
        description="官方骨骼名称(父)",
        default=""
    )
    custom_bone: bpy.props.StringProperty(
        name="子骨骼",
        description="自定义骨骼名称(子)",
        default=""
    )
    # 嫁接操作不需要轴控制属性

class L4D2_OT_GraftingConfirmOperator(bpy.types.Operator, L4D2_OT_BaseOperator):
    bl_idname = "l4d2.grafting_confirm"
    bl_label = "Confirm Grafting Operation"
    bl_description = "Confirm current mapping data and execute bone grafting operation"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    # 特有属性
    armature_name: bpy.props.StringProperty()
    
    # 预览数据
    selected_bones_count: bpy.props.IntProperty(default=0)
    preview_mode: bpy.props.EnumProperty(
        name="Preview Mode",
        items=[
            ('SELECTED', "Selected Bones", "Only display grafting relationships for selected bones"),
            ('ALL', "All Bones", "Display grafting relationships for all bones")
        ],
        default='SELECTED'
    )
    
    # 映射项集合 - 使用专为嫁接设计的GraftingConfirmItem
    mapping_items: bpy.props.CollectionProperty(type=GraftingConfirmItem)
    active_mapping_index: bpy.props.IntProperty(default=0)
    
    # 过滤字段
    filter_text: bpy.props.StringProperty(
        name="Filter",
        description="Filter by bone name",
        default=""
    )
    
    def draw(self, context):
        layout = self.layout
        
        # 显示基本信息
        box = layout.box()
        row = box.row()
        row.label(text=f"{_('Current Preset')}: {self.preset_name}")
        row.label(text=f"{_('Data Source')}: {self.mapping_source}")
        
        row = box.row()
        row.label(text=f"{_('Target Armature')}: {self.armature_name}")
        
        # 显示映射统计信息
        row = box.row()
        row.label(text=f"{_('Official Mapping Bones')}: {self.mapping_count}")
        row.label(text=f"{_('Common Mapping Bones')}: {self.common_count}")
        row.label(text=f"{_('Unique Mapping Bones')}: {self.unique_count}")
        
        # 显示选择模式
        if self.selected_bones_count > 0:
            row = box.row()
            row.label(text=f"{_('Selected Bones Count')}: {self.selected_bones_count}")
            row.prop(self, "preview_mode", text="")
        
        # 显示映射关系 - 使用专为嫁接设计的UIList
        mapping_box = layout.box()
        row = mapping_box.row()
        row.label(text=f"{_('Grafting Mapping Relationships')} ({_('Total')} {len(self.mapping_items)}):")
        row.prop(self, "filter_text", text=_("Filter"), icon='VIEWZOOM')
        
        # 创建分割布局
        split = mapping_box.split(factor=0.45)  # 45%给左侧，55%给右侧
        
        # 左侧布局 - 父骨骼(官方)
        left_col = split.column()
        left_col.label(text=f"        {_('Parent Bone')}")
        
        # 右侧布局 - 子骨骼(自定义)
        right_col = split.column()
        right_col.label(text=f"        {_('Child Bone')}")
        
        # 使用专为嫁接设计的UIList
        mapping_box.template_list(
            "GRAFTING_UL_MappingList", "", 
            self, "mapping_items", 
            self, "active_mapping_index", 
            rows=10  # 显示行数，超过会自动出现滚动条
        )
        
        # 显示处理流程信息
        operation_box = layout.box()
        operation_box.label(text=f"{_('Processing Flow')}:")
        if self.preview_mode == 'SELECTED' and self.selected_bones_count > 0:
            operation_box.label(text=f"1. {_('Process')} {self.selected_bones_count} {_('selected non-official bones')}")
            operation_box.label(text=f"2. {_('Set parent-child relationships based on the above mappings')}")
        else:
            operation_box.label(text=f"1. {_('Process all non-official bones')}")
            operation_box.label(text=f"2. {_('Set parent-child relationships based on the above mappings')}")
        
        # 提示信息
        layout.label(text=_("Please confirm the above information and click OK to execute bone grafting operation"))
    
    def invoke(self, context, event):
        # 解析映射数据
        try:
            mapping_data = json.loads(self.mapping_data)
            official_to_customs = mapping_data.get('official_to_customs', {})
            custom_to_official = mapping_data.get('custom_to_official', {})
            
            # 清空现有项
            self.mapping_items.clear()
            
            # 创建映射项 - 从custom_to_official反向显示父子关系
            # 自定义骨骼(子) -> 官方骨骼(父)
            added_relations = set()
            
            # 选择需要显示的骨骼
            obj = bpy.data.objects.get(self.armature_name)
            
            # 确保当前对象存在且为骨架
            if not obj or obj.type != 'ARMATURE':
                self.report({'ERROR'}, _("Armature object not found or not an armature type"))
                return {'CANCELLED'}
                
            # 保存当前模式并设置为编辑模式以获取选中骨骼
            current_mode = context.mode
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            
            # 获取编辑骨骼和选中骨骼
            edit_bones = obj.data.edit_bones
            selected_bones = [bone for bone in edit_bones if bone.select]
            
            # 获取所有骨骼的简化名称
            bone_simplified_names = {bone.name: simplify_bonename(bone.name) for bone in edit_bones}
            
            # 官方骨骼列表 - 用于识别哪些是非官方骨骼
            official_bones_set = set(current_bone_mapping.keys())
            
            # 根据预览模式选择处理的骨骼
            if self.preview_mode == 'SELECTED' and self.selected_bones_count > 0:
                # 获取选中的非官方骨骼
                non_official_selected = [bone for bone in selected_bones if bone.name not in official_bones_set]
                
                # 为每个选中的非官方骨骼检查映射关系
                for bone in non_official_selected:
                    simplified_name = simplify_bonename(bone.name)
                    
                    # 查找匹配的自定义到官方映射
                    for custom_name, official_name in custom_to_official.items():
                        if simplified_name == simplify_bonename(custom_name) and official_name in edit_bones:
                            # 避免重复添加
                            if (bone.name, official_name) not in added_relations:
                                item = self.mapping_items.add()
                                item.official_bone = official_name  # 父骨骼(官方)
                                item.custom_bone = bone.name  # 子骨骼(自定义)
                                added_relations.add((bone.name, official_name))
                                break
            else:
                # 显示所有可能的嫁接关系
                # 获取所有非官方骨骼
                non_official_bones = [bone for bone in edit_bones if bone.name not in official_bones_set]
                
                # 为每个非官方骨骼检查映射关系
                for bone in non_official_bones:
                    simplified_name = simplify_bonename(bone.name)
                    
                    # 查找匹配的自定义到官方映射
                    for custom_name, official_name in custom_to_official.items():
                        if simplified_name == simplify_bonename(custom_name) and official_name in edit_bones:
                            # 避免重复添加
                            if (bone.name, official_name) not in added_relations:
                                item = self.mapping_items.add()
                                item.official_bone = official_name  # 父骨骼(官方)
                                item.custom_bone = bone.name  # 子骨骼(自定义)
                                added_relations.add((bone.name, official_name))
                                break
            
            # 恢复原来的模式
            if current_mode == 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            elif current_mode == 'POSE':
                bpy.ops.object.mode_set(mode='POSE')
            elif current_mode == 'EDIT_ARMATURE':
                pass  # 已经在编辑模式
                
            if len(self.mapping_items) == 0:
                self.report({'WARNING'}, _("No bone mapping relationships found that match the criteria"))
        except (json.JSONDecodeError, TypeError) as e:
            self.report({'ERROR'}, f"{_('Failed to parse mapping data')}: {str(e)}")
            return {'CANCELLED'}
        
        return super().invoke(context, event)
    
    def execute(self, context):
        # 获取目标骨架
        obj = bpy.data.objects.get(self.armature_name)
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, _("Armature object not found"))
            return {'CANCELLED'}
            
        # 保存当前模式
        current_mode = context.mode
        
        # 设置为编辑模式
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = obj.data.edit_bones
        selected_bones = [bone for bone in edit_bones if bone.select]
        
        # 解析传递的映射数据
        try:
            mapping_data = json.loads(self.mapping_data)
            official_to_customs = mapping_data.get('official_to_customs', {})
            custom_to_official = mapping_data.get('custom_to_official', {})
        except (json.JSONDecodeError, TypeError) as e:
            self.report({'ERROR'}, f"{_('Failed to parse mapping data')}: {str(e)}")
            return {'CANCELLED'}
        
        # 根据预览模式执行相应的处理
        if selected_bones and self.preview_mode == 'SELECTED':
            # 处理选中的骨骼
            processed_bones = graft_process_selected_bones(
                edit_bones, selected_bones, official_to_customs, custom_to_official
            )
            status_message = f"{_('Processed')} {len(processed_bones)} {_('selected bones')}"
        else:
            # 处理所有骨骼
            processed_bones = graft_process_all_bones(
                edit_bones, official_to_customs, custom_to_official
            )
            status_message = f"{_('Processed')} {len(processed_bones)} {_('bones')}"
        
        # 恢复到姿态模式
        bpy.ops.object.mode_set(mode='POSE')
        
        # 报告结果
        if processed_bones:
            self.report({'INFO'}, f"{_('Bone grafting completed')}. {status_message}")
        else:
            self.report({'WARNING'}, _("No suitable bones found for grafting, please check bone positions and mapping relationships"))
            
        return {'FINISHED'}

class L4D2_OT_GraftingOperator(bpy.types.Operator, L4D2_OT_BaseOperator):
    bl_idname = "l4d2.grafting_operator"
    bl_label = "Graft Bone"
    bl_description = "Automatically set the parent-child level of bones based on bone mapping relationships"
    bl_options = {'REGISTER', 'UNDO'}

    # threshold = 0.01  # 设置阈值

    def invoke(self, context, event):
        # 步骤 1: 初始化和验证
        # 准备基础数据
        self._prepare_base_data(context)
        
        # 如果映射计数为0，可能表示数据加载失败
        if self.mapping_count == 0:
            self.report({'ERROR'}, _("Failed to load mapping data"))
            return {'CANCELLED'}
        
        # 验证目标骨架
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, _("Armature object not selected or selected object is not an armature type"))
            return {'CANCELLED'}
            
        # 进入编辑模式并获取骨骼数量
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = obj.data.edit_bones
        selected_bones = [bone for bone in edit_bones if bone.select]
        selected_bones_count = len(selected_bones)
        
        # 构建映射关系
        official_to_customs, custom_to_official = graft_build_mappings()
        
        # 生成预览数据
        mapping_preview = generate_grafting_preview(
            edit_bones, selected_bones, official_to_customs, custom_to_official
        )
        
        # 返回到对象模式
        bpy.ops.object.mode_set(mode='OBJECT')
            
        if not official_to_customs:
            self.report({'WARNING'}, _("No available bone mapping relationships, grafting may be incomplete"))
            
        # 简化映射数据，只包含必要信息减少JSON序列化负担
        mapping_data = {
            'official_to_customs': official_to_customs,
            'custom_to_official': custom_to_official,
            'mapping_only': True
        }
        
        # 序列化映射关系
        try:
            mapping_data_json = json.dumps(mapping_data)
        except TypeError as e:
            self.report({'ERROR'}, f"{_('Failed to serialize mapping data')}: {str(e)}")
            return {'CANCELLED'}
            
        # 调用确认面板
        bpy.ops.l4d2.grafting_confirm(
            'INVOKE_DEFAULT',
            mapping_source=self.mapping_source,
            preset_name=self.preset_name,
            armature_name=obj.name,
            mapping_count=self.mapping_count,
            common_count=self.common_count,
            unique_count=self.unique_count,
            selected_bones_count=selected_bones_count,
            mapping_preview=mapping_preview,
            mapping_data=mapping_data_json
        )
        
        return {'FINISHED'}
        
    def execute(self, context):
        # 调用invoke方法来显示确认面板
        return self.invoke(context, None)

class L4D2_OT_RenameBonesOperator(bpy.types.Operator, L4D2_OT_BaseOperator):
    bl_idname = "l4d2.rename_bones_operator"
    bl_label = _("Rename Bone")
    bl_description = _("Rename custom bone names to Valve bone names based on bone mapping relationships")
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # 准备基础数据
        self._prepare_base_data(context)
        
        # 如果映射计数为0，可能表示数据加载失败
        if self.mapping_count == 0:
            self.report({'ERROR'}, _("Failed to load mapping data"))
            return {'CANCELLED'}
        
        # 验证目标骨架
        armature_obj = context.active_object
        if not armature_obj or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, _("Armature object not selected or selected object is not an armature type"))
            return {'CANCELLED'}
        
        # 构建映射关系
        official_to_customs, custom_to_official = graft_build_mappings()
        
        # 添加映射源信息
        mapping_sources = {}
        for custom_name, official_name in custom_to_official.items():
            # 确定映射来源
            mapping_sources[custom_name] = "Common"  # 默认来源
            for common_bone, customs in current_unique_mapping.items():
                if custom_name in customs:
                    mapping_sources[custom_name] = "Unique"
                    break
        
        # 准备映射数据
        mapping_data = {
            'official_to_customs': official_to_customs,
            'custom_to_official': custom_to_official,
            'mapping_sources': mapping_sources
        }
        
        # 序列化映射关系
        try:
            mapping_data_json = json.dumps(mapping_data)
        except TypeError as e:
            self.report({'ERROR'}, f"{_('Failed to serialize mapping data')}: {str(e)}")
            return {'CANCELLED'}
        
        # 调用确认面板
        bpy.ops.l4d2.rename_bones_confirm(
            'INVOKE_DEFAULT',
            mapping_source=self.mapping_source,
            preset_name=self.preset_name,
            armature_name=armature_obj.name,
            mapping_count=self.mapping_count,
            common_count=self.common_count,
            unique_count=self.unique_count,
            mapping_data=mapping_data_json
        )
        
        return {'FINISHED'}
    
    def execute(self, context):
        # 调用invoke方法来显示确认面板
        return self.invoke(context, None)

class RenameBonesConfirmItem(bpy.types.PropertyGroup):
    """用于存储重命名骨骼映射关系的属性组"""
    official_bone: bpy.props.StringProperty(
        name=_("Target Name"),
        description=_("The new name to rename the bone to"),
        default=""
    )
    custom_bone: bpy.props.StringProperty(
        name=_("Current Name"),
        description=_("The current bone name to be renamed"),
        default=""
    )
    source: bpy.props.StringProperty(
        name=_("Source"),
        description=_("Source of the mapping relationship"),
        default=""
    )

class RENAME_UL_MappingList(bpy.types.UIList):
    """用于绘制重命名骨骼映射关系的UIList"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # 使用分割布局控制列宽比例
            split = layout.split(factor=0.05)  # 10%给序号
            # 显示序号（从1开始）
            split.label(text=f"{index+1}")
            
            # 剩余部分继续分割
            remaining = split.split(factor=0.45)  # 45%给官方骨骼名称
            # 官方骨骼名称列
            remaining.label(text=item.official_bone, translate=False)
            
            # 剩余部分继续分割
            custom_src = remaining.split(factor=0.6)  # 70%给自定义骨骼名称
            # 自定义骨骼名称列
            custom_src.label(text=item.custom_bone, translate=False)
            
            # 最后显示来源
            custom_src.label(text=f"[{item.source}]", translate=False)
            
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.official_bone)

    def filter_items(self, context, data, propname):
        """用于过滤和排序UIList项"""
        flt_flags = []
        flt_neworder = []
        
        items = getattr(data, propname)
        
        # 默认过滤标志
        if self.filter_name:
            flt_flags = bpy.types.UI_UL_list.filter_items_by_name(
                self.filter_name, self.bitflag_filter_item, items, 
                "official_bone", "custom_bone", "source"
            )
        else:
            flt_flags = [self.bitflag_filter_item] * len(items)
            
        return flt_flags, flt_neworder

class L4D2_OT_RenameBonesConfirmOperator(bpy.types.Operator, L4D2_OT_BaseOperator):
    bl_idname = "l4d2.rename_bones_confirm"
    bl_label = _("Confirm Bone Renaming")
    bl_description = _("Confirm current mapping data and execute bone renaming operation")
    bl_options = {'REGISTER', 'INTERNAL'}
    
    # 特有属性
    armature_name: bpy.props.StringProperty()
    
    # 映射项集合
    mapping_items: bpy.props.CollectionProperty(type=RenameBonesConfirmItem)
    active_mapping_index: bpy.props.IntProperty(default=0)
    
    # 过滤字段
    filter_text: bpy.props.StringProperty(
        name=_("Filter"),
        description=_("Filter by bone name"),
        default=""
    )
    
    def draw(self, context):
        layout = self.layout
        
        # 显示基本信息
        box = layout.box()
        row = box.row()
        row.label(text=f"{_('Current Preset')}: {self.preset_name}")
        row.label(text=f"{_('Data Source')}: {self.mapping_source}")
        
        row = box.row()
        row.label(text=f"{_('Target Armature')}: {self.armature_name}")
        
        # 显示映射统计信息
        row = box.row()
        row.label(text=f"{_('Official Mapping Bones')}: {self.mapping_count}")
        row.label(text=f"{_('Common Mapping Bones')}: {self.common_count}")
        row.label(text=f"{_('Unique Mapping Bones')}: {self.unique_count}")
        
        # 显示映射关系
        mapping_box = layout.box()
        
        # 分为两行，第一行显示标题，第二行显示过滤器
        row = mapping_box.row()
        row.label(text=f"{_('Renaming Mapping Relationships')} ({len(self.mapping_items)})")
        
        row = mapping_box.row()
        row.prop(self, "filter_text", text=_("Filter"), icon='VIEWZOOM')
        
        # 创建表头 - 与UIList中的布局保持一致
        header_row = mapping_box.row()
        split = header_row.split(factor=0.05)  # 10%给序号
        split.label(text="  #")
        
        remaining = split.split(factor=0.45)  # 45%给官方骨骼名称
        remaining.label(text="            " + _("Target Name"))
        
        custom_src = remaining.split(factor=0.6)  # 70%给自定义骨骼名称
        custom_src.label(text=_("Current Name"))
        custom_src.label(text=_("Source"))
        
        # 使用专为重命名设计的UIList
        mapping_box.template_list(
            "RENAME_UL_MappingList", "", 
            self, "mapping_items", 
            self, "active_mapping_index", 
            rows=10  # 显示行数，超过会自动出现滚动条
        )
        
        # 显示操作信息
        operation_box = layout.box()
        operation_box.label(text=_("Operation Process:"))
        row = operation_box.row()
        row.label(text="1. " + _("Load mapping relationships"))
        row = operation_box.row()
        row.label(text="2. " + _("Match custom bones to official bones"))
        row = operation_box.row()
        row.label(text="3. " + _("Rename custom bones to official names"))

    def invoke(self, context, event):
        try:
            # 解析映射数据
            mapping_data = json.loads(self.mapping_data)
            official_to_customs = mapping_data.get('official_to_customs', {})
            custom_to_official = mapping_data.get('custom_to_official', {})
            mapping_sources = mapping_data.get('mapping_sources', {})
            
            # 清空现有项
            self.mapping_items.clear()
            
            # 获取目标骨架
            obj = bpy.data.objects.get(self.armature_name)
            
            # 确保当前对象存在且为骨架
            if not obj or obj.type != 'ARMATURE':
                self.report({'ERROR'}, _("Armature object not found or not an armature type"))
                return {'CANCELLED'}
            
            # A->B和B->A形式的映射处理
            if official_to_customs and custom_to_official:
                # 获取所有骨骼的简化名称
                bone_simplified_names = {simplify_bonename(bone.name): bone.name for bone in obj.data.bones}
                
                # 处理每个自定义到官方的映射关系
                for custom_name, official_name in custom_to_official.items():
                    simplified_name = simplify_bonename(custom_name)
                    # 查找骨架中匹配的骨骼
                    for bone_simplified, bone_name in bone_simplified_names.items():
                        if simplified_name == bone_simplified:
                            # 添加映射项
                            item = self.mapping_items.add()
                            item.official_bone = official_name
                            item.custom_bone = bone_name
                            item.source = mapping_sources.get(custom_name, "Default")
                            break
            
            if len(self.mapping_items) == 0:
                self.report({'WARNING'}, _("No bone mapping relationships found that match the current armature"))
                
        except (json.JSONDecodeError, TypeError) as e:
            self.report({'ERROR'}, f"{_('Failed to parse mapping data')}: {str(e)}")
            return {'CANCELLED'}
        
        return super().invoke(context, event)
    
    def execute(self, context):
        # 获取目标骨架
        obj = bpy.data.objects.get(self.armature_name)
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, _("Armature object not found or not an armature type"))
            return {'CANCELLED'}
        
        # 确保在物体模式
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # 遍历所有映射项执行重命名
        renamed_count = 0
        for item in self.mapping_items:
            bone = obj.data.bones.get(item.custom_bone)
            if bone:
                bone.name = item.official_bone
                renamed_count += 1
        
        # 报告结果
        if renamed_count > 0:
            self.report({'INFO'}, f"{_('Renamed')} {renamed_count} {_('bones successfully')}")
        else:
            self.report({'WARNING'}, _("No bones were renamed, please check the mapping relationships"))
        
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
        layout.operator("l4d2.rename_bones_operator", icon="OUTLINER_OB_FONT")



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
    use_x: bpy.props.BoolProperty(
        name="X",
        description="使用X轴约束",
        default=True
    )
    use_y: bpy.props.BoolProperty(
        name="Y",
        description="使用Y轴约束",
        default=True
    )
    use_z: bpy.props.BoolProperty(
        name="Z",
        description="使用Z轴约束",
        default=True
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
            
            
            elif context.scene.mapping_ui_tab == 'UNIQUE' or context.scene.mapping_ui_tab == 'COMMON':
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

            elif context.scene.mapping_ui_tab == 'AXIS':
                 # 轴控制标签页布局
                 # 左侧：官方骨骼名称
                 split = row.split(factor=0.6) # 60% for name
                 split.prop(item, "official_bone", text="", emboss=False) # Allow editing? Or just label? Use label for now.
                 # split.label(text=item.official_bone) # Use label if not editable

                 # 右侧：XYZ轴控制
                 axis_col = split.column()
                 axis_row = axis_col.row(align=True)
                 # Ensure these props exist on the item; _add_mapping_item should handle defaults
                 axis_row.prop(item, "use_x", text="X", toggle=True)
                 axis_row.prop(item, "use_y", text="Y", toggle=True)
                 axis_row.prop(item, "use_z", text="Z", toggle=True)

                 # No remove button directly here, as removing the official bone mapping is complex.
                 # Users should manage mappings in the 'ALL' tab.

        elif self.layout_type in {'GRID'}:
            # Handle GRID layout if necessary, maybe just show official bone name
            layout.alignment = 'CENTER'
            if context.scene.mapping_ui_tab == 'AXIS':
                 layout.label(text=item.official_bone)
            else:
                 # Keep existing GRID logic for other tabs if any
                 layout.label(text=item.official_bone) # Default or adapt as needed

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # 根据搜索字符串过滤
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "official_bone")
        else:
            flt_flags = [self.bitflag_filter_item] * len(items)
            
        return flt_flags, []

# 生成预设列表用于枚举属性
def get_preset_enum_items(self, context):
    items = []
    if os.path.exists(MAPPING_PRESETS_DIR):
        for file in os.listdir(MAPPING_PRESETS_DIR):
            if file.endswith('.json'):
                name = file[:-5]  # 去掉.json后缀
                items.append((name, name, ""))
    return items if items else [("None", "None", "")]

# 预设选择操作符
class L4D2_OT_SelectPreset(bpy.types.Operator):
    bl_idname = "l4d2.select_preset"
    bl_label = "Select Preset"
    bl_description = "选择预设并应用"
    
    preset_name: bpy.props.EnumProperty(
        name="预设",
        description="选择要使用的预设",
        items=get_preset_enum_items
    )
    
    def execute(self, context):
        # 设置活动预设并加载
        context.scene.active_preset_name = self.preset_name
        success, error_msg = MappingDataManager.load_preset_data(context, self.preset_name)
        if not success:
            self.report({'ERROR'}, f"加载预设失败: {error_msg}")
            return {'CANCELLED'}
            
        # 更新UI列表
        if not MappingDataManager.update_ui_list(context):
            self.report({'ERROR'}, "更新UI列表失败")
            return {'CANCELLED'}
            
        self.report({'INFO'}, f"预设 {self.preset_name} 已加载")
        return {'FINISHED'}

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
        
        # 从映射列表获取XYZ轴控制，存储到自定义属性
        # 创建一个字典，存储每个官方骨骼的XYZ轴控制信息
        bone_axis_controls = {}
        for item in scene.mapping_list:
            if item.official_bone:
                bone_axis_controls[item.official_bone] = {
                    'use_x': item.use_x,
                    'use_y': item.use_y,
                    'use_z': item.use_z
                }
        
        # 将轴控制信息存储到场景自定义属性中
        scene['bone_axis_controls'] = json.dumps(bone_axis_controls)
        
        print("全局变量已更新:")
        print(f"current_bone_mapping: {current_bone_mapping}")
        print(f"current_unique_mapping: {current_unique_mapping}")
        print(f"current_common_mapping: {current_common_mapping}")
        print(f"bone_axis_controls: {bone_axis_controls}")
        
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

class L4D2_OT_RiggingOperator(bpy.types.Operator, L4D2_OT_BaseOperator):
    bl_idname = "l4d2.rigging_operator"
    bl_label = "Align Bone"
    bl_description = "Align bones by batch adding copy location constrains to the bones\nThe mechanism of bone alignment is based on the mapping dictionary\n1、Ensure the TPOSE is approximately consistent\n2、Make sure the name of the skeleton is the same as the name of the first level under the skeleton"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # 准备基础数据
        self._prepare_base_data(context)
        
        # 如果映射计数为0，可能表示数据加载失败
        if self.mapping_count == 0:
            self.report({'ERROR'}, "映射数据加载失败")
            return {'CANCELLED'}
            
        # 验证骨架（仅检查存在性，不修改模式）
        armature_A, armature_B = validate_armatures(context)
        if not armature_A or not armature_B:
            self.report({'ERROR'}, "请先选择官方骨架和自定义骨架")
            return {'CANCELLED'}
            
        # 构建映射关系（只计算一次）
        base_official_to_customs = build_mapping_relation()
        
        # 增强映射关系，包含XYZ轴控制信息
        official_to_customs = {}
        
        # 获取当前活动预设中的项和轴控制信息
        active_items = []
        item_by_official = {}
        
        # 从映射列表构建官方骨骼到项的字典
        for item in context.scene.mapping_list:
            if item.official_bone:
                item_by_official[item.official_bone] = item
                active_items.append(item)
        
        # 对每个官方骨骼应用轴控制信息
        for official_bone, custom_bones in base_official_to_customs.items():
            # 在活动列表中查找该官方骨骼
            if official_bone in item_by_official:
                item = item_by_official[official_bone]
                # 包含轴控制信息
                official_to_customs[official_bone] = {
                    'custom_bones': custom_bones,
                    'use_x': item.use_x,
                    'use_y': item.use_y,
                    'use_z': item.use_z
                }
            else:
                # 使用默认轴控制，特殊处理盆骨
                use_x = use_y = True
                use_z = official_bone != 'ValveBiped.Bip01_Pelvis'
                
                official_to_customs[official_bone] = {
                    'custom_bones': custom_bones,
                    'use_x': use_x,
                    'use_y': use_y, 
                    'use_z': use_z
                }
        
        # 准备映射预览 - 显示所有映射，不再限制数量
        mapping_preview = ""
        simplified_bone_map = {simplify_bonename(bone.name): bone.name for bone in armature_B.data.bones}
        
        for official, mapping_info in official_to_customs.items():
            if isinstance(mapping_info, dict) and mapping_info['custom_bones']:
                custom_bone_names = mapping_info['custom_bones']
                use_x = mapping_info['use_x']
                use_y = mapping_info['use_y']
                use_z = mapping_info['use_z']
                
                for custom_name in custom_bone_names:
                    simplified_name = simplify_bonename(custom_name)
                    if simplified_name in simplified_bone_map:
                        axis_info = f"[X:{use_x} Y:{use_y} Z:{use_z}]"
                        mapping_preview += f"{official} -> {simplified_bone_map[simplified_name]} {axis_info}\n"
                        break
        
        # 序列化映射关系，避免重复计算
        try:
            mapping_data_json = json.dumps(official_to_customs)
        except TypeError as e:
            self.report({'ERROR'}, f"序列化映射数据失败: {str(e)}")
            return {'CANCELLED'}
        
        # 调用确认面板
        bpy.ops.l4d2.rigging_confirm(
            'INVOKE_DEFAULT',
            mapping_source=self.mapping_source,
            preset_name=self.preset_name,
            armature_a_name=armature_A.name,
            armature_b_name=armature_B.name,
            mapping_count=self.mapping_count,
            common_count=self.common_count,
            unique_count=self.unique_count,
            mapping_preview=mapping_preview,
            mapping_data=mapping_data_json  # 传递序列化的映射数据
        )
        
        return {'FINISHED'}

    def execute(self, context):
        # 调用invoke方法来显示确认面板
        return self.invoke(context, None)

# 更新classes列表
classes = [
    CustomBoneItem,  
    MappingListItem,
    RiggingConfirmItem,
    GraftingConfirmItem,
    RenameBonesConfirmItem,  # 添加新的重命名项类
    MappingData,
    TempMappingData,
    BONE_UL_MappingList,
    RIGGING_UL_MappingList,
    GRAFTING_UL_MappingList,
    RENAME_UL_MappingList,  # 添加新的重命名UIList类
    L4D2_OT_RiggingConfirmOperator,
    L4D2_OT_GraftingOperator,
    L4D2_OT_GraftingConfirmOperator,
    L4D2_OT_RiggingOperator,
    L4D2_OT_RenameBonesOperator,
    L4D2_OT_RenameBonesConfirmOperator,  # 添加新的重命名确认操作符
    L4D2_OT_UnbindAndKeepShape,
    L4D2_OT_CreatePreset,
    L4D2_OT_DeletePreset,
    L4D2_OT_LoadPreset,
    L4D2_OT_ImportPreset,
    L4D2_OT_ExportPreset,
    L4D2_PT_BoneModifyPanel,
    MAPPING_OT_AddNewMapping,
    MAPPING_OT_ApplyChanges,
    MAPPING_OT_ToggleSearchMode,
    MAPPING_MT_CustomBonesMenu,
    MAPPING_OT_SelectCustomBone,
    MAPPING_OT_AddCustomBone,
    MAPPING_OT_RemoveCustomBone,
    MAPPING_OT_RemoveMapping,
    L4D2_OT_SelectPreset,
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
            ('COMMON', "通用映射", ""),
            ('AXIS', "轴控制", "")
        ],
        default='ALL',
        update=MappingDataManager.update_mapping_list  # 更新回调函数引用
    )
    bpy.types.Scene.use_search_mode = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.active_preset_name = bpy.props.EnumProperty(
        name="活动预设",
        description="当前活动的预设",
        items=get_preset_enum_items
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
