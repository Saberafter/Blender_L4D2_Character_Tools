import bpy
import os
from bpy.props import StringProperty, CollectionProperty, PointerProperty, FloatProperty, FloatVectorProperty, BoolProperty
from bpy.types import PropertyGroup, Operator, Panel, UIList
from mathutils import Vector
from bpy_extras import view3d_utils
from bpy.app.translations import pgettext_iface as _

class VertexGroupItem(PropertyGroup):
    name: StringProperty(name=_("Vertex Group Name"), description=_("The name of the vertex group"))
    actual_group: StringProperty(name=_("Actual Vertex Group"), description=_("The actual selected vertex group"))

class L4D2_UL_VertexGroups(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            obj = None
            if context.scene.target_mesh_object:
                obj = bpy.data.objects.get(context.scene.target_mesh_object)
            
            # 如果目标物体存在，则使用 prop_search
            if obj:
                # 要显示的顶点组名称列表来源于目标物体的顶点组集合
                layout.prop_search(item, "actual_group", obj, "vertex_groups", text="")
            else:
                # 如果目标物体不存在，则只显示名称
                layout.label(text=item.name)
                
            remove_op = layout.operator("scene.remove_vertex_group", text="", icon="X")
            remove_op.index = data.vertex_group_names.values().index(item)

class L4D2_PT_WeightsPanel(Panel):
    bl_label = _("Weight Editing Tools")
    bl_idname = "L4D2_PT_WeightsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 添加顶点组编辑的折叠开关
        layout.prop(scene, "bl_VGE", text=_("Vertex Group Editing"), icon="TRIA_DOWN" if scene.bl_VGE else "TRIA_RIGHT")

        # 如果折叠开关打开，显示详细控制
        if scene.bl_VGE:
            # 显示当前目标物体
            if scene.target_mesh_object:
                obj = bpy.data.objects.get(scene.target_mesh_object)
                if obj:
                    row = layout.row()
                    row.label(text=f"{_('Target Object:')} {obj.name}")
            
            # 添加按钮行，包含从骨骼添加和从顶点组添加按钮
            row = layout.row(align=True)
            row.operator("scene.add_from_selected_bones", text=_("Add from Selected Bones"), icon="BONE_DATA")
            row.operator("scene.add_empty_vertex_group", text=_("Add from Vertex Groups"), icon="GROUP_VERTEX")
            
            # 添加重置按钮
            reset_row = layout.row()
            reset_row.operator("scene.clear_vertex_groups", text=_("Reset"), icon="FILE_REFRESH")
            
            # 显示已添加的顶点组列表
            layout.template_list("L4D2_UL_VertexGroups", "", scene, "vertex_group_names", scene, "active_vertex_group_index", rows=3)
            
            # 权重处理按钮
            if len(scene.vertex_group_names) > 0:
                # 将两个按钮分开为两列
                row1 = layout.row()
                row1.operator("l4d2.process_vertex_groups", text=_("Merge Vertex Groups")).operation = 'MERGE'
                row2 = layout.row()
                row2.operator("l4d2.process_vertex_groups", text=_("Even Weight Transfer")).operation = 'EVEN_WEIGHT_TRANSFER'

                # 如果顶点组数量足够显示二分权重选项
                if len(scene.vertex_group_names) >= 3:
                    layout.separator()
                    
                    # 第一行：分割模式按钮
                    layout.label(text=_("Split Mode:"))
                    
                    # 创建分割模式按钮组
                    split_mode_row = layout.row(align=True)
                    
                    # 创建四个分割模式按钮，当前选中的会高亮显示
                    split_mode = scene.split_mode
                    
                    # X轴按钮
                    icon_x = 'RADIOBUT_ON' if split_mode == 'X_AXIS' else 'RADIOBUT_OFF'
                    x_op = split_mode_row.operator("l4d2.set_split_mode", text=_("X Axis"), icon=icon_x, depress=(split_mode == 'X_AXIS'))
                    x_op.mode = 'X_AXIS'
                    
                    # Y轴按钮
                    icon_y = 'RADIOBUT_ON' if split_mode == 'Y_AXIS' else 'RADIOBUT_OFF'
                    y_op = split_mode_row.operator("l4d2.set_split_mode", text=_("Y Axis"), icon=icon_y, depress=(split_mode == 'Y_AXIS'))
                    y_op.mode = 'Y_AXIS'
                    
                    # Z轴按钮
                    icon_z = 'RADIOBUT_ON' if split_mode == 'Z_AXIS' else 'RADIOBUT_OFF'
                    z_op = split_mode_row.operator("l4d2.set_split_mode", text=_("Z Axis"), icon=icon_z, depress=(split_mode == 'Z_AXIS'))
                    z_op.mode = 'Z_AXIS'
                    
                    # 自定义分割线按钮
                    icon_custom = 'RADIOBUT_ON' if split_mode == 'CUSTOM' else 'RADIOBUT_OFF'
                    custom_op = split_mode_row.operator("l4d2.draw_split_line", text=_("Custom"), icon=icon_custom, depress=(split_mode == 'CUSTOM'))
                    
                    # 如果当前是自定义分割线模式且未设置，显示警告
                    if split_mode == 'CUSTOM' and not scene.use_custom_split_line:
                        warning_row = layout.row()
                        warning_row.label(text=_("Please draw the split line first"), icon='ERROR')
                    
                    # 第二行：混合因子滑块
                    blend_row = layout.row()
                    blend_row.prop(scene, "blend_factor")
                    
                    # 第三行：二分权重执行按钮
                    weight_btn_row = layout.row()
                    weight_btn_row.scale_y = 1.2
                    weight_btn_row.operator("l4d2.process_vertex_groups", text=_("Execute Bisect Weight")).operation = 'WEIGHT_TRANSFER'
            else:
                layout.label(text=_("Please add vertex groups first"))

class L4D2_OT_AddFromSelectedBones(Operator):
    bl_idname = "scene.add_from_selected_bones"
    bl_label = _("Add from Selected Bones")
    bl_description = _("Automatically add corresponding vertex groups from bones selected in pose mode")
    
    def execute(self, context):
        # 检查是否在pose mode
        if not (context.active_object and context.active_object.type == 'ARMATURE' 
                and context.active_object.mode == 'POSE'):
            self.report({'WARNING'}, _("Please select bones in Pose Mode"))
            return {'CANCELLED'}
            
        # 获取选中的骨骼
        armature = context.active_object
        selected_bones = [bone.name for bone in armature.pose.bones if bone.bone.select]
        if not selected_bones:
            self.report({'WARNING'}, _("No bones selected"))
            return {'CANCELLED'}
        
        # 获取关联的网格物体
        related_objects = self.get_related_mesh_objects(armature)
        if not related_objects:
            self.report({'WARNING'}, _("Could not find mesh objects associated with the armature"))
            return {'CANCELLED'}
        
        # 处理物体选择
        mesh_obj = None
        if len(related_objects) == 1:
            # 如果只有一个物体，直接使用
            mesh_obj = related_objects[0]
            context.scene.target_mesh_object = mesh_obj.name
        else:
            # 如果有多个物体，优先使用已保存的物体
            if context.scene.target_mesh_object in [obj.name for obj in related_objects]:
                mesh_obj = bpy.data.objects.get(context.scene.target_mesh_object)
            else:
                # 显示选择对话框
                context.scene.related_objects.clear()
                for obj in related_objects:
                    item = context.scene.related_objects.add()
                    item.name = obj.name
                bpy.ops.wm.select_mesh_object('INVOKE_DEFAULT')
                return {'FINISHED'}
        
        # 如果成功获取物体，添加顶点组
        if mesh_obj:
            self.add_vertex_groups_from_bones(context, mesh_obj, selected_bones)
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
    
    def add_vertex_groups_from_bones(self, context, mesh_obj, bone_names):
        # 添加顶点组到列表
        added = 0
        not_found = 0
        for bone_name in bone_names:
            if bone_name in mesh_obj.vertex_groups:
                # 检查是否已经在列表中
                if not any(group.name == bone_name or group.actual_group == bone_name for group in context.scene.vertex_group_names):
                    group_item = context.scene.vertex_group_names.add()
                    group_item.name = bone_name
                    group_item.actual_group = bone_name
                    added += 1
            else:
                not_found += 1
        
        if added > 0:
            self.report({'INFO'}, f"{_('Added')} {added} {_('vertex groups')}")
        if not_found > 0:
            self.report({'WARNING'}, f"{not_found} {_('bone names do not exist in vertex groups')}")
    
    def get_related_mesh_objects(self, armature):
        """获取与骨架关联的所有网格物体"""
        related_objects = []
        
        # 检查子对象
        for child in armature.children:
            if child.type == 'MESH':
                related_objects.append(child)
        
        # 检查具有Armature修改器的物体
        for obj in bpy.context.view_layer.objects:
            if obj.type == 'MESH':
                for modifier in obj.modifiers:
                    if modifier.type == 'ARMATURE' and modifier.object == armature:
                        if obj not in related_objects:
                            related_objects.append(obj)
        
        return related_objects

class L4D2_OT_SelectMeshObject(Operator):
    bl_idname = "wm.select_mesh_object"
    bl_label = _("Select Target Object")
    
    # 存储用户选择的物体名称
    selected_object: StringProperty(default="")
    
    def invoke(self, context, event):
        # 使用invoke_props_dialog而不是invoke_popup以获得确认按钮
        # 存储引用到全局变量，以便子操作符能够访问
        bpy.types.Scene.current_select_dialog = self
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text=_("Select the target object to process:"))
        
        # 获取当前选中的物体名称
        current_object = self.selected_object
        
        # 绘制物体列表
        for i, item in enumerate(context.scene.related_objects):
            row = layout.row()
            
            # 判断是否为当前选中物体
            is_selected = (item.name == current_object)
            
            # 使用不同的图标和样式区分选中状态
            if is_selected:
                # 选中状态使用醒目的样式
                row.alert = True  # 使用红色高亮
                op = row.operator("wm.select_object_item", text="✓ " + item.name, icon="CHECKBOX_HLT")
            else:
                # 未选中状态使用普通样式
                op = row.operator("wm.select_object_item", text="   " + item.name, icon="MESH_DATA")
            
            op.object_name = item.name
    
    def execute(self, context):
        # 清除全局引用
        if hasattr(bpy.types.Scene, "current_select_dialog"):
            del bpy.types.Scene.current_select_dialog
            
        # 如果已选择物体
        if self.selected_object:
            # 设置目标物体
            context.scene.target_mesh_object = self.selected_object
            
            # 检查是否从骨骼添加
            armature = context.active_object
            if armature and armature.type == 'ARMATURE' and armature.mode == 'POSE':
                selected_bones = [bone.name for bone in armature.pose.bones if bone.bone.select]
                mesh_obj = bpy.data.objects.get(self.selected_object)
                if mesh_obj and selected_bones:
                    self.add_vertex_groups_from_bones(context, mesh_obj, selected_bones)
            # 如果不是从骨骼添加，可能是从顶点组添加，添加一个空项
            else:
                mesh_obj = bpy.data.objects.get(self.selected_object)
                if mesh_obj and mesh_obj.type == 'MESH' and mesh_obj.vertex_groups:
                    # 添加一个空的顶点组条目
                    group_item = context.scene.vertex_group_names.add()
                    group_item.name = ""  # 初始名称为空
                    group_item.actual_group = ""  # 初始顶点组为空
        
        # 强制刷新所有区域的UI
        for area in context.screen.areas:
            area.tag_redraw()
            
        return {'FINISHED'}
    
    def add_vertex_groups_from_bones(self, context, mesh_obj, bone_names):
        # 添加顶点组到列表
        added = 0
        not_found = 0
        for bone_name in bone_names:
            if bone_name in mesh_obj.vertex_groups:
                # 检查是否已经在列表中
                if not any(group.name == bone_name or group.actual_group == bone_name for group in context.scene.vertex_group_names):
                    group_item = context.scene.vertex_group_names.add()
                    group_item.name = bone_name
                    group_item.actual_group = bone_name
                    added += 1
            else:
                not_found += 1
        
        if added > 0:
            self.report({'INFO'}, f"{_('Added')} {added} {_('vertex groups')}")
        if not_found > 0:
            self.report({'WARNING'}, f"{not_found} {_('bone names do not exist in vertex groups')}")

