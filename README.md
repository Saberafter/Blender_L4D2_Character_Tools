<div class="title" align=center>
    <h1>L4D2 Character Tools</h1>
    <div>一款旨在提升求生之路2人物模组制作效率的Blender插件(*´▽｀)ノノ</div>
    <br/>
    <p>
    <img src="https://img.shields.io/github/license/Saberafter/Blender_L4D2_Character_Tools">
    <img src="https://img.shields.io/github/release/Saberafter/Blender_L4D2_Character_Tools">
</div>

## 🚩 前言
⚠️本插件由AI语言模型ChatGPT辅助编写代码，基于个人模组制作中的工作流程和习惯开发，尽量考虑了通用性和可扩展性，但仍可能会有潜在的bug或兼容性问题。

📢如果您在使用过程中遇到任何问题或有任何改进建议，欢迎在Github仓库中提交Issue或者联系我，我会认真查阅并努力满足大家的需求。

## 💡 特性
- ✨运用预设的骨骼映射关系快速进行骨骼对齐与合并

- ✨插入动作关键帧辅助生成VRD文本

- ✨快捷编写抖动骨骼参数，支持批量设置，文本输入输出，预设管理

- ✨通过操控原始形态键的混合数值生成适配自己面部规则的表情集

## 📥 安装方式
1. 在[发行版](https://github.com/Saberafter/Blender_L4D2_Character_Tools/releases)页面下载最新的zip压缩包

2. 打开Blender，找到编辑(Edit)-偏好设置(Preferences)-插件(Add-ons)

3. 在插件(Add-ons)选项卡中安装(Install)这个压缩包并启用(√)

## 🗝 使用说明
📌 **操作面板**: 

- 安装并启用插件后，在3D视图的右侧面板(N键呼出)中可以找到插件的操作面板，点击💝LCT图标即可展开。

<p align="center">
  <img src="assets/0.png" alt="操作面板"/>
</p>

📌 **对齐骨骼**: 

1. 在插件面板中设置"<span style="color:yellow">官方骨架</span>"和"<span style="color:yellow">自定义骨架</span>"对象。
2. 点击"<span style="color:yellow">对齐骨骼</span>"按钮，插件会自动为官方骨架的主要骨骼添加复制位置约束，约束目标为自定义骨架中相应部位的骨骼。骨骼的对应关系取自预设的骨骼映射字典。

![对齐骨骼](assets/1.gif)
3. 对骨操作补充：使用"<span style="color:yellow">对齐骨骼</span>"功能创建骨骼约束后，先设置一次静置姿势以定位骨骼，然后移除约束完成对齐操作。

![对骨补充](assets/4.gif)

📌 **骨骼映射管理**: 

- "<span style="color:yellow">骨骼映射列表</span>"分为两栏:第一栏为"<span style="color:yellow">官方骨骼列表</span>"，第二栏为与之对应的"<span style="color:yellow">自定义骨列表</span>"。例如，官方骨架的"pelvis"骨骼对应自定义骨架的"hips"和"pelvis"骨骼。
- 3D视图选中自定义骨架并进入姿态模式，界面上会显示"<span style="color:yellow">骨骼名称</span>"栏。在上两栏选择需要映射的一组"<span style="color:yellow">官方骨骼</span>"和"<span style="color:yellow">自定义骨骼</span>"，点击"<span style="color:yellow">添加骨骼</span>"按钮，即可将第三栏设置好的骨骼添加到"<span style="color:yellow">自定义骨列表</span>"中，界面会实时刷新映射关系。

<p align="center">
  <img src="assets/2.png" alt="编写骨骼映射字典"/>
</p>

- 通过编辑骨骼映射，可以灵活处理预设字典未包含的骨骼名称，无需离开Blender即可完成字典的维护。

![插件使用说明](assets/3.gif)

📌 **嫁接骨骼**: 

- 平时的嫁接流程里对骨骼的操作方法可以分为两种:

   - 使用插件将自定义骨骼的权重合并至官方骨骼，并将自定义骨骼删除。这是较通用的方法，因为很多游戏不允许存在非官方骨骼或者不会自动塌陷掉自定义骨骼。
    
      参考视频：[星落老师的权重转移插件](https://www.bilibili.com/video/BV121421R7J7/)

   - 保留原自定义骨骼，使用插件重新设置骨骼的父子级关系。这是接下来要介绍的插件功能，主要依托于对骨阶段使用的骨骼映射关系。这种方法可以使用的前提是编译时骨骼通过$bonemerge参数塌陷，也是3DMAX流程里普遍使用的方法。


- "<span style="color:yellow">嫁接骨骼</span>"功能利用骨骼映射关系和骨骼间的距离判定，自动为重合的骨骼设置父子级关系。
- "<span style="color:yellow">嫁接骨骼</span>"功能的三种使用情况:
  1. 未选中任何骨骼时，对全部骨骼进行嫁接操作。
  2. 选中部分骨骼时，只对选中的骨骼进行嫁接操作。
  3. 特别的，多选骨骼时，如果选中了官方骨骼，其他选中的和官骨距离重合的骨骼(无论是否存在映射关系)都会成为该官方骨骼的子级。

![嫁接1](assets/5.gif)
![嫁接2](assets/6.gif)


📌 **VRD**: 
- 关于借助人物动作辅助生成VRD文本的原理不再赘述，这里主要讲解使用插件生成VRD文本的流程过一遍插件的VRD相关功能。
1. 选中官方骨架，点击"<span style="color:yellow">生成VRD动作</span>"，插件会自动为驱动骨骼创建名为"VRD"和"VRD_Foot"的动作，分别用于制作裙子VRD、修正持枪动作以及修复高跟鞋角色的IK。之后可以参考驱动骨骼的动作，自行为程序骨骼添加关键帧。

![VRD1](assets/7.gif)

2. 在"<span style="color:yellow">VRD项目管理</span>"中新建项目，项目数量应与VRD动作数量一致。为每个项目绑定相应的VRD动作。这里解释一下，因为如果想得到正确的足VRD坐标，和动过腿的动作共用一个动作肯定是不行的(虽然可以断开，但操作麻烦不方便修改)，而手和腿没有冲突可以放一个动作里，所以得看情况分开处理VRD的辅助动作。
3. 在VRD项目中添加程序骨骼和驱动骨骼，列表中同一行的骨骼相互对应。程序骨骼列表每一项右侧的数字为VRD参数中的第一组角度值。
4. 设置好骨骼列表后，在面板下方选择导出路径和文本格式，即可导出VRD文本。

![VRD2](assets/8.gif)

📌 **飘骨**: 
- 飘骨工具以骨骼列表为核心，用于管理骨骼的抖动参数。添加骨骼后，选中列表中的骨骼，在右侧参数面板中可以详细设置该骨骼的各类抖动参数。导出的文本会自动转化为编译器可识别的格式。
- 插件提供了一系列功能提高抖动参数的编辑效率:
  1. "<span style="color:yellow">同步</span>"按钮可同步骨骼列表和3D视图中的选中状态，便于在两个视图间切换浏览。

![飘骨1](assets/9.gif)

  2. "<span style="color:yellow">预设</span>"功能可保存和载入抖动参数配置，支持多选骨骼批量应用预设。

![飘骨2](assets/10.gif)

  3. 右侧参数面板开关下面的的扳手按钮用于批量设置参数，支持多选骨骼统一调整数值，也可设置数值范围实现参数的递增或递减。

  4. 参数面板最后一个按钮可以从剪贴板导入外部文件中复制的标准格式抖动参数。（已更新，支持对多选骨骼批量导入）
  5. "复制到剪贴板"的功能，当有勾选项时只导出勾选项，方便单独微调一根骨骼后用导入剪贴板的功能回转进行批量修改.
<p align="center">
  <img src="assets/11.gif" alt="批量设置抖动参数" width="400px" />
  <img src="assets/12.gif" alt="从剪贴板导入" width="400px" />
</p>

📌 **表情**: 
- 表情工具基于自定义原模的形态键，通过混合这些形态键的变形数值，生成适配目标面部规则的新形态键。
- MMD模型和VRC模型各自之间的形态键名称和表情通常是一致的，因此可以通过记录形态键名称和变形数值，构建可复用的形态键混合字典。(也可以针对某些游戏，模型不同但表情同名的情况，来制定一套字典)
- 插件内置了一些形态键混合字典，下拉菜单中的AU表情对应最终生成的形态键，每个AU表情绑定了一套或多套用于混合的形态键组合。这些内容都可以在Blender中进行编辑。
- 这里视频+文字展示一下基本流程：
  1. 通过"<span style="color:yellow">捕捉形态键</span>"功能记录形态键，添加到混合表情集的形态键列表中。 
  2. 使用"<span style="color:yellow">批量创建</span>"功能，选择我们面部规则需要的表情和顺序生成新的形态键。
  3. "<span style="color:yellow">整理形态键</span>"，只保留使用插件生成的表情。
  


https://github.com/Saberafter/Blender_L4D2_Character_Tools/assets/46404382/a98e7858-69f2-4035-986d-4df931404993


## 致谢
- 抹茶芝士✰：对骨脚本&实用性反馈
- 残剑斩龙：3DMax的VRD插件
- [bonjorno7/SourceOps](https://github.com/bonjorno7/SourceOps)：获取骨骼位置&旋转坐标
- [kumopult/BoneAnimCopy](https://github.com/kumopult/blender_BoneAnimCopy)：骨骼映射思路
- 制作人物模组教程的作者们：插件学习基础
- miHoYo：演示用模型版权所属

## 相关工具
星落老师的Neko系列工具：
- 更好 更快 更强的MDL编译器：[NekoMdl](https://steamcommunity.com/sharedfiles/filedetails/?id=3142607978)
- 通用游戏MOD权重转移插件：[NekoTools](https://github.com/Starfelll/Blender_Neko_Tools)
- 模组管理工具：[NekoVpk](https://github.com/Starfelll/NekoVpk)
