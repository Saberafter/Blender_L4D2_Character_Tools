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
import copy
from .resources import bone_dict

preset_dir = os.path.join(bpy.utils.resource_path('USER'), 'scripts', 'presets', 'L4D2 Character Tools')
BONE_NAMES_FILE_PATH = os.path.join(preset_dir,"bone_dict.json")
BONE_MAPPING_PRESETS_DIR = os.path.join(preset_dir, "mapping_presets")

# 骨骼映射相关的全局变量
current_bone_mapping = bone_dict.bone_mapping.copy()  # 当前正在使用的映射
current_unique_mapping = {}  # 当前正在使用的独立映射 {"通用骨骼": ["自定义骨骼1", "自定义骨骼2"]}
current_common_mapping = {}  # 存储所有已加载的独立映射预设

# 确保预设目录存在
if not os.path.exists(BONE_MAPPING_PRESETS_DIR):
    os.makedirs(BONE_MAPPING_PRESETS_DIR)
    # 创建默认的V社预设
    default_preset = {
        "name": "Valve_L4D2",
        "description": "默认映射表",
        "mapping": bone_dict.bone_mapping,
        "unique_mapping": {}
    }
    default_preset_path = os.path.join(BONE_MAPPING_PRESETS_DIR, "Valve_L4D2.json")
    try:
        with open(default_preset_path, 'w', encoding='utf-8') as f:
            # 使用相同的格式化方式
            f.write('{\n')
            f.write('    "name": "Valve_L4D2",\n')
            f.write('    "description": "默认映射表",\n')
            f.write('    "mapping": {\n')
            
            # 写入mapping部分，每个键值对占一行
            mapping_items = list(bone_dict.bone_mapping.items())
            for i, (key, value) in enumerate(mapping_items):
                is_last = i == len(mapping_items) - 1
                line = f'        "{key}": {json.dumps(value, ensure_ascii=False)}'
                f.write(line + (',' if not is_last else '') + '\n')
            
            f.write('    },\n')
            f.write('    "unique_mapping": {}\n')
            f.write('}\n')
    except Exception as e:
        print(f"创建默认预设时发生错误: {e}")

def get_preset_files():
    """获取所有预设文件"""
    if not os.path.exists(BONE_MAPPING_PRESETS_DIR):
        return []
    return [f for f in os.listdir(BONE_MAPPING_PRESETS_DIR) if f.endswith('.json')]

def get_preset_enum_items(self, context):
    """生成预设下拉列表的选项"""
    items = []
    for preset_file in get_preset_files():
        name = os.path.splitext(preset_file)[0]
        # 尝试读取预设文件获取描述
        try:
            with open(os.path.join(BONE_MAPPING_PRESETS_DIR, preset_file), 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
                description = preset_data.get('description', '')
                items.append((preset_file, name, description))
        except Exception:
            items.append((preset_file, name, ""))
    return items

def load_preset(preset_file):
    """加载预设"""
    global current_bone_mapping, current_unique_mapping
    try:
        # 从文件加载
        with open(os.path.join(BONE_MAPPING_PRESETS_DIR, preset_file), 'r', encoding='utf-8') as f:
            preset_data = json.load(f)
            
        # 更新全局变量
        current_bone_mapping = preset_data.get('mapping', {}).copy()
        current_unique_mapping = preset_data.get('unique_mapping', {}).copy()
        
        # 更新属性管理器的数据
        props = bpy.context.scene.bone_dict_manager
        props.load_data_from_preset(preset_data)
        
        return True
    except Exception as e:
        print(f"加载预设时发生错误: {e}")
        return False

def save_formatted_json(filepath, data, mapping_order=None):
    """
    通用的JSON格式化保存函数
    
    Args:
        filepath: 保存文件的路径
        data: 要保存的数据字典，必须包含 name, description 和 mapping
        mapping_order: 可选的映射顺序列表，用于控制mapping的保存顺序
    """
    try:
        # 检查数据完整性
        if not isinstance(data, dict):
            raise ValueError(f"数据必须是字典类型,当前类型: {type(data)}")
        
        # 检查必要的键
        required_keys = ['name', 'description', 'mapping']
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"数据缺少必要的键: {missing_keys}")
        
        # 检查mapping中是否有空条目
        empty_mappings = []
        if mapping_order is not None:
            for item in mapping_order:
                if not item.official_bone.strip() or not item.common_bone.strip():
                    empty_mappings.append(f"{item.official_bone} → {item.common_bone}")
        else:
            for key, value in data["mapping"].items():
                if not key.strip() or not value or not value[0].strip():
                    empty_mappings.append(f"{key} → {value[0] if value else ''}")
        
        if empty_mappings:
            return False

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('{\n')
            f.write(f'    "name": "{data["name"]}",\n')
            f.write(f'    "description": "{data["description"]}",\n')
            
            # 写入mapping部分
            f.write('    "mapping": {\n')
            if mapping_order is not None:
                mapping_items = [(item.official_bone, [item.common_bone]) for item in mapping_order]
            else:
                mapping_items = list(data["mapping"].items())
            
            # 写入mapping部分，每个键值对占一行
            for i, (key, value) in enumerate(mapping_items):
                is_last = i == len(mapping_items) - 1
                line = f'        "{key}": {json.dumps(value, ensure_ascii=False)}'
                f.write(line + (',' if not is_last else '') + '\n')
            f.write('    }')
            
            # 如果存在unique_mapping，则写入
            if "unique_mapping" in data:
                f.write(',\n    "unique_mapping": {\n')
                unique_items = list(data["unique_mapping"].items())
                for i, (key, value) in enumerate(unique_items):
                    is_last = i == len(unique_items) - 1
                    line = f'        "{key}": {json.dumps(value, ensure_ascii=False)}'
                    f.write(line + (',' if not is_last else '') + '\n')
                f.write('    }')
            
            f.write('\n}\n')
            
        return True
    except Exception as e:
        return False

def simplify_bonename(n):
    return n.lower().translate(dict.fromkeys(map(ord, u" _.")))

