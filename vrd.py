import os
import bpy
import math
from collections import defaultdict
from bpy.props import FloatProperty, BoolProperty, EnumProperty, StringProperty, CollectionProperty, IntProperty, PointerProperty


last_export_path = ""

def get_animations_enum(self, context):
    items = [(action.name, action.name, "") for action in bpy.data.actions]
    return items

# 辅助函数：查找包含指定骨骼名称的对象
def find_object_with_bone(bone_name):
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and bone_name in obj.data.bones:
            return obj
    return None

# 辅助函数：生成导出内容文本
def generate_export_content(context, project_item):  # 接受 project_item 参数
    cxbones = project_item.bone_set.cxbone_list  # 利用 project_item 获取 cxbones
    qdbones = project_item.bone_set.qdbone_list  # 利用 project_item 获取 qdbones
    
    content = ""

    for i, (cxbone, qdbone) in enumerate(zip(cxbones, qdbones)):
        # 获取包含cxbone的对象
        obj = find_object_with_bone(cxbone.name)
        if obj is None:
            continue
        # 获取父级骨骼
        cxfbone = obj.data.bones[cxbone.name].parent.name
        qdfbone = obj.data.bones[qdbone.name].parent.name

        # 移除骨骼名中的'ValveBiped.'
        cxfbone = cxfbone.replace('ValveBiped.', '')
        qdfbone = qdfbone.replace('ValveBiped.', '')
        qdbone_name = qdbone.name.replace('ValveBiped.', '')

        # 添加helper行
        content += f"<helper> {cxbone.name} {cxfbone} {qdfbone} {qdbone_name}\n"
        # 添加basepos行
        basepos = get_transforms(obj.pose.bones[cxbone.name], 'TRANSLATION')
        content += f"<basepos> {basepos}\n"
        # 添加trigger行
        basepos_split = list(map(float, basepos.split()))  # 将basepos字符串转换为浮点型列表
        for frame in range(0, 40, 10):
            bpy.context.scene.frame_set(frame)
            qd_rotation = get_transforms(obj.pose.bones[qdbone.name], 'ROTATION')
            cx_rotation = get_transforms(obj.pose.bones[cxbone.name], 'ROTATION')
            frame_translation = get_transforms(obj.pose.bones[cxbone.name], 'TRANSLATION')
            frame_translation_split = list(map(float, frame_translation.split()))  # 将frame_translation字符串转换为浮点型列表
            xyz_translation = [str(round(float(frame_translation_split[j] - basepos_split[j]), 6)) for j in range(3)]  # 计算XYZ坐标
            content += f"<trigger> {cxbone.angle} {qd_rotation} {cx_rotation} {' '.join(xyz_translation)}\n"
        if i < len(cxbones) - 1:
            content += "\n"
    return content


# 辅助函数：生成新的导出内容文本
def generate_export_content_neko(context, project_item):  # 接受 project_item 参数
    cxbones = project_item.bone_set.cxbone_list  # 利用 project_item 获取 cxbones
    qdbones = project_item.bone_set.qdbone_list  # 利用 project_item 获取 qdbones
    
    animation_name = project_item.animation_name  # 动态获取当前项目绑定的动画名
    content = ""
   
    # 根据qdbone和cxbone的angle值对cxbone进行分组
    bone_dict = defaultdict(lambda: defaultdict(list))
    for cxbone, qdbone in zip(cxbones, qdbones):
        bone_dict[qdbone.name][cxbone.angle].append(cxbone.name)

    # 处理每个qdbone及其对应的cxbone
    for qdbone_name, angle_dict in bone_dict.items():
        # 对每个角度值的cxbone分别处理
        for angle, cxbone_names in angle_dict.items():
            # 获取包含qdbone的对象
            obj = find_object_with_bone(qdbone_name)
            if obj is None:
                print("找不到包含qdbone的对象: ", qdbone_name)
                continue
            
            # 创建输出字符串
            content += f'$NekoDriverBone "{qdbone_name}" {{\n'
            content += f'    pose "{animation_name}.smd"\n'
            # 将每个cxbone的angle值用作trigger的第一个参数
            for frame in range(0, 40, 10):
                content += f'    trigger {angle} {frame}\n'
            # 添加所有对应的cxbone
            for cxbone_name in cxbone_names:
                content += f'    "{cxbone_name}"\n'
            content += '}\n\n'
   
    return content