class L4D2_OT_SelectObjectItem(Operator):
    bl_idname = "wm.select_object_item"
    bl_label = _("Select Object Item")
    
    object_name: StringProperty()
    
    def execute(self, context):
        # 安全地获取父对话框操作符
        if hasattr(bpy.types.Scene, "current_select_dialog"):
            parent_op = bpy.types.Scene.current_select_dialog
            parent_op.selected_object = self.object_name
            
            # 刷新UI以更新选中状态
            for area in context.screen.areas:
                area.tag_redraw()
            
        return {'FINISHED'}

class L4D2_OT_SetTargetMesh(Operator):
    bl_idname = "scene.set_target_mesh"
    bl_label = _("Set Target Object")
    
    object_name: StringProperty()
    
    def execute(self, context):
        # 只设置目标物体，不添加顶点组
        context.scene.target_mesh_object = self.object_name
        return {'FINISHED'}

class L4D2_OT_ClearVertexGroups(Operator):
    bl_idname = "scene.clear_vertex_groups"
    bl_label = _("Clear Vertex Group List")
    bl_description = _("Clear the current vertex group list and reset target object selection for switching to new armatures and objects")
    
    def execute(self, context):
        # 清空顶点组列表
        context.scene.vertex_group_names.clear()
        # 清空目标物体选择
        context.scene.target_mesh_object = ""
        self.report({'INFO'}, _("Vertex group list and target object selection cleared"))
        return {'FINISHED'}

