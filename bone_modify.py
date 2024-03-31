import bpy
import json
import os
from .resources import bone_dict

preset_dir = os.path.join(bpy.utils.resource_path('USER'), 'scripts', 'presets', 'L4D2 Character Tools')
BONE_NAMES_FILE_PATH = os.path.join(preset_dir,"bone_dict.json")
global_bone_names = {}

def simplify_bonename(n):
    return n.lower().translate(dict.fromkeys(map(ord, u" _.")))

# 保存骨骼字典到文件
def save_bone_names(bone_names_dict):
    try:
        with open(BONE_NAMES_FILE_PATH, 'w') as f:
            json.dump(bone_names_dict, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"保存文件时发生错误: {e}")

# 使用全局变量从文件加载骨骼字典
def load_bone_names():
    global global_bone_names
    # 确保预设目录存在，如果不存在则创建它
    if not os.path.isdir(preset_dir):
        os.makedirs(preset_dir)
    if os.path.isfile(BONE_NAMES_FILE_PATH):
        try:
            with open(BONE_NAMES_FILE_PATH, 'r') as f:
                global_bone_names = json.load(f)
        except json.JSONDecodeError as e:
            print(f"读取JSON文件时发生解析错误: {e}")
            # 如果解析错误，转而使用 bone_dict.py 里的字典
            global_bone_names = bone_dict.bone_names
            save_bone_names(global_bone_names)  # 将 python 字典写入新的 json 文件
    else:
        print(f"找不到文件: {BONE_NAMES_FILE_PATH}，将使用 bone_dict.py 中的字典并创建一个新的 json 文件。")
        global_bone_names = bone_dict.bone_names
        save_bone_names(global_bone_names)  # 将 python 字典写入新的 json 文件

load_bone_names() 

# 创建反向映射，以便能够定位到 bone_mapping 的键。此处只使用每个键的最后一个值。
reverse_bone_mapping = {}
for k, v in bone_dict.bone_mapping.items():
    reverse_bone_mapping[v[-1].lower()] = k

# 修改后的下拉列表枚举项创建函数
def bone_keys_enum(self, context):
    items = []
    for key in global_bone_names:
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
def bone_values_enum(self, context):
    bdm_props = context.scene.bone_dict_manager_props
    bone_key = bdm_props.bone_key_enum
    
    # 检查键是否存在于字典里，然后生成值的枚举
    if bone_key in global_bone_names:
        items = [(v, v, "") for v in global_bone_names[bone_key]]
        return items
    return []
    
# 用于存储下拉列表选择的属性
class BoneDictManagerProperties(bpy.types.PropertyGroup):
    bone_key_enum: bpy.props.EnumProperty(
        name="Dictionary Key",
        description="Select the key in the dictionary",
        items=bone_keys_enum
    )
    
    # 这里我们把 bone_name_enum 改成了一个StringProperty，因为prop_search用于搜索
    bone_name_search: bpy.props.StringProperty(
        name="Bone Name",
        description="Select the bone name in the current skeleton"
    )
    bone_value_enum: bpy.props.EnumProperty(
        name="Dictionary Value",
        description="Display all values for the selected dictionary key",
        items=bone_values_enum
    )
# 添加骨骼名到所选键操作
class L4D2_OT_AddBoneName(bpy.types.Operator):
    """Automatically remove symbols and convert to lowercase"""
    bl_label = "Add Bone"
    bl_idname = "bone_dict_manager.add_bone_name"

    def execute(self, context):
        global global_bone_names  # 记得使用全局字典
        bdm_props = context.scene.bone_dict_manager_props
        bone_key = bdm_props.bone_key_enum
        # 此处转化为小写并移除空格和点，与 `simplify_bonename` 函数执行相同处理
        bone_name = simplify_bonename(bdm_props.bone_name_search)
        
        # 添加骨骼名到所选键中，如果它尚不存在于列表中
        if bone_key in global_bone_names:
            # 使用集合来快速检查是否已存在（考虑到了大小写不敏感性）
            existing_bones = set(map(str.lower, global_bone_names[bone_key]))
            if bone_name not in existing_bones:
                global_bone_names[bone_key].append(bone_name)
                save_bone_names(global_bone_names)  # 保存更改到文件
                self.report({'INFO'}, f"{bone_name} 已添加到 {bone_key}")
            else:
                self.report({'INFO'}, f"{bone_name} 已经存在于 {bone_key}")
        else:
            # 可以选择在这里创建新的键并添加骨骼名，或者报告一个错误
            self.report({'ERROR'}, "选择的键不存在")
            
        return {'FINISHED'}
    