# 保存骨骼字典到文件
def save_bone_names(bone_names_dict):
    """保存骨骼字典到文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(BONE_NAMES_FILE_PATH), exist_ok=True)
        
        with open(BONE_NAMES_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(bone_names_dict, f, ensure_ascii=False, indent=4)
            print(f"保存骨骼字典到: {BONE_NAMES_FILE_PATH}")
            print(f"保存的内容: {bone_names_dict}")
    except Exception as e:
        print(f"保存骨骼字典失败: {e}")

# 使用全局变量从文件加载骨骼字典
def load_bone_names():
    """加载全局的骨骼字典"""
    global current_common_mapping
    
    # 确保预设目录存在
    if not os.path.isdir(preset_dir):
        try:
            os.makedirs(preset_dir)
            print(f"创建预设目录: {preset_dir}")
        except Exception as e:
            print(f"创建预设目录失败: {e}")
            current_common_mapping = bone_dict.bone_names
            return

    # 检查文件是否存在
    if os.path.isfile(BONE_NAMES_FILE_PATH):
        try:
            with open(BONE_NAMES_FILE_PATH, 'r', encoding='utf-8') as f:
                current_common_mapping = json.load(f)
                print(f"从文件加载骨骼字典: {BONE_NAMES_FILE_PATH}")
                print(f"加载的内容: {current_common_mapping}")
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            current_common_mapping = bone_dict.bone_names
            save_bone_names(current_common_mapping)
        except Exception as e:
            print(f"加载骨骼字典文件失败: {e}")
            current_common_mapping = bone_dict.bone_names
            save_bone_names(current_common_mapping)
    else:
        print(f"骨骼字典文件不存在，使用默认值: {BONE_NAMES_FILE_PATH}")
        current_common_mapping = bone_dict.bone_names
        save_bone_names(current_common_mapping)

load_bone_names() 

# 创建反向映射，以便能够定位到 bone_mapping 的键。此处只使用每个键的最后一个值。
reverse_bone_mapping = {}
for k, v in bone_dict.bone_mapping.items():
    reverse_bone_mapping[v[-1].lower()] = k

# 修改后的下拉列表枚举项创建函数
def bone_keys_enum(self, context):
    items = []
    for key in current_common_mapping:
        # 对于 'spine'，我们需要确保映射到 'ValveBiped.Bip01_Spine'
        if key == 'spine':
            desired_mapping = 'ValveBiped.Bip01_Spine' 
        else:
            # 查找用于显示的bone_mapping键
            desired_mapping = reverse_bone_mapping.get(key, key) # 若未找到，则回退到原始键

        items.append((key, desired_mapping, '')) # UI显示的文本是desired_mapping，但内部操作基于key

    return items

# 骨架骨骼名称下拉列表枚举项创建函数
def bone_names_enum(self, context):
    # 假设armature_object是用户选择的骨架对象，这一部分的实现取决于实际数据
    armature_object = bpy.context.object
    if armature_object and armature_object.type == 'ARMATURE':
        items = [(b.name, b.name, '') for b in armature_object.data.bones]
        return items
    return []

# 用于存储下拉列表选择的属性
class BoneMappingItem(bpy.types.PropertyGroup):
    def on_official_bone_update(self, context):
        # 当从prop_search选择新值时，这个回调会被触发
        if hasattr(context.scene, "bone_dict_manager"):
            context.scene.bone_dict_manager.update_temp_data(self)

    def on_common_bone_update(self, context):
        # 当通用骨骼名称更改时，更新temp_data
        if hasattr(context.scene, "bone_dict_manager"):
            context.scene.bone_dict_manager.update_temp_data(self)

    def on_custom_bone_update(self, context):
        # 当自定义骨骼名称更改时，更新temp_data
        if hasattr(context.scene, "bone_dict_manager"):
            context.scene.bone_dict_manager.update_temp_data(self)

    # 用于UI显示和编辑的临时值
    official_bone: bpy.props.StringProperty(
        name="Official Bone",
        update=on_official_bone_update
    )
    common_bone: bpy.props.StringProperty(
        name="Common Bone",
        update=on_common_bone_update
    )

    # 存储未保存的自定义骨骼列表
    temp_custom_bones: bpy.props.CollectionProperty(
        type=bpy.types.PropertyGroup,
        name="Temporary Custom Bones"
    )

    # 使用StringProperty替换EnumProperty
    custom_bone: bpy.props.StringProperty(
        name="Custom Bone",
        update=on_custom_bone_update
    )

    # 用于存储原始值
    original_official_bone: bpy.props.StringProperty()
    original_common_bone: bpy.props.StringProperty()
    original_custom_bone: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    # 添加官方骨骼输入模式
    official_bone_input_mode: bpy.props.EnumProperty(
        name="Official Bone Input Mode",
        items=[
            ('SEARCH', "搜索模式", "从现有骨骼中搜索"),
            ('MANUAL', "手动输入", "手动输入骨骼名称")
        ],
        default='SEARCH'
    )

def update_active_tab(self, context):
    """标签页切换回调"""
    props = context.scene.bone_dict_manager
    current_tab = props.active_tab
    
    # 保存当前标签页的数据到temp_data
    if len(props.mapping_list) > 0:
        if current_tab == 'ALL':
            # 保存所有映射
            for item in props.mapping_list:
                if item.official_bone and item.common_bone:
                    props.temp_data["official_mapping"][item.official_bone] = [item.common_bone]
                    # 更新自定义骨骼
                    custom_bones = [bone.name for bone in item.temp_custom_bones]
                    if custom_bones:
                        if item.common_bone not in current_common_mapping:
                            props.temp_data["unique_mapping"][item.common_bone] = custom_bones
                        else:
                            props.temp_data["common_mapping"][item.common_bone] = custom_bones
        elif current_tab == 'UNIQUE':
            # 保存独立映射
            for item in props.mapping_list:
                if item.common_bone:
                    custom_bones = [bone.name for bone in item.temp_custom_bones]
                    if custom_bones:
                        props.temp_data["unique_mapping"][item.common_bone] = custom_bones
        else:  # COMMON
            # 保存通用映射
            for item in props.mapping_list:
                if item.common_bone:
                    custom_bones = [bone.name for bone in item.temp_custom_bones]
                    if custom_bones:
                        props.temp_data["common_mapping"][item.common_bone] = custom_bones
    
    # 同步到新标签页的视图
    props.sync_views()

def update_target_bone(self, context):
    """处理选择变化的回调"""
    if self.mapping_list_index >= 0 and len(self.mapping_list) > self.mapping_list_index:
        selected_item = self.mapping_list[self.mapping_list_index]
        self.target_official_bone = selected_item.official_bone

class BoneDictManagerProperties(bpy.types.PropertyGroup):
    def __init__(self):
        super().__init__()
        # 初始化主数据源和临时数据源
        self.main_data = {"mappings": []}
        self.temp_data = {"mappings": []}
    
    def build_main_data(self):
        """构建主数据源"""
        mappings = []
        
        # 从current_bone_mapping构建基础映射
        for official_bone, common_bones in current_bone_mapping.items():
            if common_bones:
                common_bone = common_bones[0]
                mapping = {
                    "official_bone": official_bone,
                    "common_bone": common_bone,
                    "custom_bones": [],
                    "is_unique": False
                }
                
                # 获取自定义骨骼
                if common_bone in current_unique_mapping:
                    mapping["custom_bones"] = current_unique_mapping[common_bone].copy()
                    mapping["is_unique"] = True
                elif common_bone in current_common_mapping:
                    mapping["custom_bones"] = current_common_mapping[common_bone].copy()
                    mapping["is_unique"] = False
                
                mappings.append(mapping)
        
        # 添加独立映射中的额外映射（那些不在current_bone_mapping中的）
        for common_bone, custom_bones in current_unique_mapping.items():
            if not any(m["common_bone"] == common_bone for m in mappings):
                mapping = {
                    "official_bone": "",
                    "common_bone": common_bone,
                    "custom_bones": custom_bones.copy(),
                    "is_unique": True
                }
                mappings.append(mapping)
        
        self.main_data = {"mappings": mappings}
        self.temp_data = copy.deepcopy(self.main_data)
    
    def update_mapping_list(self):
        """更新UI列表显示"""
        # 清空当前列表
        self.mapping_list.clear()
        
        # 根据当前标签页筛选数据
        if self.active_tab == 'ALL':
            items = self.temp_data["mappings"]
        elif self.active_tab == 'UNIQUE':
            items = [m for m in self.temp_data["mappings"] if m["is_unique"]]
        else:  # COMMON
            items = [m for m in self.temp_data["mappings"] if not m["is_unique"]]
        
        # 构建UI列表
        for mapping in items:
            item = self.mapping_list.add()
            if "official_bone" in mapping:
                item.official_bone = mapping["official_bone"]
                item.original_official_bone = mapping["official_bone"]
            item.common_bone = mapping["common_bone"]
            item.original_common_bone = mapping["common_bone"]
            
            # 添加自定义骨骼
            for bone_name in mapping["custom_bones"]:
                temp_bone = item.temp_custom_bones.add()
                temp_bone.name = bone_name
            
            if item.temp_custom_bones:
                item.custom_bone = item.temp_custom_bones[0].name
                item.original_custom_bone = item.custom_bone
    
    def apply_changes(self):
        """应用更改到全局变量和文件"""
        global current_bone_mapping, current_unique_mapping, current_common_mapping
        
        # 清空全局变量
        current_bone_mapping = {}
        current_unique_mapping = {}
        current_common_mapping = {}
        
        # 从temp_data重建全局变量
        for mapping in self.temp_data["mappings"]:
            # 更新current_bone_mapping
            if "official_bone" in mapping:
                current_bone_mapping[mapping["official_bone"]] = [mapping["common_bone"]]
            
            # 根据is_unique更新对应的映射
            if mapping["is_unique"]:
                current_unique_mapping[mapping["common_bone"]] = mapping["custom_bones"]
            else:
                current_common_mapping[mapping["common_bone"]] = mapping["custom_bones"]
        
        # 保存到文件
        save_bone_names(current_common_mapping)
        
        # 如果有活动预设，保存预设
        if self.active_preset:
            preset_data = {
                "name": os.path.splitext(self.active_preset)[0],
                "description": loaded_presets.get(self.active_preset, {}).get('description', ''),
                "mapping": current_bone_mapping,
                "unique_mapping": current_unique_mapping
            }
            preset_path = os.path.join(BONE_MAPPING_PRESETS_DIR, self.active_preset)
            save_formatted_json(preset_path, preset_data)
            loaded_presets[self.active_preset] = preset_data
        
        # 更新主数据源
        self.main_data = copy.deepcopy(self.temp_data)
        self.has_unsaved_changes = False
    
    # 统一的临时数据源
    temp_data = {
        "official_mapping": {},  # 官方到通用的映射
        "common_mapping": {},    # 通用到自定义的映射(来自current_common_mapping)
        "unique_mapping": {}     # 独立的通用到自定义的映射
    }
    
    # 视图相关属性
    active_tab: bpy.props.EnumProperty(
        name="当前标签页",
        items=[
            ('ALL', "全部映射", "显示所有骨骼映射"),
            ('UNIQUE', "独有映射", "显示独立映射"),
            ('COMMON', "通用映射", "显示通用映射")
        ],
        default='ALL',
        update=update_active_tab
    )
    
    mapping_list: bpy.props.CollectionProperty(
        type=BoneMappingItem,
        name="Mapping List"
    )
    
    mapping_list_index: bpy.props.IntProperty(
        name="Mapping List Index",
        default=0,
        update=update_target_bone
    )
    
    # 数据操作方法
    def update_mapping(self, mapping_type, key, value):
        """统一的数据更新接口"""
        self.temp_data[mapping_type][key] = value
        self.sync_views()
        self.has_unsaved_changes = True
    
    def get_view_for_tab(self):
        """根据当前标签页获取对应的视图数据"""
        if self.active_tab == 'ALL':
            return self.create_all_view()
        elif self.active_tab == 'UNIQUE':
            return self.create_unique_view()
        else:
            return self.create_common_view()
    
    def create_all_view(self):
        """创建全部映射的视图"""
        view_data = []
        for official_bone, common_bones in self.temp_data["official_mapping"].items():
            if common_bones:
                common_bone = common_bones[0]
                custom_bones = []
                
                # 获取自定义骨骼
                if common_bone in self.temp_data["unique_mapping"]:
                    custom_bones = self.temp_data["unique_mapping"][common_bone]
                elif common_bone in self.temp_data["common_mapping"]:
                    custom_bones = self.temp_data["common_mapping"][common_bone]
                    
                view_data.append({
                    "official_bone": official_bone,
                    "common_bone": common_bone,
                    "custom_bones": custom_bones
                })
        return view_data
    
    def create_unique_view(self):
        """创建独立映射的视图"""
        view_data = []
        for common_bone, custom_bones in self.temp_data["unique_mapping"].items():
            view_data.append({
                "common_bone": common_bone,
                "custom_bones": custom_bones
            })
        return view_data
    
    def create_common_view(self):
        """创建通用映射的视图"""
        view_data = []
        for common_bone, custom_bones in self.temp_data["common_mapping"].items():
            view_data.append({
                "common_bone": common_bone,
                "custom_bones": custom_bones
            })
        return view_data
    
    def sync_views(self):
        """同步所有视图数据到UI列表"""
        # 清空当前列表
        self.mapping_list.clear()
        
        # 确保temp_data中包含所有必要的数据
        if "official_mapping" not in self.temp_data:
            self.temp_data["official_mapping"] = current_bone_mapping.copy()
        if "common_mapping" not in self.temp_data:
            self.temp_data["common_mapping"] = current_common_mapping.copy()
        if "unique_mapping" not in self.temp_data:
            self.temp_data["unique_mapping"] = current_unique_mapping.copy()
        
        if self.active_tab == 'ALL':
            # 显示官方映射和对应的通用/自定义骨骼
            for official_bone, common_bones in self.temp_data["official_mapping"].items():
                if common_bones:
                    common_bone = common_bones[0]
                    item = self.mapping_list.add()
                    item.official_bone = official_bone
                    item.common_bone = common_bone
                    item.original_official_bone = official_bone
                    item.original_common_bone = common_bone
                    
                    # 添加自定义骨骼
                    custom_bones = []
                    if common_bone in self.temp_data["unique_mapping"]:
                        custom_bones = self.temp_data["unique_mapping"][common_bone]
                    elif common_bone in self.temp_data["common_mapping"]:
                        custom_bones = self.temp_data["common_mapping"][common_bone]
                    
                    for bone_name in custom_bones:
                        temp_bone = item.temp_custom_bones.add()
                        temp_bone.name = bone_name
                    
                    if item.temp_custom_bones:
                        item.custom_bone = item.temp_custom_bones[0].name
                        item.original_custom_bone = item.custom_bone
                    
        elif self.active_tab == 'UNIQUE':
            # 显示独立映射
            for common_bone, custom_bones in self.temp_data["unique_mapping"].items():
                item = self.mapping_list.add()
                item.common_bone = common_bone
                item.original_common_bone = common_bone
                
                for bone_name in custom_bones:
                    temp_bone = item.temp_custom_bones.add()
                    temp_bone.name = bone_name
                
                if item.temp_custom_bones:
                    item.custom_bone = item.temp_custom_bones[0].name
                    item.original_custom_bone = item.custom_bone
                
        else:  # COMMON
            # 显示通用映射
            for common_bone, custom_bones in self.temp_data["common_mapping"].items():
                item = self.mapping_list.add()
                item.common_bone = common_bone
                item.original_common_bone = common_bone
                
                for bone_name in custom_bones:
                    temp_bone = item.temp_custom_bones.add()
                    temp_bone.name = bone_name
                
                if item.temp_custom_bones:
                    item.custom_bone = item.temp_custom_bones[0].name
                    item.original_custom_bone = item.custom_bone
        
        # 强制更新UI
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    
    def load_data_from_preset(self, preset_data):
        """从预设加载数据"""
        global current_bone_mapping, current_unique_mapping
        current_bone_mapping = preset_data.get("mapping", {}).copy()
        current_unique_mapping = preset_data.get("unique_mapping", {}).copy()
        
        # 同步视图并重置修改状态
        self.sync_views()
        
        # 重置所有项的original属性
        for item in self.mapping_list:
            if hasattr(item, 'official_bone'):
                item.original_official_bone = item.official_bone
            item.original_common_bone = item.common_bone
            item.original_custom_bones = ','.join([bone.name for bone in item.temp_custom_bones])
        
        self.has_unsaved_changes = False
    
    def save_data_to_preset(self):
        """保存数据到预设"""
        return {
            "mapping": self.temp_data["official_mapping"],
            "unique_mapping": self.temp_data["unique_mapping"]
        }

    def get_bone_values(self, context):
        """为选中的键生成值的列表"""
        if self.bone_key_enum in current_common_mapping:
            return [(v, v, "") for v in current_common_mapping[self.bone_key_enum]]
        return []

    # 添加一个新的方法来处理选择变化 - 移到前面
    def update_target_bone(self, context):
        if self.mapping_list_index >= 0 and len(self.mapping_list) > self.mapping_list_index:
            selected_item = self.mapping_list[self.mapping_list_index]
            self.target_official_bone = selected_item.official_bone

    # 添加未保存更改标记
    has_unsaved_changes: bpy.props.BoolProperty(
        name="Has Unsaved Changes",
        description="标记是否有未保存的更改",
        default=False
    )

    # 预设相关属性
    active_preset: bpy.props.EnumProperty(
        name="Active Preset",
        description="Select a bone mapping preset",
        items=get_preset_enum_items
    )
    
    new_preset_name: bpy.props.StringProperty(
        name="预设名称",
        description="输入新预设的名称",
        default=""
    )
    
    preset_description: bpy.props.StringProperty(
        name="预设描述",
        description="输入预设的描述信息",
        default=""
    )

    # 添加保存当前映射的布尔属性
    save_current_mapping: bpy.props.BoolProperty(
        name="Save Current Mapping",
        description="Save the current bone mapping as a new preset",
        default=False
    )

    # 修改target_official_bone的定义，添加update回调
    target_official_bone: bpy.props.StringProperty(
        name="Target Official Bone",
        description="当前选中的目标官方骨骼"
    )

    # 添加标签页属性
    active_tab: bpy.props.EnumProperty(
        name="当前标签页",
        items=[
            ('ALL', "全部映射", "显示所有骨骼映射"),
            ('UNIQUE', "独有映射", "显示独有映射"),
            ('COMMON', "通用映射", "显示通用映射")
        ],
        default='ALL',
        update=update_active_tab
    )

    # 添加映射列表属性
    mapping_list: bpy.props.CollectionProperty(
        type=BoneMappingItem,
        name="Mapping List"
    )
    mapping_list_index: bpy.props.IntProperty(
        name="Mapping List Index",
        default=0,
        update=update_target_bone
    )

    # 添加显示映射列表属性
    show_mapping_list: bpy.props.BoolProperty(
        name="显示映射列表",
        default=True
    )

    # 用于存储所有标签页的临时数据
    temp_all_mappings = {}  # 存储ALL标签页的临时数据
    temp_unique_mappings = {}  # 存储UNIQUE标签页的临时数据
    temp_common_mappings = {}  # 存储COMMON标签页的临时数据

    def update_mapping_list(self):
        """更新映射列表"""
        # 保存当前列表的临时状态到对应的临时存储中
        if len(self.mapping_list) > 0:
            if self.active_tab == 'ALL':
                # 不再清空temp_all_mappings，而是更新已有的条目
                for item in self.mapping_list:
                    if hasattr(item, 'official_bone'):
                        self.temp_all_mappings[item.official_bone] = {
                            'common_bone': item.common_bone,
                            'custom_bones': [bone.name for bone in item.temp_custom_bones],
                            'original_official_bone': item.original_official_bone,
                            'original_common_bone': item.original_common_bone,
                            'original_custom_bone': item.original_custom_bone
                        }
            elif self.active_tab == 'UNIQUE':
                # 不再清空temp_unique_mappings，而是更新已有的条目
                for item in self.mapping_list:
                    if item.common_bone not in current_common_mapping:
                        self.temp_unique_mappings[item.common_bone] = {
                            'custom_bones': [bone.name for bone in item.temp_custom_bones],
                            'original_common_bone': item.original_common_bone,
                            'original_custom_bone': item.original_custom_bone
                        }
            elif self.active_tab == 'COMMON':
                # 不再清空temp_common_mappings，而是更新已有的条目
                for item in self.mapping_list:
                    if item.common_bone in current_common_mapping:
                        self.temp_common_mappings[item.common_bone] = {
                            'custom_bones': [bone.name for bone in item.temp_custom_bones],
                            'original_common_bone': item.original_common_bone,
                            'original_custom_bone': item.original_custom_bone
                        }

        # 清空当前列表
        self.mapping_list.clear()

        if self.active_tab == 'ALL':
            # 如果有临时数据，使用临时数据
            if self.temp_all_mappings:
                # 按照current_bone_mapping的顺序添加项
                for official_bone, common_bones in current_bone_mapping.items():
                    if official_bone in self.temp_all_mappings:
                        data = self.temp_all_mappings[official_bone]
                        item = self.mapping_list.add()
                        item.official_bone = official_bone
                        item.common_bone = data['common_bone']
                        
                        # 恢复临时自定义骨骼列表
                        for bone_name in data['custom_bones']:
                            temp_bone = item.temp_custom_bones.add()
                            temp_bone.name = bone_name
                        
                        if item.temp_custom_bones:
                            item.custom_bone = item.temp_custom_bones[0].name
                        
                        # 恢复原始值
                        item.original_official_bone = data['original_official_bone']
                        item.original_common_bone = data['original_common_bone']
                        item.original_custom_bone = data['original_custom_bone']
            else:
                # 如果没有临时数据，从current_bone_mapping加载
                for official_bone, common_bones in current_bone_mapping.items():
                    if common_bones:
                        item = self.mapping_list.add()
                        item.official_bone = official_bone
                        item.common_bone = common_bones[0]
                        
                        # 从其他数据源加载自定义骨骼
                        if item.common_bone in current_unique_mapping:
                            for bone_name in current_unique_mapping[item.common_bone]:
                                temp_bone = item.temp_custom_bones.add()
                                temp_bone.name = bone_name
                        elif item.common_bone in current_common_mapping:
                            for bone_name in current_common_mapping[item.common_bone]:
                                temp_bone = item.temp_custom_bones.add()
                                temp_bone.name = bone_name
                        
                        if item.temp_custom_bones:
                            item.custom_bone = item.temp_custom_bones[0].name
                        
                        # 存储原始值
                        item.original_official_bone = official_bone
                        item.original_common_bone = common_bones[0]
                        if item.custom_bone:
                            item.original_custom_bone = item.custom_bone

        elif self.active_tab == 'UNIQUE':
            # 如果有临时数据，使用temp_data["unique_mapping"]
            for common_bone, custom_bones in self.temp_data["unique_mapping"].items():
                if common_bone not in current_common_mapping:  # 只显示不在current_common_mapping中的映射
                    item = self.mapping_list.add()
                    item.common_bone = common_bone
                    item.original_common_bone = common_bone
                    
                    for bone_name in custom_bones:
                        temp_bone = item.temp_custom_bones.add()
                        temp_bone.name = bone_name
                    
                    if item.temp_custom_bones:
                        item.custom_bone = item.temp_custom_bones[0].name
                        item.original_custom_bone = item.custom_bone

        else:  # COMMON
            # 如果有临时数据，使用临时数据
            if self.temp_common_mappings:
                # 按照current_common_mapping的顺序添加项
                for common_bone, custom_bones in current_common_mapping.items():
                    if common_bone in self.temp_common_mappings:
                        data = self.temp_common_mappings[common_bone]
                        item = self.mapping_list.add()
                        item.common_bone = common_bone
                        
                        # 恢复临时自定义骨骼列表
                        for bone_name in data['custom_bones']:
                            temp_bone = item.temp_custom_bones.add()
                            temp_bone.name = bone_name
                        
                        if item.temp_custom_bones:
                            item.custom_bone = item.temp_custom_bones[0].name
                        
                        # 恢复原始值
                        item.original_common_bone = data['original_common_bone']
                        item.original_custom_bone = data['original_custom_bone']
            else:
                # 如果没有临时数据，从current_common_mapping加载
                for common_bone, custom_bones in current_common_mapping.items():
                    item = self.mapping_list.add()
                    item.common_bone = common_bone
                    
                    for bone_name in custom_bones:
                        temp_bone = item.temp_custom_bones.add()
                        temp_bone.name = bone_name
                    
                    if item.temp_custom_bones:
                        item.custom_bone = item.temp_custom_bones[0].name
                    
                    # 存储原始值
                    item.original_common_bone = common_bone
                    if item.custom_bone:
                        item.original_custom_bone = item.custom_bone

    def init_temp_data(self):
        """初始化临时数据源"""
        # 清空现有数据
        self.temp_data["official_mapping"].clear()
        self.temp_data["common_mapping"].clear()
        self.temp_data["unique_mapping"].clear()
        
        # 从全局变量复制数据
        self.temp_data["official_mapping"].update(current_bone_mapping)
        # 使用深拷贝确保数据独立性
        for common_bone, custom_bones in current_common_mapping.items():
            self.temp_data["common_mapping"][common_bone] = custom_bones.copy()
        self.temp_data["unique_mapping"].update(current_unique_mapping)
        
        # 同步视图
        self.sync_views()

    def update_temp_data(self, item, is_new=False):
        """更新临时数据并追踪修改"""
        if not is_new:
            # 检查是否有修改
            has_changes = False
            
            # 检查官方骨骼名称是否改变
            if hasattr(item, 'official_bone') and item.official_bone != item.original_official_bone:
                has_changes = True
                
            if item.common_bone != item.original_common_bone:
                has_changes = True
                
            # 检查自定义骨骼列表是否改变
            current_custom_bones = [bone.name for bone in item.temp_custom_bones]
            if hasattr(item, 'original_custom_bones'):
                original_custom_bones = item.original_custom_bones.split(',') if item.original_custom_bones else []
                if set(current_custom_bones) != set(original_custom_bones):
                    has_changes = True
            else:
                if current_custom_bones:  # 如果有新的自定义骨骼被添加
                    has_changes = True
            
            # 更新修改状态
            if has_changes:
                self.has_unsaved_changes = True
        
        # 更新temp_data
        if self.active_tab == 'ALL':
            if hasattr(item, 'official_bone') and item.official_bone and item.common_bone:
                self.temp_data["official_mapping"][item.official_bone] = [item.common_bone]
                # 更新自定义骨骼
                custom_bones = [bone.name for bone in item.temp_custom_bones]
                if custom_bones:
                    # 检查是否是通用骨骼
                    if item.common_bone in self.temp_data["common_mapping"]:
                        # 如果是通用骨骼，更新到common_mapping
                        self.temp_data["common_mapping"][item.common_bone] = custom_bones
                    else:
                        # 如果不是通用骨骼，更新到unique_mapping
                        self.temp_data["unique_mapping"][item.common_bone] = custom_bones
        
        elif self.active_tab == 'UNIQUE':
            if item.common_bone:
                custom_bones = [bone.name for bone in item.temp_custom_bones]
                self.temp_data["unique_mapping"][item.common_bone] = custom_bones
        
        else:  # COMMON
            if item.common_bone:
                custom_bones = [bone.name for bone in item.temp_custom_bones]
                self.temp_data["common_mapping"][item.common_bone] = custom_bones
        
        # 如果是新项，设置original值
        if is_new:
            if hasattr(item, 'official_bone'):
                item.original_official_bone = item.official_bone
            item.original_common_bone = item.common_bone
            item.original_custom_bones = ','.join([bone.name for bone in item.temp_custom_bones])

# 添加一个函数来动态更新自定义骨骼列表
def update_custom_bones_enum(self, context):
    props = context.scene.bone_dict_manager
    items = []
    # 从current_common_mapping中获取当前common_bone对应的自定义骨骼列表
    if hasattr(self, "common_bone") and self.common_bone in current_common_mapping:
        for bone in current_common_mapping[self.common_bone]:
            items.append((bone, bone, ""))
    return items

# 添加骨骼名到所选键操作
class L4D2_OT_AddBoneName(bpy.types.Operator):
    """Automatically remove symbols and convert to lowercase"""
    bl_label = "Add Bone"
    bl_idname = "l4d2.add_bone_name"

    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 检查是否选择了映射项
        if props.mapping_list_index < 0 or props.mapping_list_index >= len(props.mapping_list):
            self.report({'ERROR'}, "请先在映射列表中选择一个项")
            return {'CANCELLED'}
            
        # 获取当前选中的项
        target_item = props.mapping_list[props.mapping_list_index]
        
        # 根据输入模式获取骨骼名称并进行处理
        if props.input_mode == 'SEARCH':
            # 如果在搜索模式下有手动输入的文本，也接受它
            bone_name = props.bone_name_search or props.bone_name_manual
        else:
            bone_name = props.bone_name_manual
            
        # 检查并处理骨骼名称
        if not bone_name:
            self.report({'ERROR'}, "请输入骨骼名称")
            return {'CANCELLED'}
            
        # 简化骨骼名称
        bone_name = simplify_bonename(bone_name)
            
        # 检查是否已存在于临时列表中（使用小写比较）
        if target_item.temp_custom_bones:
            existing_bones = {bone.name.lower() for bone in target_item.temp_custom_bones}
            if bone_name.lower() in existing_bones:
                self.report({'INFO'}, f"{bone_name} 已存在于 {target_item.common_bone}")
                return {'FINISHED'}
        else:
            # 如果还没有临时列表，从current_common_mapping创建
            if target_item.common_bone in current_common_mapping:
                for existing_bone in current_common_mapping[target_item.common_bone]:
                    temp_bone = target_item.temp_custom_bones.add()
                    temp_bone.name = simplify_bonename(existing_bone)  # 确保现有骨骼也被处理
        
        # 添加新骨骼到临时列表
        temp_bone = target_item.temp_custom_bones.add()
        temp_bone.name = bone_name
        
        # 如果是第一个骨骼，设置为当前选中
        if len(target_item.temp_custom_bones) == 1:
            target_item.custom_bone = bone_name
            
        # 标记为已修改
        target_item.original_custom_bone = "has_been_modified"
            
        # 设置未保存更改标记
        props.has_unsaved_changes = True
            
        self.report({'INFO'}, f"{bone_name} 已添加到 {target_item.common_bone}")
        return {'FINISHED'}
    
class L4D2_OT_RemoveBoneName(bpy.types.Operator):
    """Remove selected bone names from the custom bone list"""
    bl_label = "Remove Bone"
    bl_idname = "l4d2.remove_bone_name"
    
    @classmethod
    def poll(cls, context):
        bdm_props = context.scene.bone_dict_manager
        # 只有当选中的键和值都有效时，此操作才可用
        return bdm_props.bone_key_enum and bdm_props.bone_value_enum
    
    def execute(self, context):
        global current_common_mapping
        bdm_props = context.scene.bone_dict_manager
        bone_key = bdm_props.bone_key_enum
        bone_value = bdm_props.bone_value_enum
        
        if bone_key in current_common_mapping and bone_value in current_common_mapping[bone_key]:
            current_common_mapping[bone_key].remove(bone_value)  # 从键对应的列表中移除选定的值
            save_bone_names(current_common_mapping)  # 保存更改到文件
            
            # 更新 bone_value_enum 属性，如果还有其他值则选择第一个值
            if current_common_mapping[bone_key]:
                bdm_props.bone_value_enum = current_common_mapping[bone_key][0]
            else:
                # 如果已经没有值了，则重置 bone_value_enum 属性
                bdm_props.bone_value_enum = ''
                
            self.report({'INFO'}, f"骨骼名 {bone_value} 已从 {bone_key} 中移除")
        else:
            self.report({'ERROR'}, "选中的键或值无效，无法删除")
            
        return {'FINISHED'}
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
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
        load_bone_names()

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
            # 简化骨骼名，并使用简化后的骨骼名在字典 bone_names 中查找对应的键
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
        load_bone_names()

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

class VIEW3D_PT_CustomBoneDictManager(bpy.types.Panel):
    bl_label = "Dict Tools"
    bl_idname = "VIEW3D_PT_custom_bone_dict_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '💝LCT'
    bl_options = {'DEFAULT_CLOSED'}

    @staticmethod
    def has_unsaved_changes(props):
        """检查是否有未保存的更改"""
        if props.active_tab == 'ALL':
            # 检查全部映射列表的更改
            for item in props.mapping_list:
                if (item.official_bone != item.original_official_bone or
                    item.common_bone != item.original_common_bone or
                    item.custom_bone != item.original_custom_bone):
                    return True
        elif props.active_tab == 'COMMON':
            # 检查通用映射列表的更改
            for item in props.mapping_list:
                if (item.common_bone != item.original_common_bone or
                    item.custom_bone != item.original_custom_bone):
                    # 检查临时自定义骨骼列表是否有变化
                    current_custom_bones = {bone.name for bone in item.temp_custom_bones}
                    original_custom_bones = set(current_common_mapping.get(item.original_common_bone, []))
                    if current_custom_bones != original_custom_bones:
                        return True
                    return True
        return False

    def draw(self, context):
        layout = self.layout
        props = context.scene.bone_dict_manager
        obj = context.object

        # 预设管理部分
        box = layout.box()
        box.label(text="预设管理")
        
        row = box.row(align=True)
        row.prop(props, "active_preset", text="当前预设")
        row.operator("l4d2.load_preset", text="", icon='FILE_REFRESH')
        row.operator("l4d2.save_preset", text="", icon='DUPLICATE')
        row.operator("l4d2.delete_preset", text="", icon='TRASH')

        row = box.row()
        row.operator("l4d2.import_preset", icon='IMPORT')
        row.operator("l4d2.export_preset", icon='EXPORT')

        # 标签页UI
        box = layout.box()
        row = box.row()
        row.prop(props, "show_mapping_list", text="Bone Mapping", 
                icon='TRIA_DOWN' if props.show_mapping_list else 'TRIA_RIGHT')
        
        if props.show_mapping_list:
            # 标签页按钮
            row = box.row(align=True)
            for tab in [('ALL', "全部映射"), ('UNIQUE', "独立映射"), ('COMMON', "通用映射")]:
                op = row.operator("l4d2.switch_tab", text=tab[1], depress=(props.active_tab == tab[0]))
                op.tab = tab[0]

            # 根据当前标签页显示不同内容
            if props.active_tab == 'ALL':
                # 显示全部映射列表
                row = box.row()
                row.template_list("BONE_UL_mapping_list", "", props, 
                                "mapping_list", props, "mapping_list_index", rows=12)
                
                # 显示当前选中的映射项和保存状态
                if props.mapping_list_index >= 0 and len(props.mapping_list) > props.mapping_list_index:
                    selected_item = props.mapping_list[props.mapping_list_index]
                    row = box.row()
                    row.label(text=f"当前选中: {selected_item.official_bone}")
                    if self.has_unsaved_changes(props):
                        status_row = row.row()
                        status_row.alignment = 'RIGHT'
                        status_row.alert = True
                        status_row.label(text="有未保存的更改", icon='ERROR')

                # 添加和管理按钮
                row = box.row()
                row.operator("l4d2.add_complete_mapping", text="添加新映射", icon='ADD')
                # 应用更改按钮
                row = box.row(align=True)
                row.operator("l4d2.save_mapping_changes", text="应用更改", icon='FILE_TICK')

            elif props.active_tab == 'UNIQUE':
                # 显示独立映射列表
                row = box.row()
                row.template_list("BONE_UL_unique_mapping_list", "unique_mapping", props, 
                                "mapping_list", props, "mapping_list_index", rows=12)
                
                # 显示当前选中的映射项和保存状态
                if props.mapping_list_index >= 0 and len(props.mapping_list) > props.mapping_list_index:
                    selected_item = props.mapping_list[props.mapping_list_index]
                    row = box.row()
                    row.label(text=f"当前选中: {selected_item.common_bone}")
                    if self.has_unsaved_changes(props):
                        status_row = row.row()
                        status_row.alignment = 'RIGHT'
                        status_row.alert = True
                        status_row.label(text="有未保存的更改", icon='ERROR')
                
                row = box.row()
                row.operator("l4d2.add_unique_mapping", text="添加独立映射", icon='ADD')
                # 应用更改按钮
                row = box.row(align=True)
                row.operator("l4d2.save_unique_mapping_changes", text="应用更改", icon='FILE_TICK')
            
            else:  # COMMON
                # 显示通用映射列表
                row = box.row()
                row.template_list("BONE_UL_common_mapping_list", "common_mapping", props, 
                                "mapping_list", props, "mapping_list_index", rows=12)
                
                # 显示当前选中的映射项和保存状态
                if props.mapping_list_index >= 0 and len(props.mapping_list) > props.mapping_list_index:
                    selected_item = props.mapping_list[props.mapping_list_index]
                    row = box.row()
                    row.label(text=f"当前选中: {selected_item.common_bone}")
                    if self.has_unsaved_changes(props):
                        status_row = row.row()
                        status_row.alignment = 'RIGHT'
                        status_row.alert = True
                        status_row.label(text="有未保存的更改", icon='ERROR')
                
                row = box.row()
                row.operator("l4d2.add_common_mapping", text="添加通用映射", icon='ADD')
                # 应用更改按钮
                row = box.row(align=True)
                row.operator("l4d2.save_common_mapping_changes", text="应用更改", icon='FILE_TICK')

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
    def disconnect_pose_bones(armature, bone_names):
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature.data.edit_bones
        for bone_name in bone_names:
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

class L4D2_OT_SavePreset(bpy.types.Operator):
    """Save current bone mapping as a new preset"""
    bl_idname = "l4d2.save_preset"
    bl_label = "Save Preset"
    
    # 添加预设名称和描述的属性
    new_preset_name: bpy.props.StringProperty(
        name="预设名称",
        description="输入新预设的名称",
        default=""
    )
    
    preset_description: bpy.props.StringProperty(
        name="预设描述",
        description="输入预设的描述信息",
        default=""
    )

    use_unsaved_changes: bpy.props.BoolProperty(
        name="使用未保存的更改",
        description="是否使用当前未保存的更改创建新预设",
        default=False
    )

    def has_unsaved_changes(self, context):
        """检查是否有未保存的修改"""
        props = context.scene.bone_dict_manager
        # 从UI列表创建临时映射
        temp_mapping = {}
        for item in props.mapping_list:
            temp_mapping[item.official_bone] = [item.common_bone]
        
        # 比较与current_bone_mapping
        if len(temp_mapping) != len(current_bone_mapping):
            return True
            
        for key, value in temp_mapping.items():
            if key not in current_bone_mapping or current_bone_mapping[key] != value:
                return True
        return False

    def invoke(self, context, event):
        # 如果有未保存的更改，显示菜单让用户选择数据源
        if self.has_unsaved_changes(context):
            context.window_manager.popup_menu(self.draw_choose_data_source, title="选择数据源")
            return {'INTERFACE'}
        
        # 直接打开属性对话框
        return context.window_manager.invoke_props_dialog(self)

    def draw_choose_data_source(self, menu, context):
        layout = menu.layout
        layout.label(text="请选择要用于创建新预设的数据来源：")
        
        # 使用已保存的数据
        op = layout.operator(self.bl_idname, text="使用已保存的数据")
        op.use_unsaved_changes = False
        
        # 使用未保存的更改
        op = layout.operator(self.bl_idname, text="使用当前显示的数据")
        op.use_unsaved_changes = True
        
        # 取消选项（实际上不需要，因为点击外部就会关闭菜单）

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "new_preset_name")
        layout.prop(self, "preset_description")
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        if not self.new_preset_name:
            self.report({'ERROR'}, "请输入预设名称")
            return {'CANCELLED'}
            
        # 根据选择决定使用哪个数据源
        if self.use_unsaved_changes:
            # 使用UI列表中的当前数据
            new_mapping = {}
            for item in props.mapping_list:
                new_mapping[item.official_bone] = [item.common_bone]
        else:
            # 使用已保存的数据
            new_mapping = current_bone_mapping.copy()
        
        preset_data = {
            "name": self.new_preset_name,
            "description": self.preset_description,
            "mapping": new_mapping,
            "unique_mapping": current_unique_mapping.copy()
        }
        
        file_path = os.path.join(BONE_MAPPING_PRESETS_DIR, f"{self.new_preset_name}.json")
        
        # 使用通用保存函数保存文件
        if save_formatted_json(file_path, preset_data, props.mapping_list if self.use_unsaved_changes else None):
            self.report({'INFO'}, f"预设 {self.new_preset_name} 已保存")
        else:
            self.report({'ERROR'}, "保存预设失败")
            
        return {'FINISHED'}

class L4D2_OT_LoadPreset(bpy.types.Operator):
    """加载选中的骨骼映射预设"""
    bl_idname = "l4d2.load_preset"
    bl_label = "Load Preset"
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        if not props.active_preset:
            self.report({'ERROR'}, "请选择一个预设")
            return {'CANCELLED'}
            
        if load_preset(props.active_preset):
            # 初始化temp_data
            props.temp_data = {
                "official_mapping": {},
                "common_mapping": {},
                "unique_mapping": {}
            }
            
            # 更新临时数据
            props.temp_data["official_mapping"] = current_bone_mapping.copy()
            props.temp_data["unique_mapping"] = current_unique_mapping.copy()
            props.temp_data["common_mapping"] = current_common_mapping.copy()
            
            # 清空现有列表
            props.mapping_list.clear()
            
            # 强制更新所有标签页
            # 保存当前标签页
            current_tab = props.active_tab
            
            # 依次切换到每个标签页并更新
            for tab in ['ALL', 'UNIQUE', 'COMMON']:
                props.active_tab = tab
                props.sync_views()
            
            # 恢复原始标签页
            props.active_tab = current_tab
            props.sync_views()
            
            # 重置修改状态
            props.has_unsaved_changes = False
            
            # 重置所有项的original属性
            for item in props.mapping_list:
                if hasattr(item, 'official_bone'):
                    item.original_official_bone = item.official_bone
                item.original_common_bone = item.common_bone
                item.original_custom_bones = ','.join([bone.name for bone in item.temp_custom_bones])
            
            self.report({'INFO'}, f"预设 {props.active_preset} 已加载")
        else:
            self.report({'ERROR'}, "加载预设失败")
            
        return {'FINISHED'}
            

class L4D2_OT_ImportPreset(bpy.types.Operator):
    """Import a bone mapping preset from file"""
    bl_idname = "l4d2.import_preset"
    bl_label = "Import Preset"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        if not self.filepath:
            return {'CANCELLED'}
            
        try:
            # 读取源文件
            with open(self.filepath, 'r', encoding='utf-8') as f:
                source_data = json.load(f)
                
            # 验证文件格式
            if not all(key in source_data for key in ['name', 'description', 'mapping']):
                self.report({'ERROR'}, "无效的预设文件格式")
                return {'CANCELLED'}
                
            # 使用文件名作为预设名称，但确保不会覆盖现有预设
            base_name = os.path.splitext(os.path.basename(self.filepath))[0]
            preset_name = base_name
            counter = 1
            while os.path.exists(os.path.join(BONE_MAPPING_PRESETS_DIR, f"{preset_name}.json")):
                preset_name = f"{base_name}_{counter}"
                counter += 1
            
            # 创建新的预设数据
            new_preset_data = {
                "name": preset_name,
                "description": source_data.get('description', ''),
                "mapping": source_data['mapping']
            }
            
            # 保存到预设目录
            target_path = os.path.join(BONE_MAPPING_PRESETS_DIR, f"{preset_name}.json")
            if save_formatted_json(target_path, new_preset_data):
                # 更新内存中的预设
                loaded_presets[f"{preset_name}.json"] = new_preset_data
                self.report({'INFO'}, f"预设已导入为 {preset_name}")
            else:
                self.report({'ERROR'}, "导入预设失败")
                    
        except json.JSONDecodeError:
            self.report({'ERROR'}, "无效的JSON文件格式")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"导入预设失败: {e}")
            return {'CANCELLED'}
            
        return {'FINISHED'}

class L4D2_OT_ExportPreset(bpy.types.Operator):
    """Export the current bone mapping preset to file"""
    bl_idname = "l4d2.export_preset"
    bl_label = "Export Preset"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        if not self.filepath:
            return {'CANCELLED'}
            
        try:
            props = context.scene.bone_dict_manager
            # 根据选择决定导出当前映射还是选中的预设
            mapping_to_export = current_bone_mapping if props.save_current_mapping else loaded_presets.get(props.active_preset, {}).get('mapping', current_bone_mapping)
            
            preset_data = {
                "name": os.path.splitext(os.path.basename(self.filepath))[0],
                "description": props.preset_description if props.save_current_mapping else 
                             loaded_presets.get(props.active_preset, {}).get('description', ''),
                "mapping": mapping_to_export
            }
            
            if save_formatted_json(self.filepath, preset_data):
                self.report({'INFO'}, f"预设已导出到 {self.filepath}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "导出预设失败")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"导出预设失败: {e}")
            return {'CANCELLED'}

class BONE_UL_mapping_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            # 检查修改状态
            official_changed = item.official_bone != item.original_official_bone
            common_changed = item.common_bone != item.original_common_bone
            
            # 检查自定义骨骼是否有修改
            custom_bones_changed = False
            if item.original_custom_bone == "has_been_modified":  # 已经被标记为修改
                custom_bones_changed = True
            elif item.temp_custom_bones:  # 有临时列表
                if item.original_common_bone in current_common_mapping:  # 原始通用骨骼存在
                    # 比较临时列表和原始列表
                    current_bones = {bone.name.lower() for bone in item.temp_custom_bones}
                    original_bones = {bone.lower() for bone in current_common_mapping[item.original_common_bone]}
                    custom_bones_changed = current_bones != original_bones
                else:  # 新添加的通用骨骼
                    custom_bones_changed = True
            elif item.original_custom_bone:  # 有原始值但临时列表为空
                custom_bones_changed = True
            
            # 主布局分为三部分：官方骨骼、通用骨骼、自定义骨骼和按钮
            split = row.split(factor=0.4)  # 官方骨骼占40%
            
            # 左侧：官方骨骼名称和切换按钮
            left_row = split.row(align=True)
            if official_changed:
                left_row.alert = True
            
            # 创建一个子行用于对齐官方骨骼名称和切换按钮
            bone_row = left_row.row(align=True)
            
            # 根据输入模式显示不同的输入控件
            if item.official_bone_input_mode == 'SEARCH':
                if hasattr(context.scene, "Valve_Armature") and context.scene.Valve_Armature:
                    bone_row.prop_search(item, "official_bone", context.scene.Valve_Armature.data, "bones", text="", icon='BONE_DATA')
                else:
                    bone_row.prop(item, "official_bone", text="", icon='BONE_DATA')
            else:
                bone_row.prop(item, "official_bone", text="", icon='BONE_DATA')
            
            # 添加切换按钮
            op = bone_row.operator("l4d2.toggle_official_bone_input", text="", 
                                 icon='VIEWZOOM' if item.official_bone_input_mode == 'SEARCH' else 'GREASEPENCIL')
            op.index = index
            
            # 右侧部分（通用骨骼、自定义骨骼和按钮）
            right_side = split.split(factor=0.4)  # 通用骨骼占右侧40%
            
            # 中间：通用骨骼名称
            middle_row = right_side.row(align=True)
            # 箭头和通用骨骼名称
            arrow_row = middle_row.row(align=True)
            arrow_row.scale_x = 0.3  # 缩小箭头占用的空间
            if official_changed:  # 只有官方骨骼改变时，第一个箭头才标红
                arrow_row.alert = True
            arrow_row.label(text="→")
            name_row = middle_row.row()
            if common_changed:  # 只有通用骨骼改变时才标红
                name_row.alert = True
            name_row.prop(item, "common_bone", text="", emboss=False)
            
            # 右侧：自定义骨骼和按钮
            right_row = right_side.row(align=True)
            # 第二个箭头
            arrow_row = right_row.row(align=True)
            arrow_row.scale_x = 0.3
            if common_changed:  # 只有通用骨骼改变时，第二个箭头才标红
                arrow_row.alert = True
            arrow_row.label(text="→")
            
            # 自定义骨骼选择按钮和添加/删除按钮组
            custom_group = right_row.row(align=True)
            if custom_bones_changed:  # 只关注自定义骨骼的变化
                custom_group.alert = True
            text = item.custom_bone if item.custom_bone else "选择骨骼"
            if custom_bones_changed:  # 只关注自定义骨骼的变化
                text = "* " + text
            op = custom_group.operator("l4d2.select_custom_bone", text=text)
            op.index = index
            
            # 添加[+]和[-]按钮
            custom_group.operator("l4d2.add_bone_popup", text="", icon='ADD').index = index
            custom_group.operator("l4d2.remove_custom_bone_single", text="", icon='REMOVE').index = index
            
            # 分隔的删除映射按钮
            row.operator("l4d2.remove_mapping", text="", icon='X').index = index

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # 根据搜索字符串过滤
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "official_bone")
        else:
            flt_flags = [self.bitflag_filter_item] * len(items)
            
        return flt_flags, []

class L4D2_OT_RemoveCustomBoneSingle(bpy.types.Operator):
    """从当前显示的自定义骨骼中移除选中的骨骼"""
    bl_idname = "l4d2.remove_custom_bone_single"
    bl_label = "Remove Custom Bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(
        name="Index",
        description="映射列表中的索引",
        options={'HIDDEN'}
    )
    
    def invoke(self, context, event):
        props = context.scene.bone_dict_manager
        item = props.mapping_list[self.index]
        
        # 如果临时列表为空，直接报错
        if len(item.temp_custom_bones) == 0:
            self.report({'ERROR'}, "没有可删除的自定义骨骼")
            return {'CANCELLED'}
            
        return context.window_manager.invoke_confirm(
            self, 
            event,
            message=f"确定要删除 {item.common_bone} 的自定义骨骼 {item.custom_bone} 吗？"
        )
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        item = props.mapping_list[self.index]
        
        # 从临时列表中移除骨骼
        for i, temp_bone in enumerate(item.temp_custom_bones):
            if temp_bone.name == item.custom_bone:
                item.temp_custom_bones.remove(i)
                # 如果临时列表为空，直接清空选择并返回
                if len(item.temp_custom_bones) == 0:
                    item.custom_bone = ""
                    item.original_custom_bone = "has_been_modified"
                    props.has_unsaved_changes = True
                    self.report({'INFO'}, f"已从列表中移除最后一个自定义骨骼 {temp_bone.name}")
                    return {'FINISHED'}
                
                # 如果还有其他骨骼，选择第一个
                item.custom_bone = item.temp_custom_bones[0].name
                item.original_custom_bone = "has_been_modified"
                props.has_unsaved_changes = True
                
                # 强制更新UI
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                
                self.report({'INFO'}, f"已从列表中移除自定义骨骼 {temp_bone.name}")
                break
        
        return {'FINISHED'}

class L4D2_OT_RemoveMapping(bpy.types.Operator):
    """删除选中的映射"""
    bl_idname = "l4d2.remove_mapping"
    bl_label = "Remove Mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(
        options={'HIDDEN'}  # 隐藏index属性，这样就不会弹出小窗口
    )
    
    def invoke(self, context, event):
        props = context.scene.bone_dict_manager
        item = props.mapping_list[self.index]
        
        # 根据当前标签页显示不同的确认消息
        if props.active_tab == 'ALL':
            message = f"确定要从列表中移除 {item.official_bone} → {item.common_bone} 的映射关系吗？"
        elif props.active_tab == 'COMMON':
            message = f"确定要从列表中移除通用骨骼 {item.common_bone} 吗？"
        else:  # UNIQUE
            message = f"确定要从列表中移除独立映射 {item.common_bone} 吗？"
            
        return context.window_manager.invoke_confirm(
            self, 
            event,
            message=message
        )
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 记住要删除的项
        item_to_remove = props.mapping_list[self.index]
        common_bone = item_to_remove.common_bone
        
        # 根据当前标签页执行不同的删除操作
        if props.active_tab == 'ALL':
            # 从official_mapping中删除
            if hasattr(item_to_remove, 'official_bone') and item_to_remove.official_bone in props.temp_data["official_mapping"]:
                del props.temp_data["official_mapping"][item_to_remove.official_bone]
            
            # 如果有自定义骨骼，也需要从相应的映射中删除
            if item_to_remove.temp_custom_bones:
                if common_bone in props.temp_data["unique_mapping"]:
                    del props.temp_data["unique_mapping"][common_bone]
                elif common_bone in props.temp_data["common_mapping"]:
                    del props.temp_data["common_mapping"][common_bone]
                    
        elif props.active_tab == 'UNIQUE':
            # 从unique_mapping中删除
            if common_bone in props.temp_data["unique_mapping"]:
                del props.temp_data["unique_mapping"][common_bone]
                
        else:  # COMMON
            # 从common_mapping中删除
            if common_bone in props.temp_data["common_mapping"]:
                del props.temp_data["common_mapping"][common_bone]
        
        # 更新UI列表
        props.sync_views()
        
        # 设置未保存更改标记
        props.has_unsaved_changes = True
        
        # 更新索引
        if len(props.mapping_list) > 0:
            if self.index >= len(props.mapping_list):
                props.mapping_list_index = len(props.mapping_list) - 1
            else:
                props.mapping_list_index = self.index
        else:
            props.mapping_list_index = -1
        
        # 根据当前标签页显示不同的成功消息
        if props.active_tab == 'ALL':
            self.report({'INFO'}, f"已从列表中移除映射 {common_bone}，请记得应用更改")
        elif props.active_tab == 'COMMON':
            self.report({'INFO'}, f"已从列表中移除通用骨骼 {common_bone}，请记得应用更改")
        else:  # UNIQUE
            self.report({'INFO'}, f"已从列表中移除独立映射 {common_bone}，请记得应用更改")
        
        return {'FINISHED'}

class L4D2_OT_AddCompleteMapping(bpy.types.Operator):
    """添加一条空的完整映射到列表中"""
    bl_idname = "l4d2.add_complete_mapping"
    bl_label = "Add Complete Mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        global current_unique_mapping
        props = context.scene.bone_dict_manager
        
        # 添加一个空的映射项
        item = props.mapping_list.add()
        item.official_bone = ""
        item.common_bone = ""
        
        # 将original值设为空字符串，这样会使整行都标红
        item.original_official_bone = ""
        item.original_common_bone = ""
        item.original_custom_bone = ""
        
        # 设置未保存更改标记
        props.has_unsaved_changes = True
        
        # 更新索引到新添加的项
        props.mapping_list_index = len(props.mapping_list) - 1
        
        # 调用update_temp_data更新临时数据
        props.update_temp_data(item, is_new=True)
        
        return {'FINISHED'}

class L4D2_OT_SaveMappingChanges(bpy.types.Operator):
    bl_idname = "l4d2.save_mapping_changes"
    bl_label = "Save Changes"
    
    def execute(self, context):
        global current_bone_mapping, current_unique_mapping, current_common_mapping  # 只在开头声明一次
        
        # 检查current_common_mapping是否正确初始化
        if not current_common_mapping:
            print("警告: current_common_mapping 为空，尝试重新加载")
            load_bone_names()
            if not current_common_mapping:
                self.report({'ERROR'}, "无法加载骨骼字典，请检查文件是否存在")
                return {'CANCELLED'}
        
        props = context.scene.bone_dict_manager
        
        # 检查空映射
        empty_mappings = []
        for item in props.mapping_list:
            if not item.common_bone.strip():
                empty_mappings.append(item.common_bone)
            elif props.active_tab == 'ALL' and not item.official_bone.strip():
                empty_mappings.append(f"{item.official_bone} → {item.common_bone}")
        
        if empty_mappings:
            self.report({'ERROR'}, "存在空的映射条目")
            return {'CANCELLED'}
        
        # 从UI列表重建映射前，先备份现有的通用映射
        backup_global_bones = current_common_mapping.copy()
        
        # 创建新的映射字典
        new_bone_mapping = {}      # 官方到通用的映射
        new_unique_mapping = {}    # 独立的通用到自定义的映射
        new_global_bones = {}      # 通用到自定义的映射(current_common_mapping)
        
        # 从UI列表重建映射
        for item in props.mapping_list:
            # 1. 处理官方到通用的映射
            if hasattr(item, 'official_bone') and item.official_bone:
                new_bone_mapping[item.official_bone] = [item.common_bone]
            
            # 2. 收集自定义骨骼
            custom_bones = [bone.name for bone in item.temp_custom_bones]
            if not custom_bones:
                continue
                
            # 3. 判断是通用映射还是独立映射
            # 如果这个通用骨骼在原始的current_common_mapping中，就认为它是通用映射
            if item.common_bone in backup_global_bones:
                new_global_bones[item.common_bone] = custom_bones
            else:
                # 否则认为是独立映射
                new_unique_mapping[item.common_bone] = custom_bones
        
        # 更新全局变量（不需要再次声明global）
        current_bone_mapping = new_bone_mapping
        current_unique_mapping = new_unique_mapping
        current_common_mapping = new_global_bones
        
        # 保存通用映射到文件
        save_bone_names(current_common_mapping)
        
        # 如果有活动预设，保存预设
        if props.active_preset:
            preset_path = os.path.join(BONE_MAPPING_PRESETS_DIR, props.active_preset)
            try:
                # 读取现有预设以保留描述信息
                with open(preset_path, 'r', encoding='utf-8') as f:
                    existing_preset = json.load(f)
                    description = existing_preset.get('description', '')
            except:
                description = ""
                
            preset_data = {
                "name": os.path.splitext(props.active_preset)[0],
                "description": description,
                "mapping": current_bone_mapping,
                "unique_mapping": current_unique_mapping
            }
            
            if save_formatted_json(preset_path, preset_data):
                # 重置所有项的原始值
                for item in props.mapping_list:
                    if hasattr(item, 'official_bone'):
                        item.original_official_bone = item.official_bone
                    item.original_common_bone = item.common_bone
                    item.original_custom_bones = ','.join([bone.name for bone in item.temp_custom_bones])
                
                # 清除未保存更改标记
                props.has_unsaved_changes = False
                
                self.report({'INFO'}, "已保存")
            else:
                self.report({'ERROR'}, "保存预设失败")
        else:
            # 即使没有活动预设，也重置原始值
            for item in props.mapping_list:
                if hasattr(item, 'official_bone'):
                    item.original_official_bone = item.official_bone
                item.original_common_bone = item.common_bone
                item.original_custom_bones = ','.join([bone.name for bone in item.temp_custom_bones])
            
            # 清除未保存更改标记
            props.has_unsaved_changes = False
            
            self.report({'INFO'}, "已保存")
        
        return {'FINISHED'}

class L4D2_OT_DeletePreset(bpy.types.Operator):
    """删除选中的骨骼映射预设"""
    bl_idname = "l4d2.delete_preset"
    bl_label = "Delete Preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        if not props.active_preset:
            self.report({'ERROR'}, "未选择预设")
            return {'CANCELLED'}
            
        # 从预设目录删除文件
        preset_path = os.path.join(BONE_MAPPING_PRESETS_DIR, props.active_preset)
        try:
            os.remove(preset_path)
            
            # 更新active_preset为其他可用预设
            available_presets = get_preset_files()
            if available_presets:
                props.active_preset = available_presets[0]
            else:
                props.active_preset = ''
                
            self.report({'INFO'}, "已删除")
        except Exception as e:
            self.report({'ERROR'}, "删除失败")
            return {'CANCELLED'}
            
        return {'FINISHED'}
        
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

class L4D2_OT_SelectCustomBone(bpy.types.Operator):
    """选择自定义骨骼"""
    bl_idname = "l4d2.select_custom_bone"
    bl_label = "Select Custom Bone"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        props = context.scene.bone_dict_manager
        item = props.mapping_list[self.index]
        
        # 如果临时列表为空，且这是第一次打开菜单（没有修改过），则从current_common_mapping创建
        if not item.temp_custom_bones and item.original_custom_bone == item.custom_bone:
            if item.common_bone in current_common_mapping:
                for bone_name in current_common_mapping[item.common_bone]:
                    temp_bone = item.temp_custom_bones.add()
                    temp_bone.name = bone_name
        
        # 创建弹出菜单
        context.window_manager.popup_menu(self.draw_menu, title="选择自定义骨骼")
        return {'INTERFACE'}
    
    def draw_menu(self, menu, context):
        layout = menu.layout
        props = context.scene.bone_dict_manager
        item = props.mapping_list[self.index]
        
        # 直接显示临时列表中的骨骼，不再自动从current_common_mapping创建
        if item.temp_custom_bones:
            for bone in item.temp_custom_bones:
                op = layout.operator("l4d2.set_custom_bone", text=bone.name)
                op.index = self.index
                op.bone_name = bone.name
        else:
            layout.label(text="没有可选的自定义骨骼")

class L4D2_OT_SetCustomBone(bpy.types.Operator):
    """设置选中的自定义骨骼"""
    bl_idname = "l4d2.set_custom_bone"
    bl_label = "Set Custom Bone"
    
    index: bpy.props.IntProperty()
    bone_name: bpy.props.StringProperty()
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        item = props.mapping_list[self.index]
        item.custom_bone = self.bone_name
        return {'FINISHED'}

class L4D2_OT_ToggleOfficialBoneInput(bpy.types.Operator):
    """切换官方骨骼的输入模式"""
    bl_idname = "l4d2.toggle_official_bone_input"
    bl_label = "Toggle Official Bone Input Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: bpy.props.IntProperty(
        name="Index",
        description="映射列表中的索引",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        item = props.mapping_list[self.index]
        
        # 切换输入模式
        if item.official_bone_input_mode == 'SEARCH':
            item.official_bone_input_mode = 'MANUAL'
        else:
            item.official_bone_input_mode = 'SEARCH'
            
        return {'FINISHED'}

class L4D2_OT_ToggleNewOfficialBoneInput(bpy.types.Operator):
    """切换新的官方骨骼输入模式"""
    bl_idname = "l4d2.toggle_new_official_bone_input"
    bl_label = "Toggle New Official Bone Input Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 切换输入模式
        if props.new_official_bone_input_mode == 'SEARCH':
            props.new_official_bone_input_mode = 'MANUAL'
        else:
            props.new_official_bone_input_mode = 'SEARCH'
            
        return {'FINISHED'}

class L4D2_OT_ToggleInputMode(bpy.types.Operator):
    """切换输入模式"""
    bl_idname = "l4d2.toggle_input_mode"
    bl_label = "Toggle Input Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 切换输入模式
        if props.input_mode == 'SEARCH':
            props.input_mode = 'MANUAL'
        else:
            props.input_mode = 'SEARCH'
            
        return {'FINISHED'}

class BONE_UL_common_mapping_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            # 检查修改状态
            common_changed = item.common_bone != item.original_common_bone
            custom_bones_changed = False
            if item.original_custom_bone == "has_been_modified":  # 已经被标记为修改
                custom_bones_changed = True
            elif item.temp_custom_bones:  # 有临时列表
                if item.original_common_bone in current_common_mapping:  # 原始通用骨骼存在
                    # 比较临时列表和原始列表
                    current_bones = {bone.name.lower() for bone in item.temp_custom_bones}
                    original_bones = {bone.lower() for bone in current_common_mapping[item.original_common_bone]}
                    custom_bones_changed = current_bones != original_bones
                else:  # 新添加的通用骨骼
                    custom_bones_changed = True
            elif item.original_custom_bone:  # 有原始值但临时列表为空
                custom_bones_changed = True
            
            # 主布局分为两部分：通用骨骼和自定义骨骼
            split = row.split(factor=0.4)  # 通用骨骼占40%
            
            # 左侧：通用骨骼名称
            left_row = split.row(align=True)
            name_row = left_row.row()
            if common_changed:  # 只有通用骨骼改变时才标红
                name_row.alert = True
            name_row.prop(item, "common_bone", text="", emboss=False)
            
            # 右侧：自定义骨骼和按钮
            right_row = split.row(align=True)
            # 箭头
            arrow_row = right_row.row(align=True)
            arrow_row.scale_x = 0.3
            if common_changed:  # 只有通用骨骼改变时，箭头才标红
                arrow_row.alert = True
            arrow_row.label(text="→")
            
            # 自定义骨骼选择按钮和添加/删除按钮组
            custom_group = right_row.row(align=True)
            if custom_bones_changed:  # 只关注自定义骨骼的变化
                custom_group.alert = True
            text = item.custom_bone if item.custom_bone else "选择骨骼"
            if custom_bones_changed:  # 只关注自定义骨骼的变化
                text = "* " + text
            op = custom_group.operator("l4d2.select_custom_bone", text=text)
            op.index = index
            
            # 添加[+]和[-]按钮
            custom_group.operator("l4d2.add_bone_popup", text="", icon='ADD').index = index
            custom_group.operator("l4d2.remove_custom_bone_single", text="", icon='REMOVE').index = index
            
            # 分隔的删除映射按钮
            row.operator("l4d2.remove_mapping", text="", icon='X').index = index
    
    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # 根据搜索字符串过滤
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "common_bone")
        else:
            flt_flags = [self.bitflag_filter_item] * len(items)
            
        return flt_flags, []

class L4D2_OT_AddCommonMapping(bpy.types.Operator):
    """添加新的通用骨骼映射"""
    bl_idname = "l4d2.add_common_mapping"
    bl_label = "Add Common Mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 添加一个空的映射项
        item = props.mapping_list.add()
        item.common_bone = ""
        
        # 将original值设为空字符串，这样会使整行都标红
        item.original_common_bone = ""
        item.original_custom_bone = ""
        
        # 设置未保存更改标记
        props.has_unsaved_changes = True
        
        # 更新索引到新添加的项
        props.mapping_list_index = len(props.mapping_list) - 1
        
        self.report({'INFO'}, "已添加新的空映射，请直接在列表中编辑")
        return {'FINISHED'}

class L4D2_OT_SaveCommonMappingChanges(bpy.types.Operator):
    """保存通用骨骼映射的更改"""
    bl_idname = "l4d2.save_common_mapping_changes"
    bl_label = "Save Common Mapping Changes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 检查空映射
        empty_mappings = []
        for item in props.mapping_list:
            if not item.common_bone.strip():
                empty_mappings.append(item.common_bone)
        
        if empty_mappings:
            self.report({'ERROR'}, f"发现空的映射条目，请删除后再保存:\n{', '.join(empty_mappings)}")
            return {'CANCELLED'}
        
        # 创建新的current_common_mapping字典，而不是直接修改现有的
        new_current_common_mapping = {}
        
        # 从UI列表收集所有有效的映射
        for item in props.mapping_list:
            if item.common_bone:
                # 收集所有自定义骨骼
                custom_bones = []
                if item.temp_custom_bones:
                    custom_bones = [bone.name for bone in item.temp_custom_bones]
                
                # 只有当有自定义骨骼时才添加到映射中
                if custom_bones:
                    new_current_common_mapping[item.common_bone] = custom_bones
        
        # 完全替换current_common_mapping的内容
        current_common_mapping.clear()
        current_common_mapping.update(new_current_common_mapping)
        
        # 保存到文件
        save_bone_names(current_common_mapping)
        
        # 重置所有项的原始值
        for item in props.mapping_list:
            item.original_common_bone = item.common_bone
            if item.temp_custom_bones:
                item.original_custom_bone = item.custom_bone
            else:
                item.original_custom_bone = ""
        
        # 清除未保存更改标记
        props.has_unsaved_changes = False
        
        self.report({'INFO'}, "已保存所有更改")
        return {'FINISHED'}

class L4D2_OT_SwitchTab(bpy.types.Operator):
    bl_idname = "l4d2.switch_tab"
    bl_label = "切换标签页"
    bl_description = "切换到不同的标签页"
    bl_options = {'INTERNAL'}

    tab: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 确保temp_data中包含所有必要的数据
        if not props.temp_data.get("common_mapping"):
            props.temp_data["common_mapping"] = current_common_mapping.copy()
        
        # 切换标签页
        props.active_tab = self.tab
        
        # 同步视图
        props.sync_views()
        
        return {'FINISHED'}

class L4D2_OT_ResetMappingList(bpy.types.Operator):
    """重置当前标签页的映射列表到初始状态"""
    bl_idname = "l4d2.reset_mapping_list"
    bl_label = "重置列表"
    bl_description = "将当前标签页的映射列表重置到初始状态"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 创建新的列表，只包含当前标签页的项
        new_list = []
        for item in props.mapping_list:
            if props.active_tab == 'ALL':
                # 只重置全部映射列表的项
                if hasattr(item, 'official_bone'):
                    new_list.append((
                        item.original_official_bone,
                        item.original_common_bone,
                        item.original_custom_bone,
                        [(bone.name, bone.name) for bone in item.temp_custom_bones],
                        item.original_official_bone,
                        item.original_common_bone,
                        item.original_custom_bone
                    ))
            elif props.active_tab == 'COMMON':
                # 只重置通用映射列表的项
                if not hasattr(item, 'official_bone'):
                    new_list.append((
                        None,  # 通用映射没有official_bone
                        item.original_common_bone,
                        item.original_custom_bone,
                        [(bone.name, bone.name) for bone in item.temp_custom_bones],
                        None,
                        item.original_common_bone,
                        item.original_custom_bone
                    ))
        
        # 清空当前列表
        props.mapping_list.clear()
        
        # 重新填充列表
        for official, common, custom, temp_bones, orig_official, orig_common, orig_custom in new_list:
            item = props.mapping_list.add()
            if official is not None:
                item.official_bone = official
            item.common_bone = common
            item.custom_bone = custom
            
            # 保持原始值不变
            if orig_official is not None:
                item.original_official_bone = orig_official
            item.original_common_bone = orig_common
            item.original_custom_bone = orig_custom
            
            # 恢复临时自定义骨骼列表
            for bone_name, _ in temp_bones:
                temp_bone = item.temp_custom_bones.add()
                temp_bone.name = bone_name
        
        # 清除未保存更改标记
        props.has_unsaved_changes = False
        
        # 更新索引
        if len(props.mapping_list) > 0:
            if props.mapping_list_index >= len(props.mapping_list):
                props.mapping_list_index = len(props.mapping_list) - 1
        else:
            props.mapping_list_index = -1
        
        self.report({'INFO'}, "已重置当前标签页的列表")
        return {'FINISHED'}

class BONE_UL_unique_mapping_list(bpy.types.UIList):
    """独立映射列表"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            # 检查修改状态
            common_changed = item.common_bone != item.original_common_bone
            custom_bones_changed = False
            if item.original_custom_bone == "has_been_modified":  # 已经被标记为修改
                custom_bones_changed = True
            elif item.temp_custom_bones:  # 有临时列表
                if item.original_common_bone in current_unique_mapping:  # 原始通用骨骼存在
                    # 比较临时列表和原始列表
                    current_bones = {bone.name.lower() for bone in item.temp_custom_bones}
                    original_bones = {bone.lower() for bone in current_unique_mapping[item.original_common_bone]}
                    custom_bones_changed = current_bones != original_bones
                else:  # 新添加的通用骨骼
                    custom_bones_changed = True
            elif item.original_custom_bone:  # 有原始值但临时列表为空
                custom_bones_changed = True
            
            # 通用骨骼名称
            name_row = row.row()
            if common_changed:
                name_row.alert = True
            name_row.prop(item, "common_bone", text="", emboss=False)
            
            # 箭头
            arrow_row = row.row(align=True)
            arrow_row.scale_x = 0.3
            if common_changed:
                arrow_row.alert = True
            arrow_row.label(text="→")
            
            # 自定义骨骼选择按钮和添加/删除按钮组
            custom_group = row.row(align=True)
            if custom_bones_changed:
                custom_group.alert = True
            text = item.custom_bone if item.custom_bone else "选择骨骼"
            if custom_bones_changed:  # 只关注自定义骨骼的变化
                text = "* " + text
            op = custom_group.operator("l4d2.select_custom_bone", text=text)
            op.index = index
            
            # 添加[+]和[-]按钮
            custom_group.operator("l4d2.add_bone_popup", text="", icon='ADD').index = index
            custom_group.operator("l4d2.remove_custom_bone_single", text="", icon='REMOVE').index = index
            
            # 分隔的删除映射按钮
            row.operator("l4d2.remove_mapping", text="", icon='X').index = index

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # 根据搜索字符串过滤
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, "common_bone")
        else:
            flt_flags = [self.bitflag_filter_item] * len(items)
            
        return flt_flags, []