class L4D2_OT_RemoveVertexGroup(Operator):
    bl_idname = "scene.remove_vertex_group"
    bl_label = _("Remove Vertex Group")
    bl_description = _("Remove this vertex group from the list")
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.vertex_group_names.remove(self.index)
        return {'FINISHED'}

class L4D2_OT_ProcessVertexGroups(Operator):
    bl_idname = "l4d2.process_vertex_groups"
    bl_label = _("Process Vertex Groups")
    bl_description = _("Merge: Merge weights of subsequent groups into the first group.\n"
                       "Even: Evenly distribute weights of the first group to subsequent groups.\n"
                       "Bisect: Distribute the first group's weight to the 2nd and 3rd groups based on the selected axis or custom line.")
    
    operation: bpy.props.StringProperty()
    
    def execute(self, context):
        scene = context.scene
        if not scene.target_mesh_object:
            self.report({'WARNING'}, _("Target object not set"))
            return {'CANCELLED'}
            
        obj = bpy.data.objects.get(scene.target_mesh_object)
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, _("Target object is invalid or not a mesh object"))
            return {'CANCELLED'}
        
        # 从列表项获取顶点组名称，优先使用 actual_group 字段，如果为空则使用 name 字段
        group_names = []
        for group in scene.vertex_group_names:
            group_name = group.actual_group if group.actual_group else group.name
            if group_name and group_name in obj.vertex_groups:
                group_names.append(group_name)
        
        if len(group_names) < 2:
            self.report({'WARNING'}, _("Please select at least two vertex groups"))
            return {'CANCELLED'}
        
        if self.operation == 'MERGE':
            self.merge_vertex_groups(obj, group_names)
        elif self.operation == 'EVEN_WEIGHT_TRANSFER':
            self.even_weight_transfer(context, obj, group_names)
        elif self.operation == 'WEIGHT_TRANSFER':
            if len(group_names) < 3:
                self.report({'WARNING'}, _("Bisect weight requires at least three vertex groups selected"))
                return {'CANCELLED'}
            self.weight_transfer(context, obj, group_names)
        
        return {'FINISHED'}
    
    def merge_vertex_groups(self, obj, group_names):
        target_group = obj.vertex_groups[group_names[0]]
        for group_name in group_names[1:]:
            group = obj.vertex_groups.get(group_name)
            if group:
                for vertex in obj.data.vertices:
                    try:
                        weight = group.weight(vertex.index)
                    except RuntimeError:
                        weight = 0.0
                    if weight > 0.0:
                        target_group.add([vertex.index], weight, 'ADD')
                obj.vertex_groups.remove(group)
        self.report({'INFO'}, _("Vertex group merge completed"))

    def even_weight_transfer(self, context, obj, group_names):
        middle_group_name = group_names[0]
        target_groups = group_names[1:]

        if middle_group_name in obj.vertex_groups and \
           all(group_name in obj.vertex_groups for group_name in target_groups):

            middle_group_index = obj.vertex_groups[middle_group_name].index
            target_group_indices = [obj.vertex_groups[group_name].index for group_name in target_groups]
            split_weight = 1.0 / len(target_groups)

            for vert in obj.data.vertices:
                for group in vert.groups:
                    if group.group == middle_group_index:
                        weight = group.weight * split_weight
                        obj.vertex_groups[middle_group_index].remove([vert.index])
                        for target_group_index in target_group_indices:
                            obj.vertex_groups[target_group_index].add([vert.index], weight, 'ADD')

            self.report({'INFO'}, _("Weight distribution completed"))
        else:
            self.report({'WARNING'}, _("One or more specified vertex groups do not exist"))

    # 辅助函数：Smoothstep
    def _smoothstep(self, edge0, edge1, x):
        if edge0 == edge1: # 处理边缘情况
            return 0.0 if x < edge0 else 1.0
        # Clamp x to be within the range [edge0, edge1]
        t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
        # Evaluate polynomial
        return t * t * (3.0 - 2.0 * t)

    def weight_transfer(self, context, obj, group_names):
        """根据当前分割模式调用对应的权重转移函数"""
        split_mode = context.scene.split_mode
        
        if split_mode == 'X_AXIS':
            self.weight_transfer_axis(context, obj, group_names, 'X')
        elif split_mode == 'Y_AXIS':
            self.weight_transfer_axis(context, obj, group_names, 'Y')
        elif split_mode == 'Z_AXIS':
            self.weight_transfer_axis(context, obj, group_names, 'Z')
        elif split_mode == 'CUSTOM' and context.scene.use_custom_split_line:
            self.weight_transfer_custom(context, obj, group_names)
        else:
            # 默认使用X轴
            self.weight_transfer_axis(context, obj, group_names, 'X')
    
    def weight_transfer_axis(self, context, obj, group_names, axis):
        """按指定轴向进行二分权重转移"""
        middle_group_name = group_names[0]
        left_group_name = group_names[1]  # 接收正侧的权重
        right_group_name = group_names[2] # 接收负侧的权重

        if middle_group_name in obj.vertex_groups and \
           left_group_name in obj.vertex_groups and \
           right_group_name in obj.vertex_groups:

            middle_group_index = obj.vertex_groups[middle_group_name].index
            left_group_index = obj.vertex_groups[left_group_name].index
            right_group_index = obj.vertex_groups[right_group_name].index

            # 获取混合因子
            blend_factor = context.scene.blend_factor

            # 收集受影响顶点及其信息
            vertices_to_process = [] # (vert_index, original_weight, position)
            positions = []
            
            # 根据轴向获取位置坐标
            for vert in obj.data.vertices:
                for group in vert.groups:
                    if group.group == middle_group_index and group.weight > 0.0001:
                        # 根据选择的轴向获取坐标
                        if axis == 'X':
                            pos = vert.co.x
                        elif axis == 'Y':
                            pos = vert.co.y
                        else:  # Z轴
                            pos = vert.co.z
                            
                        vertices_to_process.append((vert.index, group.weight, pos))
                        positions.append(pos)
                        break
            
            if not vertices_to_process:
                self.report({'INFO'}, _("No vertices found affected by the middle vertex group"))
                return
            
            # 计算中心线和混合区域
            min_pos = min(positions)
            max_pos = max(positions)
            center_line = sum(positions) / len(positions)
            
            # 如果所有点位置相同或混合因子为0，则等同于硬分割
            if max_pos == min_pos or blend_factor == 0.0:
                blend_start = center_line
                blend_end = center_line
            else:
                half_width = (max_pos - min_pos) * blend_factor * 0.5
                blend_start = center_line - half_width
                blend_end = center_line + half_width
                # 钳制混合区域在实际坐标范围内
                blend_start = max(min_pos, blend_start)
                blend_end = min(max_pos, blend_end)
                # 再次检查防止浮点误差导致 start > end
                if blend_start > blend_end:
                    blend_start = blend_end = center_line

            # 优化：一次性移除所有相关顶点在中间组的权重
            vert_indices_to_remove = [v[0] for v in vertices_to_process]
            obj.vertex_groups[middle_group_index].remove(vert_indices_to_remove)

            # 遍历并分配权重
            for vert_index, original_weight, position in vertices_to_process:
                # 计算平滑因子 (0 -> 1)
                s_factor = self._smoothstep(blend_start, blend_end, position)

                # 计算分配给左右组的权重
                weight_left = original_weight * s_factor
                weight_right = original_weight * (1.0 - s_factor)

                # 添加权重 (使用 ADD 是因为中间组权重已被移除)
                if weight_left > 0.0001: # 忽略极小的权重以保持稀疏性
                    obj.vertex_groups[left_group_index].add([vert_index], weight_left, 'ADD')
                if weight_right > 0.0001:
                    obj.vertex_groups[right_group_index].add([vert_index], weight_right, 'ADD')

            self.report({'INFO'}, f"{_('Bisect weight completed using')} {axis} {_('axis')} ({_('Blend Factor:')} {blend_factor:.2f})")
        else:
            self.report({'WARNING'}, _("One or more specified vertex groups do not exist"))
    
    def weight_transfer_custom(self, context, obj, group_names):
        """使用自定义分割线进行二分权重转移"""
        middle_group_name = group_names[0]
        left_group_name = group_names[1]  # 接收正侧的权重
        right_group_name = group_names[2] # 接收负侧的权重

        if middle_group_name in obj.vertex_groups and \
           left_group_name in obj.vertex_groups and \
           right_group_name in obj.vertex_groups:

            middle_group_index = obj.vertex_groups[middle_group_name].index
            left_group_index = obj.vertex_groups[left_group_name].index
            right_group_index = obj.vertex_groups[right_group_name].index

            # 获取混合因子
            blend_factor = context.scene.blend_factor
            
            # 获取分割线的起点和终点
            start_point = Vector(context.scene.split_line_start)
            end_point = Vector(context.scene.split_line_end)
            
            # 计算分割线的方向向量
            line_direction = (end_point - start_point).normalized()
            
            # 构建分割平面的法向量 (线的垂直方向)
            # 注意：在3D空间中，一条线的垂直方向有无数种，这里我们取一个合理的
            if abs(line_direction.z) < 0.9:  # 如果线不是接近垂直的
                plane_normal = Vector((line_direction.y, -line_direction.x, 0)).normalized()
            else:  # 如果线接近垂直，使用X轴作为参考
                plane_normal = Vector((1, 0, 0)) - line_direction * line_direction.x
                plane_normal.normalize()
            
            # 使用平面方程 ax + by + cz + d = 0 来计算顶点相对于平面的位置
            # 其中 (a,b,c) 是平面法向量，d 是平面常数
            plane_d = -start_point.dot(plane_normal)
            
            # 收集顶点并计算它们相对于分割平面的有符号距离
            vertices_to_process = [] # (vert_index, original_weight, distance)
            distances = []
            
            for vert in obj.data.vertices:
                for group in vert.groups:
                    if group.group == middle_group_index and group.weight > 0.0001:
                        # 计算顶点到平面的有符号距离
                        distance = vert.co.dot(plane_normal) + plane_d
                        vertices_to_process.append((vert.index, group.weight, distance))
                        distances.append(distance)
                        break
            
            # 如果没有影响顶点
            if not vertices_to_process:
                self.report({'INFO'}, _("No vertices found affected by the middle vertex group"))
                return
            
            # 计算距离的最大和最小值用于混合
            min_distance = min(distances)
            max_distance = max(distances)
            
            # 如果所有点在平面上或混合因子为0，则进行硬分割
            if min_distance == max_distance or blend_factor == 0.0:
                blend_start = 0
                blend_end = 0
            else:
                # 计算混合区域
                half_width = (max_distance - min_distance) * blend_factor * 0.5
                blend_start = -half_width
                blend_end = half_width

            # 一次性移除所有相关顶点在中间组的权重
            vert_indices_to_remove = [v[0] for v in vertices_to_process]
            obj.vertex_groups[middle_group_index].remove(vert_indices_to_remove)

            # 遍历并分配权重
            for vert_index, original_weight, distance in vertices_to_process:
                # 根据顶点到平面的距离计算混合因子
                s_factor = self._smoothstep(blend_start, blend_end, distance)

                # 计算分配给左右组的权重
                weight_left = original_weight * s_factor
                weight_right = original_weight * (1.0 - s_factor)

                # 添加权重
                if weight_left > 0.0001:
                    obj.vertex_groups[left_group_index].add([vert_index], weight_left, 'ADD')
                if weight_right > 0.0001:
                    obj.vertex_groups[right_group_index].add([vert_index], weight_right, 'ADD')

            self.report({'INFO'}, f"{_('Bisect weight completed using custom split line')} ({_('Blend Factor:')} {blend_factor:.2f})")
        else:
            self.report({'WARNING'}, _("One or more specified vertex groups do not exist"))

