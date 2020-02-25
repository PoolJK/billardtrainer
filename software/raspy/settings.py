"""
Some settings to evaluate on runtime to be accessed across all modules
"""

on_raspy = False
on_win = False
debugging = True
debug_level = 1
#: x resolution of beamer in pixels
beamer_resolution_x = 1280
#: y resolution of beamer in pixels
beamer_resolution_y = 720
#: resolution of beamer in pixels per mm
beamer_pix_per_mm = 206 / 170
#: x offset of beamer from table mid point in mm
beamer_offset_x = 0  # 1000
#: y offset of beamer from table mid point in mm
beamer_offset_y = 0  # -100
#: rotation of beamer relative to table
beamer_rotation = 0
#: x resolution of camera image in pixels
camera_resolution_x = 1280
#: y resolution of camera image in pixels
camera_resolution_y = 720
#: x offset of camera from table mid point in mm
camera_offset_x = 0  # 1000
#: y offset of camera from table mid point in mm
camera_offset_y = 0  # -100
#: rotation off camera to table
camera_rotation = 0
#: resolution of camera at mounted height
camera_pix_per_mm = 1.21
#: mounted height of camera lens in mm
camera_mount_height = 927.0