# 获取骨骼的平移或旋转坐标
def get_transforms(bone, transform_type):
    if bone.parent:
        parent = bone.parent.matrix.inverted_safe()
        matrix = parent @ bone.matrix
    else:
        matrix = bone.matrix

    if transform_type == 'ROTATION':
        vector = matrix.to_euler()
        vector = [math.degrees(n) for n in vector]
    else:
        vector = matrix.to_translation().xyz

    return ' '.join(str(round(n, 6)) for n in vector)

# 骨骼属性组
class BonePropertyGroup(bpy.types.PropertyGroup):
    name: StringProperty()
    angle: FloatProperty(name="Angle", default=90, precision=0)

class BoneListSet(bpy.types.PropertyGroup):
    cxbone_list: CollectionProperty(type=BonePropertyGroup)
    qdbone_list: CollectionProperty(type=BonePropertyGroup)

class ProjectItem(bpy.types.PropertyGroup):
    name: StringProperty(name="VRD Project Name")
    bone_set: PointerProperty(type=BoneListSet)
    cxbone_index: IntProperty()  
    qdbone_index: IntProperty()
    animation_name: EnumProperty(
        items=get_animations_enum,
        name="Action Name",
        description="Select the action bound to the project"
    )


class CXBONE_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.scale_x = 0.1
            row.label(text=str(index+1))  # 新增的代码: 在列表每一项前面加一个数字顺序
            row.scale_x = 0.9
            split = layout.split(factor=0.7)
            split.prop(item, "name", text="", emboss=False, translate=False, icon='BONE_DATA')  
            split.prop(item, "angle", text="")  
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.prop(item, "name", text="")


# 定义一个UI列表用于显示qdbone
class QDBONE_UL_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, translate=False, icon='BONE_DATA')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.prop(item, "name", text="")

class VRD_UL_ProjectList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False, icon='CON_SPLINEIK')
            layout.prop(item, "animation_name", text="", emboss=False, icon_value=icon, icon='ACTION_TWEAK')

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='CON_SPLINEIK')
            