class L4D2_OT_RemoveBoneName(bpy.types.Operator):
    """Remove selected bone names from the custom bone list"""
    bl_label = "Remove Bone"
    bl_idname = "bone_dict_manager.remove_bone_name"
    
    @classmethod
    def poll(cls, context):
        bdm_props = context.scene.bone_dict_manager_props
        # 只有当选中的键和值都有效时，此操作才可用
        return bdm_props.bone_key_enum and bdm_props.bone_value_enum
    
    def execute(self, context):
        global global_bone_names
        bdm_props = context.scene.bone_dict_manager_props
        bone_key = bdm_props.bone_key_enum
        bone_value = bdm_props.bone_value_enum
        
        if bone_key in global_bone_names and bone_value in global_bone_names[bone_key]:
            global_bone_names[bone_key].remove(bone_value)  # 从键对应的列表中移除选定的值
            save_bone_names(global_bone_names)  # 保存更改到文件
            
            # 更新 bone_value_enum 属性，如果还有其他值则选择第一个值
            if global_bone_names[bone_key]:
                bdm_props.bone_value_enum = global_bone_names[bone_key][0]
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
        armature_A = bpy.data.objects[context.scene.Valve_Armature]
        armature_B = bpy.data.objects[context.scene.Custom_Armature]

        # 确保在物体模式
        bpy.ops.object.mode_set(mode='OBJECT')

        # 设置骨架A为姿势模式
        bpy.ops.object.select_all(action='DESELECT')
        armature_A.select_set(True)
        bpy.context.view_layer.objects.active = armature_A
        bpy.ops.object.mode_set(mode='POSE')

        for bone in armature_B.data.bones:
            # 简化骨骼名，并使用简化后的骨骼名在字典 bone_names 中查找对应的键
            simplified_name = simplify_bonename(bone.name)
            bone_name_from_global_bones = next((key for key, value in global_bone_names.items() if simplified_name in value), None)
            # 如果找到了键，那么就将这个键用于在字典 bone_dict.bone_mapping 中查找对应的键
            if bone_name_from_global_bones:
                bone_name_in_mapping = next((key for key, value in bone_dict.bone_mapping.items() if bone_name_from_global_bones in value), None)
                # 如果在字典 bone_dict.bone_mapping 中找到了匹配的键，那么就将该键用于创建骨架A的骨骼约束，并将约束目标设置为当前遍历到的骨架B的骨骼
                if bone_name_in_mapping:
                    constraint_target_bone_name = bone.name
                    bone_A_name = bone_name_in_mapping
                    
                    if bone_A_name in armature_A.pose.bones:
                        constraint = armature_A.pose.bones[bone_A_name].constraints.new('COPY_LOCATION')
                        constraint.target = armature_B
                        constraint.subtarget = constraint_target_bone_name
                        constraint.head_tail = 0

        # 遍历字典
        for bone_A_name, bone_B_names in bone_dict.bone_mapping.items():
            for bone_B_name in bone_B_names:
                # 获取B骨架中的骨骼
                bone_B = armature_B.pose.bones.get(bone_B_name)
                if not bone_B:
                    print(f"Bone '{bone_B_name}' not found in armature B")
                    continue

                # 获取A骨架中的骨骼
                bone_A = armature_A.pose.bones.get(bone_A_name)
                if not bone_A:
                    print(f"Bone '{bone_A_name}' not found in armature A")
                    continue

                # 为A骨架中的骨骼添加一个复制位置的骨骼约束
                constraint = bone_A.constraints.new('COPY_LOCATION')
                # 将约束目标设置为B骨架中的骨骼
                constraint.target = armature_B
                constraint.subtarget = bone_B.name
                constraint.head_tail = 0
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
                                bone.parent = parent_bone
                else:
                    # 如果骨骼名称不在bone_dict.bone_mapping的值当中，简化骨骼名称
                    simplified_name = simplify_bonename(bone.name)
                    for parent_name, child_names in global_bone_names.items():
                        if simplified_name in child_names:
                            for map_par_name, map_child_names in bone_dict.bone_mapping.items():
                                if parent_name in map_child_names:
                                    parent_bone = edit_bones.get(map_par_name)
                                    if parent_bone:
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
            # 然后再按照新增的global_bone_names处理机制设置父子关系
            for bone in edit_bones:
                simplified_name = simplify_bonename(bone.name)
                for parent_name, child_names in global_bone_names.items():
                    if simplified_name in child_names:
                        for map_par_name, map_child_names in bone_dict.bone_mapping.items():
                            if parent_name in map_child_names:
                                parent_bone = edit_bones.get(map_par_name)
                                if parent_bone:
                                    if bone.use_connect:
                                        bone.use_connect = False
                                    bone.parent = parent_bone


        bpy.ops.object.mode_set(mode='OBJECT')  # 返回对象模式
        return {'FINISHED'}
		