# 用于存储关联物体列表的属性类
class RelatedObjectItem(PropertyGroup):
    name: StringProperty()

# 添加L4D2_OT_DrawSplitLine模态操作符类
class L4D2_OT_DrawSplitLine(Operator):
    bl_idname = "l4d2.draw_split_line"
    bl_label = _("Draw Split Line")
    bl_description = _("Draw a split line in the 3D view for custom weight splitting direction")
    
    # 存储鼠标状态和操作阶段
    _state = 'NONE'  # 可能的状态: 'NONE', 'START', 'END'
    _mouse_pos = Vector((0, 0))
    _handler = None
    
    @staticmethod
    def draw_callback_px(self, context):
        """绘制临时分割线的回调函数"""
        import bpy
        import gpu
        from gpu_extras.batch import batch_for_shader
        
        # 获取分割线坐标
        if self._state == 'NONE':
            return
        elif self._state == 'START':
            # 当只有起点时，使用鼠标位置作为临时终点
            start = Vector(context.scene.split_line_start)
            
            # 将3D起点转换为屏幕空间
            region = context.region
            rv3d = context.region_data
            start_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, start)
            
            if start_2d:
                points = [start_2d, self._mouse_pos]
            else:
                return
        else:  # 'END'状态，显示完整分割线
            # 获取视图坐标的3D点
            start = Vector(context.scene.split_line_start)
            end = Vector(context.scene.split_line_end)
            
            # 将3D点转换为屏幕空间
            region = context.region
            rv3d = context.region_data
            start_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, start)
            end_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, end)
            
            if start_2d and end_2d:
                points = [start_2d, end_2d]
            else:
                return
        
        # 设置着色器
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": points})
        
        # 设置线条属性
        shader.bind()
        shader.uniform_float("color", (1, 0.2, 0.2, 1.0))  # 红色
        gpu.state.line_width_set(2.0)
        
        # 绘制线条
        batch.draw(shader)
    
    def invoke(self, context, event):
        # 检查是否在正确的上下文中
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, _("This tool must be used in the 3D View"))
            return {'CANCELLED'}
        
        # 重置状态
        self.__class__._state = 'NONE'
        context.scene.use_custom_split_line = False
        
        # 设置分割模式为自定义
        context.scene.split_mode = 'CUSTOM'
        
        # 设置模态处理器
        context.window_manager.modal_handler_add(self)
        
        # 添加绘制回调
        args = (self, context)
        self.__class__._handler = bpy.types.SpaceView3D.draw_handler_add(
            self.__class__.draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        
        # 提示用户
        self.report({'INFO'}, _("Click to set the start point, move, then click again to set the end point"))
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        # 始终更新鼠标位置用于绘制
        if event.type == 'MOUSEMOVE':
            self.__class__._mouse_pos = Vector((event.mouse_region_x, event.mouse_region_y))
            context.area.tag_redraw()
        
        # ESC键取消操作
        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            self.cleanup(context)
            self.report({'INFO'}, _("Cancelled drawing split line"))
            return {'CANCELLED'}
        
        # 左键点击设置点
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # 获取3D鼠标位置
            coord = (event.mouse_region_x, event.mouse_region_y)
            region = context.region
            rv3d = context.region_data
            
            # 射线投射获取3D位置
            view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            
            # 假设在中心深度平面上投射
            # 如果有活动对象，我们也可以使用物体的位置或射线与物体相交来确定深度
            if context.scene.target_mesh_object:
                obj = bpy.data.objects.get(context.scene.target_mesh_object)
                if obj:
                    # 使用目标对象的位置作为深度参考
                    hit, loc, norm, face = obj.ray_cast(ray_origin, view_vector)
                    point_3d = ray_origin + view_vector * ((obj.location - ray_origin).dot(Vector((0,0,1))) / view_vector.dot(Vector((0,0,1)))) if not hit else loc
                else:
                    # 深度不重要时，可以使用视图中心的深度
                    depth_factor = 5.0  # 任意深度因子
                    point_3d = ray_origin + view_vector * depth_factor
            else:
                # 深度不重要时，可以使用视图中心的深度
                depth_factor = 5.0  # 任意深度因子
                point_3d = ray_origin + view_vector * depth_factor
            
            if self.__class__._state == 'NONE':
                # 设置起点
                context.scene.split_line_start = point_3d
                self.__class__._state = 'START'
                self.report({'INFO'}, _("Start point set, move mouse and click again to set end point"))
            elif self.__class__._state == 'START':
                # 设置终点
                context.scene.split_line_end = point_3d
                self.__class__._state = 'END'
                
                # 启用自定义分割线
                context.scene.use_custom_split_line = True
                
                # 完成操作
                self.cleanup(context)
                self.report({'INFO'}, _("Split line set"))
                return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
    
    def cleanup(self, context):
        # 移除绘制回调
        if self.__class__._handler:
            bpy.types.SpaceView3D.draw_handler_remove(self.__class__._handler, 'WINDOW')
            self.__class__._handler = None
        
        # 标记区域重绘
        if context.area:
            context.area.tag_redraw()

# 添加L4D2_OT_SetSplitMode类
class L4D2_OT_SetSplitMode(Operator):
    bl_idname = "l4d2.set_split_mode"
    bl_label = _("Set Split Mode")
    bl_description = _("Set the splitting mode for bisect weight")
    
    mode: bpy.props.StringProperty()
    
    def execute(self, context):
        scene = context.scene
        
        # 设置分割模式
        scene.split_mode = self.mode
        
        # 如果选择自定义分割线模式，处理相关状态
        if self.mode == 'CUSTOM':
            # 如果尚未设置自定义分割线，启动绘制操作
            if not scene.use_custom_split_line:
                bpy.ops.l4d2.draw_split_line('INVOKE_DEFAULT')
        else:
            # 如果不是自定义模式，禁用自定义分割线
            scene.use_custom_split_line = False
            
        return {'FINISHED'}

class L4D2_OT_AddEmptyVertexGroup(Operator):
    bl_idname = "scene.add_empty_vertex_group"
    bl_label = _("Add from Vertex Groups")
    bl_description = _("Add an empty vertex group selector to the list")
    
    def execute(self, context):
        # 检查是否有目标物体
        if not context.scene.target_mesh_object:
            # 如果没有目标物体，调用物体选择对话框
            # 这里复用 SelectMeshObject 操作符的邏輯
            if hasattr(bpy.types.Scene, "related_objects"):
                context.scene.related_objects.clear()
            
            # 寻找合适的网格物体
            mesh_objects = [obj for obj in bpy.context.view_layer.objects 
                          if obj.type == 'MESH' and obj.vertex_groups]
            
            if not mesh_objects:
                self.report({'WARNING'}, _("No mesh objects with vertex groups found"))
                return {'CANCELLED'}
            
            # 将找到的物体添加到相关物体列表
            for obj in mesh_objects:
                item = context.scene.related_objects.add()
                item.name = obj.name
            
            # 调用选择物体操作符
            bpy.ops.wm.select_mesh_object('INVOKE_DEFAULT')
            return {'FINISHED'}
        
        # 如果有目标物体
        obj = bpy.data.objects.get(context.scene.target_mesh_object)
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, _("Target object is invalid or not a mesh object"))
            return {'CANCELLED'}
        
        # 检查是否有顶点组
        if len(obj.vertex_groups) == 0:
            self.report({'WARNING'}, _("Target object has no vertex groups"))
            return {'CANCELLED'}
        
        # 添加一个空的顶点组条目到列表
        group_item = context.scene.vertex_group_names.add()
        group_item.name = ""  # 初始名称为空
        group_item.actual_group = ""  # 初始顶点组为空
        
        return {'FINISHED'}