# 面板 UI 类
class L4D2_PT_VRDPanel(bpy.types.Panel):
    bl_label = "VRD Bone List"
    bl_idname = "L4D2_PT_vrd_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '💝'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 项目管理
        box = layout.box()
        box.label(text="VRD Action Management:")
        row = box.row()
        row.template_list("VRD_UL_ProjectList", "", scene, "project_items", scene, "active_project_index", rows=2)

        col = row.column(align=True)
        col.operator("vrd.add_project", icon='ADD', text="")
        col.operator("vrd.remove_project", icon='REMOVE', text="")
        split = layout.split(factor=0.5)
        col1 = split.column()   
        col2 = split.column()

        col1.label(text="Procedural Bone:")
        col2.label(text="Driver Bone:")
        # 确保索引有效
        if scene.active_project_index >= 0 and len(scene.project_items) > scene.active_project_index:
            project_item = scene.project_items[scene.active_project_index]

            # 使用template_list展示cxbone_list和qdbone_list
            split = layout.split(factor=0.55)
            
            col = split.column()
            col.template_list(
                "CXBONE_UL_List", "cxbone_list",
                project_item.bone_set, "cxbone_list", project_item, "cxbone_index", rows=10)
            row = col.row()
            left = row.row(align=True)
            left.scale_x = 1.25
            left.operator("vrd.edit_bone_list_ops", text="", icon='ADD').operation = 'ADD_CX'
            left.operator("vrd.edit_bone_list_ops", text="", icon='REMOVE').operation = 'REMOVE_CX'
            left.operator("vrd.edit_bone_list_ops", text="", icon='TRASH').operation = 'CLEAR_CX'
            right = row.row(align=True)
            right.scale_x = 1.25
            right.alignment = 'RIGHT'
            right.operator("vrd.edit_bone_list_ops", text="", icon='TRIA_UP').operation = 'MOVE_UP_CX'
            right.operator("vrd.edit_bone_list_ops", text="", icon='TRIA_DOWN').operation = 'MOVE_DOWN_CX'

            col = split.column()
            col.template_list(
                "QDBONE_UL_List", "qdbone_list",
                project_item.bone_set, "qdbone_list", project_item, "qdbone_index", rows=10)
            row = col.row()
            left = row.row(align=True)
            left.scale_x = 1.25
            left.operator("vrd.edit_bone_list_ops", text="", icon='ADD').operation = 'ADD_QD'
            left.operator("vrd.edit_bone_list_ops", text="", icon='REMOVE').operation = 'REMOVE_QD'
            left.operator("vrd.edit_bone_list_ops", text="", icon='TRASH').operation = 'CLEAR_QD'
            right = row.row(align=True)
            right.scale_x = 1.25
            right.alignment = 'RIGHT'
            right.operator("vrd.edit_bone_list_ops", text="", icon='TRIA_UP').operation = 'MOVE_UP_QD'
            right.operator("vrd.edit_bone_list_ops", text="", icon='TRIA_DOWN').operation = 'MOVE_DOWN_QD'

        else:
            # 项目列表为空或无效索引
            layout.label(text="No Items or Invalid Index,Create New VRD Action First")
        
        row = layout.row()
        row.operator("vrd.auto_pose", icon="OUTLINER_DATA_ARMATURE") 
        row = layout.row()
        row.prop(context.scene, 'vrd_export_path')
        row = layout.row()
        row.prop(context.scene, 'export_default', toggle=True, translate=False, icon="FILE_CACHE")
        row.prop(context.scene, 'export_nekomdl', toggle=True, translate=False, icon="FILE_CACHE")
        row.operator("vrd.open_file", text="", icon='CURRENT_FILE').open_type = 'FILE'
        row.operator("vrd.open_file", text="", icon='FILE_FOLDER').open_type = 'FOLDER'

        if context.scene.export_default:
            if scene.export_all:
                icon_value = 'CHECKBOX_HLT'  # 激活状态的图标
            else:
                icon_value = 'CHECKBOX_DEHLT'  # 未激活状态的图标

            # 绘制复选按钮，并设置图标
            layout.prop(scene, 'export_all', toggle=True, icon=icon_value)

            layout.operator('vrd.export_bones', text='Copy to Clipboard', icon="COPYDOWN").action='DEFAULT_EXPORT_CLIPBOARD'
            layout.operator('vrd.export_bones', text='Export to File', icon="FILE_NEW").action='DEFAULT_EXPORT_FILE'

        if context.scene.export_nekomdl:
            if scene.export_all:
                icon_value = 'CHECKBOX_HLT'  # 激活状态的图标
            else:
                icon_value = 'CHECKBOX_DEHLT'  # 未激活状态的图标

            # 绘制复选按钮，并设置图标
            layout.prop(scene, 'export_all', toggle=True, icon=icon_value)
            layout.operator('vrd.export_bones', text='Copy to Clipboard', icon="COPYDOWN").action='NEKOMDL_EXPORT_CLIPBOARD'
            layout.operator('vrd.export_bones', text='Export to File', icon="FILE_NEW").action='NEKOMDL_EXPORT_FILE'


