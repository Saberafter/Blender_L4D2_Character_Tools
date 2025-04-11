# Copyright C <2024> <Merami>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# at your option any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-

data = {
        # Preferences
        "View3D > Tool Shelf > 💝LCT": "3D视图 > 侧栏 > 💝LCT",
        "A plugin designed to enhance the efficiency of creating Left 4 Dead 2 character mods.": "这是一个旨在提升求生之路2人物Mod制作效率的插件。",
        
        # 🛠️ Bone Tools
        "Valve Rig:": "官方骨架:",
        "Custom Rig:": "自定义骨架:",

        "Align Bone": "对齐骨骼",
        "Align bones by batch adding copy location constrains to the bones\nThe mechanism of bone alignment is based on the mapping dictionary\n1、Ensure the TPOSE is approximately consistent\n2、Make sure the name of the skeleton is the same as the name of the first level under the skeleton": "通过批量添加复制位置的骨骼约束来对骨\n对骨匹配机制来源于映射字典\n1、确保TPOSE近似一致\n2、确保骨架名和骨架下第一个层级名字一样",

        # RiggingConfirmOperator translations
        "Confirm Bone Alignment": "确认对骨操作",
        "Confirm current mapping data and execute bone alignment operation": "确认当前映射数据并执行对骨操作",
        "Filter": "过滤",
        "Filter by bone name": "按骨骼名称过滤",
        "Current Preset": "当前预设",
        "Data Source": "数据来源",
        "Preset File": "预设文件",
        "Memory Data": "内存数据",
        "Official Armature": "官方骨架",
        "Custom Armature": "自定义骨架",
        "Total Mappings": "总映射数",
        "Bone Mapping and Axis Control": "骨骼映射及轴控制",
        "Official Bone": "官方骨骼",
        "Custom Bone": "自定义骨骼",
        "Axis Control": "轴控制",
        "Please adjust axis control settings and confirm to execute bone alignment": "请调整轴控制设置并确认后执行对骨操作",
        "Failed to parse mapping data": "解析映射数据失败",
        "Could not find armature objects": "无法找到骨架对象",
        "Alignment completed, added": "对骨完成，共添加了",
        "bone constraints": "个骨骼约束",

        # RiggingConfirmItem translations
        "Official bone name": "官方骨骼名称",
        "Corresponding custom bone name": "对应的自定义骨骼名称",
        "Use X axis constraint": "使用X轴约束",
        "Use Y axis constraint": "使用Y轴约束",
        "Use Z axis constraint": "使用Z轴约束",

        # GraftingConfirmOperator translations
        "Confirm Grafting Operation": "确认嫁接操作",
        "Confirm current mapping data and execute bone grafting operation": "确认当前映射数据并执行骨骼嫁接操作",
        "Preview Mode": "预览模式",
        "Selected Bones": "选中骨骼",
        "Only display grafting relationships for selected bones": "仅显示选中骨骼的嫁接关系",
        "All Bones": "所有骨骼",
        "Display grafting relationships for all bones": "显示所有骨骼的嫁接关系",
        "Target Armature": "目标骨架",
        "Official Mapping Bones": "官方映射骨骼数",
        "Common Mapping Bones": "通用映射骨骼数",
        "Unique Mapping Bones": "独立映射骨骼数",
        "Selected Bones Count": "已选中骨骼数",
        "Grafting Mapping Relationships": "嫁接映射关系",
        "Total": "共",
        "Parent Bone": "父骨骼",
        "Child Bone": "子骨骼",
        "Processing Flow": "处理流程",
        "Process": "处理",
        "selected non-official bones": "个选中的非官方骨骼",
        "Process all non-official bones": "处理所有非官方骨骼",
        "Set parent-child relationships based on the above mappings": "根据上述映射设置父子关系",
        "Please confirm the above information and click OK to execute bone grafting operation": "请确认以上信息无误后点击确定执行骨骼嫁接操作",
        "Armature object not found or not an armature type": "未找到骨架对象或不是骨架类型",
        "No bone mapping relationships found that match the criteria": "未找到任何符合条件的骨骼映射关系",
        "Armature object not found": "未找到骨架对象",
        "Processed": "已处理",
        "selected bones": "个选中骨骼",
        "bones": "个骨骼",
        "Bone grafting completed": "骨骼嫁接完成",
        "No suitable bones found for grafting, please check bone positions and mapping relationships": "未找到合适的骨骼进行嫁接，请检查骨骼位置和映射关系",

        "Graft Bone": "嫁接骨骼",
        "Automatically set the parent-child level of bones based on bone mapping relationships": "根据骨骼映射关系自动设置骨骼的父子级",
        # GraftingOperator translations
        "Failed to load mapping data": "映射数据加载失败",
        "Armature object not selected or selected object is not an armature type": "未选中骨架对象或选中的不是骨架类型",
        "No available bone mapping relationships, grafting may be incomplete": "没有可用的骨骼映射关系，嫁接可能不完整",
        "Failed to serialize mapping data": "序列化映射数据失败",


        "Rename Bone": "重命名骨骼",
        "Rename custom bone names to Valve bone names based on bone mapping relationships": "根据骨骼映射关系把自定义骨骼名字重命名为Valve官方骨骼名字",

        
        # RenameBonesOperator translations
        "Target Name": "目标名称",
        "The new name to rename the bone to": "将骨骼重命名为的新名称",
        "Current Name": "当前名称",
        "The current bone name to be renamed": "将被重命名的当前骨骼名称",
        "Source": "来源",
        "Source of the mapping relationship": "映射关系的来源",
        "Confirm Bone Renaming": "确认骨骼重命名",
        "Renaming Mapping Relationships": "重命名映射关系",
        "Operation Process:": "操作流程：",
        "Load mapping relationships": "加载映射关系",
        "Match custom bones to official bones": "匹配自定义骨骼到官方骨骼",
        "Rename custom bones to official names": "将自定义骨骼重命名为官方名称",
        "No bone mapping relationships found that match the current armature": "未找到与当前骨架匹配的骨骼映射关系",
        "Failed to parse mapping data": "解析映射数据失败",
        "Renamed": "已重命名",
        "bones successfully": "个骨骼成功",
        "No bones were renamed, please check the mapping relationships": "没有骨骼被重命名，请检查映射关系",

        "Unbind Preserve Shape": "骨骼断绑保形",
        "Maintain shape and transformation when breaking bone parent-child relationships": "在断开骨骼父子关系时保持其形状和变换",

        # New translations from bone_modify.py
        "Failed to load mapping data": "映射数据加载失败",
        "Please select the official and custom armatures first": "请先选择官方骨架和自定义骨架",
        "Custom Bones": "自定义骨骼",
        "No custom bones": "没有自定义骨骼",
        "Select preferred bone:": "选择首选骨骼:",
        "Add new bone mapping relationship": "添加新的骨骼映射关系",
        "Apply changes in the current UI list to the preset file": "将当前UI列表的更改应用到预设文件",
        "Set the selected bone as preferred": "将选中的骨骼设为首选项",
        "Add a new custom bone": "添加新的自定义骨骼",
        "Bone Name": "骨骼名称",
        "Select from Armature": "从骨架中选择",
        "Manual Input": "手动输入",
        "Add Mode": "添加模式",
        "Bone": "骨骼",
        "Please select an armature": "请选择一个骨架",
        "Bone name cannot be empty!": "骨骼名称不能为空!",
        "Bone": "骨骼",
        "already exists!": "已存在!",
        "Remove the preferred custom bone": "删除首选的自定义骨骼",
        "Remove the current mapping entry": "删除当前映射条目",
        "Error when deleting UI list entry": "删除UI列表条目时发生错误",
        "Failed to delete mapping data": "删除映射数据失败",
        "No correct bones selected or not in pose mode": "没有选择正确的骨骼或者不在姿态模式",
        "Official bone name (parent)": "官方骨骼名称(父)",
        "Custom bone name (child)": "自定义骨骼名称(子)",
        "Whether the bone is selected": "是否被选中",
        "Official bone name": "官方骨骼名称",
        "Common bone name": "通用骨骼名称",
        "Custom bones list": "自定义骨骼列表",
        "Index of the preferred bone in the list": "首选骨骼在列表中的索引",
        "Source tab of the mapping": "映射的来源标签页",
        "Use X axis constraint": "使用X轴约束",
        "Use Y axis constraint": "使用Y轴约束",
        "Use Z axis constraint": "使用Z轴约束",

        "Remove Bone Constraint": "移除骨骼约束",
        "Bulk Remove Constraints from Selected Bones": "批量移除所选骨骼的约束",
        "Remove All Constraint": "移除骨骼约束",
        "Cancel Y RotationConstraint": "取消Y轴旋转约束",
        "Remove TransformConstraint": "移除变换约束",

        "Bone Mapping Management": "骨骼映射管理",
        "Valve BoneList": "官方骨骼列表",
        "Custom BoneList": "自定义骨列表",
        "Bone Name": "骨骼名",
        "Add Bone": "添加骨骼",
        "Automatically remove symbols and convert to lowercase": "自动去掉符号转化为小写",
        "Remove Bone": "移除骨骼",
        "Remove selected bone names from the custom bone list": "从自定义骨列表中移除选定的骨骼名",
        "Dictionary Key": "字典键",
        "Select the key in the dictionary": "选择字典中的键",
        "Bone Name": "骨骼名称",
        "Select the bone name in the current skeleton": "选择当前骨架中的骨骼名称",
        "Dictionary Value": "字典值",
        "Display all values for the selected dictionary key": "显示所选字典键的所有值",

        # 添加新的顶点组相关翻译
        "Add from Vertex Groups": "从顶点组添加",
        "Add an empty vertex group selector to the list": "添加一个空的顶点组选择器到列表",
        "No mesh objects with vertex groups found": "未找到包含顶点组的网格物体",
        "Target object has no vertex groups": "目标物体没有顶点组",
        "The name of the vertex group": "顶点组的名称",
        "Actual Vertex Group": "实际顶点组",
        "The actual selected vertex group": "实际选中的顶点组",

        # New translations from bone_modify.py function calls
        "Failed to load preset data": "无法加载预设数据",
        "Preset": "预设",
        "already exists!": "已存在!",
        "created successfully!": "创建成功!",
        "Failed to create preset": "创建预设失败",
        "does not exist!": "不存在!",
        "has been deleted!": "已删除!",
        "Failed to delete preset": "删除预设失败",
        "Failed to load preset": "加载预设失败",
        "Failed to update UI list": "更新UI列表失败",
        "loaded successfully!": "加载成功!",
        "loaded": "已加载",
        "Selected file does not exist!": "选择的文件不存在!",
        "Invalid preset file format!": "无效的预设文件格式!",
        "imported successfully!": "导入成功!",
        "Failed to import preset": "导入预设失败",
        "exported successfully!": "导出成功!",
        "Failed to export preset": "导出预设失败",
        "Invalid bone index!": "无效的骨骼索引!",
        "Mapping changes applied and saved to preset": "映射更改已应用并保存到预设",
        "Mapping changes applied but failed to save to preset": "映射更改已应用，但保存到预设失败",
        "Failed to serialize mapping data": "序列化映射数据失败",

        # Additional translations for missed items
        "Select preset and apply": "选择预设并应用",
        "Preset": "预设",
        "Select preset to use": "选择要使用的预设",
        "None": "无", 
        "Active Preset": "活动预设",
        "Current active preset": "当前活动的预设",
        
        # Additional error messages
        "Failed to save UI list to temp_data": "保存UI列表到temp_data失败",
        "Failed to get temp_data": "获取temp_data失败",
        "Failed to delete custom bone": "删除自定义骨骼失败",

        # Additional missing translations
        "All Mappings": "全部映射",
        "Unique Mappings": "独立映射",
        "Common Mappings": "通用映射",
        "Axis Control": "轴控制",

        
        # weights.py UI Elements
        "Weight Editing Tools": "权重编辑工具",
        "Vertex Group Editing": "顶点组编辑", # Also used as BoolProperty name/desc
        "Target Object:": "目标物体:",
        "Add from Selected Bones": "从选中骨骼添加", # Also used as Operator label
        "Reset": "重置",
        "Merge Vertex Groups": "合并顶点组",
        "Even Weight Transfer": "均分权重",
        "Split Mode:": "分割模式:",
        "X Axis": "X轴", # Also used in EnumProperty item
        "Y Axis": "Y轴", # Also used in EnumProperty item
        "Z Axis": "Z轴", # Also used in EnumProperty item
        "Custom": "自定义", # Also used in EnumProperty item
        "Please draw the split line first": "请先绘制分割线",
        "Execute Bisect Weight": "执行二分权重",
        "Please add vertex groups first": "请先添加顶点组",
        "Select Target Object": "选择目标物体",
        "Select the target object to process:": "选择要处理的目标物体:",
        "Select Object Item": "选择物体项",
        "Set Target Object": "设置目标物体",
        "Clear Vertex Group List": "清空顶点组列表",
        "Clear the current vertex group list and reset target object selection for switching to new armatures and objects": "清空当前的顶点组列表并重置目标物体选择，便于切换到新的骨架和物体",
        "Vertex group list and target object selection cleared": "已清空顶点组列表和目标物体选择",
        "Remove Vertex Group": "移除顶点组", # Also used as Operator label
        "Remove this vertex group from the list": "从列表中移除此顶点组",
        "Process Vertex Groups": "处理顶点组",
        "Merge: Merge weights of subsequent groups into the first group.\nEven: Evenly distribute weights of the first group to subsequent groups.\nBisect: Distribute the first group's weight to the 2nd and 3rd groups based on the selected axis or custom line.": "合并: 合并后续组权重到首个组。\n均分: 均分首个组权重给后续组。\n二分: 根据选择的方向或自定义线分配首组权重给第2、3组。",
        "Target object not set": "未设置目标物体",
        "Target object is invalid or not a mesh object": "目标物体无效或不是网格物体",
        "Please select at least two vertex groups": "请至少选择两个顶点组",
        "Bisect weight requires at least three vertex groups selected": "二分权重需要至少选择三个顶点组",
        "Vertex group merge completed": "顶点组合并完成",
        "Weight distribution completed": "权重均匀分配完成",
        "One or more specified vertex groups do not exist": "一个或多个指定的顶点组不存在",
        "No vertices found affected by the middle vertex group": "没有找到中间顶点组影响的顶点",
        "Bisect weight completed using": "使用", # Part of f-string
        "axis": "轴完成二分权重", # Part of f-string
        "Blend Factor:": "混合因子:", # Part of f-string, also FloatProperty name
        "Bisect weight completed using custom split line": "使用自定义分割线完成二分权重", # Part of f-string
        "Draw Split Line": "绘制分割线",
        "Draw a split line in the 3D view for custom weight splitting direction": "在3D视图中绘制分割线，用于自定义权重分割方向",
        "This tool must be used in the 3D View": "必须在3D视图中使用此工具",
        "Click to set the start point, move, then click again to set the end point": "单击设置分割线起点，移动后再次单击设置终点",
        "Cancelled drawing split line": "取消绘制分割线",
        "Start point set, move mouse and click again to set end point": "起点已设置，移动鼠标并再次单击设置终点",
        "Split line set": "分割线已设置",
        "Set Split Mode": "设置分割模式",
        "Set the splitting mode for bisect weight": "设置二分权重的分割模式",

        # weights.py Operator Labels/Descriptions
        "Automatically add corresponding vertex groups from bones selected in pose mode": "从姿势模式下选中的骨骼自动添加对应的顶点组",
        "Please select bones in Pose Mode": "请在姿势模式下选择骨骼",
        "No bones selected": "未选择任何骨骼",
        "Could not find mesh objects associated with the armature": "未找到与骨架关联的网格物体",
        "Added": "已添加", # Part of f-string
        "vertex groups": "个顶点组", # Part of f-string
        "bone names do not exist in vertex groups": "个骨骼名称在顶点组中不存在", # Part of f-string

        # weights.py Property Names/Descriptions
        "Vertex Group Name": "顶点组名称",
        "Target Mesh Object": "目标网格物体",
        "Target mesh object for adding vertex groups": "用于添加顶点组的目标网格物体",
        
        # "Vertex Group Editing": "顶点组编辑", # Defined above
        "Smoothness of the transition area for bisect weight (0=Hard Split, 1=Max Smoothness)": "二分权重时过渡区域的平滑度 (0=硬分割, 1=最大平滑)",
        "Split Line Start": "分割线起点",
        "Start point of the custom split line": "自定义分割线的起点",
        "Split Line End": "分割线终点",
        "End point of the custom split line": "自定义分割线的终点",
        "Use Custom Split Line": "使用自定义分割线",
        "When enabled, bisect weight uses the custom split line instead of an axis": "启用后二分权重将使用自定义分割线而非轴向",
        "Split Mode": "分割模式", # Also used as EnumProperty name
        "Select the axis or method for weight splitting": "选择权重分割的轴向或方式",
        "Split weights along the X axis": "沿X轴分割权重", # EnumProperty item description
        "Split weights along the Y axis": "沿Y轴分割权重", # EnumProperty item description
        "Split weights along the Z axis": "沿Z轴分割权重", # EnumProperty item description
        "Use custom split line": "使用自定义分割线", # EnumProperty item description

        # bone_modify.py UI Elements
        "Bone Quick Select": "骨骼快捷选择",
        "Select bones according to the bone set defined in the dictionary": "根据定义好的骨骼集合选择骨骼",
        "Valve Bone": "官方骨骼",
        "Custom Bone": "自定义骨骼",
        "Jiggle Bone": "飘动骨骼",
        "Skirt Bone": "裙子骨骼",
        "Hair Bone": "头发骨骼",

        "Select by pattern": "按名称选择",
        "By default, turn off case distinction and turn on merge selection": "默认关闭大小写区分和打开并入选择",

        # VRD Tools
        "VRD Action Management:": "VRD动作管理",
        "Add New Project": "添加VRD动作项目",
        "Add new project to the project list": "添加新的项目到项目列表",
        "VRD Project Name": "VRD项目名称",

        "Action Name": "动作名称:",
        "Select the action bound to the project": "选择与项目绑定的动画",
        "Procedural Bone:": "程序骨骼:",

        "Remove Project": "移除VRD动作项目",
        "Remove the currently selected project from the project list": "从项目列表移除当前选中的项目",     

        "Procedural Bone:": "程序骨骼:",
        "Driver Bone:": "驱动骨骼:",
        "No Items or Invalid Index,Create New VRD Action First": "没有可选的项目或项目索引无效，请先新建VRD动作项目",
        
        "Operations for editing the bone list": "编辑骨骼列表的操作",
        "Edit the bone list including adding, removing, moving and clearing bones": "编辑骨骼列表，包括添加、移除、移动及清空骨骼",

        "Generate VRD Action": "生成VRD动作",
        "Create actions named 'VRD' and 'VRD_Foot', insert keyframes of 4 standard bone 'VRD' poses from 0 to 30 frames": "新建名为 'VRD' 和 'VRD_Foot' 的动作,在0至30帧插入4种官骨 'VRD' 姿势的关键帧",
        "The exported text will be output in the VRD text format that can be received by StudioMDL": "导出的文本将以 StudioMDL 能接收的 VRD 文本格式输出",
        "The exported text will be output in the VRD text format that can be received by NekoMDL": "导出的文本将以 NekoMDL 能接收的 VRD 文本格式输出",
        "Export Path": "导出路径",
        "Export All VRD": "导出全部VRD",
        "Export all VRD texts obtained from the bound animations": "导出所有根据绑定动画得到的 VRD 文本",

        "Copy to Clipboard": "复制到剪贴板",
        "Export to File": "导出至文件",

        "Open File or Folder": "打开文件或文件夹",
        "Open the file or folder specified by 'Export Path'": "打开在 '导出路径' 指定的文件或者文件夹",

        "Export bone VRD data": "导出骨骼VRD数据",

        # 🪄 JiggleBone Tools
        "Manually update the jigglebone list": "手动更新飘骨列表",
        "Synchronize 3D view selection state and jump": "同步3D视图选中状态并跳转",
        "Manipulate the selection state of the list": "操作列表的选中状态",
        "Select All/Deselect All/Invert Selection\nSynchronize selection with 3D view": "全选/取消全选/反选\n与3D视图同步选中状态",

        "Apply Preset": "应用预设",
        "Add/Overwrite Preset": "添加/覆盖预设",
        "Delete Preset": "删除预设",
        "The name of the new preset. If this name is the same as an existing preset, the existing preset will be overwritten": "新预设的名字，如果这个名字和现有预设的名字相同，将会覆盖现有预设",
        "Preset Name": "预设名",

        "Add Jigglebone to the list": "添加飘骨到列表",
        "Supports multiple selection and addition in the 3D view and outline view": "支持在3D视图和大纲视图多选添加",
        "Remove selected bones from the list": "从列表中删除选中的骨骼",
        "Priority: delete the selected bones in the 3D view first;\nif there are no selected bones, delete the checked items;\nif there are no checked items, delete the highlighted items": "优先删除3D视图中选中的骨骼，其次删除打勾项，否则删除高亮项",
        "Clear the bone list": "清空骨骼列表",
        "Remove all bones in the list": "移除列表中所有骨骼",
        "Support multi-selection, otherwise only move the selected highlighted bones": "支持多选，否则只移动选中高亮的骨骼",
        "Apply jitter parameters from the clipboard (individually)": "从剪贴板应用抖动参数（单独）",
        "Apply a set of floating bone text from the clipboard to the current selection": "把剪贴板中的一组飘骨文本应用到当前选择项",
        "Import jitter parameters from the clipboard (All)": "从剪贴板导入抖动参数（全部）",
        "Import all floating bone text from the clipboard to the current list": "把剪贴板中的全部飘骨文本导入到当前列表",

        "Jigglebone Parameters Panel": "抖动参数面板",
        "Parameter Step Setting": "参数步进设置",
        "Batch customize settings for selected bones": "批量自定义设置选中骨骼的参数",

        "Minimum": "最小值",
        "The minimum value of the parameter": "设置参数最小值",
        "Maximum": "最大值",
        "The maximum value of the parameter": "设置参数最大值",
        "Reverse": "反向",
        "Decrease parameter values instead of increasing": "递减参数值而不是递增",
        "Minimum X": "最小值X",
        "The X component of the minimum value of the parameter": "设置参数最小值的X分量",
        "Minimum Y": "最小值Y",
        "The Y component of the minimum value of the parameter": "设置参数最小值的Y分量",
        "Maximum X": "最大值X",
        "The X component of the maximum value of the parameter": "设置参数最大值的X分量",
        "Maximum Y": "最大值Y",
        "The Y component of the maximum value of the parameter": "设置参数最大值的Y分量",
        "Target Parameter": "目标参数",
        "Choose the parameter to be incremented or decremented": "选择要进行递增或递减设置的参数",
        "Parameter Selection": "参数选择",

        # 😇 Flex Tools
        "Shape Keys Capture": "形态键捕捉",
        "Capture Non-Zero Deformation Shape Keys": "捕捉所有变形数值非零的形态键",
        "Add to Dict": "添加到字典",
        "Add the captured shape key values into the currently selected dictionary key": "将捕捉到的形态键值添加到当前选定的字典键中",
        "Organize Shape Keys": "整理形态键列表",
        "Automatically delete useless shape keys and organize the shape key list\nBe sure to backup": "自动删除无用形态键整理形态键列表\n注意备份",
        "Batch Create": "批量创建",
        "Batch create shape keys in custom order": "批量自选顺序创建形态键",
        "Create Shape Keys": "形态键创建",
        "Create shape keys based on the key selected in the drop-down menu": "根据下拉菜单选择的键创建形态键",
        "Add New Key": "添加新键",
        "Add a new key to the dictionary": "添加一个新的键到字典中",
        "Delete Key-Value Pair": "删除键值对",
        "Rename Key": "重命名键",
        "Rename the key currently selected in the drop-down menu": "重命名当前下拉菜单中选中的键",
        "Delete Key": "删除键",
        "Delete the currently selected key and its key-value pair": "删除当前选中的键及其键值对",
        "Select All/Deselect All/Invert Selection": "全选/取消全选/反选",

        # Update related translations
        "Check for updates": "检查更新",
        "Update Available!": "有可用更新！",
        "Version Check": "版本检查",
        "Current version:": "当前版本：",
        "Latest version:": "最新版本：",
        "Update Notes:": "更新说明：",
        "Go to download page": "前往下载页面",
        "You are using the latest version": "您正在使用最新版本",
        "New version available:": "新版本可用：",
        "Download": "下载",



        

}