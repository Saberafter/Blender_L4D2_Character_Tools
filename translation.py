# -*- coding: utf-8 -*-

translation_dict = {

    "zh_CN": {
        # Preferences
        ("*", "View3D > Tool Shelf > 💝"): "3D视图 > 侧栏 > 💝",
        ("*", "A plugin designed to enhance the efficiency of creating Left 4 Dead 2 Mods."): "这是一个旨在提升求生之路2人物Mod制作效率的插件。",
        
        # 🛠️ General Tools
        ("*", "Valve Rig:"): "官方骨架:",
        ("*", "Custom Rig:"): "自定义骨架:",

        ("Operator", "Align Bone"): "对齐骨骼",
        ("*", "Align bones by batch adding copy location constrains to the bones\nThe mechanism of bone alignment is based on the mapping dictionary\n1、Ensure the TPOSE is approximately consistent\n2、Make sure the name of the skeleton is the same as the name of the first level under the skeleton"): "通过批量添加复制位置的骨骼约束来对骨\n对骨匹配机制来源于映射字典\n1、确保TPOSE近似一致\n2、确保骨架名和骨架下第一个层级名字一样",

        ("Operator", "Graft Bone"): "嫁接骨骼",
        ("*", "Automatically set the parent-child level of bones based on bone mapping relationships"): "根据骨骼映射关系自动设置骨骼的父子级",

        ("Operator", "Rename Bone"): "重命名骨骼",
        ("*", "Rename Bones According to Bone Mapping"): "根据骨骼映射关系重命名骨骼",

        ("Operator", "Remove Bone Constraint"): "移除骨骼约束",
        ("*", "Bulk Remove Constraints from Selected Bones"): "批量移除所选骨骼的约束",
        ("Operator", "Remove All Constraint"): "移除骨骼约束",
        ("Operator", "Cancel Y RotationConstraint"): "取消Y轴旋转约束",
        ("Operator", "Remove TransformConstraint"): "移除变换约束",

        ("*", "Bone Mapping Management"): "骨骼映射管理",
        ("*", "Valve BoneList"): "官方骨骼列表",
        ("*", "Custom BoneList"): "自定义骨列表",
        ("*", "Bone Name"): "骨骼名",
        ("Operator", "Add Bone"): "添加骨骼",
        ("*", "Automatically remove symbols and convert to lowercase"): "自动去掉符号转化为小写",
        ("Operator", "Remove Bone"): "移除骨骼",
        ("*", "Remove selected bone names from the custom bone list"): "从自定义骨列表中移除选定的骨骼名",
        ("*", "Dictionary Key"): "字典键",
        ("*", "Select the key in the dictionary"): "选择字典中的键",
        ("*", "Bone Name"): "骨骼名称",
        ("*", "Select the bone name in the current skeleton"): "选择当前骨架中的骨骼名称",
        ("*", "Dictionary Value"): "字典值",
        ("*", "Display all values for the selected dictionary key"): "显示所选字典键的所有值",

        ("*", "Bone Quick Select"): "骨骼快捷选择",
        ("*", "Select bones according to the bone set defined in the dictionary"): "根据定义好的骨骼集合选择骨骼",
        ("Operator", "Valve Bone"): "官方骨骼",
        ("Operator", "Custom Bone"): "自定义骨骼",
        ("Operator", "Jiggle Bone"): "飘动骨骼",
        ("Operator", "Skirt Bone"): "裙子骨骼",
        ("Operator", "Hair Bone"): "头发骨骼",

        ("Operator", "Select by pattern"): "按名称选择",
        ("*", "By default, turn off case distinction and turn on merge selection"): "默认关闭大小写区分和打开并入选择",

        ("Operator", "Merge Vertex Group"): "合并顶点组",
        ("*", "By default, turn off case distinction and turn on merge selection"): "把第二栏的顶点组权重合并进第一栏的顶点组\n适合没有骨骼但是顶点组有权重的特殊情况",

        # 🕹️ VRD Tools
        ("*", "VRD Action Management:"): "VRD动作管理",
        ("Operator", "Add New Project"): "添加VRD动作项目",
        ("*", "Add new project to the project list"): "添加新的项目到项目列表",
        ("*", "VRD Project Name"): "VRD项目名称",

        ("*", "Action Name"): "动作名称:",
        ("*", "Select the action bound to the project"): "选择与项目绑定的动画",
        ("*", "Procedural Bone:"): "程序骨骼:",


        ("Operator", "Remove Project"): "添加VRD动作项目",
        ("*", "Remove the currently selected project from the project list"): "从项目列表移除当前选中的项目",     

        ("*", "Procedural Bone:"): "程序骨骼:",
        ("*", "Driver Bone:"): "驱动骨骼:",
        ("*", "No Items or Invalid Index,Create New VRD Action First"): "没有可选的项目或项目索引无效，请先新建VRD动作项目",
        

        ("Operator", "Operations for editing the bone list"): "编辑骨骼列表的操作",
        ("*", "Edit the bone list including adding, removing, moving and clearing bones"): "编辑骨骼列表，包括添加、移除、移动及清空骨骼",

        ("Operator", "Generate VRD Action"): "生成VRD动作",
        ("*", "Create actions named 'VRD' and 'VRD_Foot', insert keyframes of 4 standard bone 'VRD' poses from 0 to 30 frames"): "新建名为 'VRD' 和 'VRD_Foot' 的动作,在0至30帧插入4种官骨 'VRD' 姿势的关键帧",
        ("*", "The exported text will be output in the VRD text format that can be received by StudioMDL"): "导出的文本将以 StudioMDL 能接收的 VRD 文本格式输出",
        ("*", "The exported text will be output in the VRD text format that can be received by NekoMDL"): "导出的文本将以 NekoMDL 能接收的 VRD 文本格式输出",
        ("*", "Export Path"): "导出路径:",
        ("*", "Export All VRD"): "导出全部VRD",
        ("*", "Export all VRD texts obtained from the bound animations"): "导出所有根据绑定动画得到的 VRD 文本",

        ("*", "Copy to Clipboard"): "复制到剪贴板",
        ("*", "Export to File"): "导出到文件",

        ("Operator", "Open File or Folder"): "打开文件或文件夹",
        ("*", "Open the file or folder specified by 'Export Path'"): "打开在 '导出路径' 指定的文件或者文件夹",


        ("*", "Export bone VRD data"): "导出骨骼VRD数据",

        # 🪄 JiggleBone Tools
        ("*", "Manually update the jigglebone list"): "手动更新飘骨列表",
        ("Operator", "Synchronize 3D view selection state and jump"): "同步3D视图选中状态并跳转",
        ("Operator", "Manipulate the selection state of the list"): "操作列表的选中状态",
        ("*", "Select All/Deselect All/Invert Selection\nSynchronize selection with 3D view"): "全选/取消全选/反选\n与3D视图同步选中状态",

        ("Operator", "Apply Preset"): "应用预设",
        ("Operator", "Add/Overwrite Preset"): "添加/覆盖预设",
        ("*", "The name of the new preset. If this name is the same as an existing preset, the existing preset will be overwritten"): "新预设的名字，如果这个名字和现有预设的名字相同，将会覆盖现有预设",
        ("*", "Preset Name"): "预设名",

        ("Operator", "Add Jigglebone to the list"): "添加飘骨到列表",
        ("*", "Supports multiple selection and addition in the 3D view and outline view"): "支持在3D视图和大纲视图多选添加",
        ("Operator", "Remove selected bones from the list"): "从列表中删除选中的骨骼",
        ("*", "Priority to delete the checked items, otherwise delete the highlighted items"): "优先删除打勾项，否则删除高亮项",
        ("Operator", "Clear the bone list"): "清空骨骼列表",
        ("*", "Remove all bones in the list"): "移除列表中所有骨骼",
        ("*", "Support multi-selection, otherwise only move the selected highlighted bones"): "支持多选，否则只移动选中高亮的骨骼",
        ("Operator", "Apply jitter parameters from clipboard"): "从剪贴板应用抖动参数",
        ("*", "Jigglebone Parameters Panel"): "抖动参数面板",
        ("Operator", "Parameter Step Setting"): "参数步进设置",
        ("*", "Batch customize settings for selected bones"): "批量自定义设置选中骨骼的参数",

        ("*", "Minimum"): "最小值",
        ("*", "The minimum value of the parameter"): "设置参数最小值",
        ("*", "Maximum"): "最大值",
        ("*", "The maximum value of the parameter"): "设置参数最大值",
        ("*", "Reverse"): "反向",
        ("*", "Decrease parameter values instead of increasing"): "递减参数值而不是递增",
        ("*", "Minimum X"): "最小值X",
        ("*", "The X component of the minimum value of the parameter"): "设置参数最小值的X分量",
        ("*", "Minimum Y"): "最小值Y",
        ("*", "The Y component of the minimum value of the parameter"): "设置参数最小值的Y分量",
        ("*", "Maximum X"): "最大值X",
        ("*", "The X component of the maximum value of the parameter"): "设置参数最大值的X分量",
        ("*", "Maximum Y"): "最大值Y",
        ("*", "The Y component of the maximum value of the parameter"): "设置参数最大值的Y分量",
        ("*", "Target Parameter"): "目标参数",
        ("*", "Choose the parameter to be incremented or decremented"): "选择要进行递增或递减设置的参数",
        ("*", "Parameter Selection"): "参数选择",

        # 😇 Flex Tools
        ("Operator", "Shape Keys Capture"): "形态键捕捉",
        ("*", "Capture Non-Zero Deformation Shape Keys"): "捕捉所有变形数值非零的形态键",
        ("Operator", "Add to Dict"): "添加到字典",
        ("*", "Add the captured shape key values into the currently selected dictionary key"): "将捕捉到的形态键值添加到当前选定的字典键中",
        ("Operator", "Organize Shape Keys"): "整理形态键列表",
        ("*", "Automatically delete useless shape keys and organize the shape key list\nBe sure to backup"): "自动删除无用形态键整理形态键列表\n注意备份",
        ("Operator", "Batch Create"): "批量创建",
        ("*", "Batch create shape keys in custom order"): "批量自选顺序创建形态键",
        ("Operator", "Create Shape Keys"): "形态键创建",
        ("*", "Create shape keys based on the key selected in the drop-down menu"): "根据下拉菜单选择的键创建形态键",
        ("Operator", "Add New Key"): "添加新键",
        ("*", "Add a new key to the dictionary"): "添加一个新的键到字典中",
        ("Operator", "Delete Key-Value Pair"): "删除键值对",
        ("Operator", "Rename Key"): "重命名键",
        ("*", "Rename the key currently selected in the drop-down menu"): "重命名当前下拉菜单中选中的键",
        ("Operator", "Delete Key"): "删除键",
        ("*", "Delete the currently selected key and its key-value pair"): "删除当前选中的键及其键值对",
        ("*", "Select All/Deselect All/Invert Selection"): "全选/取消全选/反选",


























    },
}