class VRD_OT_ExportBones(bpy.types.Operator):
    bl_idname = "vrd.export_bones"
    bl_label = "Export bone VRD data"
    
    action: EnumProperty(
        name="动作",
        items=[
            ('DEFAULT_EXPORT_FILE', "StudioMDL：导出到文件", ""),
            ('DEFAULT_EXPORT_CLIPBOARD', "StudioMDL：复制到剪贴板", ""),
            ('NEKOMDL_EXPORT_FILE', "NekoMDL：导出到文件", ""),
            ('NEKOMDL_EXPORT_CLIPBOARD', "NekoMDL：复制到剪贴板", "") 
        ]
    )
    
    bpy.types.Scene.vrd_export_path = StringProperty(
            name="Export Path",
            subtype='FILE_PATH', 
            default="//"
        )

    # 修改后的execute函数
    def execute(self, context):
        # 如果选择了导出所有项目
        if context.scene.export_all:
            full_content = ""
            for project_item in context.scene.project_items:
                # 设置当前项目的动画作为对象的动画
                if not self.set_animation(context, project_item.animation_name):
                    self.report({'ERROR'}, f"找不到动画：{project_item.animation_name}")
                    continue  # 找不到动画则跳过当前项目

                # 生成当前项目的内容
                content = self.generate_content(context, project_item)
                if full_content:
                    full_content += f"\n// {project_item.name}\n{content}"
                else:
                    full_content += f"// {project_item.name}\n{content}"

            content_to_export = full_content
        else:
            # 只处理当前选中的项目
            project_item = context.scene.project_items[context.scene.active_project_index]
            if not self.set_animation(context, project_item.animation_name):
                self.report({'ERROR'}, f"找不到动画：{project_item.animation_name}")
                return {'CANCELLED'}
            content_to_export = self.generate_content(context, project_item)


        if not content_to_export:
            self.report({'ERROR'}, "无可导出的数据")
            return {'CANCELLED'}
 
        if self.action in {'DEFAULT_EXPORT_FILE', 'NEKOMDL_EXPORT_FILE'}:
            if not context.scene.vrd_export_path:
                self.report({'ERROR'}, "请先设置导出的文件路径！")
                return {'CANCELLED'}
        filepath = bpy.path.abspath(context.scene.vrd_export_path)
        if filepath.endswith(('\\', '/')):
            self.report({'ERROR'}, "请在导出路径提供一个具体的文件名")
            return {'CANCELLED'}
        try:
            with open(filepath, 'w') as f:
                f.write(content_to_export)
        except Exception as e:
            self.report({'ERROR'}, "文件写入失败: {}".format(e))
            return {'CANCELLED'}
            self.report({'INFO'}, "文本已保存到文件：{}".format(context.scene.vrd_export_path))
        else:  
            context.window_manager.clipboard = content_to_export
            self.report({'INFO'}, "文本已复制到剪贴板。")

        return {'FINISHED'}
    
    # 根据action类型生成导出内容
    def generate_content(self, context, project_item):
        if self.action in {'NEKOMDL_EXPORT_FILE', 'NEKOMDL_EXPORT_CLIPBOARD'}:
            return generate_export_content_neko(context, project_item)
        else:
            return generate_export_content(context, project_item)

    # 设置动画数据到当前激活的对象
    def set_animation(self, context, animation_name):
        anim = bpy.data.actions.get(animation_name)
        if not anim:
            return False
        context.scene.frame_set(0)
        obj = context.view_layer.objects.active
        if obj is None:  # 检查活动对象是否存在
            self.report({'ERROR'}, "没有活动的对象可以设置动画")
            return False
        if obj.animation_data is None:
            obj.animation_data_create()
        obj.animation_data.action = anim
        return True

# 添加项目的运算符
class VRD_OT_AddProject(bpy.types.Operator):
    """Add new project to the project list"""
    bl_idname = "vrd.add_project"
    bl_label = "Add New Project"

    def execute(self, context):
        scene = context.scene
        # 创建新的ProjectItem
        new_project = scene.project_items.add()
        # 给新项目设置一个名字
        new_project.name = f"VRD Project {len(scene.project_items)}"
        # 设置项目的初始cxbone和qdbone列表的索引
        # 初始状态下，可能没有骨骼，所以先设为-1
        new_project.cxbone_index = -1
        new_project.qdbone_index = -1
        # 更新当前活动项目索引
        scene.active_project_index = len(scene.project_items) - 1

        return {'FINISHED'}

