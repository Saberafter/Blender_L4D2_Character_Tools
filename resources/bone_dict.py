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

# 这里存储了对骨和嫁接中使用的骨骼映射关系字典
# 已收录：Manuka，MMD/CATS，Karin，Kikyou，Lime，Maya，Moe，Rindo，Selestia
# 左侧为官骨，名称固定不用修改
# 右侧括号内添加对应部位的自定义骨骼名字

# 嫁接算法逻辑：不需要字典，读取当前未隐藏的官骨骨骼，然后在0.1范围寻找最近的其他骨骼作为子级
# 比如读到ValveBiped.Bip01_Head1，距离最近的是Head，就会把他俩自动设为父子。
# 自己要做的就是做好分组，除了要用的骨骼全部隐藏，防止别的骨骼干扰算法
bone_mapping = {
    # 身体
    'ValveBiped.Bip01_Pelvis': ['hips'],
    'ValveBiped.Bip01_Spine': ['spine'],
    'ValveBiped.Bip01_Spine1': ['spine'],
    'ValveBiped.Bip01_Spine2': ['spine'],
    'ValveBiped.Bip01_Spine4': ['chest'],
    'ValveBiped.Bip01_Neck1': ['neck'],
    'ValveBiped.Bip01_Head1': ['head'],
    # 左
    'ValveBiped.Bip01_L_Clavicle': ['left_shoulder'],
    'ValveBiped.Bip01_L_UpperArm': ['left_arm'],
    'ValveBiped.Bip01_L_Forearm': ['left_elbow'],
    'ValveBiped.Bip01_L_Hand': ['left_wrist'],
    'ValveBiped.Bip01_L_Finger0': ['thumb_1_l'],
    'ValveBiped.Bip01_L_Finger01': ['thumb_2_l'],
    'ValveBiped.Bip01_L_Finger02': ['thumb_3_l'],
    'ValveBiped.Bip01_L_Finger1': ['index_1_l'],
    'ValveBiped.Bip01_L_Finger11': ['index_2_l'],
    'ValveBiped.Bip01_L_Finger12': ['index_3_l'],
    'ValveBiped.Bip01_L_Finger2': ['middle_1_l'],
    'ValveBiped.Bip01_L_Finger21': ['middle_2_l'],
    'ValveBiped.Bip01_L_Finger22': ['middle_3_l'],
    'ValveBiped.Bip01_L_Finger3': ['ring_1_l'],
    'ValveBiped.Bip01_L_Finger31': ['ring_2_l'],
    'ValveBiped.Bip01_L_Finger32': ['ring_3_l'],
    'ValveBiped.Bip01_L_Finger4': ['pinkie_1_l'],
    'ValveBiped.Bip01_L_Finger41': ['pinkie_2_l'],
    'ValveBiped.Bip01_L_Finger42': ['pinkie_3_l'],
    # 右
    'ValveBiped.Bip01_R_Clavicle': ['right_shoulder'],
    'ValveBiped.Bip01_R_UpperArm': ['right_arm'],
    'ValveBiped.Bip01_R_Forearm': ['right_elbow'],
    'ValveBiped.Bip01_R_Hand': ['right_wrist'],
    'ValveBiped.Bip01_R_Finger0': ['thumb_1_r'],
    'ValveBiped.Bip01_R_Finger01': ['thumb_2_r'],
    'ValveBiped.Bip01_R_Finger02': ['thumb_3_r'],
    'ValveBiped.Bip01_R_Finger1': ['index_1_r'],
    'ValveBiped.Bip01_R_Finger11': ['index_2_r'],
    'ValveBiped.Bip01_R_Finger12': ['index_3_r'],
    'ValveBiped.Bip01_R_Finger2': ['middle_1_r'],
    'ValveBiped.Bip01_R_Finger21': ['middle_2_r'],
    'ValveBiped.Bip01_R_Finger22': ['middle_3_r'],
    'ValveBiped.Bip01_R_Finger3': ['ring_1_r'],
    'ValveBiped.Bip01_R_Finger31': ['ring_2_r'],
    'ValveBiped.Bip01_R_Finger32': ['ring_3_r'],
    'ValveBiped.Bip01_R_Finger4': ['pinkie_1_r'],
    'ValveBiped.Bip01_R_Finger41': ['pinkie_2_r'],
    'ValveBiped.Bip01_R_Finger42': ['pinkie_3_r'],
    # 下半身
    'ValveBiped.Bip01_L_Thigh': ['left_leg'],
    'ValveBiped.Bip01_L_Calf': ['left_knee'],
    'ValveBiped.Bip01_L_Foot': ['left_ankle'],
    'ValveBiped.Bip01_L_Toe0': ['left_toe'],
    'ValveBiped.Bip01_R_Thigh': ['right_leg'],
    'ValveBiped.Bip01_R_Calf': ['right_knee'],
    'ValveBiped.Bip01_R_Foot': ['right_ankle'],
    'ValveBiped.Bip01_R_Toe0': ['right_toe'],
}

