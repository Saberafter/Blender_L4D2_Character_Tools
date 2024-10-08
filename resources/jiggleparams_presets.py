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

presets = {
    "base": {
        "is_flexible": True,
        "has_base_spring": False,
        "enable_length": True,
        "length": 30.0,
        "enable_tip_mass": True,
        "tip_mass": 200.0,
        "enable_pitch_stiffness": True,
        "pitch_stiffness": 50.0,
        "enable_pitch_damping": True,
        "pitch_damping": 7.0,
        "enable_pitch_constraint": False,
        "pitch_constraint": [
            0.0,
            0.0
        ],
        "enable_pitch_friction": False,
        "pitch_friction": 0.0,
        "enable_yaw_stiffness": True,
        "yaw_stiffness": 50.0,
        "enable_yaw_damping": True,
        "yaw_damping": 7.0,
        "enable_yaw_constraint": False,
        "yaw_constraint": [
            0.0,
            0.0
        ],
        "enable_yaw_friction": False,
        "yaw_friction": 0.0,
        "enable_allow_length_flex": False,
        "enable_along_stiffness": True,
        "along_stiffness": 100.0,
        "enable_along_damping": True,
        "along_damping": 0.0,
        "enable_angle_constraint": True,
        "angle_constraint": 35.0
    },
    "breast_natural": {
        "is_flexible": True,
        "has_base_spring": True,
        "enable_length": True,
        "length": 10.0,
        "enable_tip_mass": True,
        "tip_mass": 5.0,
        "enable_pitch_stiffness": True,
        "pitch_stiffness": 44.0,
        "enable_pitch_damping": True,
        "pitch_damping": 7.0,
        "enable_pitch_constraint": False,
        "pitch_constraint": [
            0.0,
            0.0
        ],
        "enable_pitch_friction": False,
        "pitch_friction": 0.0,
        "enable_yaw_stiffness": True,
        "yaw_stiffness": 44.0,
        "enable_yaw_damping": True,
        "yaw_damping": 7.0,
        "enable_yaw_constraint": False,
        "yaw_constraint": [
            0.0,
            0.0
        ],
        "enable_yaw_friction": False,
        "yaw_friction": 0.0,
        "enable_allow_length_flex": False,
        "enable_along_stiffness": False,
        "along_stiffness": 100.0,
        "enable_along_damping": False,
        "along_damping": 0.0,
        "enable_angle_constraint": True,
        "angle_constraint": 5.0,
        "enable_stiffness": True,
        "stiffness": 255.0,
        "enable_damping": True,
        "damping": 8.0,
        "enable_left_constraint": True,
        "left_constraint": [
            -0.15000000596046448,
            0.15000000596046448
        ],
        "enable_left_friction": True,
        "left_friction": 0.009999999776482582,
        "enable_up_constraint": True,
        "up_constraint": [
            -0.15000000596046448,
            0.15000000596046448
        ],
        "enable_up_friction": True,
        "up_friction": 0.009999999776482582,
        "enable_forward_constraint": True,
        "forward_constraint": [
            -0.009999999776482582,
            0.009999999776482582
        ],
        "enable_forward_friction": True,
        "forward_friction": 0.05000000074505806,
        "enable_base_mass": True,
        "base_mass": 1.0
    },
    "butt": {
        "is_flexible": True,
        "has_base_spring": True,
        "enable_length": True,
        "length": 10.0,
        "enable_tip_mass": True,
        "tip_mass": 10.0,
        "enable_pitch_stiffness": True,
        "pitch_stiffness": 120.0,
        "enable_pitch_damping": True,
        "pitch_damping": 4.0,
        "enable_pitch_constraint": False,
        "pitch_constraint": [
            0.0,
            0.0
        ],
        "enable_pitch_friction": False,
        "pitch_friction": 0.0,
        "enable_yaw_stiffness": True,
        "yaw_stiffness": 120.0,
        "enable_yaw_damping": True,
        "yaw_damping": 4.0,
        "enable_yaw_constraint": False,
        "yaw_constraint": [
            0.0,
            0.0
        ],
        "enable_yaw_friction": False,
        "yaw_friction": 0.0,
        "enable_allow_length_flex": True,
        "enable_along_stiffness": True,
        "along_stiffness": 100.0,
        "enable_along_damping": True,
        "along_damping": 0.0,
        "enable_angle_constraint": True,
        "angle_constraint": 12.5,
        "enable_stiffness": True,
        "stiffness": 100.0,
        "enable_damping": True,
        "damping": 3.0,
        "enable_left_constraint": True,
        "left_constraint": [
            -0.30000001192092896,
            0.30000001192092896
        ],
        "enable_left_friction": True,
        "left_friction": 0.0,
        "enable_up_constraint": True,
        "up_constraint": [
            -0.30000001192092896,
            0.30000001192092896
        ],
        "enable_up_friction": True,
        "up_friction": 0.0,
        "enable_forward_constraint": True,
        "forward_constraint": [
            -0.30000001192092896,
            0.30000001192092896
        ],
        "enable_forward_friction": True,
        "forward_friction": 0.0,
        "enable_base_mass": True,
        "base_mass": 0.0
    },
    "hair_root": {
        "is_flexible": True,
        "has_base_spring": False,
        "enable_length": True,
        "length": 30.0,
        "enable_tip_mass": True,
        "tip_mass": 50.0,
        "enable_pitch_stiffness": True,
        "pitch_stiffness": 50.0,
        "enable_pitch_damping": True,
        "pitch_damping": 7.0,
        "enable_pitch_constraint": False,
        "pitch_constraint": [
            0.0,
            0.0
        ],
        "enable_pitch_friction": False,
        "pitch_friction": 0.0,
        "enable_yaw_stiffness": True,
        "yaw_stiffness": 50.0,
        "enable_yaw_damping": True,
        "yaw_damping": 7.0,
        "enable_yaw_constraint": False,
        "yaw_constraint": [
            0.0,
            0.0
        ],
        "enable_yaw_friction": False,
        "yaw_friction": 0.0,
        "enable_allow_length_flex": False,
        "enable_along_stiffness": True,
        "along_stiffness": 100.0,
        "enable_along_damping": True,
        "along_damping": 0.0,
        "enable_angle_constraint": True,
        "angle_constraint": 10.0
    },
    "halo": {
        "is_flexible": True,
        "has_base_spring": True,
        "enable_length": True,
        "length": 5.0,
        "enable_tip_mass": True,
        "tip_mass": 0.0,
        "enable_pitch_stiffness": True,
        "pitch_stiffness": 1.0,
        "enable_pitch_damping": True,
        "pitch_damping": 10.0,
        "enable_pitch_constraint": True,
        "pitch_constraint": [
            -5.0,
            5.0
        ],
        "enable_pitch_friction": False,
        "pitch_friction": 0.0,
        "enable_yaw_stiffness": True,
        "yaw_stiffness": 1.0,
        "enable_yaw_damping": True,
        "yaw_damping": 10.0,
        "enable_yaw_constraint": True,
        "yaw_constraint": [
            -5.0,
            5.0
        ],
        "enable_yaw_friction": False,
        "yaw_friction": 0.0,
        "enable_allow_length_flex": True,
        "enable_along_stiffness": True,
        "along_stiffness": 1.0,
        "enable_along_damping": True,
        "along_damping": 10.0,
        "enable_angle_constraint": False,
        "angle_constraint": 5.0,
        "enable_stiffness": True,
        "stiffness": 50.0,
        "enable_damping": True,
        "damping": 7.0,
        "enable_left_constraint": True,
        "left_constraint": [
            -16.0,
            16.0
        ],
        "enable_left_friction": False,
        "left_friction": 0.009999999776482582,
        "enable_up_constraint": True,
        "up_constraint": [
            -16.0,
            16.0
        ],
        "enable_up_friction": False,
        "up_friction": 0.009999999776482582,
        "enable_forward_constraint": True,
        "forward_constraint": [
            -16.0,
            3.0
        ],
        "enable_forward_friction": False,
        "forward_friction": 0.05000000074505806,
        "enable_base_mass": False,
        "base_mass": 1.0
    }
}