# 移除项目的运算符
class VRD_OT_RemoveProject(bpy.types.Operator):
    """Remove the currently selected project from the project list"""
    bl_idname = "vrd.remove_project"
    bl_label = "Remove Project"

    @classmethod
    def poll(cls, context):
        # 确保有存在的项目可移除
        return len(context.scene.project_items) > 0

    def execute(self, context):
        scene = context.scene
        # 获取当前选中的项目索引
        active_idx = scene.active_project_index

        # 确保选中项目索引是有效的
        if active_idx < 0 or active_idx >= len(scene.project_items):
            self.report({'ERROR'}, "没有选中有效的项目")
            return {'CANCELLED'}

        # 移除当前选中的项目
        scene.project_items.remove(active_idx)

        # 如果移除了最后一个项目，递减活动项目索引
        if active_idx >= len(scene.project_items):
            scene.active_project_index -= 1

        # 如果没有任何项目了，重置活动项目索引为-1
        if len(scene.project_items) == 0:
            scene.active_project_index = -1
        
        return {'FINISHED'}
    
class VRD_OT_EditBoneListOps(bpy.types.Operator):
    bl_idname = "vrd.edit_bone_list_ops"
    bl_label = "Operations for editing the bone list"
    bl_description = "Edit the bone list including adding, removing, moving and clearing bones"

    operation: EnumProperty(
        items=[
            ('ADD_CX', "Add Procedural Bone", ""),
            ('ADD_QD', "Add Driver Bone", ""),
            ('REMOVE_CX', "Remove Selected Procedural Bone", ""),
            ('REMOVE_QD', "Remove Selected Driver Bone", ""),
            ('CLEAR_CX', "Clear Procedural Bone List", ""),
            ('CLEAR_QD', "Clear Driver Bone List", ""),
            ('MOVE_UP_CX', "Move Up Procedural Bone", ""),
            ('MOVE_DOWN_CX', "Move Down Procedural Bone", ""),
            ('MOVE_UP_QD', "Move Up Driver Bone", ""),
            ('MOVE_DOWN_QD', "Move Down Driver Bone", ""),
        ]
    )
    
    def execute(self, context):
        scene = context.scene
        active_index = scene.active_project_index
        if active_index < 0 or active_index >= len(scene.project_items):
            self.report({'ERROR'}, "项目索引无效")
            return {'CANCELLED'}

        project_item = scene.project_items[active_index]
        bone_set = project_item.bone_set
        operation = self.operation
        
        # 根据operation执行对应的操作
        if operation == 'ADD_CX':
            return self.add_bone(context, bone_set.cxbone_list)
        elif operation == 'ADD_QD':
            return self.add_bone(context, bone_set.qdbone_list)
        elif operation.startswith('REMOVE_'):
            return self.remove_bone(context, bone_set, operation.endswith('CX'))
        elif operation.startswith('CLEAR_'):
            return self.clear_bone_list(bone_set, operation.endswith('CX'))
        elif operation.startswith('MOVE_UP_'):
            return self.move_bone(bone_set, operation.endswith('CX'), True)
        elif operation.startswith('MOVE_DOWN_'):
            return self.move_bone(bone_set, operation.endswith('CX'), False)
        return {'FINISHED'}

    def add_bone(self, context, target_list):
        armature = context.active_object
        if armature and armature.type == 'ARMATURE' and context.mode == 'POSE':
            for bone in context.selected_pose_bones:
                new_bone_property = target_list.add()
                new_bone_property.name = bone.name
                self.report({'INFO'}, f"添加骨骼: {bone.name}")
        else:
            self.report({'ERROR'}, "没有选中合适的骨骼或不处于姿势模式")
            return {'CANCELLED'}
        return {'FINISHED'}

    def remove_bone(self, context, bone_set, is_cxbone):
        lista = bone_set.cxbone_list if is_cxbone else bone_set.qdbone_list
        index_name = 'cxbone_index' if is_cxbone else 'qdbone_index'
        idx = getattr(context.scene.project_items[context.scene.active_project_index], index_name)

        if idx >= 0 and idx < len(lista):
            lista.remove(idx)
            setattr(context.scene.project_items[context.scene.active_project_index], index_name, idx - 1)
            self.report({'INFO'}, "移除了选定的骨骼")
        else:
            self.report({'ERROR'}, "选定的骨骼无效或不存在")
            return {'CANCELLED'}
        return {'FINISHED'}

    def clear_bone_list(self, bone_set, is_cxbone):
        lista = bone_set.cxbone_list if is_cxbone else bone_set.qdbone_list
        lista.clear()
        self.report({'INFO'}, "清空了骨骼列表")
        return {'FINISHED'}

    def move_bone(self, bone_set, is_cxbone, move_up):
        lista = bone_set.cxbone_list if is_cxbone else bone_set.qdbone_list
        index_name = 'cxbone_index' if is_cxbone else 'qdbone_index'
        project = bpy.context.scene.project_items[bpy.context.scene.active_project_index]
        idx = getattr(project, index_name)

        if idx < 0 or idx >= len(lista):
            self.report({'ERROR'}, "选定的骨骼无效或不存在")
            return {'CANCELLED'}

        swap_idx = idx - 1 if move_up else idx + 1
        if swap_idx < 0 or swap_idx >= len(lista):
            self.report({'ERROR'}, "不能移动，已经在列表边界")
            return {'CANCELLED'}

        lista.move(idx, swap_idx)
        setattr(project, index_name, swap_idx)
        # 根据移动方向，输出不同的信息
        move_direction = "上" if move_up else "下"
        self.report({'INFO'}, f"骨骼已经向{move_direction}移动")
        return {'FINISHED'}
    