class L4D2_OT_AddUniqueMapping(bpy.types.Operator):
    """添加新的独立映射"""
    bl_idname = "l4d2.add_unique_mapping"
    bl_label = "Add Unique Mapping"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 添加一个空的映射项
        item = props.mapping_list.add()
        item.common_bone = ""
        
        # 将original值设为空字符串，这样会使整行都标红
        item.original_common_bone = ""
        item.original_custom_bone = ""
        
        # 设置未保存更改标记
        props.has_unsaved_changes = True
        
        # 更新索引到新添加的项
        props.mapping_list_index = len(props.mapping_list) - 1
        
        self.report({'INFO'}, "已添加新的空映射，请直接在列表中编辑")
        return {'FINISHED'}

class L4D2_OT_SaveUniqueMappingChanges(bpy.types.Operator):
    """保存独立映射的更改"""
    bl_idname = "l4d2.save_unique_mapping_changes"
    bl_label = "Save Unique Mapping Changes"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        global current_unique_mapping
        props = context.scene.bone_dict_manager
        
        # 检查空映射
        empty_mappings = []
        for item in props.mapping_list:
            if not item.common_bone.strip():
                empty_mappings.append(item.common_bone)
        
        if empty_mappings:
            self.report({'ERROR'}, f"发现空的映射条目，请删除后再保存:\n{', '.join(empty_mappings)}")
            return {'CANCELLED'}
        
        # 创建新的映射字典
        new_mapping = {}
        
        # 从UI列表收集数据
        for item in props.mapping_list:
            if item.common_bone:
                # 收集所有自定义骨骼
                custom_bones = []
                if item.temp_custom_bones:
                    custom_bones = [bone.name for bone in item.temp_custom_bones]
                
                # 只有当有自定义骨骼时才添加到映射中
                if custom_bones:
                    new_mapping[item.common_bone] = custom_bones
        
        # 更新当前独立映射
        current_unique_mapping = new_mapping
        
        # 如果有活动的预设，更新预设文件
        if props.active_preset:
            preset_path = os.path.join(BONE_MAPPING_PRESETS_DIR, props.active_preset)
            try:
                with open(preset_path, 'r', encoding='utf-8') as f:
                    preset_data = json.load(f)
                
                # 添加或更新独立映射数据
                preset_data['unique_mapping'] = new_mapping
                
                # 保存更新后的预设
                if save_formatted_json(preset_path, preset_data):
                    # 重置所有项的原始值
                    for item in props.mapping_list:
                        item.original_common_bone = item.common_bone
                        if item.temp_custom_bones:
                            item.original_custom_bone = item.custom_bone
                        else:
                            item.original_custom_bone = ""
                    
                    # 清除未保存更改标记
                    props.has_unsaved_changes = False
                    
                    self.report({'INFO'}, "已保存所有更改")
                else:
                    self.report({'ERROR'}, "保存预设失败")
            except Exception as e:
                self.report({'ERROR'}, f"保存预设时发生错误: {str(e)}")
                return {'CANCELLED'}
        
        return {'FINISHED'}

