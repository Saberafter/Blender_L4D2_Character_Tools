import bpy
from bpy.props import StringProperty, CollectionProperty, PointerProperty, FloatProperty
from bpy.types import PropertyGroup, Operator, Panel, UIList

class VertexGroupItem(PropertyGroup):
    name: StringProperty(name="顶点组名称")

class L4D2_UL_VertexGroups(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
            remove_op = layout.operator("scene.remove_vertex_group", text="", icon="X")
            remove_op.index = data.vertex_group_names.values().index(item)

class L4D2_PT_WeightsPanel(Panel):
    bl_label = "权重编辑工具"
    bl_idname = "L4D2_PT_WeightsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 添加顶点组编辑的折叠开关
        layout.prop(scene, "bl_VGE", text="顶点组编辑", icon="TRIA_DOWN" if scene.bl_VGE else "TRIA_RIGHT")

        # 如果折叠开关打开，显示详细控制
        if scene.bl_VGE:
            # 显示当前目标物体
            if scene.target_mesh_object:
                obj = bpy.data.objects.get(scene.target_mesh_object)
                if obj:
                    row = layout.row()
                    row.label(text=f"目标物体: {obj.name}")
            
            # 添加从骨骼添加按钮
            row = layout.row(align=True)
            row.operator("scene.add_from_selected_bones", text="从选中骨骼添加", icon="BONE_DATA")
            row.operator("scene.clear_vertex_groups", text="重置", icon="FILE_REFRESH")
            
            # 显示已添加的顶点组列表
            layout.template_list("L4D2_UL_VertexGroups", "", scene, "vertex_group_names", scene, "active_vertex_group_index", rows=3)
            
            # 权重处理按钮
            if len(scene.vertex_group_names) > 0:
                # 将两个按钮分开为两列
                row1 = layout.row()
                row1.operator("l4d2.process_vertex_groups", text="合并顶点组").operation = 'MERGE'
                row2 = layout.row()
                row2.operator("l4d2.process_vertex_groups", text="均分权重").operation = 'EVEN_WEIGHT_TRANSFER'

                # 如果顶点组数量足够显示二分权重选项
                if len(scene.vertex_group_names) >= 3:
                    # 添加混合因子滑块和二分权重按钮在同一行
                    row = layout.row(align=True)
                    row.operator("l4d2.process_vertex_groups", text="二分权重").operation = 'WEIGHT_TRANSFER'
                    row.prop(scene, "blend_factor")
            else:
                layout.label(text="请先添加顶点组")

class L4D2_OT_AddFromSelectedBones(Operator):
    bl_idname = "scene.add_from_selected_bones"
    bl_label = "从选中骨骼添加"
    bl_description = "从姿势模式下选中的骨骼自动添加对应的顶点组"
    
    def execute(self, context):
        # 检查是否在pose mode
        if not (context.active_object and context.active_object.type == 'ARMATURE' 
                and context.active_object.mode == 'POSE'):
            self.report({'WARNING'}, "请在姿势模式下选择骨骼")
            return {'CANCELLED'}
            
        # 获取选中的骨骼
        armature = context.active_object
        selected_bones = [bone.name for bone in armature.pose.bones if bone.bone.select]
        if not selected_bones:
            self.report({'WARNING'}, "未选择任何骨骼")
            return {'CANCELLED'}
        
        # 获取关联的网格物体
        related_objects = self.get_related_mesh_objects(armature)
        if not related_objects:
            self.report({'WARNING'}, "未找到与骨架关联的网格物体")
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
                if not any(group.name == bone_name for group in context.scene.vertex_group_names):
                    group_item = context.scene.vertex_group_names.add()
                    group_item.name = bone_name
                    added += 1
            else:
                not_found += 1
        
        if added > 0:
            self.report({'INFO'}, f"已添加{added}个顶点组")
        if not_found > 0:
            self.report({'WARNING'}, f"{not_found}个骨骼名称在顶点组中不存在")
    
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
    bl_label = "选择目标物体"
    
    # 存储用户选择的物体名称
    selected_object: StringProperty(default="")
    
    def invoke(self, context, event):
        # 使用invoke_props_dialog而不是invoke_popup以获得确认按钮
        # 存储引用到全局变量，以便子操作符能够访问
        bpy.types.Scene.current_select_dialog = self
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="选择要处理的目标物体:")
        
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
            
            # 添加顶点组
            armature = context.active_object
            if armature and armature.type == 'ARMATURE' and armature.mode == 'POSE':
                selected_bones = [bone.name for bone in armature.pose.bones if bone.bone.select]
                mesh_obj = bpy.data.objects.get(self.selected_object)
                if mesh_obj and selected_bones:
                    self.add_vertex_groups_from_bones(context, mesh_obj, selected_bones)
        
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
                if not any(group.name == bone_name for group in context.scene.vertex_group_names):
                    group_item = context.scene.vertex_group_names.add()
                    group_item.name = bone_name
                    added += 1
            else:
                not_found += 1
        
        if added > 0:
            self.report({'INFO'}, f"已添加{added}个顶点组")
        if not_found > 0:
            self.report({'WARNING'}, f"{not_found}个骨骼名称在顶点组中不存在")