class VRD_OT_OpenFile(bpy.types.Operator):
    bl_idname = "vrd.open_file"
    bl_label = "Open File or Folder"
    bl_description = "Open the file or folder specified by 'Export Path'"

    open_type: EnumProperty(
        items=[
            ('FILE', "文本文件", "打开在 'vrd_export_path' 指定的文件"),
            ('FOLDER', "文件夹", "打开在 'vrd_export_path' 指定的文件所在的文件夹"),
        ]
    )

    def execute(self, context):
        if not context.scene.vrd_export_path:
            self.report({'ERROR'}, "请先设置文件路径！")
            return {'CANCELLED'}

        try:
            # 选择打开文件或文件夹
            to_open = bpy.path.abspath(context.scene.vrd_export_path) if self.open_type == 'FILE' else os.path.dirname(bpy.path.abspath(context.scene.vrd_export_path))
            os.startfile(to_open)
        except Exception as e:
            self.report({'ERROR'}, "打开失败: {}".format(str(e)))
            return {'CANCELLED'}

        return {'FINISHED'}

class VRD_OT_AutoPose(bpy.types.Operator):
    bl_idname = "vrd.auto_pose"
    bl_label = "Generate VRD Action"
    bl_description = "Create actions named 'VRD' and 'VRD_Foot', insert keyframes of 4 official bone 'VRD' poses from 0 to 30 frames"

    @staticmethod
    def set_keyframes(armature, frame, bone_names, rotations):
        # 设置当前帧
        bpy.context.scene.frame_set(frame)

        # 获取姿势模式下的骨骼数据
        pose_bones = armature.pose.bones

        # 遍历指定的骨骼名称
        for bone_name, rotation in zip(bone_names, rotations):
            pose_bone = pose_bones.get(bone_name)

            if pose_bone:
                # 设置四元数旋转值
                pose_bone.rotation_quaternion = rotation

                # 记录关键帧
                pose_bone.keyframe_insert(data_path="rotation_quaternion")
                pose_bone.keyframe_insert(data_path="location")
            else:
                print(f"未找到名为 {bone_name} 的骨骼。")

    def define_actions(self, armature, action_name, bone_names, rotations):
        # 创建一个action
        action = bpy.data.actions.new(name=action_name)
        armature.animation_data_create()
        armature.animation_data.action = action
        action.use_fake_user = True  # 确保动作在没有用户使用时仍然被保存

        # 切换到姿势模式并全选骨骼
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')

        # 返回第0帧并记录所有骨骼的位置和旋转关键帧
        bpy.context.scene.frame_set(0)
        bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_LocRot')

        # 在第 10 帧、第 20 帧和第 30 帧修改指定骨骼的四元数旋转值并记录关键帧
        for i, frame in enumerate([10, 20, 30]):
            self.set_keyframes(armature, frame, bone_names, rotations[i])

        # 返回对象模式
        bpy.ops.object.mode_set(mode='OBJECT')

    def execute(self, context):
        # 确保当前活动对象是骨架
        armature = context.active_object
        if armature and armature.type == 'ARMATURE':
            # 定义操作中所用的骨骼和四元数
            actions = [
                {"name": "VRD", "bones": ["ValveBiped.Bip01_L_Thigh", "ValveBiped.Bip01_R_Thigh", "ValveBiped.Bip01_L_Hand", "ValveBiped.Bip01_R_Hand"],
                "rotations": [
                    [(0.608762, 0, 0, -0.793354), (0.608762, 0, 0, -0.793354), (0.707107, 0.707107, 0, 0), (0.707107, -0.707107, 0, 0)],
                    [(0.630365, -0.163028, -0.104526, -0.796198), (0.630365, 0.163028, 0.104526, -0.796198), (0.707107, -0.707107, 0, 0), (0.707107, 0.707107, 0, 0)],
                    [(0.707107, 0, -0.707107, 0), (0.707107, 0, 0.707107, 0), (1,0, 0, 0), (1,0, 0, 0)]
                ]},
                
                {"name": "VRD_Foot", "bones": ["ValveBiped.Bip01_L_Foot", "ValveBiped.Bip01_R_Foot"],
                "rotations": [
                    [(0.866025, -0.059726, 0.017433, -0.496114), (0.866025, 0.059727, -0.023217, -0.495877)],
                    [(0.866025, 0.059726, -0.017433, 0.496114), (0.866025, -0.059727, 0.023217, 0.495877)],
                    [(0.866025, -0.469559, 0.160158, 0.062157), (0.866025, 0.469559, -0.159423, 0.064021)]
                ]}
            ]
            for action in actions:
                self.define_actions(armature, action['name'], action['bones'], action['rotations'])
                bpy.context.scene.frame_set(0)
        else:
            return {'CANCELLED'}
        return {'FINISHED'}