class L4D2_OT_AddBonePopup(bpy.types.Operator):
    """添加新的自定义骨骼"""
    bl_idname = "l4d2.add_bone_popup"
    bl_label = "添加自定义骨骼"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}  # 添加INTERNAL选项以隐藏左下角提示
    
    index: bpy.props.IntProperty(
        name="Index",
        description="映射列表中的索引",
        options={'HIDDEN'}
    )
    
    input_mode: bpy.props.EnumProperty(
        name="输入模式",
        items=[
            ('SEARCH', "搜索模式", "从现有骨骼中搜索"),
            ('MANUAL', "手动输入", "手动输入骨骼名称")
        ],
        default='SEARCH',
        options={'SKIP_SAVE'}  # 防止模式被保存，每次打开都使用默认值
    )
    
    bone_name_search: bpy.props.StringProperty(
        name="骨骼名称",
        description="搜索骨骼名称"
    )
    
    bone_name_manual: bpy.props.StringProperty(
        name="骨骼名称",
        description="手动输入骨骼名称"
    )
    
    def invoke(self, context, event):
        # 验证索引是否有效
        props = context.scene.bone_dict_manager
        if self.index < 0 or self.index >= len(props.mapping_list):
            self.report({'ERROR'}, "无效的映射索引")
            return {'CANCELLED'}
            
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        # 添加模式切换按钮
        row = layout.row()
        row.prop(self, "input_mode", expand=True)
        
        # 根据模式显示不同的输入控件
        if self.input_mode == 'SEARCH':
            if hasattr(context.scene, "Custom_Armature") and context.scene.Custom_Armature:
                layout.prop_search(self, "bone_name_search", context.scene.Custom_Armature.data, "bones", text="骨骼名称")
            else:
                layout.prop(self, "bone_name_manual", text="骨骼名称")
        else:
            layout.prop(self, "bone_name_manual", text="骨骼名称")
    
    def execute(self, context):
        props = context.scene.bone_dict_manager
        
        # 验证索引是否有效
        if self.index < 0 or self.index >= len(props.mapping_list):
            self.report({'ERROR'}, "无效的映射索引")
            return {'CANCELLED'}
            
        item = props.mapping_list[self.index]
        
        # 根据输入模式获取骨骼名称
        if self.input_mode == 'SEARCH':
            bone_name = self.bone_name_search or self.bone_name_manual
        else:
            bone_name = self.bone_name_manual
            
        # 检查并处理骨骼名称
        if not bone_name:
            self.report({'ERROR'}, "请输入骨骼名称")
            return {'CANCELLED'}
            
        # 简化骨骼名称
        bone_name = simplify_bonename(bone_name)
            
        # 检查是否已存在于临时列表中（使用小写比较）
        if item.temp_custom_bones:
            existing_bones = {bone.name.lower() for bone in item.temp_custom_bones}
            if bone_name.lower() in existing_bones:
                self.report({'INFO'}, f"{bone_name} 已存在于 {item.common_bone}")
                return {'FINISHED'}
        
        # 添加新骨骼到临时列表
        temp_bone = item.temp_custom_bones.add()
        temp_bone.name = bone_name
        
        # 如果是第一个骨骼，设置为当前选中
        if len(item.temp_custom_bones) == 1:
            item.custom_bone = bone_name
            
        # 标记为已修改
        item.original_custom_bone = "has_been_modified"
            
        # 设置未保存更改标记
        props.has_unsaved_changes = True
            
        self.report({'INFO'}, f"{bone_name} 已添加到 {item.common_bone}")
        return {'FINISHED'}

