#pragma once

inline constexpr static double pi = 3.141592653589793238462643383279; // should be enough yeah?
inline constexpr static double delta_time = 0.016666699201;
inline constexpr static double max_angle_change_inv_speed_factor = 480.0;
inline constexpr static double min_speed = 64.0;
inline constexpr static double max_speed = 320.0;
inline constexpr static double decel = 165.0;
inline constexpr static double fast_decel = 220.0;
inline constexpr static double accel = 90.0;
inline constexpr static double stable_angle = 0.2;
inline constexpr static double angle_range = 2.0;
inline constexpr static double rad_to_deg = 180.0 / pi;
inline constexpr static double deg_to_rad = pi / 180.0;
inline constexpr static double stable_angle_deg = stable_angle * rad_to_deg;