common_mapping = {
    # 身体
    'hips': ["pelvis", "hips", "下半身"],
    'spine': ["torso", "spine", "上半身"],
    'chest': ["chest", "upperchest", "spine2", "上半身2"],
    'neck': ["neck", "neck1", "首"],
    'head': ["head", "head1", "頭"],
    
    # 左侧
    'left_shoulder': ["leftshoulder", "shoulderl", "lshoulder", "肩l"],
    'left_arm': ["leftarm", "arml", "rarm", "upperarml", "leftupperarm", "uparml", "luparm", "腕l"],
    'left_elbow': ["leftelbow", "elbowl", "relbow", "lowerarml", "leftlowerarm", "lowarml", "llowarm", "forearml", "leftforearm", "ひじl"],
    'left_wrist': ["leftwrist", "wristl", "rwrist", "handl", "lefthand", "lhand", "手首l"],
    
    # 左手指
    'thumb_1_l': ["thumb0l", "thumb1l","thumbproximall", "leftthumbproximal", "lefthandthumb1", "親指0l"],
    'thumb_2_l': ["thumb1l", "thumb2l", "thumbintermediatel", "leftthumbintermediate", "lefthandthumb2", "親指1l"],
    'thumb_3_l': ["thumb2l", "thumb3l", "thumbdistall", "leftthumbdistal", "lefthandthumb3", "親指2l"],
    'index_1_l': ["indexfinger1l", "index1l", "indexproximall", "leftindexproximal", "lefthandindex1", "人指1l"],
    'index_2_l': ["indexfinger2l", "index2l", "indexintermediatel", "leftindexintermediate", "lefthandindex2", "人指2l"],
    'index_3_l': ["indexfinger3l", "index3l", "indexdistall", "leftindexdistal", "lefthandindex3", "人指3l"],
    'middle_1_l': ["middlefinger1l", "middle1l", "middleproximall", "leftmiddleproximal", "lefthandmiddle1", "中指1l"],
    'middle_2_l': ["middlefinger2l", "middle2l", "middleintermediatel", "leftmiddleintermediate", "lefthandmiddle2", "中指2l"],
    'middle_3_l': ["middlefinger3l", "middle3l", "middledistall", "leftmiddledistal", "lefthandmiddle3", "中指3l"],
    'ring_1_l': ["ringfinger1l", "ring1l", "ringproximall", "leftringproximal", "lefthandring1", "薬指1l"],
    'ring_2_l': ["ringfinger2l", "ring2l", "ringintermediatel", "leftringintermediate", "lefthandring2", "薬指2l"],
    'ring_3_l': ["ringfinger3l", "ring3l", "ringdistall", "leftringdistal", "lefthandring3", "薬指3l"],
    'pinkie_1_l': ["littlefinger1l", "little1l", "littleproximall", "leftlittleproximal", "lefthandlittle1", "lefthandpinky1", "小指1l"],
    'pinkie_2_l': ["littlefinger2l", "little2l", "littleintermediatel", "leftlittleintermediate", "lefthandlittle2", "lefthandpinky2", "小指2l"],
    'pinkie_3_l': ["littlefinger3l", "little3l", "littledistall", "leftlittledistal", "lefthandlittle3", "lefthandpinky3", "小指3l"],

    # 右侧
    'right_shoulder': ["rightshoulder", "shoulderr", "rshoulder", "肩r"],
    'right_arm': ["rightarm", "armr", "rarm", "upperarmr", "rightupperarm", "uparmr", "ruparm", "腕r"],
    'right_elbow': ["rightelbow", "elbowr", "relbow", "lowerarmr", "rightlowerarm", "lowarmr", "rlowarm", "forearmr", "rightforearm", "ひじr"],
    'right_wrist': ["rightwrist", "wristr", "rwrist", "handr", "righthand", "rhand", "手首r"],

    # 右手指
    'thumb_1_r': ["thumb0r", "thumb1r", "thumbproximalr", "rightthumbproximal", "righthandthumb1", "親指0r"],
    'thumb_2_r': ["thumb1r", "thumb2r", "thumbintermediater", "rightthumbintermediate", "righthandthumb2", "親指1r"],
    'thumb_3_r': ["thumb2r", "thumb3r", "thumbdistalr", "rightthumbdistal", "righthandthumb3", "親指2r"],
    'index_1_r': ["indexfinger1r", "index1r", "indexproximalr", "rightindexproximal", "righthandindex1", "人指1r"],
    'index_2_r': ["indexfinger2r", "index2r", "indexintermediater", "rightindexintermediate", "righthandindex2", "人指2r"],
    'index_3_r': ["indexfinger3r", "index3r", "indexdistalr", "rightindexdistal", "righthandindex3", "人指3r"],
    'middle_1_r': ["middlefinger1r", "middle1r", "middleproximalr", "rightmiddleproximal", "righthandmiddle1", "中指1r"],
    'middle_2_r': ["middlefinger2r", "middle2r", "middleintermediater", "rightmiddleintermediate", "righthandmiddle2", "中指2r"],
    'middle_3_r': ["middlefinger3r", "middle3r", "middledistalr", "rightmiddledistal", "righthandmiddle3", "中指3r"],
    'ring_1_r': ["ringfinger1r", "ring1r", "ringproximalr", "rightringproximal", "righthandring1", "薬指1r"],
    'ring_2_r': ["ringfinger2r", "ring2r", "ringintermediater", "rightringintermediate", "righthandring2", "薬指2r"],
    'ring_3_r': ["ringfinger3r", "ring3r", "ringdistalr", "rightringdistal", "righthandring3", "薬指3r"],
    'pinkie_1_r': ["littlefinger1r", "little1r", "littleproximalr", "rightlittleproximal", "righthandlittle1", "righthandpinky1", "小指1r"],
    'pinkie_2_r': ["littlefinger2r", "little2r", "littleintermediater", "rightlittleintermediate", "righthandlittle2", "righthandpinky2", "小指2r"],
    'pinkie_3_r': ["littlefinger3r", "little3r", "littledistalr", "rightlittledistal", "righthandlittle3", "righthandpinky3", "小指3r"],

    # 下半身
    'left_leg': ["leftleg", "legl", "rleg", "upperlegl", "thighl", "leftupperleg", "uplegl", "lupleg", "leftupleg", "足l"],
    'left_knee': ["leftknee", "kneel", "lknee", "lowerlegl", "calfl", "leftlowerleg", "lowlegl", "llowleg", "ひざl"],
    'left_ankle': ["leftankle", "anklel", "rankle","leftfoot", "footl", "leftfeet", "feetleft", "lfeet", "feetl", "足首l"],
    'left_toe': ["lefttoe", "toeleft", "toel", "ltoe", "toesl", "ltoes", "足先l"],
    'right_leg': ["rightleg", "legr", "rleg", "upperlegr", "thighr", "rightupperleg", "uplegr", "rupleg", "rightupleg", "足r"],
    'right_knee': ["rightknee", "kneer", "rknee", "lowerlegr", "calfr", "rightlowerleg", "lowlegr", "rlowleg", "ひざr"],
    'right_ankle': ["rightankle", "ankler", "rankle", "rightfoot", "footr", "rightfeet", "feetright", "rfeet", "feetr", "足首r"],
    'right_toe': ["righttoe", "toeright", "toer", "rtoe", "toesr", "rtoes", "足先r"],
}

# 检索使用关键字，忽略大小写，存在误差
Jigglebone_list = {'wing','ribbon','ear','tail','apron','breast','bust','Cloak','Anchor','ahoge','bangs','outer','shirt','butt','hat','bell','belt','coat','band','droopy','halo','tag','飾','インナーたれ','尻','胸','耳','xz','yxz','Pendant','Strap','袖','帯','繩','背','結','面具','shawl','bag','acc'}

skirt_list = {'skirt','スカート','qz','裙子','qunzi'}

hair_list = {'hair','髪','tj','髮','头发','tf','toufa'}