def apply_changes(self):
    """应用所有更改到全局变量和文件"""
    # 更新全局变量
    global current_bone_mapping, current_unique_mapping, current_common_mapping
    
    current_bone_mapping = self.temp_data["official_mapping"].copy()
    current_unique_mapping = self.temp_data["unique_mapping"].copy()
    current_common_mapping.clear()
    current_common_mapping.update(self.temp_data["common_mapping"])
    
    # 保存到文件
    save_bone_names(current_common_mapping)
    
    # 如果有活动预设，更新预设
    if self.active_preset:
        preset_data = {
            "name": self.active_preset,
            "description": self.preset_description,
            "mapping": self.temp_data["official_mapping"],
            "unique_mapping": self.temp_data["unique_mapping"]
        }
        save_formatted_json(os.path.join(BONE_MAPPING_PRESETS_DIR, self.active_preset), preset_data)
    
    # 清除未保存标记
    self.has_unsaved_changes = False

classes = [
    BoneMappingItem,
    BONE_UL_mapping_list,
    BONE_UL_common_mapping_list,
    BONE_UL_unique_mapping_list,
    BoneDictManagerProperties,
    L4D2_OT_GraftingOperator,
    L4D2_OT_RiggingOperator,
    L4D2_OT_RenameBonesOperator,
    L4D2_PT_BoneModifyPanel,
    VIEW3D_PT_CustomBoneDictManager,
    L4D2_OT_UnbindAndKeepShape,
    L4D2_OT_SavePreset,
    L4D2_OT_LoadPreset,
    L4D2_OT_ImportPreset,
    L4D2_OT_ExportPreset,
    L4D2_OT_RemoveCustomBoneSingle,
    L4D2_OT_RemoveMapping,
    L4D2_OT_SaveMappingChanges,
    L4D2_OT_AddBoneName,
    L4D2_OT_DeletePreset,
    L4D2_OT_SelectCustomBone,
    L4D2_OT_SetCustomBone,
    L4D2_OT_AddCompleteMapping,
    L4D2_OT_ToggleOfficialBoneInput,
    L4D2_OT_ToggleNewOfficialBoneInput,
    L4D2_OT_ToggleInputMode,
    L4D2_OT_AddCommonMapping,
    L4D2_OT_SaveCommonMappingChanges,
    L4D2_OT_SwitchTab,
    L4D2_OT_ResetMappingList,
    L4D2_OT_AddUniqueMapping,
    L4D2_OT_SaveUniqueMappingChanges,
    L4D2_OT_AddBonePopup,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.bone_dict_manager = bpy.props.PointerProperty(type=BoneDictManagerProperties)
    
    # 添加一个handler来处理初始化
    @bpy.app.handlers.load_post.append
    def init_bone_dict_manager(*args):
        if hasattr(bpy.context.scene, "bone_dict_manager"):
            props = bpy.context.scene.bone_dict_manager
            props.update_mapping_list()
        return None

def unregister():
    # 移除handler
    for handler in bpy.app.handlers.load_post:
        if handler.__name__ == "init_bone_dict_manager":
            bpy.app.handlers.load_post.remove(handler)
    
    # 反向遍历类列表并尝试注销
    for cls in reversed(classes):
        try:
            if hasattr(cls, 'bl_rna'):
                bpy.utils.unregister_class(cls)
        except RuntimeError:
            print(f"警告: 无法注销类 {cls.__name__}")
            continue
            
    # 清理场景属性
    try:
        if hasattr(bpy.types.Scene, "bone_dict_manager"):
            del bpy.types.Scene.bone_dict_manager
    except:
        print("警告: 无法删除场景属性 bone_dict_manager")