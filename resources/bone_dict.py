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
    'ValveBiped.Bip01_Pelvis': ['Hips', '下半身', 'hips'],
    'ValveBiped.Bip01_Spine': ['Spine', '上半身', 'spine'],
    'ValveBiped.Bip01_Spine1': ['Spine', '上半身', 'spine'],
    'ValveBiped.Bip01_Spine2': ['Spine', '上半身', 'spine'],
    'ValveBiped.Bip01_Spine4': ['Chest', '上半身2', 'chest'],
    'ValveBiped.Bip01_Neck1': ['Neck', '首', 'neck'],
    'ValveBiped.Bip01_Head1': ['Head', '頭', 'head'],
    # 左
    'ValveBiped.Bip01_L_Clavicle': [
        'Shoulder_L_1',
        'Left shoulder',
        '肩.L',
        'Shoulder_L',
        'Shoulder.L',
        'LeftShoulder',
        'left_shoulder',
        ],

    'ValveBiped.Bip01_L_UpperArm': [
        'UpperArm_L_1',
        'Left arm',
        '腕.L',
        'UpperArm_L',
        'Upper_arm.L',
        'Upperarm.L',
        'LeftUpperArm',
        'left_arm',
        ],

    'ValveBiped.Bip01_L_Forearm': [
        'LowerArm_L_1',
        'Left elbow',
        'ひじ.L',
        'LowerArm_L',
        'Lower_arm.L',
        'Lowerarm.L',
        'LeftLowerArm',
        'left_elbow',
        ],

    'ValveBiped.Bip01_L_Hand': [
        'Hand_L_1',
        'Left wrist',
        '手首.L',
        'Hand_L',
        'Hand.L',
        'LeftHand',
        'left_wrist',
        ],

    'ValveBiped.Bip01_L_Finger0': [
        'ThumbProximal_L_1',
        'Thumb0_L',
        '親指０.L',
        'ThumbProximal_L',
        'Thumb Proximal.L',
        'ThumbProximal.L',
        'Thumb_Proximal.L',
        'Thumb_Proximal_L',
        'LeftThumbProximal',
        'thumb_1_l',
        ],

    'ValveBiped.Bip01_L_Finger01': [
        'ThumbIntermediate_L_1',
        'Thumb1_L',
        '親指１.L',
        'ThumbIntermediate_L',
        'Thumb Intermediate.L',
        'ThumbIntermediate.L',
        'Thumb_Intermediate.L',
        'Thumb_Intermediate_L',
        'LeftThumbIntermediate',
        'thumb_2_l',
        ],

    'ValveBiped.Bip01_L_Finger02': [
        'ThumbDistal_L_1',
        'Thumb2_L',
        '親指２.L',
        'ThumbDistal_L',
        'Thumb Distal.L',
        'ThumbDistal.L',
        'Thumb_Distal.L',
        'Thumb_Distal_L',
        'LeftThumbDistal',
        'thumb_3_l',
        ],

    'ValveBiped.Bip01_L_Finger1': [
        'IndexProximal_L_1',
        'IndexFinger1_L',
        '人指１.L',
        'IndexProximal_L',
        'Index Proximal.L',
        'IndexProximal.L',
        'Index_Proximal.L',
        'Index_Proximal_L',
        'LeftIndexProximal',
        'index_1_l',
        ],

    'ValveBiped.Bip01_L_Finger11': [
        'IndexIntermediate_L_1',
        'IndexFinger2_L',
        '人指２.L',
        'IndexIntermediate_L',
        'Index Intermediate.L',
        'IndexIntermediate.L',
        'Index_Intermediate.L',
        'Index_Intermediate_L',
        'LeftIndexIntermediate',
        'index_2_l',
        ],

    'ValveBiped.Bip01_L_Finger12': [
        'IndexDistal_L_1',
        'IndexFinger3_L',
        '人指３.L',
        'IndexDistal_L',
        'Index Distal.L',
        'IndexDistal.L',
        'Index_Distal.L',
        'Index_Distal_L',
        'LeftIndexDistal',
        'index_3_l',
        ],

    'ValveBiped.Bip01_L_Finger2': [
        'MiddleProximal_L_1',
        'MiddleFinger1_L',
        '中指１.L',
        'MiddleProximal_L',
        'Middle Proximal.L',
        'MiddleProximal.L',
        'Middle_Proximal.L',
        'Middle_Proximal_L',
        'LeftMiddleProximal',
        'middle_1_l',
        ],

    'ValveBiped.Bip01_L_Finger21': [
        'MiddleIntermediate_L_1',
        'MiddleFinger2_L',
        '中指２.L',
        'MiddleIntermediate_L',
        'Middle Intermediate.L',
        'MiddleIntermediate.L',
        'Middle_Intermediate.L',
        'Middle_Intermediate_L',
        'LeftMiddleIntermediate',
        'middle_2_l',
        ],

    'ValveBiped.Bip01_L_Finger22': [
        'MiddleDistal_L_1',
        'MiddleFinger3_L',
        '中指３.L',
        'MiddleDistal_L',
        'Middle Distal.L',
        'MiddleDistal.L',
        'Middle_Distal.L',
        'Middle_Distal_L',
        'LeftMiddleDistal',
        'middle_3_l',
        ],

    'ValveBiped.Bip01_L_Finger3': [
        'RingProximal_L_1',
        'RingFinger1_L',
        '薬指１.L',
        'RingProximal_L',
        'Ring Proximal.L',
        'RingProximal.L',
        'Ring_Proximal.L',
        'Ring_Proximal_L',
        'LeftRingProximal',
        'ring_1_l',
        ],

    'ValveBiped.Bip01_L_Finger31': [
        'RingIntermediate_L_1',
        'RingFinger2_L',
        '薬指２.L',
        'RingIntermediate_L',
        'Ring Intermediate.L',
        'RingIntermediate.L',
        'Ring_Intermediate.L',
        'Ring_Intermediate_L',
        'LeftRingIntermediate',
        'ring_2_l',
        ],

    'ValveBiped.Bip01_L_Finger32': [
        'RingDistal_L_1',
        'RingFinger3_L',
        '薬指３.L',
        'RingDistal_L',
        'Ring Distal.L',
        'RingDistal.L',
        'Ring_Distal.L',
        'Ring_Distal_L',
        'LeftRingDistal',
        'ring_3_l',
        ],

    'ValveBiped.Bip01_L_Finger4': [
        'LittleProximal_L_1',
        'LittleFinger1_L',
        '小指１.L',
        'LittleProximal_L',
        'Little Proximal.L',
        'LittleProximal.L',
        'Little_Proximal.L',
        'Little_Proximal_L',
        'LeftLittleProximal',
        'pinkie_1_l',
        ],

    'ValveBiped.Bip01_L_Finger41': [
        'LittleIntermediate_L_1',
        'LittleFinger2_L',
        '小指２.L',
        'LittleIntermediate_L',
        'Little Intermediate.L',
        'LittleIntermediate.L',
        'Little_Intermediate.L',
        'Little_Intermediate_L',
        'LeftLittleIntermediate',
        'pinkie_2_l',
        ],

    'ValveBiped.Bip01_L_Finger42': [
        'LittleDistal_L_1',
        'LittleFinger3_L',
        '小指３.L',
        'LittleDistal_L',
        'Little Distal.L',
        'LittleDistal.L',
        'Little_Distal.L',
        'Little_Distal_L',
        'LeftLittleDistal',
        'pinkie_3_l',
        ],
    # 右
    'ValveBiped.Bip01_R_Clavicle': [
        'Shoulder_R_1',
        'Right shoulder',
        '肩.R',
        'Shoulder_R',
        'Shoulder.R',
        'RightShoulder',
        'right_shoulder',
        ],

    'ValveBiped.Bip01_R_UpperArm': [
        'UpperArm_R_1',
        'Right arm',
        '腕.R',
        'UpperArm_R',
        'Upper_arm.R',
        'UpperArm.R',
        'RightUpperArm',
        'right_arm',
        ],

    'ValveBiped.Bip01_R_Forearm': [
        'LowerArm_R_1',
        'Right elbow',
        'ひじ.R',
        'LowerArm_R',
        'Lower_arm.R',
        'LowerArm.R',
        'RightLowerArm',
        'right_elbow',
        ],

    'ValveBiped.Bip01_R_Hand': [
        'Hand_R_1',
        'Right wrist',
        '手首.R',
        'Hand_R',
        'Hand.R',
        'RightHand',
        'right_wrist',
        ],

    'ValveBiped.Bip01_R_Finger0': [
        'ThumbProximal_R_1',
        'Thumb0_R',
        '親指０.R',
        'ThumbProximal_R',
        'Thumb Proximal.R',
        'ThumbProximal.R',
        'Thumb_Proximal.R',
        'Thumb_Proximal_R',
        'RightThumbProximal',
        'thumb_1_r',
        ],

    'ValveBiped.Bip01_R_Finger01': [
        'ThumbIntermediate_R_1',
        'Thumb1_R',
        '親指１.R',
        'ThumbIntermediate_R',
        'Thumb Intermediate.R',
        'ThumbIntermediate.R',
        'Thumb_Intermediate.R',
        'Thumb_Intermediate_R',
        'RightThumbIntermediate',
        'thumb_2_r',
        ],
    'ValveBiped.Bip01_R_Finger02': [
        'ThumbDistal_R_1',
        'Thumb2_R',
        '親指２.R',
        'ThumbDistal_R',
        'Thumb Distal.R',
        'ThumbDistal.R',
        'Thumb_Distal.R',
        'Thumb_Distal_R',
        'RightThumbDistal',
        'thumb_3_r',
        ],

    'ValveBiped.Bip01_R_Finger1': [
        'IndexProximal_R_1',
        'IndexFinger1_R',
        '人指１.R',
        'IndexProximal_R',
        'Index Proximal.R',
        'IndexProximal.R',
        'Index_Proximal.R',
        'Index_Proximal_R',
        'RightIndexProximal',
        'index_1_r',
        ],

    'ValveBiped.Bip01_R_Finger11': [
        'IndexIntermediate_R_1',
        'IndexFinger2_R',
        '人指２.R',
        'IndexIntermediate_R',
        'Index Intermediate.R',
        'IndexIntermediate.R',
        'Index_Intermediate.R',
        'Index_Intermediate_R',
        'RightIndexIntermediate',
        'index_2_r',
        ],
    'ValveBiped.Bip01_R_Finger12': [
        'IndexDistal_R_1',
        'IndexFinger3_R',
        '人指３.R',
        'IndexDistal_R',
        'Index Distal.R',
        'IndexDistal.R',
        'Index_Distal.R',
        'Index_Distal_R',
        'RightIndexDistal',
        'index_3_r',
        ],
    'ValveBiped.Bip01_R_Finger2': [
        'MiddleProximal_R_1',
        'MiddleFinger1_R',
        '中指１.R',
        'MiddleProximal_R',
        'Middle Proximal.R',
        'MiddleProximal.R',
        'Middle_Proximal.R',
        'Middle_Proximal_R',
        'RightMiddleProximal',
        'middle_1_r',
        ],

    'ValveBiped.Bip01_R_Finger21': [
        'MiddleIntermediate_R_1',
        'MiddleFinger2_R',
        '中指２.R',
        'MiddleIntermediate_R',
        'Middle Intermediate.R',
        'MiddleIntermediate.R',
        'Middle_Intermediate.R',
        'Middle_Intermediate_R',
        'RightMiddleIntermediate',
        'middle_2_r',
        ],

    'ValveBiped.Bip01_R_Finger22': [
        'MiddleDistal_R_1',
        'MiddleFinger3_R',
        '中指３.R',
        'MiddleDistal_R',
        'Middle Distal.R',
        'MiddleDistal.R',
        'Middle_Distal.R',
        'Middle_Distal_R',
        'RightMiddleDistal',
        'middle_3_r',
        ],

    'ValveBiped.Bip01_R_Finger3': [
        'RingProximal_R_1',
        'RingFinger1_R',
        '薬指１.R',
        'RingProximal_R',
        'Ring Proximal.R',
        'RingProximal.R',
        'Ring_Proximal.R',
        'Ring_Proximal_R',
        'RightRingProximal',
        'ring_1_r',
        ],

    'ValveBiped.Bip01_R_Finger31': [
        'RingIntermediate_R_1',
        'RingFinger2_R',
        '薬指２.R',
        'RingIntermediate_R',
        'Ring Intermediate.R',
        'RingIntermediate.R',
        'Ring_Intermediate.R',
        'Ring_Intermediate_R',
        'RightRingIntermediate',
        'ring_2_r',
        ],

    'ValveBiped.Bip01_R_Finger32': [
        'RingDistal_R_1',
        'RingFinger3_R',
        '薬指３.R',
        'RingDistal_R',
        'Ring Distal.R',
        'RingDistal.R',
        'Ring_Distal.R',
        'Ring_Distal_R',
        'RightRingDistal',
        'ring_3_r',
        ],

    'ValveBiped.Bip01_R_Finger4': [
        'LittleProximal_R_1',
        'LittleFinger1_R',
        '小指１.R',
        'LittleProximal_R',
        'Little Proximal.R',
        'LittleProximal.R',
        'Little_Proximal.R',
        'Little_Proximal_R',
        'RightLittleProximal',
        'pinkie_1_r',
        ],

    'ValveBiped.Bip01_R_Finger41': [
        'LittleIntermediate_R_1',
        'LittleFinger2_R',
        '小指２.R',
        'LittleIntermediate_R',
        'Little Intermediate.R',
        'LittleIntermediate.R',
        'Little_Intermediate.R',
        'Little_Intermediate_R',
        'RightLittleIntermediate',
        'pinkie_2_r',
        ],

    'ValveBiped.Bip01_R_Finger42': [
        'LittleDistal_R_1',
        'LittleFinger3_R',
        '小指３.R',
        'LittleDistal_R',
        'Little Distal.R',
        'LittleDistal.R',
        'Little_Distal.R',
        'Little_Distal_R',
        'RightLittleDistal',
        'pinkie_3_r',
        ],
    # 下半身
    'ValveBiped.Bip01_L_Thigh': [
        'UpperLeg_L_1',
        'Left leg',
        '足.L',
        'UpperLeg_L',
        'Upper_leg.L',
        'Upperleg.L',
        'LeftUpperLeg',
        'left_leg',
        ],

    'ValveBiped.Bip01_L_Calf': [
        'LowerLeg_L_1',
        'Left knee',
        'ひざ.L',
        'LowerLeg_L',
        'Lower_leg.L',
        'Lowerleg.L',
        'LeftLowerLeg',
        'left_knee',
        ],

    'ValveBiped.Bip01_L_Foot': [
        'Foot_L_1',
        'Left ankle',
        '足首.L',
        'Foot_L',
        'Foot.L',
        'LeftFoot',
        'left_ankle',
        ],

    'ValveBiped.Bip01_L_Toe0': [
        'Toe_L_1',
        'Left toe',
        '足先EX.L',
        'Toe_L',
        'Toe.L',
        'Left Toe',
        'LeftToeBase',
        'left_toe',
        ],

    'ValveBiped.Bip01_R_Thigh': [
        'UpperLeg_R_1',
        'Right leg',
        '足.R',
        'UpperLeg_R',
        'Upper_leg.R',
        'UpperLeg.R',
        'UpperLeg_R',
        'RightUpperLeg',
        'right_leg',
        ],

    'ValveBiped.Bip01_R_Calf': [
        'LowerLeg_R_1',
        'Right knee',
        'ひざ.R',
        'LowerLeg_R',
        'Lower_leg.R',
        'LowerLeg.R',
        'LowerLeg_R',
        'RightLowerLeg',
        'right_knee',
        ],

    'ValveBiped.Bip01_R_Foot': [
        'Foot_R_1',
        'Right ankle',
        '足首.R',
        'Foot_R',
        'Foot.R',
        'RightFoot',
        'right_ankle',
        ],

    'ValveBiped.Bip01_R_Toe0': [
        'Toe_R_1',
        'Right toe',
        '足先EX.R',
        'Toe_R',
        'Toe.R',
        'Right Toe',
        'RightToeBase',
        'right_toe',
        ],
}
# Bone names from https://github.com/triazo/immersive_scaler/
bone_names = {
    'hips': ["pelvis", "hips"],
    'spine': ["torso", "spine"],
    'chest': ["chest", "upperchest"],
    #'upper_chest': ["upperchest"],
    'neck': ["neck", "neck1"],
    'head': ["head", "head1"],
    #'left_eye': ["eyeleft", "lefteye", "eyel", "leye"],
    #'right_eye': ["eyeright", "righteye", "eyer", "reye"],    

    "left_shoulder": ["leftshoulder", "shoulderl", "lshoulder"],
    "left_arm": ["leftarm", "arml", "rarm", "upperarml", "leftupperarm", "uparml", "luparm"],
    "left_elbow": ["leftelbow", "elbowl", "relbow", "lowerarml", "leftlowerarm", "lowarml", "llowarm", "forearml",],
    "left_wrist": ["leftwrist", "wristl", "rwrist", "handl", "lefthand", "lhand"],

    "thumb_1_l": ['thumb0l'],
    "thumb_2_l": ['thumb1l'],
    "thumb_3_l": ['thumb2l'],

    "index_1_l": ["indexfinger1l"],
    "index_2_l": ["indexfinger2l"],
    "index_3_l": ["indexfinger3l"],

    "middle_1_l": ["middlefinger1l"],
    "middle_2_l": ["middlefinger2l"],
    "middle_3_l": ["middlefinger3l"],

    "ring_1_l": ["ringfinger1l"],
    "ring_2_l": ["ringfinger2l"],
    "ring_3_l": ["ringfinger3l"],

    "pinkie_1_l": ["littlefinger1l"],
    "pinkie_2_l": ["littlefinger2l"],
    "pinkie_3_l": ["littlefinger3l"],

    "right_shoulder": ["rightshoulder", "shoulderr", "rshoulder"],
    "right_arm": ["rightarm", "armr", "rarm", "upperarmr", "rightupperarm", "uparmr", "ruparm"],
    "right_elbow": ["rightelbow", "elbowr", "relbow", "lowerarmr", "rightlowerarm", "lowarmr", "rlowarm", "forearmr",],
    "right_wrist": ["rightwrist", "wristr", "rwrist", "handr", "righthand", "rhand"],

    "thumb_1_r": ['thumb0r'],
    "thumb_2_r": ['thumb1r'],
    "thumb_3_r": ['thumb2r'],

    "index_1_r": ["indexfinger1r"],
    "index_2_r": ["indexfinger2r"],
    "index_3_r": ["indexfinger3r"],

    "middle_1_r": ["middlefinger1r"],
    "middle_2_r": ["middlefinger2r"],
    "middle_3_r": ["middlefinger3r"],

    "ring_1_r": ["ringfinger1r"],
    "ring_2_r": ["ringfinger2r"],
    "ring_3_r": ["ringfinger3r"],

    "pinkie_1_r": ["littlefinger1r"],
    "pinkie_2_r": ["littlefinger2r"],
    "pinkie_3_r": ["littlefinger3r"],

    "left_leg": ["leftleg", "legl", "rleg", "upperlegl", "thighl","leftupperleg", "uplegl", "lupleg"],
    "left_knee": ["leftknee", "kneel", "rknee", "lowerlegl", "calfl", "leftlowerleg", 'lowlegl', 'llowleg'],
    "left_ankle": ["leftankle", "anklel", "rankle", "leftfoot", "footl", "leftfoot", "leftfeet", "feetleft", "lfeet", "feetl"],
    "left_toe": ["lefttoe", "toeleft", "toel", "ltoe", "toesl", "ltoes"],

    "right_leg": ["rightleg", "legr", "rleg", "upperlegr", "thighr", "rightupperleg", "uplegr", "rupleg"],
    "right_knee": ["rightknee", "kneer", "rknee", "lowerlegr", "calfr", "rightlowerleg", "lowlegr", "rlowleg"],
    "right_ankle": ["rightankle", "ankler", "rankle", "rightfoot", "footr", "rightfoot", "rightfeet", "feetright", "rfeet", "feetr"],
    "right_toe": ["righttoe", "toeright", "toer", "rtoe", "toesr", "rtoes"],
}

# 检索使用关键字，忽略大小写，存在误差
Jigglebone_list = {'wing','ribbon','ear','tail','apron','breast','bust','Cloak','Anchor','ahoge','bangs','outer','shirt','butt','hat','bell','belt','coat','band','droopy','halo','tag','飾','インナーたれ','尻','胸','耳','xz','yxz','Pendant','Strap','袖','帯','繩','背','結','面具','shawl','bag','acc'}

skirt_list = {'skirt','スカート','qz','裙子','qunzi'}

hair_list = {'hair','髪','tj','髮','头发','tf','toufa'}