# 注册类列表
classes = [
    VertexGroupItem,
    RelatedObjectItem,
    L4D2_UL_VertexGroups,
    # L4D2_PT_WeightsPanel,
    L4D2_OT_AddFromSelectedBones,
    L4D2_OT_SelectMeshObject,
    L4D2_OT_SelectObjectItem,
    L4D2_OT_SetTargetMesh,
    L4D2_OT_ClearVertexGroups,
    L4D2_OT_RemoveVertexGroup,
    L4D2_OT_ProcessVertexGroups,
    L4D2_OT_DrawSplitLine,
    L4D2_OT_SetSplitMode,
    L4D2_OT_AddEmptyVertexGroup  # 添加新的操作器类
]

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            # 抑制重复注册的错误消息
            pass
    
    try:
        bpy.types.Scene.vertex_group_names = CollectionProperty(type=VertexGroupItem)
        bpy.types.Scene.active_vertex_group_index = bpy.props.IntProperty(default=0)
        bpy.types.Scene.target_mesh_object = StringProperty(
            name=_("Target Mesh Object"),
            description=_("Target mesh object for adding vertex groups")
        )
        bpy.types.Scene.related_objects = CollectionProperty(type=RelatedObjectItem)
        bpy.types.Scene.bl_VGE = bpy.props.BoolProperty(
            name=_("Vertex Group Editing"),
            description=_("Vertex Group Editing"),
            default=False
        )
        # 确认 blend_factor 属性已添加
        if not hasattr(bpy.types.Scene, 'blend_factor'): # 添加检查确保不重复添加
            bpy.types.Scene.blend_factor = bpy.props.FloatProperty(
                name=_("Blend Factor"),
                description=_("Smoothness of the transition area for bisect weight (0=Hard Split, 1=Max Smoothness)"),
                default=0.5,
                min=0.0,
                max=1.0
            )
            
        # 添加分割线属性
        if not hasattr(bpy.types.Scene, 'split_line_start'):
            bpy.types.Scene.split_line_start = FloatVectorProperty(
                name=_("Split Line Start"),
                description=_("Start point of the custom split line"),
                subtype='XYZ',
                size=3,
                default=(0, 0, 0)
            )
            
        if not hasattr(bpy.types.Scene, 'split_line_end'):
            bpy.types.Scene.split_line_end = FloatVectorProperty(
                name=_("Split Line End"),
                description=_("End point of the custom split line"),
                subtype='XYZ',
                size=3,
                default=(0, 0, 0)
            )
            
        if not hasattr(bpy.types.Scene, 'use_custom_split_line'):
            bpy.types.Scene.use_custom_split_line = BoolProperty(
                name=_("Use Custom Split Line"),
                description=_("When enabled, bisect weight uses the custom split line instead of an axis"),
                default=False
            )
            
        # 添加分割模式属性
        if not hasattr(bpy.types.Scene, 'split_mode'):
            bpy.types.Scene.split_mode = bpy.props.EnumProperty(
                name=_("Split Mode"),
                description=_("Select the axis or method for weight splitting"),
                items=[
                    ('X_AXIS', _("X Axis"), _("Split weights along the X axis"), 'AXIS_SIDE', 0),
                    ('Y_AXIS', _("Y Axis"), _("Split weights along the Y axis"), 'AXIS_FRONT', 1),
                    ('Z_AXIS', _("Z Axis"), _("Split weights along the Z axis"), 'AXIS_TOP', 2),
                    ('CUSTOM', _("Custom"), _("Use custom split line"), 'CURVE_PATH', 3),
                ],
                default='X_AXIS'
            )
    except Exception as e:
        # 抑制属性注册错误的消息
        print(f"Error registering scene properties: {e}") # 打印错误以便调试
        pass

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            # 抑制注销错误的消息
            pass

    try:
        del bpy.types.Scene.vertex_group_names
        del bpy.types.Scene.active_vertex_group_index
        del bpy.types.Scene.target_mesh_object
        del bpy.types.Scene.related_objects
        del bpy.types.Scene.bl_VGE
        # 确认 blend_factor 属性已删除
        if hasattr(bpy.types.Scene, 'blend_factor'): # 添加检查确保只删除存在的属性
             del bpy.types.Scene.blend_factor
             
        # 删除分割线属性
        if hasattr(bpy.types.Scene, 'split_line_start'):
            del bpy.types.Scene.split_line_start
            
        if hasattr(bpy.types.Scene, 'split_line_end'):
            del bpy.types.Scene.split_line_end
            
        if hasattr(bpy.types.Scene, 'use_custom_split_line'):
            del bpy.types.Scene.use_custom_split_line
            
        # 删除分割模式属性
        if hasattr(bpy.types.Scene, 'split_mode'):
            del bpy.types.Scene.split_mode
    except Exception as e:
        # 抑制删除属性错误的消息
        print(f"Error unregistering scene properties: {e}") # 打印错误以便调试
        pass

if __name__ == "__main__":
    register()