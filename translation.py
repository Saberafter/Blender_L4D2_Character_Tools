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
        
        # 🛠️ General Tools
        "Valve Rig:": "官方骨架:",
        "Custom Rig:": "自定义骨架:",

        "Align Bone": "对齐骨骼",
        "Align bones by batch adding copy location constrains to the bones\nThe mechanism of bone alignment is based on the mapping dictionary\n1、Ensure the TPOSE is approximately consistent\n2、Make sure the name of the skeleton is the same as the name of the first level under the skeleton": "通过批量添加复制位置的骨骼约束来对骨\n对骨匹配机制来源于映射字典\n1、确保TPOSE近似一致\n2、确保骨架名和骨架下第一个层级名字一样",

        "Graft Bone": "嫁接骨骼",
        "Automatically set the parent-child level of bones based on bone mapping relationships": "根据骨骼映射关系自动设置骨骼的父子级",

        "Rename Bone": "重命名骨骼",
        "Rename custom bone names to Valve bone names based on bone mapping relationships": "根据骨骼映射关系把自定义骨骼名字重命名为Valve官方骨骼名字",

        "Unbind Preserve Shape": "骨骼断绑保形",
        "Maintain shape and transformation when breaking bone parent-child relationships": "在断开骨骼父子关系时保持其形状和变换",

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

        "Bone Quick Select": "骨骼快捷选择",
        "Select bones according to the bone set defined in the dictionary": "根据定义好的骨骼集合选择骨骼",
        "Valve Bone": "官方骨骼",
        "Custom Bone": "自定义骨骼",
        "Jiggle Bone": "飘动骨骼",
        "Skirt Bone": "裙子骨骼",
        "Hair Bone": "头发骨骼",

        "Select by pattern": "按名称选择",
        "By default, turn off case distinction and turn on merge selection": "默认关闭大小写区分和打开并入选择",

        "Vertex Group Editing": "顶点组编辑",


        "Add Vertex Group": "添加顶点组",
        "Add a vertex group field to select the vertex group to be processed by the current model": "增加一个顶点组栏位，用来选择当前模型需要处理的顶点组",

        "Remove Vertex Group": "删除顶点组",
        "Remove this vertex group field": "删除这个顶点组栏位",

        "Process Vertex Group": "处理顶点组",
        "The following functions are performed only on the vertex groups within the columns created with the + button:\nMerge vertex groups: Merge the weights of the vertex groups after the first column into the first column vertex group and delete these vertex groups(careful).\nEven weight: Evenly distribute the weights of the first column vertex group to the other column vertex groups.\nBisect weight: Using the X-pos of the vertices in the first column vertex group as a reference, divide the weights to the left and right. Assign the weights of the left half to the vertex group in the second column, and the weights of the right half to the vertex group in the third column": "以下功能仅针对使用+号创建的栏内顶点组进行操作\n合并顶点组：把第一栏以后的顶点组权重合并到第一栏顶点组中，并删除这些顶点组谨慎操作\n均匀权重：把第一栏顶点组的权重均匀分配给其他栏顶点组\n二分权重：以第一栏顶点组内顶点X坐标为参照，左右划分权重，左半边权重划给第二栏顶点组，右半边权重划给第三栏顶点组",
        "Merge vertex groups": "合并顶点组",
        "Even weight": "均匀权重",
        "Bisect weight": "二分权重",
        

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