# 注册插件
classes = [
    VRD_OT_EditBoneListOps,
    BonePropertyGroup,
    VRD_OT_ExportBones,
    VRD_OT_OpenFile,
    VRD_OT_AutoPose,
    CXBONE_UL_List,
    QDBONE_UL_List,
    BoneListSet,
    ProjectItem,
    VRD_OT_AddProject,
    VRD_OT_RemoveProject,
    VRD_UL_ProjectList,
]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cxbone_list = CollectionProperty(type=BonePropertyGroup)
    bpy.types.Scene.qdbone_list = CollectionProperty(type=BonePropertyGroup)
    bpy.types.Scene.cxbone_list_index = IntProperty()
    bpy.types.Scene.qdbone_list_index = IntProperty()
    bpy.types.Scene.bone_list_sets = CollectionProperty(type=BoneListSet)
    bpy.types.Scene.bone_list_sets_index = IntProperty()
    bpy.types.Scene.export_default = BoolProperty(name="Default",description="The exported text will be output in the VRD text format that can be received by StudioMDL", default=False)
    bpy.types.Scene.export_nekomdl = BoolProperty(name="NekoMDL",description="The exported text will be output in the VRD text format that can be received by NekoMDL", default=False)
    bpy.types.Scene.project_items = CollectionProperty(type=ProjectItem)
    bpy.types.Scene.active_project_index = IntProperty()
    bpy.types.Scene.export_all = BoolProperty(name="Export All VRD",description="Export all VRD texts obtained from the bound animations",default=True)


# 注销插件
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cxbone_list
    del bpy.types.Scene.qdbone_list
    del bpy.types.Scene.cxbone_list_index
    del bpy.types.Scene.qdbone_list_index
    del bpy.types.Scene.bone_list_sets
    del bpy.types.Scene.bone_list_sets_index
    del bpy.types.Scene.export_default
    del bpy.types.Scene.export_nekomdl
    del bpy.types.Scene.project_items
    del bpy.types.Scene.active_project_index
    del bpy.types.Scene.export_all