class L4D2_OT_RenameBonesOperator(bpy.types.Operator):
    bl_idname = "l4d2.rename_bones_operator"
    bl_label = "Rename Bone"
    bl_description = "Rename Bones According to Bone Mapping"

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
            for bone_key, bone_val in global_bone_names.items():
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
    bl_category = "💝"

    def draw(self, context):
        layout = self.layout
        layout.operator("l4d2.rigging_operator", icon="GROUP_BONE")
        layout.operator("l4d2.grafting_operator", icon="GP_ONLY_SELECTED")

class VIEW3D_PT_CustomBoneDictManager(bpy.types.Panel):
    bl_label = "Dict Tools"
    bl_idname = "VIEW3D_PT_custom_bone_dict_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '💝'
    bl_options = {'DEFAULT_CLOSED'} 

    def draw(self, context):
        layout = self.layout
        bdm_props = context.scene.bone_dict_manager_props

        layout.prop(bdm_props, "bone_key_enum", text="Valve BoneList")
        
        # 这里添加了显示所有值的下拉列表
        if bdm_props.bone_key_enum in global_bone_names:  # 当前选择了有效的键
            layout.prop(bdm_props, "bone_value_enum", text="Custom BoneList")
        obj = context.object
        if obj and obj.type == 'ARMATURE' and bpy.context.mode == 'POSE':
            layout.prop_search(bdm_props, "bone_name_search", obj.pose, "bones", text="Bone Name")

        row = layout.row()
        row.operator("bone_dict_manager.add_bone_name")
        row.operator("bone_dict_manager.remove_bone_name")

classes = [
    L4D2_OT_GraftingOperator,
    L4D2_OT_RiggingOperator,
    BoneDictManagerProperties,
    L4D2_OT_AddBoneName,
    L4D2_OT_RemoveBoneName,
    L4D2_OT_RenameBonesOperator,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.Valve_Armature = bpy.props.StringProperty(name="Valve Rig")
    bpy.types.Scene.Custom_Armature = bpy.props.StringProperty(name="Custom Rig")
    bpy.types.Scene.bone_dict_manager_props = bpy.props.PointerProperty(type=BoneDictManagerProperties)
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.Valve_Armature
    del bpy.types.Scene.Custom_Armature
    del bpy.types.Scene.bone_dict_manager_props