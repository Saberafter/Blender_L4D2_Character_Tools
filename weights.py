import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.types import PropertyGroup

class VertexGroupItem(PropertyGroup):
    name: StringProperty(name="顶点组名称")

class L4D2_PT_WeightsPanel(bpy.types.Panel):
    bl_label = "WeightsPanel"
    bl_idname = "L4D2_PT_WeightsPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "💝LCT"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 添加一个可以展开/折叠的UI部分的开关
        layout.prop(scene, "bl_VGE", text="Vertex Group Editing", icon="TRIA_DOWN" if scene.bl_VGE else "TRIA_RIGHT")

        # 如果 bl_is_detailed 为 True，渲染详细控制的UI
        if scene.bl_VGE:
            row = layout.row()
            # 合并和权重转移按钮
            row.operator("scene.add_vertex_group", text="", icon="ADD")
            row.operator("l4d2.process_vertex_groups", text="Merge vertex groups").operation = 'MERGE'
            row.operator("l4d2.process_vertex_groups", text="Even weight").operation = 'EVEN_WEIGHT_TRANSFER'
            row.operator("l4d2.process_vertex_groups", text="Bisect weight").operation = 'WEIGHT_TRANSFER'
            col = layout.column()
            
            # 创建顶点组列表
            for idx, group in enumerate(scene.vertex_group_names):
                row = col.row()
                row.prop_search(group, "name", context.active_object, "vertex_groups", text="")
                remove_op = row.operator("scene.remove_vertex_group", text="", icon="X")
                remove_op.index = idx

class L4D2_OT_AddVertexGroup(bpy.types.Operator):
<<<<<<< HEAD
    bl_idname = "scene.add_vertex_group"
    bl_label = "Add Vertex Group"
    bl_description = "Add a vertex group field to select the vertex group to be processed by the current model"
=======
    """Add a vertex group field to select the vertex group to be processed by the current model"""
    bl_idname = "scene.add_vertex_group"
    bl_label = "Add Vertex Group"
>>>>>>> 10981a70a90fd60c3b37a4cb29ddded12650e790

    def execute(self, context):
        context.scene.vertex_group_names.add()
        return {'FINISHED'}

class L4D2_OT_RemoveVertexGroup(bpy.types.Operator):
<<<<<<< HEAD
    bl_idname = "scene.remove_vertex_group"
    bl_label = "Remove Vertex Group"
    bl_description = "Remove this vertex group field"

=======
    """Remove this vertex group field"""
    bl_idname = "scene.remove_vertex_group"
    bl_label = "Remove Vertex Group"
    
>>>>>>> 10981a70a90fd60c3b37a4cb29ddded12650e790
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.vertex_group_names.remove(self.index)
        return {'FINISHED'}

class L4D2_OT_ProcessVertexGroups(bpy.types.Operator):
<<<<<<< HEAD
    bl_idname = "l4d2.process_vertex_groups"
    bl_label = "Process Vertex Group"
    bl_description = "The following functions are performed only on the vertex groups within the columns created with the + button:\nMerge vertex groups: Merge the weights of the vertex groups after the first column into the first column vertex group and delete these vertex groups(careful).\nEven weight: Evenly distribute the weights of the first column vertex group to the other column vertex groups.\nBisect weight: Using the X-pos of the vertices in the first column vertex group as a reference, divide the weights to the left and right. Assign the weights of the left half to the vertex group in the second column, and the weights of the right half to the vertex group in the third column"
=======
    """The following functions are performed only on the vertex groups within the columns created with the + button:\nMerge vertex groups: Merge the weights of the vertex groups after the first column into the first column vertex group and delete these vertex groups(careful).\nEven weight: Evenly distribute the weights of the first column vertex group to the other column vertex groups.\nBisect weight: Using the X-pos of the vertices in the first column vertex group as a reference, divide the weights to the left and right. Assign the weights of the left half to the vertex group in the second column, and the weights of the right half to the vertex group in the third column"""
    bl_idname = "l4d2.process_vertex_groups"
    bl_label = "Process Vertex Group"
>>>>>>> 10981a70a90fd60c3b37a4cb29ddded12650e790

    operation: bpy.props.StringProperty()  # 添加操作类型属性

    def execute(self, context):
        obj = context.active_object
        group_names = [group.name for group in context.scene.vertex_group_names if group.name]

        if len(group_names) < 2:
            self.report({'WARNING'}, "请至少选择两个顶点组")
            return {'CANCELLED'}

        if self.operation == 'MERGE':
            self.merge_vertex_groups(obj, group_names)
        elif self.operation == 'EVEN_WEIGHT_TRANSFER':
            self.even_weight_transfer(context, obj, group_names)
        elif self.operation == 'WEIGHT_TRANSFER':
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

    def even_weight_transfer(self, context, obj, group_names):
        if len(group_names) < 2:
            self.report({'WARNING'}, "请至少选择两个顶点组")
            return

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
        if len(group_names) < 3:
            self.report({'WARNING'}, "需要至少选择三个顶点组")
            return

        middle_group_name = group_names[0]
        left_group_name = group_names[1]
        right_group_name = group_names[2]

        if middle_group_name in obj.vertex_groups and \
           left_group_name in obj.vertex_groups and \
           right_group_name in obj.vertex_groups:
            
            middle_group_index = obj.vertex_groups[middle_group_name].index
            left_group_index = obj.vertex_groups[left_group_name].index
            right_group_index = obj.vertex_groups[right_group_name].index
            
            x_coords = [obj.data.vertices[vert.index].co.x for vert in obj.data.vertices for group in vert.groups if group.group == middle_group_index]
            if len(x_coords) == 0:
                self.report({'INFO'}, "没有找到中间顶点组的顶点")
                return

            center_line = sum(x_coords) / len(x_coords)

            for vert in obj.data.vertices:
                for group in vert.groups:
                    if group.group == middle_group_index:
                        weight = group.weight / 2
                        obj.vertex_groups[middle_group_index].remove([vert.index])
                        if obj.data.vertices[vert.index].co.x < center_line:
                            obj.vertex_groups[right_group_index].add([vert.index], weight, 'ADD')
                        else:
                            obj.vertex_groups[left_group_index].add([vert.index], weight, 'ADD')
        else:
            self.report({'WARNING'}, "一个或多个指定的顶点组不存在")


classes = [
    VertexGroupItem,
    L4D2_OT_AddVertexGroup,
    L4D2_OT_RemoveVertexGroup,
    L4D2_OT_ProcessVertexGroups,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.vertex_group_names = CollectionProperty(type=VertexGroupItem)
    bpy.types.Scene.bl_VGE = bpy.props.BoolProperty(
        name="Vertex Group Editing",
<<<<<<< HEAD
        description="Vertex Group Editing",
=======
        description="Toggle the visibility of detailed settings",
>>>>>>> 10981a70a90fd60c3b37a4cb29ddded12650e790
        default=False
    )
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.vertex_group_names

if __name__ == "__main__":
    register()