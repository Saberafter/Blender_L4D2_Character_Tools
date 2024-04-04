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

# 这里存储了做表情vta使用的形态键字典，其中包含形态键的名称和它们的可能混合值
# 左侧为vta使用的新形态键名称，数字对应表情模板的排序
# 右侧括号内可添加对应形态键的混合变形数值

mix_dict = {
    "default": [],# 空
    "upper_right": [{"eye_joy_R": 1},{"ウィンク右": 1},{"ｳｨﾝｸ２右": 1},{"ウインク２右": 1},{"ウインク右": 1}],# 右闭眼
    "lower_right": [{"びっくり右": 1.0}],# 右抬眼
    "upper_left": [{"eye_joy_L": 1},{"ウィンク": 1},{"ウィンク２": 1},{"ウインク２": 1},{"ウインク": 1}],# 左闭眼
    "lower_left": [{"びっくり左": 1.0}],# 左抬眼
    "AU12": [{"口角上げ": 1},{"にやり": 1},{"mouth_smile": 1}],# 嘴角微微上扬(闭嘴笑)
    "AU12+": [{"ω": 1},{"mouth_ω": 1}],# 轻轻裂开嘴上扬(咧嘴笑)
    "AU12AU25": [{"▲": 1},{"mouth_△": 1},{"△くち": 1},{"△": 1}],# 微微裂开嘴(咧嘴笑+)
    "AU15": [{"口角下げ": 1},{"mouth_sad": 1}],# 下弯曲嘴
    "AU17": [{"∧": 1},{"mouth_∧": 1},{"Λ": 1}],# 下弯曲+左右收缩嘴(噘嘴)
    "AU10": [{"mouth_v": 1},{"にっこり": 1},{"にやり": 1},{"口角上げ": 1}],# 嘴V型笑(生气龇牙)
    "AU16": [{"mouth_i 3 (no tooth)": 1},{"ワ1": 1},{"い２": 1},{"へへへ": 1},{"にやり": 0.5,"あ": 0.15},{"口角上げ": 0.5,"あ": 0.15}],# 微微咧嘴笑(额)
    "AU25": [{"vrc.v_ih": 1},{"あ": 0.5}],# 半张口		louis_no
    "AU18": [{"vrc.v_oh": 1},{"お": 1},{"mouth_o": 1}],# O型嘴(嘟凸嘴)		louis_no
    "AU18+": [{"vrc.v_ou": 1},{"う": 1}],# 窄O型嘴
    "AU22": [{"vrc.v_oh": 0.8},{"お": 0.75}],# 扁O型嘴
    "AU20": [{"mouth_~": 1},{"口角広げ": 0.75},{"mouth_wide": 0.75},{"口_横幅1": 1}],# 嘴角左右扩抿嘴
    "AU32": [{"vrc.v_ff": 1},{"え": 0.25}],# 轻轻裂开嘴(咬牙切齿) 	coach&louis_no
    "AU26": [{"mouth_a": 1},{"vrc.v_aa": 1},{"あ２": 1},{"あ": 1}],# 张大口(垮下巴)
    "AU27": [{"vrc.v_aa": 0.7},{"あ": 0.7}],# 张口
    "AU26Z": [{"vrc.v_th": 1},{"よだれ": 1},{"え": 1}],# 张小口
    "AU1": [{"困る": 1},{"brow_sad": 1}],# 眉毛无奈八字下弯
    "AU2": [{"眉_斜め2": 1},{"brow_tsuri": 1},{"怒り": 1},{"真面目": 1}],# 眉毛皱眉倒八字弯曲
    "AU4": [{"怒り": 1},{"brow_anger": 1},{"真面目": 1}],# 眉毛生气倒八字弯曲
    "AU1AU2": [{"上": 1},{"brow_up": 1},{"眉_上": 1},{"眉上": 1}],# 眉毛上抬
    "AU42": [{"upper_right": 1,"upper_left": 1}], # 眨眼
    "AU45": [{"AU42": 1},], # 眨眼
    "f00": [{"Basis": 1},], # 眨眼
    "f01": [{"AU45": 1}], # 眨眼
    "f02": [], # 抬眼,下眼睑↑
    "f03": [], # 低眼,下眼睑↓
    "f04": [], # 半眯眼 
    "AU17D": [], # 收下唇抿嘴
    "AU6": [], # 痛苦半眯眼
    "AU9": [], # 提鼻子嘴巴
    "AU38": [], # 收鼻子
    "AU24": [], # 收嘴唇抿嘴
    "AU31": [], # 收下巴
    "AU27Z": [], # 张大口
    "AU30L": [], # 下巴左挪
    "AU30R": [], # 下巴右挪
    "AU1AU4": [], # 眉毛无奈八字下弯+
    "AU2AU4": [], # 眉毛生气倒八字弯曲-
    "AU6Z": [], # 痛苦半眯眼+
    "AU18Z": [{"vrc.v_ou": 1},{"う": 1}],# 窄凸O型嘴
    "AU22Z": [{"vrc.v_oh": 0.8},{"お": 0.75}],# 扁凸O型嘴
    "AU13": [], # 脸颊鼓气
    "AD96L": [], # 左歪嘴
    "AD96R": [], # 右歪嘴
    "AU5": [],
    "AU7": []
}

key_notes = {
    "default": "空",
    "upper_right": "右闭眼",
    "lower_right": "右抬眼",
    "upper_left": "左闭眼",
    "lower_left": "左抬眼",
    "AU12": "嘴角微微上扬(闭嘴笑)",
    "AU12+": "轻轻裂开嘴上扬(咧嘴笑)",
    "AU12AU25": "微微裂开嘴(咧嘴笑+)",
    "AU15": "下弯曲嘴",
    "AU17": "下弯曲+左右收缩嘴(噘嘴)",
    "AU10": "嘴V型笑(生气龇牙)",
    "AU16": "微微咧嘴笑(额)",
    "AU25": "半张口",
    "AU18": "O型嘴(嘟凸嘴)",
    "AU18+": "窄O型嘴",
    "AU22": "扁O型嘴",
    "AU20": "嘴角左右扩抿嘴",
    "AU32": "轻轻裂开嘴(咬牙切齿)",
    "AU26": "张大口(垮下巴)",
    "AU27": "张口",
    "AU26Z": "张小口",
    "AU1": "眉毛无奈八字下弯",
    "AU2": "眉毛皱眉倒八字弯曲",
    "AU4": "眉毛生气倒八字弯曲",
    "AU1AU2": "眉毛上抬",
    "AU42": "闭眼",
    "AU45": "闭眼",
    "f00": "",
    "f01": "闭眼",
    "f02": "抬眼,下眼睑↑",
    "f03": "低眼,下眼睑↓",
    "f04": "半眯眼 ", 
    "AU17D": "收下唇抿嘴",
    "AU6": "痛苦半眯眼",
    "AU9": "提鼻子嘴巴",
    "AU38": "收鼻子",
    "AU24": "收嘴唇抿嘴",
    "AU31": "收下巴",
    "AU27Z": "张大口",
    "AU30L": "下巴左挪",
    "AU30R": "下巴右挪",
    "AU1AU4": "眉毛无奈八字下弯+",
    "AU2AU4": "眉毛生气倒八字弯曲-",
    "AU6Z": "痛苦半眯眼+",
    "AU18Z": "窄凸O型嘴",
    "AU22Z": "扁凸O型嘴",
    "AU13": "脸颊鼓气",
    "AD96L": "左歪嘴",
    "AD96R": "右歪嘴",
    "AU5": "抬眼",
    "AU7": "下眼睑↑"
}