class L4D2_OT_SelectObjectItem(Operator):
    bl_idname = "wm.select_object_item"
    bl_label = "选择物体项"
    
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
    bl_label = "设置目标物体"
    
    object_name: StringProperty()
    
    def execute(self, context):
        # 只设置目标物体，不添加顶点组
        context.scene.target_mesh_object = self.object_name
        return {'FINISHED'}

class L4D2_OT_ClearVertexGroups(Operator):
    bl_idname = "scene.clear_vertex_groups"
    bl_label = "清空顶点组列表"
    bl_description = "清空当前的顶点组列表并重置目标物体选择，便于切换到新的骨架和物体"
    
    def execute(self, context):
        # 清空顶点组列表
        context.scene.vertex_group_names.clear()
        # 清空目标物体选择
        context.scene.target_mesh_object = ""
        self.report({'INFO'}, "已清空顶点组列表和目标物体选择")
        return {'FINISHED'}

class L4D2_OT_RemoveVertexGroup(Operator):
    bl_idname = "scene.remove_vertex_group"
    bl_label = "移除顶点组"
    bl_description = "从列表中移除此顶点组"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        context.scene.vertex_group_names.remove(self.index)
        return {'FINISHED'}

class L4D2_OT_ProcessVertexGroups(Operator):
    bl_idname = "l4d2.process_vertex_groups"
    bl_label = "处理顶点组"
    bl_description = "合并: 合并后续组权重到首个组。\n均分: 均分首个组权重给后续组。\n二分: 按X坐标平滑分配首组权重给第2、3组 (受混合因子影响)。"
    
    operation: bpy.props.StringProperty()
    
    def execute(self, context):
        scene = context.scene
        if not scene.target_mesh_object:
            self.report({'WARNING'}, "未设置目标物体")
            return {'CANCELLED'}
            
        obj = bpy.data.objects.get(scene.target_mesh_object)
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "目标物体无效或不是网格物体")
            return {'CANCELLED'}
        
        group_names = [group.name for group in scene.vertex_group_names if group.name]
        
        if len(group_names) < 2:
            self.report({'WARNING'}, "请至少选择两个顶点组")
            return {'CANCELLED'}
        
        if self.operation == 'MERGE':
            self.merge_vertex_groups(obj, group_names)
        elif self.operation == 'EVEN_WEIGHT_TRANSFER':
            self.even_weight_transfer(context, obj, group_names)
        elif self.operation == 'WEIGHT_TRANSFER':
            if len(group_names) < 3:
                self.report({'WARNING'}, "二分权重需要至少选择三个顶点组")
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
        self.report({'INFO'}, "顶点组合并完成")

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

            self.report({'INFO'}, "权重均匀分配完成")
        else:
            self.report({'WARNING'}, "一个或多个指定的顶点组不存在")

    def weight_transfer(self, context, obj, group_names):
        # 辅助函数：Smoothstep
        def _smoothstep(edge0, edge1, x):
            if edge0 == edge1: # 处理边缘情况
                return 0.0 if x < edge0 else 1.0
            # Clamp x to be within the range [edge0, edge1]
            t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
            # Evaluate polynomial
            return t * t * (3.0 - 2.0 * t)

        middle_group_name = group_names[0]
        left_group_name = group_names[1]  # 接收 X >= center 的权重 (blend factor = 1)
        right_group_name = group_names[2] # 接收 X < center 的权重 (blend factor = 0)

        if middle_group_name in obj.vertex_groups and \
           left_group_name in obj.vertex_groups and \
           right_group_name in obj.vertex_groups:

            middle_group_index = obj.vertex_groups[middle_group_name].index
            left_group_index = obj.vertex_groups[left_group_name].index
            right_group_index = obj.vertex_groups[right_group_name].index

            # 获取混合因子 - 从场景属性读取
            blend_factor = context.scene.blend_factor

            # 收集受影响顶点及其信息
            vertices_to_process = [] # (vert_index, original_weight)
            x_coords = []
            for vert in obj.data.vertices:
                for group in vert.groups:
                    if group.group == middle_group_index and group.weight > 0.0001: # 忽略极小权重
                        vertices_to_process.append((vert.index, group.weight))
                        x_coords.append(vert.co.x)
                        break # 每个顶点只处理一次

            if not vertices_to_process:
                self.report({'INFO'}, "没有找到中间顶点组影响的顶点")
                return

            # 计算中心线和混合区域
            min_x = min(x_coords)
            max_x = max(x_coords)
            center_line = sum(x_coords) / len(x_coords)

            # 如果所有点 X 坐标相同或 blend_factor 为 0，则等同于硬分割
            if max_x == min_x or blend_factor == 0.0:
                blend_start = center_line
                blend_end = center_line
            else:
                half_width = (max_x - min_x) * blend_factor * 0.5
                blend_start = center_line - half_width
                blend_end = center_line + half_width
                # 钳制混合区域在实际坐标范围内
                blend_start = max(min_x, blend_start)
                blend_end = min(max_x, blend_end)
                # 再次检查防止浮点误差导致 start > end
                if blend_start > blend_end:
                    blend_start = blend_end = center_line

            # --- 权重转移 --- 
            # 优化：一次性移除所有相关顶点在中间组的权重
            vert_indices_to_remove = [v[0] for v in vertices_to_process]
            obj.vertex_groups[middle_group_index].remove(vert_indices_to_remove)

            # 遍历并分配权重
            for vert_index, original_weight in vertices_to_process:
                vert_co_x = obj.data.vertices[vert_index].co.x

                # 计算平滑因子 (0 -> 1)
                s_factor = _smoothstep(blend_start, blend_end, vert_co_x)

                # 计算分配给左右组的权重
                weight_left = original_weight * s_factor
                weight_right = original_weight * (1.0 - s_factor)

                # 添加权重 (使用 ADD 是因为中间组权重已被移除)
                if weight_left > 0.0001: # 忽略极小的权重以保持稀疏性
                    obj.vertex_groups[left_group_index].add([vert_index], weight_left, 'ADD')
                if weight_right > 0.0001:
                    obj.vertex_groups[right_group_index].add([vert_index], weight_right, 'ADD')
            # --- 结束权重转移 ---

            self.report({'INFO'}, f"权重二分完成 (混合因子: {blend_factor:.2f})")
        else:
            self.report({'WARNING'}, "一个或多个指定的顶点组不存在")

# 用于存储关联物体列表的属性类
class RelatedObjectItem(PropertyGroup):
    name: StringProperty()

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
    L4D2_OT_ProcessVertexGroups
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
            name="目标网格物体",
            description="用于添加顶点组的目标网格物体"
        )
        bpy.types.Scene.related_objects = CollectionProperty(type=RelatedObjectItem)
        bpy.types.Scene.bl_VGE = bpy.props.BoolProperty(
            name="顶点组编辑",
            description="顶点组编辑",
            default=False
        )
        # 确认 blend_factor 属性已添加
        if not hasattr(bpy.types.Scene, 'blend_factor'): # 添加检查确保不重复添加
            bpy.types.Scene.blend_factor = bpy.props.FloatProperty(
                name="混合因子",
                description="二分权重时过渡区域的平滑度 (0=硬分割, 1=最大平滑)",
                default=0.5,
                min=0.0,
                max=1.0
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
    except Exception as e:
        # 抑制删除属性错误的消息
        print(f"Error unregistering scene properties: {e}") # 打印错误以便调试
        pass

if __name__ == "__main__":
    register()